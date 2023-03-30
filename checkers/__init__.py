# Make these accessible to the module
from checkers.board import Piece, Board, Move, LegalMoveGenerator

RED = True

BLACK = False

EMPTY = 0

PIECE = 2

KING = 4

_rows = "ABCDEFGH"

def index_to_square(index):
	return _rows[index[0]] + str(index[1] + 1)

# Convert A1 etc to an index
def parse_square(square):
	if type(square) == tuple:
		return square
	
	return (_rows.index(square[0]), int(square[1]) - 1)

STARTING_BOARD_FEN = 'PPPPPPPP/PPPPPPPP/8/8/8/8/PPPPPPPP/PPPPPPPP'

class InvalidMoveError(Exception):
	pass

class IllegalMoveError(Exception):
	pass
	
class AmbiguousMoveError(Exception):
	pass