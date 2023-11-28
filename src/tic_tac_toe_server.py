from node import Node
from game.tic_tac_toe import TicTacToe, Player
import sys
import json


class TicTacToeServer(Node):
    def __init__(self, server_port, host="localhost"):
        super().__init__(server_port, host=host)
        self.tic_tac_toe = TicTacToe()
        self.players = []

    def listen_for_players(self):
        print("[!] Listening to broadcast address for players.")
        while len(self.players) < 2:
            try:
                message_info = self.connection.listen()
                player_address = (message_info.ip, message_info.port)

                if player_address not in self.players:
                    self.players.append(player_address)
                    print(f"[!] Received request from {player_address}")
                    print(f"[!] Listening for more players..")

            except Exception as e:
                print("[!] Error while listening for players:", e)

        print("[!] All players connected.")
        print("\nPlayer list:")
        for i, player in enumerate(self.players, start=1):
            print(f"{i}. {player[0]}:{player[1]}")

    def receive_move(self, player):
        print()
        received_data = self.receive(
            [player.ip, player.port], 30, n_resend_ack=2)
        print()
        move = received_data.decode("utf-8")
        return move

    def send_message(self, player_address, message: dict):
        print(f"[!] Sending message to {player_address}: {message}")
        self.send(player_address, json.dumps(message).encode("utf-8"))

    def send_state(self, player, message: str = ""):
        print()
        current_player = self.tic_tac_toe.get_current_player()
        print(
            f"[!] Sending state to {player.symbol} with address {player.ip}:{player.port}"
        )
        dict = self.tic_tac_toe.to_dict(player == current_player)
        dict["message"] = message
        self.send(
            player.address,
            json.dumps(dict).encode("utf-8"),
        )
        print()

    def start_game(self):
        player1 = Player("X", self.players[0][0], self.players[0][1])
        player2 = Player("O", self.players[1][0], self.players[1][1])

        self.tic_tac_toe.add_player(player1)
        self.tic_tac_toe.add_player(player2)

        print("\n=========== Game started ===========\n")
        for player in self.tic_tac_toe.players:
            self.send_state(
                player, "Game started. Your symbol: " + player.symbol)
        while True:
            current_player: Player = self.tic_tac_toe.get_current_player()
            print(f"Current player: {current_player.symbol}")
            print("Current board:\n")
            self.tic_tac_toe.print_board()

            print("\nWaiting for move...")
            move = self.receive_move(current_player)
            print(f"Received move: {move}")

            try:
                row, col = move.split(" ")
                row, col = int(row), int(col)

                if self.tic_tac_toe.move(current_player, row, col):
                    print("> Move successful.")
                else:
                    print("> Move unsuccessful.")
                    self.send_state(
                        current_player, "Invalid move. Please try again.")
                    continue

                if self.tic_tac_toe.check_winner(current_player.symbol):
                    self.tic_tac_toe.print_board()
                    print(f"> Player {current_player.symbol} wins!")
                    self.send_state(
                        current_player, "Congratulations! You win!")
                    self.tic_tac_toe.switch_player()
                    self.send_state(
                        self.tic_tac_toe.get_current_player(),
                        f"You Lose. Player {current_player.symbol} wins.",
                    )
                    break

                if self.tic_tac_toe.is_board_full():
                    self.tic_tac_toe.print_board()
                    print(f"> Game is a tie!")
                    self.send_state(current_player, "Game is a tie!")
                    self.tic_tac_toe.switch_player()
                    self.send_state(
                        self.tic_tac_toe.get_current_player(), "Game is a tie!"
                    )
                    break

                self.tic_tac_toe.switch_player()
                self.send_state(current_player, "Move successful.")
                self.send_state(
                    self.tic_tac_toe.get_current_player(), "Your turn.")
            except Exception as e:
                print("[!] Error while processing move:", e)

        self.connection.close()
        sys.exit(0)

    def start(self):
        print(f"[!] Server started at localhost:{self.node_port}")
        self.listen_for_players()

        for player_address in self.players:
            if self.respond_handshake(player_address):
                print(f"[!] [Player {player_address}] Handshake complete.")

        self.start_game()
        self.connection.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 server.py [server port]")
        print(
            "Use flag -h=[your ip] to expose server to other devices on the network.")
        sys.exit(1)

    server_port = sys.argv[1]
    host = "localhost"
    if len(sys.argv) == 3 and "-h" in sys.argv[2]:
        host = sys.argv[2].split("=")[1]
    server = TicTacToeServer(server_port, host)
    server.start()
