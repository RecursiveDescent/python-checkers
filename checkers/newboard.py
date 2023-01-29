import checkers

class Move:
	def __init__(self, from_square, to_square, drop = None, last = None):
		self.from_square = from_square
		
		self.to_square = to_square

		self.drop = drop

		self.dropped = []

		self.last = last

		self.promotion = (to_square >= 0 and to_square < 8) or (to_square >= 56 and to_square < 64)

	def from_uci(uci_string):
		if len(uci_string) % 2 != 0 or len(uci_string) < 4:
			raise ValueError("Invalid uci string: %s" % uci_string)

		if len(uci_string) > 4:
			ucistr = uci_string

			moves = []

			lastsq = None

			while len(ucistr) > 2:
				move = Move.from_uci(ucistr[:4])
				
				moves.append(move)

				ucistr = ucistr[2:]
				
				lastsq = move.to_square

			try:
				if not checkers.SQUARES[ucistr[:2].upper()] == lastsq:
					moves.append(Move(lastsq, checkers.SQUARES[ucistr[:2].upper()]))

				return MultiJump(moves)
			except:
				raise ValueError("Invalid uci string: %s" % uci_string)
				
		
		try:
			from_square = checkers.SQUARES[uci_string[0:2].upper()]
	
			to_square = checkers.SQUARES[uci_string[2:4].upper()]

			print(f"Move {checkers.index_to_square(from_square)} -> {checkers.index_to_square(to_square)}")

			return Move(from_square, to_square)
		except KeyError:
			raise ValueError("Invalid move: " + uci_string)

	def __str__(self):
		return f"<{checkers.index_to_square(self.from_square)} {checkers.index_to_square(self.to_square)} {[checkers.index_to_square(square) for square in self.drops]}>"

	def __repr__(self):
		return str(self)

class MultiJump(Move):
	def __init__(self, moves):
		self.moves = moves

		if len(self.moves) > 0:
			super().__init__(self.moves[0].from_square, self.moves[-1].to_square)
		else:
			super().__init__(0, 0)

	def __str__(self):
		string = "["

		for move in self.moves:
			string += str(move) + " "

		return string + "]"

class Piece:
	def __init__(self, king, color, square = None):
		self.is_king = king

		self.color = color

		self.square = square

	def __repr__(self):
		repr = "K" if self.is_king else "P"

		if self.color == checkers.RED:
			repr = repr.lower()

		return repr + f" {checkers.index_to_square(self.square)}"
	
class Board:
	def __init__(self, fen):
		self.squares = [None] * 64

		self.turn = checkers.RED

		self.move_stack = []

		self.load_fen(fen)

	# Implementation of pseudo-FEN for checkers, only suitable for setting starting state
	def load_fen(self, fen):
		self.red_pieces = 0

		self.black_pieces = 0
		
		spl = fen.replace("\n", "").split("/")

		i = 0
		
		for row in spl:
			if len(row) < 1 or (len(row) < 8 and len(row) > 1) or len(row) > 8:
				raise Exception("Invalid FEN")

			if len(row) < 8:
				try:
					i += int(row[0]) - 1
				except:
					raise Exception("Invalid FEN")
			
			for column in row:
				if column == "p" or column == "k":
					self.squares[i] = Piece(column == "k", checkers.RED, i)

					print("-", checkers.index_to_square(i), i)

					self.red_pieces += 1

				if column == "P" or column == "K":
					self.squares[i] = Piece(column == "K", checkers.BLACK, i)

					self.black_pieces += 1

				i += 1

	def push(self, move):
		