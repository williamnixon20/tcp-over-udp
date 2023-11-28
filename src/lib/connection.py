import socket
from lib.segment import Segment, SegmentFlag
import threading


class Connection:
    def __init__(self, ip="localhost", port=0):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        print(f"[!] Connection started at {self.ip}:{self.port}")

    def send(self, ip, port, segment):
        dest = (ip, port)
        segment_bytes = segment.to_bytes()
        self.socket.sendto(segment_bytes, dest)

    def listen(self, timeout=None):
        self.socket.settimeout(timeout)
        try:
            data, address = self.socket.recvfrom(
                int(Segment.MAX_PAYLOAD_SIZE * 2.5))
            segment_received = Segment.from_bytes(data)
            message_info = MessageInfo(
                ip=address[0], port=address[1], segment=segment_received
            )
            return message_info
        except socket.timeout as e:
            raise e
        except Exception as e:
            raise e

    def close(self):
        self.socket.close()


class MessageInfo:
    def __init__(self, ip, port, segment):
        self.ip = ip
        self.port = port
        self.segment = segment
