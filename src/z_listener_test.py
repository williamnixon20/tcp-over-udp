from lib.connection import Connection, MessageInfo, Segment, SegmentFlag

connection_a = Connection(ip="localhost", port=12346)

class ReceiverHandler:
    def handle_message(self, message_info):
        if (message_info.segment.is_ack()):
            print(f"Program B: Received ACK from Program A: {message_info.segment.acknowledgment_number}")
            return
        print(f"Program B: Received data from Program A: {message_info.segment.data_payload.decode()}")
        ack_segment = Segment.ack(message_info.segment.sequence_number + 1, 0)
        print("I RECEIVED THIS SEGMENT FROM A: " + str(message_info.segment))
        connection_a.send("localhost", 12345, ack_segment)

receiver_handler = ReceiverHandler()

while True:
    try:
        message_info = connection_a.listen()
        if message_info is not None:
            # Handle the received message
            receiver_handler.handle_message(message_info)
    except KeyboardInterrupt:
        print("[!] Listener terminated.")
        break
    except Exception as e:
        print(f"[!] Error in listener: {e}")

