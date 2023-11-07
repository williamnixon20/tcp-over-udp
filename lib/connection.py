import socket
from segment import Segment, SegmentFlag 
import threading

class Connection:
    def __init__(self, ip="localhost", port=0):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.handlers = []

    def send(self, ip, port, segment):
        dest = (ip, port)
        print(len(segment.to_bytes()))
        self.socket.sendto(segment.to_bytes(), dest)

    def listen(self, timeout=None):
        self.socket.bind((self.ip, self.port))
        self.socket.settimeout(timeout)
        while True:
            try:
                data, address = self.socket.recvfrom(1024)
                message_info = MessageInfo(ip=address[0], port=address[1], segment=Segment.from_bytes(data))
                self.notify(message_info)
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                break

    def close(self):
        self.socket.close()

    def register_handler(self, handler):
        self.handlers.append(handler)

    def notify(self, message_info):
        for handler in self.handlers:
            handler.handle_message(message_info)

class MessageInfo:
    def __init__(self, ip, port, segment):
        self.ip = ip
        self.port = port
        self.segment = segment

# Kalau di mac, ada OS Error UDP terlalu gede. 
# Fix pake ini sudo sysctl -w net.inet.udp.maxdgram=65535
# Kalo komputer di reboot ga bs lagi, jadi harus di run lagi
if __name__ == "__main__":
    connection_a = Connection(ip="localhost", port=12345)
    connection_b = Connection(ip="localhost", port=12346)

    class SenderHandler:
        def handle_message(self, message_info):
            print(f"Program A: Received ACK from Program B: {message_info.segment.acknowledgment_number}")

    sender_handler = SenderHandler()
    connection_a.register_handler(sender_handler)

    class ReceiverHandler:
        def handle_message(self, message_info):
            print(f"Program B: Received data from Program A: {message_info.segment.data_payload.decode()}")

            ack_segment = Segment(acknowledgment_number=message_info.segment.sequence_number + 1)
            print("I RECEIVED THIS SEGMENT FROM A: " + str(message_info.segment))
            connection_b.send("localhost", 12345, ack_segment)

    receiver_handler = ReceiverHandler()
    connection_b.register_handler(receiver_handler)

    # Thread to start listening for Program A
    def program_a_listener():
        connection_a.listen()

    # Thread to start listening for Program B
    def program_b_listener():
        connection_b.listen()

    # Start listening for both Program A and Program B
    thread_a = threading.Thread(target=program_a_listener)
    thread_b = threading.Thread(target=program_b_listener)

    thread_a.start()
    thread_b.start()

    data_payload = b'Hello, Program B!'
    sequence_number = 0
    acknowledgment_number = 0
    flags = SegmentFlag(syn=True, ack=True)

    for i in range(99999999):
        if (i % 10000000) == 0:
            segment = Segment(sequence_number, acknowledgment_number, flags, 0, data_payload)
            connection_a.send("localhost", 12346, segment)
            sequence_number += 1
            acknowledgment_number += 1
