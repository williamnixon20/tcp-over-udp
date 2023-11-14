import sys
import os
import time
from lib.connection import Connection, MessageInfo, Segment, SegmentFlag

class client:
    def __init__(self, client_port, broadcast_port, output_path):
        self.client_port = int(client_port)
        self.broadcast_port = int(broadcast_port)
        self.output_path = output_path
        self.connection = Connection(ip="localhost", port=self.client_port)

    def initiate_handshake(self):
        syn_segment = Segment.syn(0) 
        self.connection.send("localhost", self.broadcast_port, syn_segment)
        print("[!] [Handshake] Sending broadcast SYN request to port", self.broadcast_port)

        try:
            message_info = self.connection.listen(timeout=5)
            received_segment = message_info.segment
            print(received_segment)
            if received_segment.is_syn() and received_segment.is_ack() and received_segment.is_valid_checksum():
                print("[!] [Handshake] Received valid SYN-ACK response. Initiating ACK...")
                ack_segment = Segment.ack(0, 0)
                self.connection.send(message_info.ip, message_info.port, ack_segment)
                print("[!] [Handshake] Handshake complete.")
            else:
                print("[!] [Handshake] Received invalid SYN-ACK response. Exiting...")
                exit(1)
        except Exception as e:
            print("[!] [Handshake] Handshake fail, exiting...")
            exit(1)

def receive_data(self, output_filename):
    expected_sequence_number = 0 
    received_data = b"" 

    while True:
        try:
            message_info = self.connection.listen(timeout=10)
            received_segment = message_info.segment

            if received_segment.sequence_number == expected_sequence_number and received_segment.is_fin():
                print("[Segment SEQ={}] Received FIN. Closing connection.".format(received_segment.sequence_number))
                break
            elif received_segment.sequence_number == expected_sequence_number and received_segment.is_valid_checksum():
                print("[Segment SEQ={}] Received, Ack sent".format(received_segment.sequence_number))

                received_data += received_segment.data_payload

                ack_segment = Segment.ack(expected_sequence_number + 1, received_segment.sequence_number + 1)
                self.connection.send(message_info.ip, message_info.port, ack_segment)

                expected_sequence_number += 1
            else:
                raise Exception("Invalid segment received.")

        except Exception as e:
            print("[!] Retrying...")
            print("[Segment SEQ={}] Checksum failed. Ack previous sequence number.".format(received_segment.sequence_number))
            ack_segment = Segment.ack(expected_sequence_number, received_segment.sequence_number + 1)
            self.connection.send(message_info.ip, message_info.port, ack_segment)

    with open(output_filename, 'wb') as output_file:
        output_file.write(received_data)


    def start(self):
        print(f"[!] Client started at localhost:{self.client_port}")
        print("[!] Initiating three-way handshake...")

        self.initiate_handshake()
        self.receive_data()
        print("[!] Successfully received all data. Closing connection.")
        self.connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 client.py [client port] [broadcast port] [path output]")
        sys.exit(1)

    client_port, broadcast_port, output_path = sys.argv[1], sys.argv[2], sys.argv[3]
    client = client(client_port, broadcast_port, output_path)
    client.start()
