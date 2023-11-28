import math
from lib.connection import Connection

from lib.segment import Segment, SegmentFlag

from lib.connection import Connection, MessageInfo, Segment, SegmentFlag

from abc import ABC, abstractmethod


class Node(ABC):
    def __init__(self, node_port, host="localhost"):
        self.node_port = int(node_port)
        self.connection = Connection(
            ip=host, port=self.node_port)

    @abstractmethod
    def start(self):
        pass

    def initiate_handshake(self, dest_ip, dest_port):
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        syn_segment = Segment.syn(0)
        self.connection.send(dest_ip, dest_port, syn_segment)
        print("[!] [Handshake] Sending broadcast SYN request to ",
              dest_ip, dest_port)

        try:
            message_info: MessageInfo = self.connection.listen(timeout=180)
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
                    f"[!] [Handshake] Invalid ACK received from source {source_address}. Closing connection with this client..."
                )
        except:
            print(
                f"[!] [Handshake] Timeout waiting for ACK from source {source_address}. Closing connection with this client..."
            )
        return False

    def send(self, dest_address, data):
        sequence_base = 0
        window_size = 4
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
                self.connection.send(dest_address[0], dest_address[1], segment)
                print(
                    f"[!] [Dest. Node {dest_address}] [Seq={sequence_number}] Sending segment to dest. node..."
                )
            # make this range = 1 if you need faster transfer
            # max_seq = min(window_size, total_segments - sequence_base)
            max_seq = 3
            for i in range(max_seq):
                try:
                    message_info = self.connection.listen(timeout=0.2)
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

        tries = 5
        while True and tries != 0:
            try:
                tries -= 1
                fin_segment = Segment.fin()
                fin_segment.sequence_number = -1
                fin_segment.acknowledgment_number = -1
                self.connection.send(
                    dest_address[0], dest_address[1], fin_segment)
                print(
                    f"[!] [Dest. Node {dest_address}] [CLS] Data transfer completed, initiating closing connection..."
                )
                message_info = self.connection.listen(timeout=2)
                received_segment = message_info.segment

                if received_segment.is_ack() and received_segment.sequence_number == -1:
                    print(
                        f"[!] [Dest. Node {dest_address}] [ACK] ACK received for FIN. Closing connection..."
                    )
                    break
                else:
                    print(
                        f"[!] [Dest. Node {dest_address}] [Error] Invalid ACK received for FIN. Retrying..."
                    )
            except Exception as e:
                print(
                    f"[!] [Dest. Node {dest_address}] [Error] Timeout waiting for ACK after FIN. Retrying..."
                )
        if tries == 0:
            print("Ack was never received. Terminating..")

    def receive(
        self,
        from_address,
        timeout=1,
        n_resend_ack=20
    ):
        expected_sequence_number = 0
        received_data = b""
        error_count = 0

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
                        received_segment.sequence_number, received_segment.sequence_number
                    )
                    self.connection.send(
                        message_info.ip, message_info.port, ack_segment
                    )
                    break
                elif (
                    received_segment.sequence_number == expected_sequence_number
                    and not received_segment.is_ack()
                ):
                    print(
                        "[Segment SEQ={}] Received, Ack sent".format(
                            received_segment.sequence_number
                        )
                    )

                    received_data += received_segment.get_payload()

                    ack_segment = Segment.ack(
                        expected_sequence_number, received_segment.sequence_number
                    )
                    self.connection.send(
                        message_info.ip, message_info.port, ack_segment
                    )

                    expected_sequence_number += 1
                    error_count = 0
                else:
                    print(
                        "[Segment SEQ={}] Ignoring, invalid segment received. Expected SEQ={}".format(
                            received_segment.sequence_number, expected_sequence_number
                        )
                    )
                    error_count += 1
                    if error_count > n_resend_ack:
                        error_count = 0
                        print(
                            "[!] Received too much invalid segments! Maybe Ack was lost. Resending ACK... {} to {}:{}".format(
                                expected_sequence_number - 1,
                                message_info.ip, message_info.port
                            )
                        )
                        ack_segment = Segment.ack(
                            expected_sequence_number - 1, expected_sequence_number - 1
                        )
                        self.connection.send(
                            message_info.ip, message_info.port, ack_segment
                        )

            except Exception as e:
                print("[!] Timeout waiting for segment. Retrying by sending ack {}...".format(
                    expected_sequence_number-1))
                ack_segment = Segment.ack(
                    expected_sequence_number - 1, expected_sequence_number - 1
                )
                self.connection.send(
                    from_address[0], from_address[1], ack_segment
                )

        return received_data
