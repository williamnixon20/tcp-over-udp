import os
import socket
import threading
import struct
from lib.connection import Connection

from lib.segment import Segment, SegmentFlag
from src.node import Node

class Server(Node):
    def __init__(self, broadcast_port, source_file_path):
        super().__init__()
        self.broadcast_port = broadcast_port
        self.source_file_path = source_file_path
        self.clients = []

    def run(self):
        self.connection = Connection(port=self.broadcast_port)
        self.connection.listen()

        print(f"[!] Server started at localhost:{self.broadcast_port}")
        print(f"[!] Source file | {self.source_file_path} | {os.path.getsize(self.source_file_path)} bytes")
        print("[!] Listening to broadcast address for clients.")

        while True:
            try:
                data, address = self.connection.socket.recvfrom(1024)
                segment = Segment.unpack(data)

                if segment.flags == SegmentFlag.SYN_CONST:
                    print(f"[!] Received request from {address[0]}:{address[1]}")

                    # Add client to the list
                    self.clients.append(address)

                    # Prompt to continue listening
                    response = input("[?] Listen more? (y/n) ").lower()
                    if response != 'y':
                        break

            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break

        print("\nClient list:")
        for i, client in enumerate(self.clients, start=1):
            print(f"{i}. {client[0]}:{client[1]}")

        print("\n[!] Commencing file transfer...")

        # Perform three-way handshake and file transfer to each client
        for client_address in self.clients:
            self.perform_three_way_handshake(client_address)

    def perform_three_way_handshake(self, client_address):
        print(f"[!] [Handshake] Handshake to client {client_address}...")

        # Send SYN to client
        syn_segment = Segment.syn(1)
        self.connection.send(client_address[0], client_address[1], syn_segment)

        # Wait for SYN-ACK from client
        syn_ack_segment = self.connection.receive()
        if syn_ack_segment and syn_ack_segment.flags == SegmentFlag.SYN_CONST | SegmentFlag.ACK_CONST:
            print("[!] [Handshake] Received SYN-ACK from client, sending ACK...")
            ack_segment = Segment.ack(2, syn_ack_segment.sequence_number + 1)
            self.connection.send(client_address[0], client_address[1], ack_segment)

            # Initiate file transfer
            self.send_file_segments(client_address, syn_ack_segment.sequence_number + 1)

    def send_file_segments(self, client_address, initial_sequence_number):
        file_size = os.path.getsize(self.source_file_path)
        with open(self.source_file_path, 'rb') as file:
            sequence_number = initial_sequence_number
            while True:
                data_payload = file.read(Segment.MAX_PAYLOAD_SIZE)
                if not data_payload:
                    break

                segment = Segment(sequence_number, 0, 0, 0, data_payload)
                print(f"[!] [Client {client_address}] [Num={sequence_number}] Sending segment to client...")
                self.connection.send(client_address[0], client_address[1], segment)

                # Wait for ACK from client
                ack_segment = self.connection.receive()
                if ack_segment and ack_segment.flags == SegmentFlag.ACK_CONST:
                    print(f"[!] [Client {client_address}] [Num={sequence_number}] [ACK] ACK received, new sequence base = {ack_segment.acknowledgment_number}")
                    sequence_number += 1

        print(f"[!] [Client {client_address}] [CLS] File transfer completed, initiating closing connection...")
        # Initiate connection closing
        fin_segment = Segment.fin()
        self.connection.send(client_address[0], client_address[1], fin_segment)

        # Wait for ACK from client
        ack_segment = self.connection.receive()
        if ack_segment and ack_segment.flags == SegmentFlag.ACK_CONST:
            print(f"[!] [Client {client_address}] [FIN] Sending FIN...")
            self.connection.send(client_address[0], client_address[1], fin_segment)

        # Wait for final ACK from client
        ack_segment = self.connection.receive()
        if ack_segment and ack_segment.flags == SegmentFlag.ACK_CONST:
            print(f"[!] [Client {client_address}] [FIN] Connection closed.")

# Example usage:
if __name__ == "__main__":
    server = Server(1337, "uwu.md")
    server.run()
