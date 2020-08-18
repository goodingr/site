import re as regex

from .. import config
from . import exceptions

# Class for pieces on the chessboard
class Piece:
    def __init__(self):
        self.points = 0
        self.current_position = ''
        self.color = ''
        self.label = ''
        self.name = ''
        self._html_class = 'piece '

    @property
    def html_class(self):
        html_class = self._html_class + self.label + ' square-' + self.current_position
        return html_class

    @html_class.setter
    def html_class(self, new_class):
        self._html_class = new_class

    def __str__(self):
        return self.label + self.current_position

    __repr__=__str__


class Pawn(Piece):
    def __init__(self, current_position, color):
        super().__init__()
        self.name = 'Pawn'
        self.points = 1
        self.current_position = current_position
        self.color = color
        self.label = color + "p"

class Knight(Piece):
    def __init__(self, current_position, color):
        super().__init__()
        self.name = 'Knight'
        self.points = 3
        self.current_position = current_position
        self.color = color
        self.label = color + "n"


class Bishop(Piece):
    def __init__(self, current_position, color):
        super().__init__()
        self.name = 'Bishop'
        self.points = 4
        self.current_position = current_position
        self.color = color
        self.label = color + "b"


class Rook(Piece):
    def __init__(self, current_position, color):
        super().__init__()
        self.name = 'Rook'
        self.points = 5
        self.current_position = current_position
        self.color = color
        self.label = color + "r"


class Queen(Piece):
    def __init__(self, current_position, color):
        super().__init__()
        self.name = 'Queen'
        self.points = 9
        self.current_position = current_position
        self.color = color
        self.label = color + "q"

class King(Piece):
    def __init__(self, current_position, color):
        super().__init__()
        self.name = 'King'
        self.points = 0
        self.current_position = current_position
        self.color = color
        self.label = color + "k"
        self.in_check = False

    @Piece.html_class.getter
    def html_class(self):
        html = super().html_class
        if self.in_check:
            html += ' check'
        return html


class Blank(Piece):
    def __init__(self, current_position):
        super().__init__()
        self.name = 'Blank'
        self.current_position = current_position
        self.color = "none"
        self.label = self.color + "_"

#Class for chessboard
class Chessboard:
    def __init__(self, fen_notation=config.START_POSITION_NOTATION):


        self.castling_rights_w = {
            "has_castled": False,
            "rook_a_moved": False,
            "rook_h_moved": False,
            "king_moved": False
        }
        self.castling_rights_b = {
            "has_castled": False,
            "rook_a_moved": False,
            "rook_h_moved": False,
            "king_moved": False
        }


        self._enpassant_target_square = None
        self._enpessant_flag_life = 0

        self._moves = 0
        self._half_moves = 0

        self.white_to_move = True

        # board is a 8x8 array of the pieces on the board
        # (0,0) = a1 or '11'
        # (0,7) = h1 or '81'
        # Includes blank pieces
        self._board = []

        # White king starts on e1, black on e8
        # Used to see if king is in check, updated when moved
        self.king_positions = ['51', '58']


        valid_fen = bool(regex.match(config.FEN_NOTATION_REGEX, fen_notation))
        if not valid_fen:
            fen_notation = config.START_POSITION_NOTATION
        self.load_position(fen_notation)




    # converts file|rank position notation to (row, col) for 2d array _board index
    # rank becomes row, file becomes col
    def convert_to_index(self, position):
        file = int(position[0])
        rank = int(position[1])
        return (rank - 1, file - 1)

    # converts [row][col] into file|rank
    # ex: square a1. [0][0] -> 11
    #     square c4 [3][2] -> 34
    def convert_to_position(self, row, col):
        return str(col+1) + str(row+1)

    # Creates a piece based on the name in FEN notation and appends it to the board
    def create_piece(self, position, name):
        color = None
        piece = Piece()

        if name.isupper():
            color = 'w'
        else:
            color = 'b'
        name = name.lower()
        if name == 'p':
            piece = Pawn(position, color)
        elif name == 'n':
            piece = Knight(position, color)
        elif name == 'b':
            piece = Bishop(position, color)
        elif name == 'r':
            piece = Rook(position, color)
        elif name == 'q':
            piece = Queen(position, color)
        elif name == 'k':
            piece = King(position, color)
        elif name == 'blank':
            piece = Blank(position)

        return piece

    # Returns the html for each piece in _board, excluding blanks
    
    def draw_chessboard(self):
        pieces_html = ''
        for row in self._board:
            for piece in row:
                html_class = piece.html_class
                pieces_html += "<div id='" + piece.current_position + "' class='" + html_class + "'></div>"

        return pieces_html


    def load_position(self, fen_notation, hard=True):
        # Extract parameters for Chessboard class from the notation
        fen_components = fen_notation.split(' ')
        game_component = fen_components[0]
        self.white_to_move = True if fen_components[1]=='w' else False
        castling_info = fen_components[2]
        enpassant_target_square = fen_components[3]
        half_move = int(fen_components[4])
        full_move = int(fen_components[5])

        temp_board = []
        board_row = []
        rank = 8
        file = 1

        #Initialize board with 8 empty rows
        for i in range(8):
            temp_board.append([])

        # Populate board[rank][file] with 64 Pieces representing the current position 
        for character in game_component:
            if character == '/':
                temp_board[rank-1] = board_row
                rank -= 1
                file = 1
                board_row = []
            else:
                pos = str(file) + str(rank)
                if character.isnumeric():
                    for i in range(int(character)):
                        board_row.append(self.create_piece(pos, 'blank'))
                        file += 1
                        pos = str(file) + str(rank)

                else:
                    board_row.append(self.create_piece(pos, character))
                    # Track position of kings
                    if character == "K":
                        self.king_positions[0] = pos
                    if character == "k":
                        self.king_positions[1] = pos
                    file += 1
        temp_board[rank-1] = board_row

        self._board = temp_board

        # Detime castling rights from FEN notation
        if '-' in castling_info:
            self.castling_rights_w['king_moved'] = True
            self.castling_rights_b['king_moved'] = True
        if 'Q' not in castling_info:
            self.castling_rights_w['rook_a_moved'] = True
        if 'K' not in castling_info:
            self.castling_rights_w['rook_h_moved'] = True
        if 'q' not in castling_info:
            self.castling_rights_b['rook_a_moved'] = True
        if 'k' not in castling_info:
            self.castling_rights_b['rook_h_moved'] = True



    def are_opposite_color(self, a, b):
        if a.color == 'w' and b.color == 'b':
            return True
        if a.color == 'b' and b.color == 'w':
            return True
        return False

    def generate_bishop_moves(self, bishop):
        legal_moves = []
        row, col = self.convert_to_index(bishop.current_position)
        color = bishop.color

        # column and row of potential move
        check_row, check_col = row + 1, col + 1
        # up and right
        while check_row <= 7 and check_col <= 7:
            # If the same color, stop 
            if self._board[check_row][check_col].color == color:
                break;
            # Either blank or opposite color so must be legal
            legal_move = self.convert_to_position(check_row, check_col)
            legal_moves.append(legal_move)
            # If opposite color, stop after adding to legal moves
            if self.are_opposite_color(bishop, self._board[check_row][check_col]):
                break;
            check_row += 1
            check_col += 1
        check_row, check_col = row - 1, col - 1
        # Down and Left
        while check_row >= 0 and check_col >= 0:
            # If the same color, stop 
            if self._board[check_row][check_col].color == color:
                break;
            # Either blank or opposite color so must be legal
            legal_move = self.convert_to_position(check_row, check_col)
            legal_moves.append(legal_move)
            # If opposite color, stop after adding to legal moves
            if self.are_opposite_color(bishop, self._board[check_row][check_col]):
                break;
            check_row -= 1
            check_col -= 1
        check_row, check_col = row + 1, col - 1
        # Up and Left
        while check_row <= 7 and check_col >= 0:
            # If the same color, stop 
            if self._board[check_row][check_col].color == color:
                break;
            # Either blank or opposite color so must be legal
            legal_move = self.convert_to_position(check_row, check_col)
            legal_moves.append(legal_move)
            # If opposite color, stop after adding to legal moves
            if self.are_opposite_color(bishop, self._board[check_row][check_col]):
                break;
            check_row += 1
            check_col -= 1
        check_row, check_col = row - 1, col + 1
        # Down and Right
        while check_row >= 0 and check_col <= 7:
            # If the same color, stop 
            if self._board[check_row][check_col].color == color:
                break;
            # Either blank or opposite color so must be legal
            legal_move = self.convert_to_position(check_row, check_col)
            legal_moves.append(legal_move)
            # If opposite color, stop after adding to legal moves
            if self.are_opposite_color(bishop, self._board[check_row][check_col]):
                break;
            check_row -= 1
            check_col += 1

        return legal_moves

    # Vertical and Horizontal Moves
    def generate_rook_moves(self, rook):
        legal_moves = []
        color = rook.color
        row, col = self.convert_to_index(rook.current_position)
        
        # Up
        check_row, check_col = row + 1, col
        while check_row <= 7:
            # If the same color, stop 
            if self._board[check_row][check_col].color == color:
                break;
            # Either blank or opposite color so must be legal
            legal_move = self.convert_to_position(check_row, check_col)
            legal_moves.append(legal_move)
            # If opposite color, stop after adding to legal moves
            if self.are_opposite_color(rook, self._board[check_row][check_col]):
                break;
            check_row += 1
        # Down
        check_row = row - 1
        while check_row >= 0:
            # If the same color, stop 
            if self._board[check_row][check_col].color == color:
                break;
            # Either blank or opposite color so must be legal
            legal_move = self.convert_to_position(check_row, check_col)
            legal_moves.append(legal_move)
            # If opposite color, stop after adding to legal moves
            if self.are_opposite_color(rook, self._board[check_row][check_col]):
                break;
            check_row -= 1
        # Right
        check_row = row
        check_col = col + 1
        while check_col <= 7:
            # If the same color, stop 
            if self._board[check_row][check_col].color == color:
                break;
            # Either blank or opposite color so must be legal
            legal_move = self.convert_to_position(check_row, check_col)
            legal_moves.append(legal_move)
            # If opposite color, stop after adding to legal moves
            if self.are_opposite_color(rook, self._board[check_row][check_col]):
                break;
            check_col += 1

        check_col = col - 1
        while check_col >= 0:
            # If the same color, stop 
            if self._board[check_row][check_col].color == color:
                break;
            # Either blank or opposite color so must be legal
            legal_move = self.convert_to_position(check_row, check_col)
            legal_moves.append(legal_move)
            # If opposite color, stop after adding to legal moves
            if self.are_opposite_color(rook, self._board[check_row][check_col]):
                break;
            check_col -= 1
        return legal_moves


    def generate_knight_moves(self, knight):
        legal_moves = []
        color = knight.color
        row, col = self.convert_to_index(knight.current_position)

    
        # Check forward 2 and left/right 1 if in bounds
        if row < 6 and col < 7:
            potential_move = self._board[row+2][col+1]
            # Empty square or enemy piece
            if potential_move.name == 'Blank' or self.are_opposite_color(knight, potential_move):
                legal_move = self.convert_to_position(row + 2, col + 1)
                legal_moves.append(legal_move)
        if row < 6 and col > 0:
            potential_move = self._board[row+2][col-1]
            # Empty square or enemy piece
            if potential_move.name == 'Blank' or self.are_opposite_color(knight, potential_move):
                legal_move = self.convert_to_position(row + 2, col - 1)
                legal_moves.append(legal_move)
        # Check back 2 and left/right 1
        if row > 1 and col < 7:
            potential_move = self._board[row-2][col+1]
            # Empty square or enemy piece
            if potential_move.name == 'Blank' or self.are_opposite_color(knight, potential_move):
                legal_move = self.convert_to_position(row - 2, col + 1)
                legal_moves.append(legal_move)
        if row > 1 and col > 0:
            potential_move = self._board[row-2][col-1]
            # Empty square or enemy piece
            if potential_move.name == 'Blank' or self.are_opposite_color(knight, potential_move):
                legal_move = self.convert_to_position(row - 2, col - 1)
                legal_moves.append(legal_move)
        # Check 2 right and 1 up/down
        if col < 6 and row < 7:
            potential_move = self._board[row+1][col+2]
            # Empty square or enemy piece
            if potential_move.name == 'Blank' or self.are_opposite_color(knight, potential_move):
                legal_move = self.convert_to_position(row + 1, col + 2)
                legal_moves.append(legal_move)
        if col < 6 and row > 0:
            potential_move = self._board[row-1][col+2]
            # Empty square or enemy piece
            if potential_move.name == 'Blank' or self.are_opposite_color(knight, potential_move):
                legal_move = self.convert_to_position(row - 1, col + 2)
                legal_moves.append(legal_move)
        # 2 left and 1 up/down
        if col > 1 and row < 7:
            potential_move = self._board[row+1][col-2]
            # Empty square or enemy piece
            if potential_move.name == 'Blank' or self.are_opposite_color(knight, potential_move):
                legal_move = self.convert_to_position(row + 1, col - 2)
                legal_moves.append(legal_move)
        if col > 1 and row > 0:
            potential_move = self._board[row-1][col-2]
            # Empty square or enemy piece
            if potential_move.name == 'Blank' or self.are_opposite_color(knight, potential_move):
                legal_move = self.convert_to_position(row - 1, col - 2)
                legal_moves.append(legal_move)
        
        return legal_moves
                
    # Returns all legal pawn moves for the given pawn piece
    # TODO EN PESSANT
    def generate_pawn_moves(self, pawn):
        legal_moves = []
        color = pawn.color
        row, col = self.convert_to_index(pawn.current_position)
        rank = int(pawn.current_position[1])
        file = int(pawn.current_position[0])
        # White Pawn    
        if color == 'w' and row < 7:
            # 1 space ahead of pawn
            if self._board[row+1][col].name == 'Blank':
                legal_move = self.convert_to_position(row + 1, col)
                legal_moves.append(legal_move)
                # Check for 2 space move
                if row == 1:
                    if self._board[row+2][col].name == 'Blank':
                        legal_move = self.convert_to_position(row + 2, col)
                        legal_moves.append(legal_move)
            if col < 7:
                diagonal = self._board[row+1][col+1]
                # diagonal right 
                if diagonal.color == "b" and col < 7:
                    legal_move = self.convert_to_position(row + 1, col + 1)
                    legal_moves.append(legal_move)
            if col > 0:
                diagonal = self._board[row+1][col-1]
                # diagonal left
                if diagonal.color == "b" and col > 0:
                    legal_move = self.convert_to_position(row + 1, col - 1)
                    legal_moves.append(legal_move)
        # Black
        elif color == 'b' and row < 7:
            # 1 space ahead of pawn
            if self._board[row-1][col].name == 'Blank':
                legal_move = self.convert_to_position(row - 1, col)
                legal_moves.append(legal_move)
                # Check for 2 space move
                if row == 6:
                    if self._board[row-2][col].name == 'Blank':
                        legal_move = self.convert_to_position(row - 2, col)
                        legal_moves.append(legal_move)
            if col < 7:
                diagonal = self._board[row-1][col+1]
                # diagonal right 
                if diagonal.color == "w":
                    legal_move = self.convert_to_position(row - 1, col + 1)
                    legal_moves.append(legal_move)
            if col > 0:        
                diagonal = self._board[row-1][col-1]
                # diagonal left
                if diagonal.color == "w":
                    legal_move = self.convert_to_position(row - 1, col - 1)
                    legal_moves.append(legal_move)

        return legal_moves


    # Returns legal King moves in any direction that don't put the King under attack
    def generate_king_moves(self, king):
        legal_moves = []
        color = king.color
        row, col = self.convert_to_index(king.current_position)

        # Up
        if row < 7:
            check_square = self._board[row + 1][col]
            if check_square.color != color:
                move = self.convert_to_position(row + 1, col)
                legal_moves.append(move)
        # Down
        if row > 0:
            check_square = self._board[row - 1][col]
            if check_square.color != color:
                move = self.convert_to_position(row - 1, col)
                legal_moves.append(move)
        # Right
        if col < 7:
            check_square = self._board[row][col + 1]
            if check_square.color != color:
                move = self.convert_to_position(row, col + 1)
                legal_moves.append(move)
        # Left
        if col > 0:
            check_square = self._board[row][col - 1]
            if check_square.color != color:
                move = self.convert_to_position(row, col - 1)
                legal_moves.append(move)
        # Up Right
        if row < 7 and col < 7:
            check_square = self._board[row + 1][col + 1]
            if check_square.color != color:
                move = self.convert_to_position(row + 1, col + 1)
                legal_moves.append(move)
        # Down Left
        if row > 0 and col > 0:
            check_square = self._board[row - 1][col - 1]
            if check_square.color != color:
                move = self.convert_to_position(row - 1, col - 1)
                legal_moves.append(move)
        # Up Left
        if row < 7 and col > 0:
            check_square = self._board[row + 1][col - 1]
            if check_square.color != color:
                move = self.convert_to_position(row + 1, col - 1)
                legal_moves.append(move)
        # Down Right
        if row > 0 and col < 7:
            check_square = self._board[row - 1][col + 1]
            if check_square.color != color:
                move = self.convert_to_position(row - 1, col + 1)
                legal_moves.append(move)

        # Castling
        if self.can_castle(color):
            if color == 'w':
                # White can castle Kingside
                if self._board[0][5].name == "Blank" and self._board[0][6].name == "Blank":
                    if not (self.is_under_attack('61', color) or self.is_under_attack('71', color)):
                        move = '71'
                        legal_moves.append(move)
                if self._board[0][3].name == "Blank" and self._board[0][2].name == "Blank" and self._board[0][1].name == "Blank":
                    if not(self.is_under_attack('41', color) or self.is_under_attack('31', color)):
                        move = '31'
                        legal_moves.append(move)
            if color == 'b':
                # Blank can castle Kingside
                if self._board[7][5].name == "Blank" and self._board[7][6].name == "Blank":
                    if not (self.is_under_attack('68', color) or self.is_under_attack('78', color)):
                        move = '78'
                        legal_moves.append(move)
                if self._board[7][3].name == "Blank" and self._board[7][2].name == "Blank" and self._board[7][1].name == "Blank":
                    if not(self.is_under_attack('48', color) or self.is_under_attack('38', color)):
                        move = '38'
                        legal_moves.append(move)


        # Remove moves to squares that are attacked
        legal_moves[:] = [move for move in legal_moves if not self.is_under_attack(move, color)]

        return legal_moves



    # Return true if the given color still has castling rights
    def can_castle(self, color):
        if color == 'w':
            if not(self.castling_rights_w['king_moved'] or self.castling_rights_w['rook_a_moved'] or self.castling_rights_w['rook_h_moved'] or self.castling_rights_w['has_castled']):
                return True
        if color == 'b':
            if not(self.castling_rights_b['king_moved'] or self.castling_rights_b['rook_a_moved'] or
                   self.castling_rights_b['rook_h_moved'] or self.castling_rights_b['has_castled']):
                return True
        return False

    # returns a list of legal moves for the piece in the position
    def generate_legal_moves(self, position):
        legal_moves = []
        print("generating moves for position " + position)

        #move this to helper function
        file = int(position[1])
        rank = int(position[0])        

        piece = self._board[file -1][rank -1]

        # Check whos turn it is
        if piece.color == 'w' and not self.white_to_move:
            return []
        if piece.color == 'b' and self.white_to_move:
            return []

        if piece.name == "Pawn":
            legal_moves = self.generate_pawn_moves(piece)
        if piece.name == "Knight":
            legal_moves = self.generate_knight_moves(piece)
        if piece.name == "Bishop":
            legal_moves = self.generate_bishop_moves(piece)
        if piece.name == "Rook":
            legal_moves = self.generate_rook_moves(piece)
        if piece.name == "Queen":
            legal_moves = self.generate_rook_moves(piece) + self.generate_bishop_moves(piece)
        if piece.name == "King":
            legal_moves = self.generate_king_moves(piece)



        # TODO Special King Moves

        # TODO Simulate each move and check if mover's king becomes
        legal_moves[:] = [move for move in legal_moves if not self.temp_move_check(position, move)]

        return legal_moves

    # Return true if the square is under attack from the perspective of 'color'
    def is_under_attack(self, position, color = None):
        row, col = self.convert_to_index(position)
        if color == None:
            color = self._board[row][col].color

        # Check Horizontal
        for check_col in range(col + 1, 8):
            check_square = self._board[row][check_col]

            # True if opposite color king is next to position
            if check_col == col + 1 and check_square.name == "King" and color != check_square.color:
                return True

            if (check_square.name == "Rook" or check_square.name == "Queen") and color != check_square.color:
                return True

            if check_square.color == color:
                break;
            if check_square.name in ["Bishop", "Knight", "Pawn", "King"]:
                break;
        for check_col in range(col - 1, -1, -1):
            check_square = self._board[row][check_col]

            # True if opposite color king is next to position
            if check_col == col - 1 and check_square.name == "King" and color != check_square.color:
                return True

            if (check_square.name == "Rook" or check_square.name == "Queen") and color != check_square.color:
                return True

            if check_square.color == color:
                break;
            if check_square.name in ["Bishop", "Knight", "Pawn", "King"]:
                break;

        # Check Vertical
        for check_row in range(row + 1, 8):
            check_square = self._board[check_row][col]

            # True if opposite color king is next to position
            if check_row == row + 1 and check_square.name == "King" and color != check_square.color:
                return True

            if (check_square.name == "Rook" or check_square.name == "Queen") and color != check_square.color:
                return True

            if check_square.color == color:
                break;
            if check_square.name in ["Bishop", "Knight", "Pawn", "King"]:
                break;
        for check_row in range(row - 1, -1, -1):
            check_square = self._board[check_row][col]

            # True if opposite color king is next to position
            if check_row == row - 1 and check_square.name == "King" and color != check_square.color:
                return True

            if (check_square.name == "Rook" or check_square.name == "Queen") and color != check_square.color:
                return True

            if check_square.color == color:
                break;
            if check_square.name in ["Bishop", "Knight", "Pawn", "King"]:
                break;
        # Up Right
        check_row, check_col = row + 1, col + 1
        while check_row < 8 and check_col < 8:
            check_square = self._board[check_row][check_col]

            # King or Pawn diagonal to attacked square
            if check_row == row + 1 and check_col == col + 1 and (check_square.name == "King" or check_square.name == "Pawn") and color != check_square.color:
                return True

            if (check_square.name == "Bishop" or check_square.name == "Queen") and color != check_square.color:
                return True

            if check_square.color == color:
                break;
            if check_square.name in ["Rook", "Knight", "Pawn", "King"]:
                break;

            check_row += 1
            check_col += 1

        # Down Left
        check_row, check_col = row - 1, col - 1
        while check_row >= 0 and check_col > 0:
            check_square = self._board[check_row][check_col]

            # King or Pawn diagonal to attacked square
            if check_row == row - 1 and check_col == col - 1 and (check_square.name == "King" or check_square.name == "Pawn") and color != check_square.color:
                return True

            if (check_square.name == "Bishop" or check_square.name == "Queen") and color != check_square.color:
                return True

            if check_square.color == color:
                break;
            if check_square.name in ["Rook", "Knight", "Pawn", "King"]:
                break;

            check_row -= 1
            check_col -= 1

        # Up Left
        check_row, check_col = row + 1, col - 1
        while check_row < 8 and check_col >= 0:
            check_square = self._board[check_row][check_col]

            # King or Pawn diagonal to attacked square
            if check_row == row + 1 and check_col == col - 1 and (check_square.name == "King" or check_square.name == "Pawn") and color != check_square.color:
                return True

            if (check_square.name == "Bishop" or check_square.name == "Queen") and color != check_square.color:
                return True

            if check_square.color == color:
                break;
            if check_square.name in ["Rook", "Knight", "Pawn", "King"]:
                break;

            check_row += 1
            check_col -= 1
        # Down Right
        check_row, check_col = row - 1, col + 1
        while check_row >= 0 and check_col < 8:
            check_square = self._board[check_row][check_col]

            # King or Pawn diagonal to attacked square
            if check_row == row - 1 and check_col == col + 1 and (check_square.name == "King" or check_square.name == "Pawn") and color != check_square.color:
                return True

            if (check_square.name == "Bishop" or check_square.name == "Queen") and color != check_square.color:
                return True

            if check_square.color == color:
                break;
            if check_square.name in ["Rook", "Knight", "Pawn", "King"]:
                break;

            check_row -= 1
            check_col += 1

        # Check skews for knight moves
        skews = [(2,1),(2,-1),(-2,1),(-2,-1),(1, 2),(-1,2),(1,-2),(-1,-2)]
        for skew in skews:
            check_row = row + skew[0]
            check_col = col + skew[1]

            if check_row < 8 and check_row >= 0 and check_col < 8 and check_col >=0:
                check_square = self._board[check_row][check_col]
                if check_square.name == "Knight" and check_square.color != color:
                    return True




    # Return true if the temp move puts the mover's king in check
    def temp_move_check(self, initial, destination):
        irow, icol = self.convert_to_index(initial)
        drow, dcol = self.convert_to_index(destination)
        moving_piece = self._board[irow][icol]
        destination_piece = self._board[drow][dcol]


        # Make the move on the temp board and check if king is attacked
        moving_piece.current_position = destination
        color = moving_piece.color
        self._board[drow][dcol] = moving_piece
        blank = Blank(initial)
        self._board[irow][icol] = blank

        if moving_piece.name == "King":
            if color == 'w':
                self.king_positions[0] = destination
            else:
                self.king_positions[1] = destination

        def undo():
            print(self._board[drow][dcol])
            moving_piece.current_position = initial
            self._board[irow][icol] = moving_piece
            self._board[drow][dcol] = destination_piece
            print(self._board[drow][dcol])

            if moving_piece.name == "King":
                if color == 'w':
                    self.king_positions[0] = initial
                else:
                    self.king_positions[1] = initial


        if color == 'w' and self.is_under_attack(self.king_positions[0], 'w'):
            undo()
            return True
        if color == 'b' and self.is_under_attack(self.king_positions[1], 'b'):
            undo()
            return True
        undo()
        return False



    # returns true if destination is in the list of legal moves for the initial position
    def is_legal_move(self, initial, destination):
        if destination in self.generate_legal_moves(initial):
            return True
        return False

    # Changes state of board. 
    # Changes value of board array
    # If king moves, changes king_positions
    def change_board_state(self, initial, destination):
        irow, icol = self.convert_to_index(initial)
        drow, dcol = self.convert_to_index(destination)

        changes = []

        # Change the pieces position and update the array
        moving_piece = self._board[irow][icol]
        moving_piece.current_position = destination
        color = moving_piece.color
        self._board[drow][dcol] = moving_piece
        # Set the initial square to blank
        blank = Blank(initial)
        self._board[irow][icol] = blank

        change = {
            "position": destination,
            "class": moving_piece.html_class
            }
        changes.append(change)
        change = {  "position": initial,
                    "class": blank.html_class }

        changes.append(change)

        # Track king position for determining check
        # and update castling rights
        # If castling, update rook position also
        if moving_piece.name == "King":
            if color == 'w':
                self.king_positions[0] = destination
                self.castling_rights_w["king_moved"] = True
                # Kingside Castle, move rook
                if initial == '51' and destination == '71':
                    self.castling_rights_w['has_castled'] = True
                    rook = self._board[0][7]
                    rook.current_position = '61'
                    self._board[0][5] = rook
                    blank = Blank('81')
                    self._board[0][7] = blank
                    change = {"position" : '61', "class": rook.html_class}
                    changes.append(change)
                    change = {"position": '81', "class": blank.html_class }
                    changes.append(change)
                # Queenside Castle
                if initial == '51' and destination == '31':
                    self.castling_rights_w['has_castled'] = True
                    rook = self._board[0][0]
                    rook.current_position = '41'
                    self._board[0][3] = rook
                    blank = Blank('11')
                    self._board[0][0] = blank
                    change = {"position": '41', "class": rook.html_class}
                    changes.append(change)
                    change = {"position": '11', "class": blank.html_class }
                    changes.append(change)
            else:
                self.king_positions[1] = destination
                self.castling_rights_b["king_moved"] = True
                # Kingside Castle, move rook
                if initial == '58' and destination == '78':
                    self.castling_rights_b['has_castled'] = True
                    rook = self._board[7][7]
                    rook.current_position = '68'
                    self._board[7][5] = rook
                    blank = Blank('88')
                    self._board[7][7] = blank
                    change = {"position" : '68', "class": rook.html_class}
                    changes.append(change)
                    change = {"position": '88', "class": blank.html_class }
                    changes.append(change)
                # Queenside Castle
                if initial == '58' and destination == '38':
                    self.castling_rights_b['has_castled'] = True
                    rook = self._board[7][0]
                    rook.current_position = '48'
                    self._board[7][3] = rook
                    blank = Blank('18')
                    self._board[7][0] = blank
                    change = {"position": '48', "class": rook.html_class}
                    changes.append(change)
                    change = {"position": '18', "class": blank.html_class }
                    changes.append(change)
        # Rook moves for tracking castling rights
        if moving_piece.name == "Rook":
            # Moving rook on a1
            if color == 'w' and initial == '11' and not self.castling_rights_w['rook_a_moved']:
                self.castling_rights_w['rook_a_moved'] = True
            # h1
            if color == 'w' and initial == '81' and not self.castling_rights_w['rook_h_moved']:
                self.castling_rights_w['rook_a_moved'] = True
            # a8
            if color == 'b' and initial == '18' and not self.castling_rights_b['rook_a_moved']:
                self.castling_rights_b['rook_a_moved'] = True
            # h8
            if color == 'b' and initial == '88' and not self.castling_rights_b['rook_h_moved']:
                self.castling_rights_b['rook_a_moved'] = True



        white_king_pos, black_king_pos = self.king_positions[0], self.king_positions[1]
        wrow, wcol = self.convert_to_index(white_king_pos)
        brow, bcol = self.convert_to_index(black_king_pos)

        white_king = self._board[wrow][wcol]
        black_king = self._board[brow][bcol]


        # See if opposite king is under attack
        if color == 'w' and self.is_under_attack(black_king_pos):
            black_king.in_check = True
            king_html = black_king.html_class
            change = { "position": black_king_pos, "class": king_html }
            changes.append(change)
        # See if opposite king is under attack
        if color == 'b' and self.is_under_attack(white_king_pos):
            white_king.in_check = True
            king_html = white_king.html_class
            change = { "position": white_king_pos, "class": king_html }
            changes.append(change)
        # See if mover's king is no longer in check
        if color == 'w' and self._board[wrow][wcol].in_check and not self.is_under_attack(white_king_pos):
            white_king.in_check = False
            change = { "position": white_king_pos, "class": white_king.html_class }
            changes.append(change)
        if color == 'b' and self._board[brow][bcol].in_check and not self.is_under_attack(black_king_pos):
            black_king.in_check = False
            change = { "position": black_king_pos, "class": black_king.html_class }
            changes.append(change)

        return changes



    # If move is legal, change chessboard state and white_to_move
    def move(self, initial, destination):
        changes = []
        if self.is_legal_move(initial, destination):
            changes = self.change_board_state(initial, destination)
            self.white_to_move = not self.white_to_move
        return changes



