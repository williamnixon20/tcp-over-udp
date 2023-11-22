import math
import os
import socket
import threading
import struct
from lib.connection import Connection

from lib.segment import Segment, SegmentFlag

import sys
import os
import time
from lib.connection import Connection, MessageInfo, Segment, SegmentFlag


class Server:
    def __init__(self, server_port, source_file):
        self.server_port = int(server_port)
        self.source_file = source_file
        self.clients = []
        self.connection = Connection(ip="localhost", port=self.server_port)

    def listen_for_clients(self):
        print("[!] Listening to broadcast address for clients.")
        while True:
            try:
                message_info = self.connection.listen()
                client_address = (message_info.ip, message_info.port)

                if client_address not in self.clients:
                    self.clients.append(client_address)
                    print(f"[!] Received request from {client_address}")
                    listen_more = input("[?] Listen more? (y/n) ").lower()
                    if listen_more != 'y':
                        break

            except Exception as e:
                print("[!] Error while listening for clients:", e)

        print("\nClient list:")
        for i, client in enumerate(self.clients, start=1):
            print(f"{i}. {client[0]}:{client[1]}")

    def initiate_handshake(self, client_address):
        syn_ack_segment = Segment.syn_ack()
        self.connection.send(
            client_address[0], client_address[1], syn_ack_segment)
        print(f"[!] [Handshake] Handshake to client {client_address}...")

        try:
            message_info = self.connection.listen(timeout=15)
            received_segment = message_info.segment

            if received_segment.is_ack() and received_segment.is_valid_checksum():
                print(
                    f"[!] [Handshake] ACK received from client {client_address}. Handshake complete.")
                return True
            else:
                print(
                    f"[!] [Handshake] Invalid ACK received from client {client_address}. Closing connection...")
        except:
            print(
                f"[!] [Handshake] Timeout waiting for ACK from client {client_address}. Closing connection...")
        return False

    def send_file(self, client_address):
        print("[!] Commencing file transfer...")

        with open(self.source_file, 'rb') as file:
            data = file.read()

        sequence_base = 0
        window_size = 3
        total_segments = math.ceil(len(data) / Segment.MAX_PAYLOAD_SIZE)
        print(
            f"[!] [FILE SIZE] Sending {total_segments} segments to client. Bytes: {len(data)}...")
        print(
            f"[!] [WINDOW SIZE] Sending {window_size} segments per window...")

        while sequence_base < total_segments:
            for sequence_number in range(sequence_base, min(sequence_base + window_size, total_segments)):
                start_byte = sequence_number * Segment.MAX_PAYLOAD_SIZE
                end_byte = min((sequence_number + 1) *
                               Segment.MAX_PAYLOAD_SIZE, len(data))
                segment_data = data[start_byte:end_byte]
                segment = Segment(
                    sequence_number, 0, flags=SegmentFlag(), data_payload=segment_data)
                self.connection.send(
                    client_address[0], client_address[1], segment)
                print(
                    f"[!] [Client {client_address}] [Seq={sequence_number}] Sending segment to client...")

            try:
                message_info = self.connection.listen(timeout=15)
                received_segment = message_info.segment

                if received_segment.is_ack() and received_segment.acknowledgment_number == sequence_base:
                    sequence_base += 1
                    print(
                        f"[!] [Client {client_address}] [ACK] ACK received, new sequence base = {sequence_base}")
                elif received_segment.is_ack() and received_segment.acknowledgment_number > sequence_base:
                    sequence_base = received_segment.acknowledgment_number
                    print(
                        f"[!] [Client {client_address}] [ACK] ACK received, new sequence base = {sequence_base}")

            except Exception as e:
                print(
                    f"[!] [Client {client_address}] [Timeout] ACK response timeout, resending segments...")

        fin_segment = Segment.fin()
        self.connection.send(client_address[0], client_address[1], fin_segment)
        print(
            f"[!] [Client {client_address}] [CLS] File transfer completed, initiating closing connection...")

        try:
            message_info = self.connection.listen(timeout=15)
            received_segment = message_info.segment

            if received_segment.is_ack():
                print(
                    f"[!] [Client {client_address}] [ACK] ACK received for FIN. Closing connection...")
            else:
                print(
                    f"[!] [Client {client_address}] [Error] Invalid ACK received for FIN. Closing connection...")
        except Exception as e:
            print(
                f"[!] [Client {client_address}] [Error] Timeout waiting for ACK after FIN. Closing connection...")

    def start(self):
        print(f"[!] Server started at localhost:{self.server_port}")
        print(
            f"[!] Source file | {self.source_file} | {os.path.getsize(self.source_file)} bytes")

        self.listen_for_clients()

        for client_address in self.clients:
            if (self.initiate_handshake(client_address)):
                print(
                    f"[!] [Client {client_address}] Handshake complete. Starting file transfer..")
                self.send_file(client_address)

        self.connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 server.py [server port] [source file]")
        print("sudo python src/client.py 100 123 tesme")
        sys.exit(1)

    server_port, source_file = sys.argv[1], sys.argv[2]
    server = Server(server_port, source_file)
    server.start()
