from lib.connection import Connection, MessageInfo, Segment, SegmentFlag

connection_b = Connection(ip="localhost", port=12345)

class ReceiverHandler:
    def handle_message(self, message_info):
        if (message_info.segment.is_ack()):
            print(f"Program B: Received ACK from Program A: {message_info.segment.acknowledgment_number}")
            return
        print(f"Program B: Received data from Program A: {message_info.segment.data_payload.decode()}")
        ack_segment = Segment.ack(message_info.segment.sequence_number + 1, 0)
        print("I RECEIVED THIS SEGMENT FROM A: " + str(message_info.segment))
        connection_b.send("localhost", 12346, ack_segment)

receiver_handler = ReceiverHandler()


# Simulate sending data from program A to program B
data_payload = b'Hello, Program B!'
sequence_number = 0
acknowledgment_number = 0
flags = SegmentFlag(syn=True, ack=False)

# Send 10 segments for demonstration
for i in range(10):
    segment = Segment(sequence_number, acknowledgment_number, flags, 0, data_payload)
    connection_b.send("localhost", 12346, segment)
    sequence_number += 1
    acknowledgment_number += 1

print("[!] Sender script completed.")

while True:
    try:
        message_info = connection_b.listen()
        if message_info is not None:
            # Handle the received message
            receiver_handler.handle_message(message_info)
    except KeyboardInterrupt:
        print("[!] Listener terminated.")
        break
    except Exception as e:
        print(f"[!] Error in listener: {e}")