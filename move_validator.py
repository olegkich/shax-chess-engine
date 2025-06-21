class MoveValidator():
    def __init__(self, board_state):
        self.board_state = board_state

    def is_valid_move(self, from_pos, to_pos, is_white_turn):
        piece = self.board_state[from_pos[0]][from_pos[1]]

        if not piece or (piece.isupper() != is_white_turn):
            return False
        
        move_validators = {
            'p': self._is_valid_pawn_move,
            'n': self._is_valid_knight_move,
            'b': lambda f, t: self._is_valid_sliding_move(f, t, 'b'),
            'r': lambda f, t: self._is_valid_sliding_move(f, t, 'r'),
            'q': lambda f, t: self._is_valid_sliding_move(f, t, 'q'),
            'k': self._is_valid_king_move
        }

        return move_validators.get(piece.lower(), lambda *_: False)(from_pos, to_pos)


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
            return self._is_opponent_piece(from_pos, to_pos)

        return False

    def _is_valid_knight_move(self, from_pos, to_pos):
        row_diff = abs(from_pos[0] - to_pos[0])
        col_diff = abs(from_pos[1] - to_pos[1])

        if (row_diff, col_diff) in [(2, 1), (1, 2)]:
            return self._is_capture_or_empty(from_pos, to_pos)

    def _is_valid_sliding_move(self, from_pos, to_pos, piece):
        if piece.lower() == 'q':
            return self._is_valid_diagonal_move(from_pos, to_pos) or self._is_valid_orthogonal_move(from_pos, to_pos)
        if piece.lower() == 'b':
            return self._is_valid_diagonal_move(from_pos, to_pos)
        if piece.lower() == 'r':
            return self._is_valid_orthogonal_move(from_pos, to_pos)
        return False

    def _is_valid_king_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos

        # is the move one square in any direction
        is_valid_horizontal_king_move = from_row == to_row + 1 or from_row == to_row - 1
        is_valid_vertical_king_move = from_col == to_col + 1 or from_col == to_col - 1

        if from_row == to_row and is_valid_vertical_king_move:
            return self._is_capture_or_empty(from_pos, to_pos)
        
        if from_col == to_col and is_valid_horizontal_king_move:
            return self._is_capture_or_empty(from_pos, to_pos)
        
        if is_valid_vertical_king_move and is_valid_horizontal_king_move:
            return self._is_capture_or_empty(from_pos, to_pos)
            
        return False

    def _is_valid_diagonal_move(self, from_pos, to_pos):
        row_diff = abs(from_pos[0] - to_pos[0])
        col_diff = abs(from_pos[1] - to_pos[1])

        if row_diff != col_diff:
            return False

        x_direction = 1 if (to_pos[0] - from_pos[0]) > 0 else -1
        y_direction = 1 if (to_pos[1] - from_pos[1]) > 0 else -1

        row, col = from_pos

        while (row + x_direction != to_pos[0]) or (col + y_direction != to_pos[1]):
            row += x_direction
            col += y_direction
            
            if self._is_square_occupied(row, col):
                return False

        return self._is_capture_or_empty(from_pos, to_pos)
    
    def _is_valid_orthogonal_move(self, from_pos, to_pos):
        row_diff = abs(from_pos[0] - to_pos[0])
        col_diff = abs(from_pos[1] - to_pos[1])

        # Ensure the move is either horizontal or vertical
        if row_diff != 0 and col_diff != 0:
            return False

        # Determine the direction of movement
        x_direction = 1 if to_pos[0] > from_pos[0] else -1 if to_pos[0] < from_pos[0] else 0
        y_direction = 1 if to_pos[1] > from_pos[1] else -1 if to_pos[1] < from_pos[1] else 0

        row, col = from_pos

        # Move in the direction until reaching the destination
        while (row, col) != to_pos:
            row += x_direction
            col += y_direction

            # If not at the destination and the square is occupied, the path is blocked
            if (row, col) != to_pos and self._is_square_occupied(row, col):
                return False

        # Check if the destination square is empty or holds an opponent's piece
        return self._is_capture_or_empty(from_pos, to_pos)

    # when moving to a square returns true if square is empty or it's a valid capture
    def _is_capture_or_empty(self, from_pos, to_pos):
        return (self._is_square_occupied(to_pos[0], to_pos[1]) and self._is_opponent_piece(from_pos, to_pos)) \
                or not self._is_square_occupied(to_pos[0], to_pos[1])

    def _is_square_occupied(self, row, col):
        # Ensure the indices are within the bounds of the board
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board_state[row][col] != ""
        return True  # If out of bounds, treat as occupied (invalid)

    def _is_opponent_piece(self, from_pos, to_pos):
        piece_to_move = self.board_state[from_pos[0]][from_pos[1]]
        piece_to_be_captured = self.board_state[to_pos[0]][to_pos[1]]

        return (piece_to_move.islower() and piece_to_be_captured.isupper()) or \
            (piece_to_move.isupper() and piece_to_be_captured.islower())
