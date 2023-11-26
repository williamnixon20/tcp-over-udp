from node import Node

import sys
import json


class TicTacToeClient(Node):
    def __init__(self, client_port, server_ip, server_port):
        super().__init__(client_port)
        self.server_port = int(server_port)
        self.server_ip = server_ip
        self.server_address = (self.server_ip, self.server_port)

    def start(self):
        self.initiate_handshake(self.server_ip, self.server_port)
        while True:
            self.receive_state()

    def receive(self, timeout=0.1):
        data = json.loads(super().receive(timeout).decode("utf-8"))
        print(f"[!] Received data from {self.server_address}")
        return data

    def receive_state(self):
        data = self.receive(30)
        print(f"\nMessage: {data['message']}")
        print(f"Board:\n")
        print(data["board"])

        if data.get("is_game_over"):
            self.connection.close()
            sys.exit(0)

        print(f"Current player: {data['current_player_symbol']}")
        print(f"Is current player: {data['is_current_player']}\n")

        if data["is_current_player"]:
            self.send_move()
        else:
            print(f"Waiting for other player to move...\n")

    def receive_message(self):
        data: dict = self.receive(10)
        print(f"\nMessage:")
        print(data["message"])

        self.receive_state()
        if data.get("is_winner") is not None or data.get("is_tie") is not None:
            self.connection.close()
            sys.exit(0)

    def send_move(self):
        print(f"[!] Enter move in format 'row col' e.g. 1 2.")
        move = input("[?] Enter move (30s): ")
        print()

        self.send(self.server_address, move.encode("utf-8"))
        print(f"[!] Sent move {move} to {self.server_address}.")
        self.receive_state()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python3 tic_tac_toe_client.py [client port] [server ip] [server port]"
        )
        sys.exit(1)

    client_port, server_ip, server_port = sys.argv[1], sys.argv[2], sys.argv[3]
    client = TicTacToeClient(client_port, server_ip, server_port)
    client.start()
