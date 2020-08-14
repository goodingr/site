import re as regex

from .. import config

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

        # board is a 64 size array of the pieces on the board
        # Includes blank pieces for use with FEN notation
        self._board = []

        valid_fen = bool(regex.match(config.FEN_NOTATION_REGEX, fen_notation))
        if not valid_fen:
            fen_notation = config.START_POSITION_NOTATION
        self.load_position(fen_notation)


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

        self._board.append(piece)

    # Returns the html for each piece in _board, excluding blanks
    
    def draw_chessboard(self):
        pieces_html = ''
        for piece in self._board:
            if piece.name != "Blank":
                pieces_html += "<div class='piece " + piece.label + " square-" + piece.current_position + "'></div>"

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

        rank = 8
        file = 1
        for character in game_component:
            if character == '/':
                rank -= 1
                file = 1
            else:
                pos = str(rank) + str(file)
                if character.isnumeric():
                    for i in range(int(character)):
                        self.create_piece(pos, 'blank')
                        file += 1
                else:
                    self.create_piece(pos, character)
                    file += 1

