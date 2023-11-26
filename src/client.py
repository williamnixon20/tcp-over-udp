import sys
from node import Node


class Client(Node):
    def __init__(self, client_port, server_host, server_port, output_path):
        super().__init__(client_port)
        self.server_host = server_host
        self.server_port = int(server_port)
        self.output_path = output_path

    def receive_file(self):
        received_data = self.receive([self.server_host, self.server_port])
        self.create_file(received_data)

    def create_file(self, received_data):
        output_filename = self.output_path
        with open(output_filename, "wb") as output_file:
            output_file.write(received_data)

    def start(self):
        print(f"[!] Client started at localhost:{self.node_port}")
        print("[!] Initiating three-way handshake...")

        self.initiate_handshake(self.server_host, self.server_port)
        self.receive_file()
        print("[!] Successfully received all data. Closing connection.")
        self.connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python3 client.py [client port] [broadcast host] [broadcast port] [path output]")
        # print("sudo python3 server.py 123 client.py")
        sys.exit(1)

    client_port, server_host, server_port, output_path = sys.argv[
        1], sys.argv[2], sys.argv[3], sys.argv[4]
    client = Client(client_port, server_host, server_port, output_path)
    client.start()
