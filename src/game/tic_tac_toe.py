class Player:
    def __init__(self, symbol, ip, port):
        self.symbol = symbol
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)


class TicTacToe:
    def __init__(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.players = []
        self.current_player_index = 0

    def to_dict(self, is_current_player=False):
        is_winner = self.check_winner(self.get_current_player().symbol)
        is_enemy_winner = self.check_winner(
            self.players[(self.current_player_index + 1) % 2].symbol)
        is_tie = self.is_board_full()
        return {
            "board": self.get_board_string(),
            "is_current_player": is_current_player,
            "current_player_symbol": self.get_current_player().symbol,
            "is_winner": is_winner,
            "is_tie": is_tie,
            "is_game_over": is_winner or is_enemy_winner or is_tie,
        }

    def add_player(self, player: Player):
        if len(self.players) == 2:
            raise Exception("Only 2 players are allowed.")

        self.players.append(player)

    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]

    def switch_player(self):
        self.current_player_index = (self.current_player_index + 1) % 2

    def print_board(self):
        print("-" * 9)
        for row in self.board:
            print(" | ".join(row))
            print("-" * 9)

    def check_winner(self, player):
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)) or all(self.board[j][i] == player for j in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)) or all(self.board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def is_board_full(self):
        for row in self.board:
            if " " in row:
                return False
        return True

    def get_board_string(self) -> str:
        board_string = ""
        board_string += "-" * 9 + "\n"
        for row in self.board:
            board_string += " | ".join(row) + "\n"
            board_string += "-" * 9 + "\n"

        return board_string

    def move(self, player: Player, row: int, col: int) -> str:
        if self.board[row][col] != " ":
            return False

        self.board[row][col] = player.symbol
        return True
