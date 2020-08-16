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
        self.html_class = 'piece'

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
        self._pieces = {
            'white': {},
            'black': {},
        }

        self._enpassant_target_square = None
        self._enpessant_flag_life = 0

        self._moves = 0
        self._half_moves = 0

        # board is a 8x8 array of the pieces on the board
        # Includes blank pieces for use with FEN notation
        self._board = []

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
                pieces_html += "<div id='" + piece.current_position + "' class='piece " + piece.label + " square-" + piece.current_position + "'></div>"

        return pieces_html


    def load_position(self, fen_notation, hard=True):
        # Extract parameters for Chessboard class from the notation
        fen_components = fen_notation.split(' ')
        game_component = fen_components[0]
        move = 0 if fen_components[1]=='w' else 1
        castling_infop = fen_components[2]
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
                    file += 1
        temp_board[rank-1] = board_row

        self._board = temp_board


    def generate_bishop_moves(self, bishop):
        

    def generate_knight_moves(self, knight):
        legal_moves = []
        color = knight.color
        row, col = self.convert_to_index(knight.current_position)

        if color == 'w':
            # Check forward 2 and left/right 1 if in bounds
            if row < 6 and col < 7:
                potential_move = self._board[row+2][col+1]
                # Empty square or enemy piece
                if potential_move.name == 'Blank' or potential_move.color == 'b':
                    legal_move = self.convert_to_position(row + 2, col + 1)
                    legal_moves.append(legal_move)
            if row < 6 and col > 0:
                potential_move = self._board[row+2][col-1]
                # Empty square or enemy piece
                if potential_move.name == 'Blank' or potential_move.color == 'b':
                    legal_move = self.convert_to_position(row + 2, col - 1)
                    legal_moves.append(legal_move)
            # Check back 2 and left/right 1
            if row > 1 and col < 7:
                potential_move = self._board[row-2][col+1]
                # Empty square or enemy piece
                if potential_move.name == 'Blank' or potential_move.color == 'b':
                    legal_move = self.convert_to_position(row - 2, col + 1)
                    legal_moves.append(legal_move)
            if row > 1 and col > 0:
                potential_move = self._board[row-2][col-1]
                # Empty square or enemy piece
                if potential_move.name == 'Blank' or potential_move.color == 'b':
                    legal_move = self.convert_to_position(row - 2, col - 1)
                    legal_moves.append(legal_move)
            # Check 2 right and 1 up/down
            if col < 6 and row < 7:
                potential_move = self._board[row+1][col+2]
                # Empty square or enemy piece
                if potential_move.name == 'Blank' or potential_move.color == 'b':
                    legal_move = self.convert_to_position(row + 1, col + 2)
                    legal_moves.append(legal_move)
            if col < 6 and row > 0:
                potential_move = self._board[row-1][col+2]
                # Empty square or enemy piece
                if potential_move.name == 'Blank' or potential_move.color == 'b':
                    legal_move = self.convert_to_position(row - 1, col + 2)
                    legal_moves.append(legal_move)
            # 2 left and 1 up/down
            if col > 1 and row < 7:
                potential_move = self._board[row+1][col-2]
                # Empty square or enemy piece
                if potential_move.name == 'Blank' or potential_move.color == 'b':
                    legal_move = self.convert_to_position(row + 1, col - 2)
                    legal_moves.append(legal_move)
            if col > 1 and row > 0:
                potential_move = self._board[row-1][col-2]
                # Empty square or enemy piece
                if potential_move.name == 'Blank' or potential_move.color == 'b':
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
        if color == 'w':
            # 1 space ahead of pawn
            if self._board[row+1][col].name == 'Blank':
                legal_move = self.convert_to_position(row + 1, col)
                legal_moves.append(legal_move)
                # Check for 2 space move
                if self._board[row+2][col].name == 'Blank' and row == 1:
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
        elif color == 'b':
            # 1 space ahead of pawn
            if self._board[row-1][col].name == 'Blank':
                legal_move = self.convert_to_position(row - 1, col)
                legal_moves.append(legal_move)
                # Check for 2 space move
                if self._board[row-2][col].name == 'Blank' and row == 6:
                    legal_move = self.convert_to_position(row - 2, col)
                    legal_moves.append(legal_move)
            if col < 7:
                diagonal = self._board[row-1][col+1]
                # diagonal right 
                if diagonal.color == "b":
                    legal_move = self.convert_to_position(row - 1, col + 1)
                    legal_moves.append(legal_move)
            if col > 0:        
                diagonal = self._board[row-1][col-1]
                # diagonal left
                if diagonal.color == "b":
                    legal_move = self.convert_to_position(row - 1, col - 1)
                    legal_moves.append(legal_move)

        return legal_moves




    # returns a list of legal moves for the piece in the position
    def generate_legal_moves(self, position):
        legal_moves = []
        print("generating moves for position " + position)

        #move this to helper function
        file = int(position[1])
        rank = int(position[0])
        

        piece = self._board[file -1][rank -1]

        if piece.name == "Pawn":
            legal_moves = self.generate_pawn_moves(piece)
        if piece.name == "Knight":
            legal_moves = self.generate_knight_moves(piece)

        return legal_moves




    # returns true if destination is in the list of legal moves for the initial position
    def is_legal_move(self, initial, destination):
        if destination in self.generate_legal_moves(initial):
            return True
        return False

    # Changes state of board. Changes value of board array
    def change_board_state(self, initial, destination):
        irow, icol = self.convert_to_index(initial)
        drow, dcol = self.convert_to_index(destination)

        # Change the pieces position and update the array
        moving_piece = self._board[irow][icol]
        moving_piece.current_position = destination
        self._board[drow][dcol] = moving_piece
        # Set the initial square to blank
        self._board[irow][icol] = Blank(initial)
        return

    # If move is legal, change chessboard state
    def move(self, initial, destination):
        if self.is_legal_move(initial, destination):
            self.change_board_state(initial, destination)
        return



