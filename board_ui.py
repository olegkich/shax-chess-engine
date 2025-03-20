import tkinter as tk
from tkinter import PhotoImage
from move_validator import MoveValidator
import os
from PIL import Image, ImageTk

class ChessBoard(tk.Frame):
    def __init__(self, parent, size=64):
        super().__init__(parent)
        self.parent = parent
        self.size = size

        # Path to piece images
        self.piece_image_path = "pieces/"

        # Map piece codes to image filenames
        self.piece_images = {
            "K": "wK.png", "Q": "wQ.png", "R": "wR.png", "B": "wB.png", "N": "wN.png", "P": "wP.png",
            "k": "bK.png", "q": "bQ.png", "r": "bR.png", "b": "bB.png", "n": "bN.png", "p": "bP.png"
        }

        # Store loaded images
        self.loaded_images = {}

        # Initial setup for a chess board
        self.board_state = self._initialize_board()

        self.move_validator = MoveValidator(self.board_state)

        self.squares = {}
        self.selected_square = None
        self.selected_piece = None

        self.white_to_move = True

        self.draw_board()
        self.place_pieces()

    def _initialize_board(self):
        return [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]

    def draw_board(self):
        """Draw the chess board with alternating colors"""
        # Light and dark square colors
        self.light_color = "#ececd4"  # White
        self.dark_color = "#4c749c"   # Green
        self.highlight_color = "#aaaaff"  # Light blue for selection

        # Create a canvas for the board
        self.canvas = tk.Canvas(self, width=self.size * 8, height=self.size * 8)
        self.canvas.pack()

        # Draw squares on the canvas
        for row in range(8):
            for col in range(8):
                color_index = (row + col) % 2
                square_color = self.light_color if color_index == 0 else self.dark_color

                # Create a rectangle for the square
                x1, y1 = col * self.size, row * self.size
                x2, y2 = x1 + self.size, y1 + self.size

                square_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=square_color, outline="")

                # Store square information
                self.squares[(row, col)] = {
                    "id": square_id,
                    "piece_id": None,
                    "is_light": color_index == 0,
                    "original_color": square_color
                }

        # Bind click event to the canvas
        self.canvas.bind("<Button-1>", self.canvas_clicked)

    def canvas_clicked(self, event):
        """Handle click on the canvas"""
        col = event.x // self.size
        row = event.y // self.size

        if 0 <= row < 8 and 0 <= col < 8:
            self.square_clicked(row, col)

    def place_pieces(self):
        """Place pieces on the board according to board state"""
        for row in range(8):
            for col in range(8):
                piece = self.board_state[row][col]
                if piece:
                    self.place_piece(row, col, piece)

    def load_piece_image(self, piece_code):
        """Load and cache piece images"""
        if piece_code not in self.loaded_images:
            img_path = os.path.join(self.piece_image_path, self.piece_images[piece_code])
            image = Image.open(img_path)
            image = image.resize((self.size, self.size), Image.Resampling.LANCZOS)
            self.loaded_images[piece_code] = ImageTk.PhotoImage(image)
        return self.loaded_images[piece_code]

    def move_piece(self, from_square, to_square):
        from_row, from_col = from_square
        to_row, to_col = to_square

        piece_code = self.board_state[from_row][from_col]

        # Check if the move is valid (you may want to add more validation logic here)
        if not self.move_validator.is_valid_move(from_square, to_square, self.white_to_move):
            return False

        # Move the piece in the board state
        self.board_state[to_row][to_col] = piece_code
        self.board_state[from_row][from_col] = ""  # Mark the starting square as empty

        # Clear the starting square visually
        self.place_piece(from_row, from_col, "")  # Place an empty square image

        # Redraw the piece on the destination square
        self.place_piece(to_row, to_col, piece_code)

        # Toggle the turn
        self.white_to_move = not self.white_to_move

        return True

    def place_piece(self, row, col, piece_code):
        """Place a piece on the specified square"""
        square = self.squares[(row, col)]

        # Remove existing piece if any
        if square["piece_id"]:
            self.canvas.delete(square["piece_id"])

        if piece_code:  # Only load the image if the piece code is not empty
            # Load the piece image
            image = self.load_piece_image(piece_code)

            # Calculate center position of the square
            x = col * self.size + self.size // 2
            y = row * self.size + self.size // 2

            # Place the image on the canvas
            piece_id = self.canvas.create_image(x, y, image=image)

            # Store piece ID
            square["piece_id"] = piece_id
        else:
            # If the square is empty, clear the piece ID and leave it blank
            square["piece_id"] = None

    def square_clicked(self, row, col):
        """Handle click on a square"""
        if self.selected_square is None:
            if self.board_state[row][col]:
                self.selected_square = (row, col)
                self.highlight_square(row, col, True)
        else:
            from_row, from_col = self.selected_square

            if self.move_piece(self.selected_square, (row, col)):
                turn = "Black" if self.board_state[row][col].islower() else "White"
                self.parent.status_var.set(f"{turn}'s turn")

            self.highlight_square(from_row, from_col, False)
            self.selected_square = None

    def highlight_square(self, row, col, highlight):
        square = self.squares[(row, col)]
        new_color = self.highlight_color if highlight else square["original_color"]
        self.canvas.itemconfig(square["id"], fill=new_color)

class ChessGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Game")
        self.resizable(False, False)

        self.square_size = 85
        self.board_size = self.square_size * 8

        self.status_var = tk.StringVar()
        self.status_var.set("Go Chessy")

        self.board = ChessBoard(self, size=self.square_size)
        self.board.pack(padx=10, pady=10)

        self.status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

if __name__ == "__main__":
    app = ChessGame()
    app.mainloop()
