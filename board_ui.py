import tkinter as tk

class ChessBoard(tk.Frame):
    def __init__(self, parent, size=64):
        super().__init__(parent)
        self.parent = parent
        self.size = size
        self.piece_symbols = {
            "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
            "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"
        }
        
        # Initial setup for a chess board
        self.board_state = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]
        
        self.squares = {}
        self.selected_square = None
        self.selected_piece = None
        self.draw_board()
        self.place_pieces()
        
    def draw_board(self):
        """Draw the chess board with alternating colors"""
        # Light and dark square colors
        self.light_color = "#FFFFFF"  # White
        self.dark_color = "#769656"   # Green
        self.highlight_color = "#aaaaff"  # Light blue for selection
        
        # Create a canvas for the board
        self.canvas = tk.Canvas(self, width=self.size*8, height=self.size*8)
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
        # Calculate which square was clicked
        col = event.x // self.size
        row = event.y // self.size
        
        if 0 <= row < 8 and 0 <= col < 8:
            print(f"Square clicked: {row}, {col}")  # Debug print
            self.square_clicked(row, col)
    
    def place_pieces(self):
        """Place pieces on the board according to board state"""
        for row in range(8):
            for col in range(8):
                piece = self.board_state[row][col]
                if piece:
                    self.place_piece(row, col, piece)
    
    def place_piece(self, row, col, piece_code):
        """Place a piece on the specified square"""
        square = self.squares[(row, col)]
        
        # Remove existing piece if any
        if square["piece_id"]:
            self.canvas.delete(square["piece_id"])
        
        # Get the piece symbol
        symbol = self.piece_symbols.get(piece_code, "")
        
        # Use different colors for pieces based on both piece color and square color
        is_white_piece = not piece_code.islower()
        is_light_square = square["is_light"]
        
        # Choose appropriate colors for contrast
        if is_white_piece:
            # For white pieces
            piece_color = "#999999" if is_light_square else "white"
        else:
            # For black pieces
            piece_color = "black"
        
        # Calculate center position of the square
        x = col * self.size + self.size // 2
        y = row * self.size + self.size // 2
        
        # Create text for the piece
        piece_id = self.canvas.create_text(
            x, y, 
            text=symbol, 
            font=("Arial", int(self.size * 0.7)), 
            fill=piece_color
        )
        
        # Store piece ID
        square["piece_id"] = piece_id
    
    def square_clicked(self, row, col):
        """Handle click on a square"""
        if self.selected_square is None:
            # Select piece if there is one
            if self.board_state[row][col]:
                self.selected_square = (row, col)
                # Highlight selected square
                self.highlight_square(row, col, True)
                print(f"Selected square: {row}, {col}")  # Debug print
        else:
            from_row, from_col = self.selected_square
            
            # Move piece
            if self.move_piece(self.selected_square, (row, col)):
                print(f"Moved piece from {self.selected_square} to {(row, col)}")
                # Update the status bar
                turn = "Black" if self.board_state[row][col].islower() else "White"
                self.parent.status_var.set(f"{turn}'s turn")
            
            # Remove highlight from previously selected square
            self.highlight_square(from_row, from_col, False)
            
            # Reset selection
            self.selected_square = None
    
    def highlight_square(self, row, col, highlight):
        """Highlight or unhighlight a square"""
        square = self.squares[(row, col)]
        new_color = self.highlight_color if highlight else square["original_color"]
        
        # Update square color
        self.canvas.itemconfig(square["id"], fill=new_color)
    
    def move_piece(self, from_pos, to_pos):
        """Move a piece from one position to another"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Get the piece code
        piece_code = self.board_state[from_row][from_col]
        
        if not piece_code:
            return False  # No piece at from_pos
        
        # If same position, do nothing
        if from_pos == to_pos:
            return False
        
        # Clear the destination square first (if it has a piece)
        to_square = self.squares[(to_row, to_col)]
        if to_square["piece_id"]:
            self.canvas.delete(to_square["piece_id"])
        
        # Update board state
        self.board_state[to_row][to_col] = piece_code
        self.board_state[from_row][from_col] = ""
        
        # Update visuals
        self.place_piece(to_row, to_col, piece_code)
        
        # Clear original square's piece
        from_square = self.squares[(from_row, from_col)]
        if from_square["piece_id"]:
            self.canvas.delete(from_square["piece_id"])
            from_square["piece_id"] = None
        
        return True


class ChessGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Game")
        self.resizable(False, False)
        
        # Size settings
        self.square_size = 64
        self.board_size = self.square_size * 8
        
        # Status variable
        self.status_var = tk.StringVar()
        self.status_var.set("White's turn")
        
        # Create and place board
        self.board = ChessBoard(self, size=self.square_size)
        self.board.pack(padx=10, pady=10)
        
        # Add status bar
        self.status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
