import math
from lib.connection import Connection

from lib.segment import Segment, SegmentFlag

from lib.connection import Connection, MessageInfo, Segment, SegmentFlag

from abc import ABC, abstractmethod


class Node(ABC):
    def __init__(self, node_port):
        self.node_port = int(node_port)
        self.connection = Connection(ip="localhost", port=self.node_port)

    @abstractmethod
    def start(self):
        pass

    def initiate_handshake(self, dest_address):
        syn_segment = Segment.syn(0)
        self.connection.send("localhost", dest_address, syn_segment)
        print(
            "[!] [Handshake] Sending broadcast SYN request to port", dest_address
        )

        try:
            message_info: MessageInfo = self.connection.listen(timeout=300)
            received_segment = message_info.segment
            if (
                received_segment.is_syn()
                and received_segment.is_ack()
                and received_segment.is_valid_checksum()
            ):
                print(
                    "[!] [Handshake] Received valid SYN-ACK response. Initiating ACK..."
                )
                ack_segment = Segment.ack(0, 0)
                self.connection.send(
                    message_info.ip, message_info.port, ack_segment)
                print("[!] [Handshake] Handshake complete.")
            else:
                print("[!] [Handshake] Received invalid SYN-ACK response. Exiting...")
                exit(1)
        except Exception as e:
            print("[!] [Handshake] Handshake fail, exiting...")
            exit(1)

    def respond_handshake(self, source_address):
        syn_ack_segment = Segment.syn_ack()
        self.connection.send(
            source_address[0], source_address[1], syn_ack_segment)
        print(f"[!] [Handshake] Handshake to source {source_address}...")

        try:
            message_info = self.connection.listen(timeout=15)
            received_segment = message_info.segment

            if received_segment.is_ack() and received_segment.is_valid_checksum():
                print(
                    f"[!] [Handshake] ACK received from source {source_address}. Handshake complete."
                )
                return True
            else:
                print(
                    f"[!] [Handshake] Invalid ACK received from source {source_address}. Closing connection..."
                )
        except:
            print(
                f"[!] [Handshake] Timeout waiting for ACK from source {source_address}. Closing connection..."
            )
        return False

    def send(self, dest_address, data):
        sequence_base = 0
        window_size = 3
        total_segments = math.ceil(len(data) / Segment.MAX_PAYLOAD_SIZE)
        print(
            f"[!] [DATA SIZE] Sending {total_segments} segments to source. Bytes: {len(data)}..."
        )
        print(
            f"[!] [WINDOW SIZE] Sending {window_size} segments per window...")

        while sequence_base < total_segments:
            for sequence_number in range(
                sequence_base, min(sequence_base + window_size, total_segments)
            ):
                start_byte = sequence_number * Segment.MAX_PAYLOAD_SIZE
                end_byte = min(
                    (sequence_number + 1) * Segment.MAX_PAYLOAD_SIZE, len(data)
                )
                segment_data = data[start_byte:end_byte]
                segment = Segment(
                    sequence_number, 0, flags=SegmentFlag(), data_payload=segment_data
                )
                self.connection.send(
                    dest_address[0], dest_address[1], segment)
                print(
                    f"[!] [Dest. Node {dest_address}] [Seq={sequence_number}] Sending segment to dest. node..."
                )
            # make this range = 1 if you need faster transfer
            max_seq = min(window_size, total_segments - sequence_base)
            for i in range(max_seq):
                try:
                    message_info = self.connection.listen(timeout=0.1)
                    received_segment = message_info.segment
                    if not received_segment.is_valid_checksum():
                        print(
                            f"[!] [Dest. Node {dest_address}] [Error] Invalid checksum received. Resending segments..."
                        )
                        continue

                    if (
                        not message_info.ip == dest_address[0]
                        or not message_info.port == dest_address[1]
                    ):
                        print(
                            f"[!] [Dest. Node {dest_address}] [Error] Invalid source received. Resending segments..."
                        )
                        continue

                    if (
                        received_segment.is_ack()
                        and received_segment.acknowledgment_number == sequence_base
                    ):
                        sequence_base += 1
                        print(
                            f"[!] [Dest. Node {dest_address}] [ACK] ACK number {received_segment.acknowledgment_number} received, new sequence base = {sequence_base}"
                        )
                    elif (
                        received_segment.is_ack()
                        and received_segment.acknowledgment_number > sequence_base
                    ):
                        sequence_base = received_segment.acknowledgment_number + 1
                        print(
                            f"[!] [Dest. Node {dest_address}] [ACK] ACK number {received_segment.acknowledgment_number} received, new sequence base = {sequence_base}"
                        )
                    else:
                        print(
                            f"[!] [Dest. Node {dest_address}] [ACK] ACK number {received_segment.acknowledgment_number} received < sequence base {sequence_base}"
                        )

                except Exception as e:
                    print(
                        f"[!] [Dest. Node {dest_address}] [Timeout] ACK response timeout, resending segments..."
                    )
                    break

        fin_segment = Segment.fin()
        self.connection.send(dest_address[0], dest_address[1], fin_segment)
        print(
            f"[!] [Dest. Node {dest_address}] [CLS] Data transfer completed, initiating closing connection..."
        )

        try:
            message_info = self.connection.listen(timeout=15)
            received_segment = message_info.segment

            if received_segment.is_ack():
                print(
                    f"[!] [Dest. Node {dest_address}] [ACK] ACK received for FIN. Closing connection..."
                )
            else:
                print(
                    f"[!] [Dest. Node {dest_address}] [Error] Invalid ACK received for FIN. Closing connection..."
                )
        except Exception as e:
            print(
                f"[!] [Dest. Node {dest_address}] [Error] Timeout waiting for ACK after FIN. Closing connection..."
            )

    def receive(self, timeout=0.1):
        expected_sequence_number = 0
        received_data = b""

        while True:
            try:
                message_info: MessageInfo = self.connection.listen(timeout)
                received_segment = message_info.segment

                if not received_segment.is_valid_checksum():
                    print("[!] Invalid checksum received. Retrying...")
                    continue

                if received_segment.is_fin():
                    print(
                        "[Segment SEQ={}] Received FIN. Acking and closing connection.".format(
                            received_segment.sequence_number
                        )
                    )
                    ack_segment = Segment.ack(
                        expected_sequence_number, received_segment.sequence_number
                    )
                    self.connection.send(
                        message_info.ip, message_info.port, ack_segment
                    )
                    break
                elif received_segment.sequence_number == expected_sequence_number:
                    print(
                        "[Segment SEQ={}] Received, Ack sent".format(
                            received_segment.sequence_number
                        )
                    )

                    received_data += received_segment.data_payload

                    ack_segment = Segment.ack(
                        expected_sequence_number, received_segment.sequence_number
                    )
                    self.connection.send(
                        message_info.ip, message_info.port, ack_segment
                    )

                    expected_sequence_number += 1
                else:
                    print(
                        "[Segment SEQ={}] Ignoring, invalid segment received. Expected SEQ={}".format(
                            received_segment.sequence_number, expected_sequence_number
                        )
                    )
            except Exception as e:
                print("[!] Timeout waiting for segment. Retrying...")
                ack_segment = Segment.ack(
                    expected_sequence_number - 1, expected_sequence_number - 1
                )
                self.connection.send(
                    message_info.ip, message_info.port, ack_segment)

        return received_data