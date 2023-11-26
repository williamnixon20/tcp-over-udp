import sys
import os

from node import Node


class Server(Node):
    def __init__(self, server_port, source_file):
        super().__init__(server_port)
        self.source_file = source_file
        self.clients = []

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
                    if listen_more != "y":
                        break

            except Exception as e:
                print("[!] Error while listening for clients:", e)

        print("\nClient list:")
        for i, client in enumerate(self.clients, start=1):
            print(f"{i}. {client[0]}:{client[1]}")

    def send_file(self, client_address):
        print("[!] Commencing file transfer...")

        with open(self.source_file, "rb") as file:
            data = file.read()

        self.send(client_address, data)

    def start(self):
        print(f"[!] Server started at localhost:{self.node_port}")
        print(
            f"[!] Source file | {self.source_file} | {os.path.getsize(self.source_file)} bytes"
        )

        self.listen_for_clients()

        for client_address in self.clients:
            if self.respond_handshake(client_address):
                print(
                    f"[!] [Client {client_address}] Handshake complete. Starting file transfer.."
                )
                self.send_file(client_address)

        self.connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 server.py [server port] [source file]")
        print("sudo python3 src/server.py 123 test/18mb.jpg")
        sys.exit(1)

    server_port, source_file = sys.argv[1], sys.argv[2]
    server = Server(server_port, source_file)
    server.start()
