class MoveValidator():
    def __init__(self, board_state):
        self.board_state = board_state

    def is_valid_move(self, from_pos, to_pos, is_white_turn):
        piece = self.board_state[from_pos[0]][from_pos[1]]
        
        if not piece:
            return False  # No piece on the source square
        
        # Check turn (uppercase = white, lowercase = black)
        if piece.isupper() != is_white_turn:
            return False
        
        # Route validation by piece type
        if piece.lower() == 'p':
            return self._is_valid_pawn_move(from_pos, to_pos)
        elif piece.lower() == 'n':
            return self._is_valid_knight_move(from_pos, to_pos)
        elif piece.lower() in ['q', 'b', 'r']:
            return self._is_valid_sliding_move(from_pos, to_pos, piece)

        return False

    def _is_valid_pawn_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        direction = -1 if self.board_state[from_row][from_col].isupper() else 1

        # Regular pawn move (1 square forward)
        if from_col == to_col and self.board_state[to_row][to_col] == "":
            if to_row == from_row + direction:
                return True
            # First move (2 squares forward)
            if (from_row == 6 and direction == -1) or (from_row == 1 and direction == 1):
                if to_row == from_row + 2 * direction and self.board_state[from_row + direction][to_col] == "":
                    return True

        # Capture (diagonal)
        if abs(from_col - to_col) == 1 and to_row == from_row + direction:
            # Probably will have problems because it doesn't check which color the piece is
            # TODO: is_capture_valid()
            return self._is_square_occupied

        return False

    def _is_valid_knight_move(self, from_pos, to_pos):
        row_diff = abs(from_pos[0] - to_pos[0])
        col_diff = abs(from_pos[1] - to_pos[1])
        return (row_diff, col_diff) in [(2, 1), (1, 2)]

    def _is_valid_sliding_move(self, from_pos, to_pos, piece):
        if piece.lower() == 'q':
            return True
        if piece.lower() == 'b':
            return self._is_diagonal_move_valid(from_pos, to_pos)
        if piece.lower() == 'r':
            return self._is_straight_move_valid(from_pos, to_pos)
        return False

    def _is_diagonal_move_valid(self, from_pos, to_pos):
        print("from pos: ", from_pos)

        row_diff = abs(from_pos[0] - to_pos[0])
        col_diff = abs(from_pos[1] - to_pos[1])

        if row_diff != col_diff:
            return False

        x_direction = 1 if (to_pos[0] - from_pos[0]) > 0 else -1
        y_direction = 1 if (to_pos[1] - from_pos[1]) > 0 else -1

        row, col = from_pos

        while (row != to_pos[0]) and (col != to_pos[1]):
            row += x_direction
            col += y_direction
            
            if self._is_square_occupied(row, col):
                print(f"Square at {row},{col} is occupied.")
                return False

        if self._is_square_occupied(row, col):
            return self._is_opponent_piece(row, col)
        
        return True
            
        

    def _is_square_occupied(self, row, col):
        # Ensure the indices are within the bounds of the board
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board_state[row][col] != ""
        return True  # If out of bounds, treat as occupied (invalid)

    def _is_opponent_piece(self, row, col):
        
        piece = self.board_state[row][col]
        return (piece.islower() and self.board_state[row][col].isupper()) or \
            (piece.isupper() and self.board_state[row][col].islower())