# Make these accessible to the module
from checkers.board import Piece, Board, Move, LegalMoveGenerator

# Honestly it doesn't really need to be like this since checkers is super simple in that theres really only two colors and two types of piece, but I did it like this for accuracy with the py-chess documentation
RED = True

BLACK = False

# PIECE starts at 2 so that piece ownership can be inferred by a bitmask

EMPTY = 0

PIECE = 2

KING = 4 # Not 3 because the binary for 2 and 3 overlap (0b110 vs 0b010)

# I could also find a different solution for the board but I'll adhere to what py-chess does

SQUARES = {}

def index_to_square(index):
	inverted = { v: k for k, v in SQUARES.items() }

	return inverted[index]

# Convert A1 etc to an index
def parse_square(square):
	if type(square) == int:
		return square

	if not square in SQUARES:
		raise ValueError("Invalid square: " + square)

	return SQUARES[square]

_rows = "ABCDEFGH"

_col = 1

_c = 0

for i in reversed(range(64)):
	SQUARES[f"{_rows[i % 8]}{_col}"] = i

	_c += 1

	if _c == 8:
		_c = 0
		_col += 1


STARTING_BOARD_FEN = 'PPPPPPPP/PPPPPPPP/8/8/8/8/PPPPPPPP/PPPPPPPP'

class OldPiece:
	def __init__(self, king, color):
		self.is_king = king

		self.color = color

class InvalidMoveError(Exception):
	pass

class IllegalMoveError(Exception):
	pass
	
class AmbiguousMoveError(Exception):
	pass