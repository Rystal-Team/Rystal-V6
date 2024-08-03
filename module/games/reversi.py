#  ------------------------------------------------------------
#  Copyright (c) 2024 Rystal-Team
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#  ------------------------------------------------------------
#

import copy
import random

from PIL import Image, ImageDraw, ImageFont


class Reversi:
    """A class to represent the Reversi game."""

    def __init__(self):
        """
        Initialize the Reversi game with an empty board and set the current turn to Black.
        """
        self.board = [[" " for _ in range(8)] for _ in range(8)]
        self.current_turn = "B"
        self.initialize_board()
        self.history = []

    def serialize(self):
        return {
            "board": self.board,
            "current_turn": self.current_turn,
            "history": self.history,
        }

    @classmethod
    def deserialize(cls, data):
        game = cls()
        game.board = data["board"]
        game.current_turn = data["current_turn"]
        game.history = data["history"]
        return game

    def initialize_board(self):
        """
        Set up the initial board configuration with two black and two white pieces in the center.
        """
        self.board[3][3], self.board[3][4] = "W", "B"
        self.board[4][3], self.board[4][4] = "B", "W"

    def new_game(self):
        """Start a new game by reinitializing the board and current turn."""
        self.__init__()

    def place(self, color, position):
        """
        Place a piece on the board.

        Args:
            color (str): The color of the piece ('B' for black, 'W' for white).
            position (str): The position to place the piece (e.g., 'd3').

        Raises:
            ValueError: If the position format is invalid or the move is invalid.
        """
        if not self.is_valid_position(position):
            raise ValueError("Invalid position format")
        row, col = self.position_to_indices(position)
        if self.is_valid_move(color, row, col):
            self.board[row][col] = color
            self.flip_pieces(color, row, col)
            self.current_turn = "W" if self.current_turn == "B" else "B"
        else:
            raise ValueError("Invalid move")

    @staticmethod
    def is_valid_position(position):
        """
        Check if the given position is valid.

        Args:
            position (str): The position to check (e.g., 'd3').

        Returns:
            bool: True if the position is valid, False otherwise.
        """
        if len(position) != 2:
            return False
        col, row = position[0], position[1]
        return col in "abcdefgh" and row in "12345678"

    @staticmethod
    def position_to_indices(position):
        """
        Convert a board position to row and column indices.

        Args:
            position (str): The position to convert (e.g., 'd3').

        Returns:
            tuple: A tuple containing the row and column indices.
        """
        col = ord(position[0].lower()) - ord("a")
        row = int(position[1]) - 1
        return row, col

    def is_valid_move(self, color, row, col):
        """
        Check if a move is valid.

        Args:
            color (str): The color of the piece ('B' for black, 'W' for white).
            row (int): The row index.
            col (int): The column index.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        if self.board[row][col] != " ":
            return False
        return any(
            self.check_direction(color, row, col, dr, dc)
            for dr, dc in [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1),
            ]
        )

    def check_direction(self, color, row, col, dr, dc):
        """
        Check if there are pieces to flip in a given direction.

        Args:
            color (str): The color of the piece ('B' for black, 'W' for white).
            row (int): The starting row index.
            col (int): The starting column index.
            dr (int): The row direction to check.
            dc (int): The column direction to check.

        Returns:
            bool: True if there are pieces to flip, False otherwise.
        """
        opponent = "W" if color == "B" else "B"
        r, c = row + dr, col + dc
        if not (0 <= r < 8 and 0 <= c < 8) or self.board[r][c] != opponent:
            return False
        r, c = r + dr, c + dc
        while 0 <= r < 8 and 0 <= c < 8:
            if self.board[r][c] == " ":
                return False
            if self.board[r][c] == color:
                return True
            r, c = r + dr, c + dc
        return False

    def flip_pieces(self, color, row, col):
        """
        Flip the pieces on the board after a valid move.

        Args:
            color (str): The color of the piece ('B' for black, 'W' for white).
            row (int): The row index of the placed piece.
            col (int): The column index of the placed piece.
        """
        for dr, dc in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]:
            if self.check_direction(color, row, col, dr, dc):
                r, c = row + dr, col + dc
                while self.board[r][c] != color:
                    self.board[r][c] = color
                    r, c = r + dr, c + dc

    def game_over(self):
        """
        Check if the game is over.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return not any(
            self.is_valid_move(self.current_turn, r, c)
            for r in range(8)
            for c in range(8)
        )

    def score(self):
        """
        Get the current score of the game.

        Returns:
            dict: A dictionary with the scores for black and white pieces.
        """
        return {
            "B": sum(row.count("B") for row in self.board),
            "W": sum(row.count("W") for row in self.board),
        }

    def get_valid_moves(self, color):
        """
        Get all valid moves for a given color.

        Args:
            color (str): The color of the pieces ('B' for black, 'W' for white).

        Returns:
            list: A list of valid moves.
        """
        return [
            self.indices_to_position(r, c)
            for r in range(8)
            for c in range(8)
            if self.is_valid_move(color, r, c)
        ]

    @staticmethod
    def indices_to_position(row, col):
        """
        Convert row and column indices to a board position.

        Args:
            row (int): The row index.
            col (int): The column index.

        Returns:
            str: The board position (e.g., 'd3').
        """
        return chr(col + ord("a")) + str(row + 1)

    def copy(self):
        """
        Create a deep copy of the current game state.

        Returns:
            Reversi: A new Reversi object with the same game state.
        """
        new_game = Reversi()
        new_game.board = copy.deepcopy(self.board)
        new_game.current_turn = self.current_turn
        return new_game


class AIPlayer:
    """A class to represent an AI player for the Reversi game."""

    def __init__(self, game, color, difficulty="medium"):
        """
        Initialize the AI player.

        Args:
            game (Reversi): The Reversi game object.
            color (str): The color of the AI player ('B' for black, 'W' for white).
            difficulty (str): The difficulty level of the AI ('easy', 'medium', 'hard').
        """
        self.game = game
        self.color = color
        self.difficulty = difficulty

    def serialize(self):
        return {"color": self.color, "difficulty": self.difficulty}

    @classmethod
    def deserialize(cls, data):
        return cls(None, data["color"], data["difficulty"])

    def choose_move(self):
        """
        Choose a move based on the difficulty level.

        Returns:
            str: The chosen move (e.g., 'd3'), or None if no valid moves are available.
        """
        valid_moves = self.game.get_valid_moves(self.color)
        if not valid_moves:
            return None

        if self.difficulty == "easy":
            return random.choice(valid_moves)
        elif self.difficulty == "medium":
            return (
                random.choice(valid_moves)
                if random.random() < 0.5
                else max(valid_moves, key=self.evaluate_move)
            )
        elif self.difficulty == "hard":
            return max(valid_moves, key=self.evaluate_move)

    def evaluate_move(self, move):
        """
        Evaluate a move by simulating the game state after the move.

        Args:
            move (str): The move to evaluate (e.g., 'd3').

        Returns:
            int: The score of the move for the AI player.
        """
        simulated_game = self.game.copy()
        simulated_game.place(self.color, move)
        return simulated_game.score()[self.color]

    def is_valid_move(self, move):
        """
        Check if a move is valid for the AI player.

        Args:
            move (str): The move to check (e.g., 'd3').

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        row, col = self.game.position_to_indices(move)
        return self.game.is_valid_move(self.color, row, col)


class Interactor:
    """A class to handle console interactions for the Reversi game."""

    def __init__(self, game, ai_player_black=None, ai_player_white=None):
        """
        Initialize the console interactor.

        Args:
            game (Reversi): The Reversi game object.
            ai_player_black (AIPlayer, optional): The AI player for black pieces.
            ai_player_white (AIPlayer, optional): The AI player for white pieces.
        """
        self.game = game
        self.ai_player_black = ai_player_black
        self.ai_player_white = ai_player_white

    def serialize(self):
        return {
            "game": self.game.serialize(),
            "ai_player_black": (
                self.ai_player_black.serialize() if self.ai_player_black else None
            ),
            "ai_player_white": (
                self.ai_player_white.serialize() if self.ai_player_white else None
            ),
        }

    @classmethod
    def deserialize(cls, data):
        game = Reversi.deserialize(data["game"])
        ai_player_black = (
            AIPlayer.deserialize(data["ai_player_black"])
            if data["ai_player_black"]
            else None
        )
        ai_player_white = (
            AIPlayer.deserialize(data["ai_player_white"])
            if data["ai_player_white"]
            else None
        )
        return cls(game, ai_player_black, ai_player_white)

    def display_board(self):
        """
        Display the current board state in the console and generate an image of the board.

        Returns:
            Image: The generated board image.
        """
        board_copy = [row[:] for row in self.game.board]
        for move in self.game.get_valid_moves(self.game.current_turn):
            row, col = self.game.position_to_indices(move)
            board_copy[row][col] = "*"
        print("  a b c d e f g h\n +----------------")
        for i, row in enumerate(board_copy):
            print(f"{i+1}|{' '.join(row)}")
        print()
        image = self.generate_board_image(board_copy)
        return image

    @staticmethod
    def generate_board_image(board):
        """
        Generate an image of the board with row and column labels.

        Args:
            board (list): The board state.

        Returns:
            Image: The generated board image.
        """
        cell_size = 50
        outer_line_width = 30
        board_size = 8 * cell_size
        image_size = board_size + 2 * outer_line_width
        image = Image.new("RGB", (image_size, image_size), "#219653")
        draw = ImageDraw.Draw(image)
        dot_font = ImageFont.load_default(size=20)
        font = ImageFont.load_default()

        # Draw the board cells and pieces
        for i in range(8):
            for j in range(8):
                x0, y0 = (
                    j * cell_size + outer_line_width,
                    i * cell_size + outer_line_width,
                )
                x1, y1 = x0 + cell_size, y0 + cell_size
                draw.rectangle([x0, y0, x1, y1], outline="#333333")
                piece = board[i][j]
                if piece == "B":
                    draw.ellipse([x0 + 5, y0 + 5, x1 - 5, y1 - 5], fill="#333333")
                elif piece == "W":
                    draw.ellipse([x0 + 5, y0 + 5, x1 - 5, y1 - 5], fill="#f2f2f2")
                elif piece == "*":
                    draw.text((x0 + 23, y0 + 7), ".", fill="yellow", font=dot_font)

        for j in range(8):
            x = j * cell_size + outer_line_width + cell_size // 2
            draw.text((x, 0 + 10), chr(ord("a") + j), fill="#333333", font=font)
            draw.text(
                (x, image_size - outer_line_width + 10),
                chr(ord("a") + j),
                fill="#333333",
                font=font,
            )

        for i in range(8):
            y = i * cell_size + outer_line_width + cell_size // 2
            draw.text((0 + 10, y), str(i + 1), fill="#333333", font=font)
            draw.text(
                (image_size - outer_line_width + 10, y),
                str(i + 1),
                fill="#333333",
                font=font,
            )

        return image

    def prompt_move(self):
        """
        Prompt the player or AI to make a move.

        Returns:
            str: The chosen move (e.g., 'd3'), or None if no valid moves are available.
        """
        if self.game.current_turn == "B" and self.ai_player_black:
            move = self.ai_player_black.choose_move()
            if move is None or not self.ai_player_black.is_valid_move(move):
                print("AI (Black) has no valid moves.")
                return None
            return move
        elif self.game.current_turn == "W" and self.ai_player_white:
            move = self.ai_player_white.choose_move()
            if move is None or not self.ai_player_white.is_valid_move(move):
                print("AI (White) has no valid moves.")
                return None
            return move
        while True:
            move = (
                input(f"Player {self.game.current_turn}, enter your move (e.g., d3): ")
                .strip()
                .lower()
            )
            if self.game.is_valid_position(move):
                row, col = self.game.position_to_indices(move)
                if self.game.is_valid_move(self.game.current_turn, row, col):
                    return move
            print("Invalid move. Please enter a valid move (e.g., d3).")

    def show_score(self):
        """Display the current score of the game."""
        score = self.game.score()
        print(f"Score - Black (B): {score['B']}, White (W): {score['W']}")


if __name__ == "__main__":
    game = Reversi()
    console = Interactor(
        game,
        ai_player_white=AIPlayer(game, "W", difficulty="easy"),
        ai_player_black=AIPlayer(game, "B", difficulty="hard"),
    )
    game.new_game()

    while not game.game_over():
        console.display_board()
        if not game.get_valid_moves(game.current_turn):
            print(f"No valid moves for {game.current_turn}. Skipping turn.")
            game.current_turn = "W" if game.current_turn == "B" else "B"
            if not game.get_valid_moves(game.current_turn):
                break
            continue
        move = console.prompt_move()
        if move is None:
            continue
        try:
            game.place(game.current_turn, move)
        except ValueError as e:
            print(e)
            continue

    console.display_board()
    console.show_score()
    print("Game over!")
    if game.score()["B"] > game.score()["W"]:
        print("Black wins!")
    elif game.score()["B"] < game.score()["W"]:
        print("White wins!")
    else:
        print("It's a tie!")
