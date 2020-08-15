from django.test import TestCase
from chess.utils import chessboard

# Create your tests here.
class BoardTestCase(TestCase):

    # Tests White pawns moving 1 or 2 spaces forward or diagonally
    # Does not test en pessant or diagonal on edge of board
    # Positions: 23 33 44 52 62 72
    # FEN: 7k/8/8/4p3/p1pP1p2/PPP4p/4PPP1/7K w - - 0 1
    def test_pawn_moves(self):
        fen_notation = '7k/8/8/4p3/p1pP1p2/PPP4p/4PPP1/7K w - - 0 1'
        board = chessboard.Chessboard(fen_notation)

        moves = board.generate_legal_moves('23')
        legal = ['24', '14', '34']
        self.assertEqual(set(moves), set(legal))

        moves = board.generate_legal_moves('33')
        legal = []
        self.assertEqual(set(moves), set(legal))

        moves = board.generate_legal_moves('44')
        legal = ['45', '55']
        self.assertEqual(set(moves), set(legal))

        moves = board.generate_legal_moves('52')
        legal = ['53', '54']
        self.assertEqual(set(moves), set(legal))

        moves = board.generate_legal_moves('62')
        legal = ['63']
        self.assertEqual(set(moves), set(legal))

        moves = board.generate_legal_moves('72')
        legal = ['73', '74', '83']
        self.assertEqual(set(moves), set(legal))

        moves = board.generate_legal_moves('13')
        legal = []
        self.assertEqual(set(moves), set(legal))
