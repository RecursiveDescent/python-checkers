import checkers

class Piece:
	def __init__(self, king, color):
		self.is_king = king

		self.color = color

	def __repr__(self):
		repr = "K" if self.is_king else "P"

		if self.color == checkers.RED:
			repr = repr.lower()

		return repr + f" {checkers.index_to_square(self.square)}"

class Move:
	def __init__(self, from_square, to_square, drops = [], last = None):
		self.from_square = from_square
		
		self.to_square = to_square

		self.drops = drops

		self.dropped = []

		self.last = last

		self.promotion = (to_square >= 0 and to_square < 8) or (to_square >= 56 and to_square < 64)

	def uci(self):
		return checkers.index_to_square(self.from_square) + checkers.index_to_square(self.to_square)

	def contains(self, square):
		return self.from_square == square or self.to_square == square

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

	def uci(self):
		uci = ""
				
		for move in self.moves:
			uci += move.uci()

		return uci

	def contains(self, square):
		for move in self.moves:
			if move.contains(square):
				return True

		return False

	def __str__(self):
		string = "["

		for move in self.moves:
			string += str(move) + " "

		return string + "]"

class Board:
	def __init__(self, fen = "-P-P-P-P/P-P-P-P-/-P-P-P-P/--------/--------/p-p-p-p-/-p-p-p-p/p-p-p-p-"):
		self.squares = [0] * 64

		self.load_fen(fen)

		self.turn = checkers.RED

		self.move_number = 1

		self.move_stack = []

		self.require_jumps = True

		self.require_all_jumps = True

		self.legal_moves = LegalMoveGenerator(self)

	# Returns squares that contain pieces
	def get_pieces(self):
		return [square for square in self.squares if square != checkers.EMPTY]

	def get_player_pieces(self, player):
		squares = []

		for sq in range(len(self.squares)):
			if self.squares[sq] != checkers.EMPTY and self.squares[sq] & 1 == player:
				squares.append(sq)

		return squares

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
					self.squares[i] = (checkers.PIECE if column == "p" else checkers.KING) | checkers.RED

					self.red_pieces += 1

				if column == "P" or column == "K":
					self.squares[i] = (checkers.PIECE if column == "P" else checkers.KING) | checkers.BLACK

					self.black_pieces += 1

				i += 1

	
	def do_move(self, move):
		if len(move.drops) > 0:
			move.dropped = []
			
			for sq in move.drops:
				move.dropped.append(self.squares[sq])

				if self.squares[sq] & 1 == checkers.RED:
					self.red_pieces -= 1
				else:
					self.black_pieces -= 1
				
				self.squares[sq] = checkers.EMPTY

		if move.promotion and not self.squares[move.from_square] & checkers.KING:
			self.squares[move.to_square] = checkers.KING | (self.squares[move.from_square] & 1)

			move.promoted = True
		else:
			self.squares[move.to_square] = self.squares[move.from_square]

			move.promoted = False

		self.squares[move.from_square] = checkers.EMPTY

	
	def undo_move(self, move):
		self.squares[move.from_square] = self.squares[move.to_square]

		self.squares[move.to_square] = checkers.EMPTY

		# Restore dropped pieces
		for i in range(len(move.drops)):
			self.squares[move.drops[i]] = move.dropped[i]

			if move.dropped[i] & 1 == checkers.RED:
				self.red_pieces += 1
			else:
				self.black_pieces += 1

		# Undo promotion
		if move.promotion:
			self.squares[move.from_square] = checkers.PIECE | (self.squares[move.from_square] & 1)

	def push(self, move):
		if type(move) is MultiJump:
			for m in move.moves:
				self.do_move(m)
		else:
			self.do_move(move)

		self.move_stack.append(move)

		self.turn = not self.turn

		self.legal_moves = LegalMoveGenerator(self)

	def pop(self):
		if len(self.move_stack) == 0:
			return None

		move = self.move_stack.pop()

		if type(move) is MultiJump:
			for m in reversed(move.moves):
				self.undo_move(m)
		else:
			self.undo_move(move)

		self.turn = not self.turn

		self.legal_moves = LegalMoveGenerator(self)

		return move

	def peek(self):
		if len(self.move_stack) == 0:
			return None
		
		return self.move_stack[-1]

	def is_free(self, square):
		return square >= 0 and square < 64 and self.squares[square] == checkers.EMPTY

	def calculate_jumps(self, square, up = False, down = False, visited = [], last = None):
		if square in visited:
			return []
		
		upper_right = square - 8 + 1

		lower_right = square + 8 + 1

		upper_left = square - 8 - 1

		lower_left = square + 8 - 1

		jumps = []

		# APPARENTLY, default arguments always point to the same object
		visited = visited.copy()

		visited.append(square)

		# Temporarily mark square as empty so you can jump onto the same square
		saved = self.squares[square]
		
		self.squares[square] = checkers.EMPTY

		# Prevents trying to jump the piece that was just jumped
		came_from = None

		if last:
			came_from = last.from_square

		if up and upper_left >= 0 and upper_left < 64 and not self.is_free(upper_left) and self.squares[upper_left] & 1 != self.turn:
			if self.is_free(upper_left - 8 - 1) and abs(((upper_left - 8 - 1) % 8) - square % 8) < 3 and upper_left - 8 - 1 != came_from:
				jumps.append(Move(square, upper_left - 8 - 1, [upper_left], last))
				
				for j in self.calculate_jumps(upper_left - 8 - 1, up, down, visited, jumps[-1]):
					jumps.append(j)

				visited.append(upper_left - 8 - 1)
		
		if up and upper_right >= 0 and upper_right < 64 and not self.is_free(upper_right) and self.squares[upper_right] & 1 != self.turn:
			if self.is_free(upper_right - 8 + 1) and abs(((upper_right - 8 + 1) % 8) - square % 8) < 3 and upper_right - 8 + 1 != came_from:
				jumps.append(Move(square, upper_right - 8 + 1, [upper_right], last))

				for j in self.calculate_jumps(upper_right - 8 + 1, up, down, visited, jumps[-1]):
					jumps.append(j)

				visited.append(upper_right - 8 + 1)

		if down and lower_left >= 0 and lower_left < 64 and not self.is_free(lower_left) and self.squares[lower_left] & 1 != self.turn:
			if self.is_free(lower_left + 8 - 1) and abs(((lower_left + 8 - 1) % 8) - square % 8) < 3 and lower_left + 8 - 1 != came_from:
				jumps.append(Move(square, lower_left + 8 - 1, [lower_left], last))

				for j in self.calculate_jumps(lower_left + 8 - 1, up, down, visited, jumps[-1]):
					jumps.append(j)

				visited.append(lower_left + 8 - 1)

		
		if down and lower_right >= 0 and lower_right < 64 and not self.is_free(lower_right) and self.squares[lower_right] & 1 != self.turn:
			if self.is_free(lower_right + 8 + 1) and abs(((lower_right + 8 + 1) % 8) - square % 8) < 3 and lower_right + 8 + 1 != came_from:
				jumps.append(Move(square, lower_right + 8 + 1, [lower_right], last))

				for j in self.calculate_jumps(lower_right + 8 + 1, up, down, visited, jumps[-1]):
					jumps.append(j)

				visited.append(lower_right + 8 + 1)

		self.squares[square] = saved
						
		return jumps
	
	
	
	def count_jumps(self, square, up = False, down = False):
		potential_jumps = self.calculate_jumps(square, up, down)

		max = 0

		for jump in potential_jumps:
			chain = []

			chain.append(jump)

			taken = 1

			current = jump

			while current.last:
				taken += 1
				
				chain.append(current.last)

				current = current.last

			if len(chain) > max:
				max = len(chain)

		return max
	
	
	def _jumps_to_square(self, move, king):
		up = self.squares[move.from_square] & 1 == checkers.RED

		down = self.squares[move.from_square] & 1 == checkers.BLACK
		
		potential_jumps = [j for j in self.calculate_jumps(move.from_square, up or self.squares[move.from_square] & checkers.KING, down or self.squares[move.from_square] & checkers.KING)]

		# Filter out weird duplicates
		jumps = []

		def filter_path(mp):
			if str(mp) in jumps:
				return False

			jumps.append(str(mp))
			
			if type(move) is MultiJump:
				for m in move.moves:
					if m.from_square == mp.from_square and m.to_square == mp.to_square:
						return True

				return False
			else:
				return mp.to_square == move.to_square

		
		return [j for j in potential_jumps if filter_path(j)]
	
	
	
	
	def is_legal(self, move):
		source = self.squares[move.from_square]

		target = self.squares[move.to_square]

		pos = checkers.index_to_square(move.from_square)

		to = checkers.index_to_square(move.to_square)
		
		if target != checkers.EMPTY:
			return False

		if source & 1 != self.turn:
			return False

		up = self.squares[move.from_square] & 1 == checkers.RED
		down = self.squares[move.from_square] & 1 == checkers.BLACK

		jumps_taken = len(move.moves) if type(move) is MultiJump else 1
		
		if self.require_all_jumps and self.count_jumps(move.from_square, up or source & checkers.KING, down or source & checkers.KING) > jumps_taken:
			return False

		potential_jumps = sorted(self._jumps_to_square(move, source & checkers.KING), key = lambda jump: abs(jump.from_square - move.from_square))

		if type(move) is MultiJump:
			for i in range(len(move.moves)):
				m = move.moves[i]
				
				if len([mm for mm in potential_jumps if mm.from_square == m.from_square and mm.to_square == m.to_square]) == 0:
					return False

			return True

		if len(potential_jumps) > 1 and len([mm for mm in potential_jumps if mm.from_square == move.from_square and mm.to_square == move.to_square]) == 0:
			return False

		if pos[0] == to[0]:
			return False

		if abs("ABCDEFGH".index(pos[0]) - "ABCDEFGH".index(to[0])) > 1 or abs(int(pos[1]) - int(to[1])) > 1:
			return False

		if self.turn == checkers.RED:
			if int(to[1]) < int(pos[1]) and not source & checkers.KING:
				return False
		else:
			if int(to[1]) > int(pos[1]) and not source & checkers.KING:
				return False

		if self.require_jumps and self.has_jump(self.turn):
			return False

		return True
	
	
	
	def parse_uci(self, uci):
		move = checkers.Move.from_uci(uci)

		if not self.is_legal(move):
			try:
				self.play_move(move)

				self.pop()
			except Exception as e:
				raise e

		return move
	
	
	
	def play_move(self, move):
		source = self.squares[move.from_square]

		target = self.squares[move.to_square]

		if source & 1 != self.turn:
			raise checkers.IllegalMoveError(f"It is not {'reds' if source & 1 else 'blacks'} turn to move.")

		pos = checkers.index_to_square(move.from_square)

		to = checkers.index_to_square(move.to_square)

		if target != checkers.EMPTY and move.to_square != move.from_square:
			raise checkers.IllegalMoveError("Target square is not empty.")
		
		rows = "ABCDEFGH"

		up = self.squares[move.from_square] & 1 == checkers.RED
		down = self.squares[move.from_square] & 1 == checkers.BLACK

		jumps_taken = len(move.moves) if type(move) is MultiJump else 1

		print(self.count_jumps(move.from_square, up or source & checkers.KING, down or source & checkers.KING), jumps_taken)
		
		if self.require_all_jumps and self.count_jumps(move.from_square, up or source & checkers.KING, down or source & checkers.KING) > jumps_taken:
			raise checkers.IllegalMoveError("All jumps must be taken.")

		# Filter the list of potential jumps to jumps that end in the target square
		# Sort the list of potential jumps by distance
		potential_jumps = sorted(self._jumps_to_square(move, source & checkers.KING), key = lambda jump: abs(jump.from_square - move.from_square))

		if type(move) is MultiJump:
			populated = MultiJump([]) # The drops of the moves in this object will be guaranteed filled unlike the one passed
			
			for i in range(len(move.moves)):
				m = move.moves[i]
				
				if len([mm for mm in potential_jumps if mm.from_square == m.from_square and mm.to_square == m.to_square]) == 0:
					raise checkers.IllegalMoveError("Invalid path to target square.")

				# Get the potential jump that matches this move
				self.do_move([mm for mm in potential_jumps if mm.from_square == m.from_square and mm.to_square == m.to_square][0])

				populated.moves.append([mm for mm in potential_jumps if mm.from_square == m.from_square and mm.to_square == m.to_square][0])

			self.move_stack.append(populated)

			self.turn = not self.turn

			return

		if len(potential_jumps) > 1 and len([mm for mm in potential_jumps if mm.from_square == move.from_square and mm.to_square == move.to_square]) == 0:
			raise checkers.InvalidMoveError("Ambiguous move.")

		if len(potential_jumps) > 0:
			chain = []

			jump = potential_jumps[0]

			chain.append(jump)

			while jump.last:
				chain.append(jump.last)

				jump = jump.last

			for move in reversed(chain):
				self.push(move)

			return

		# If the columns match it's not a diagonal move
		if pos[0] == to[0]:
			raise checkers.IllegalMoveError("Illegal move.")

		# If the row or columns are too far away it's an invalid move
		if abs(rows.index(pos[0]) - rows.index(to[0])) > 1 or abs(int(pos[1]) - int(to[1])) > 1:
			raise checkers.IllegalMoveError("Illegal move.")

		if self.turn == checkers.RED:
			if int(to[1]) < int(pos[1]) and not source & checkers.KING:
				raise checkers.IllegalMoveError("Illegal move. (Cannot move backwards as a normal piece)")
		else:
			if int(to[1]) > int(pos[1]) and not source & checkers.KING:
				raise checkers.IllegalMoveError("Illegal move. (Cannot move backwards as a normal piece)")

		if self.require_jumps and self.has_jump(self.turn):
			raise checkers.IllegalMoveError("Illegal move. (A jump is available and must be taken)")

		self.push(move)

	
	def has_jump(self, player):
		for square in self.get_player_pieces(player):
			up = self.squares[square] & 1 == checkers.RED

			down = self.squares[square] & 1 == checkers.BLACK
		
			if self.calculate_jumps(square, up or self.squares[square] & checkers.KING, down or self.squares[square] & checkers.KING):
				return True

		return False

	
	def is_game_over(self):
		return self.red_pieces == 0 or self.black_pieces == 0

	
	def winner(self):
		if self.black_pieces == 0:
			return checkers.RED

		if self.red_pieces == 0:
			return checkers.BLACK

		return None
		


class LegalMoveGenerator:
	def __init__(self, board, any = False):
		self.board = board

		self.piece_index = 0

		self.pieces = self.board.get_pieces()

		# A list of already known valid moves that haven't been returned yet
		self.queued = []

		# If true, then the generator will return valid moves that either player can make instead of just the current turn
		self.any = any

	def __iter__(self):
		return self

	def next(self):
		turn = self.board.turn

		if self.piece_index >= len(self.board.squares):
			raise StopIteration()

		square = self.piece_index

		piece = self.board.squares[square]

		self.piece_index += 1

		pos = checkers.index_to_square(square)

		if piece & 1 == checkers.RED or piece & checkers.KING:
			dr = f"{chr(ord(pos[0]) + 1)}{int(pos[1]) - 1}"

			dl = f"{chr(ord(pos[0]) - 1)}{int(pos[1]) - 1}"

			try:
				if self.board.is_free(checkers.parse_square(dr)):
					move = Move(square, checkers.parse_square(dr))

					if self.board.is_legal(move):
						self.queued.append(move)
	
				if self.board.is_free(checkers.parse_square(dl)):
					move = Move(square, checkers.parse_square(dl))

					if self.board.is_legal(move):
						self.queued.append(move)
			except Exception:
				pass

		if (piece & 1 == checkers.BLACK or piece & checkers.KING) and not int(pos[1]) + 1 > 8:
			ur = f"{chr(ord(pos[0]) + 1)}{int(pos[1]) + 1}"

			ul = f"{chr(ord(pos[0]) - 1)}{int(pos[1]) + 1}"

			try:
				if self.board.is_free(checkers.parse_square(ur)):
					move = Move(square, checkers.parse_square(ur))

					if self.board.is_legal(move):
						self.queued.append(move)
	
				if self.board.is_free(checkers.parse_square(ul)):
					move = Move(square, checkers.parse_square(ul))

					if self.board.is_legal(move):
						self.queued.append(move)
			except Exception:
				pass

		self.board.turn = piece & 1

		up = self.board.squares[square] & 1 == checkers.RED

		down = self.board.squares[square] & 1 == checkers.BLACK

		try:
			for move in [s for s in self.board.calculate_jumps(square, up or self.board.squares[square] & checkers.KING, down or self.board.squares[square]  & checkers.KING) if self.board.squares[s.from_square] != checkers.EMPTY]:
				self.queued.append(move)
		except KeyError:
			pass

		self.board.turn = turn
		
		if not self.any:
			self.queued = [m for m in self.queued if self.board.squares[m.from_square] & 1 == turn or m.last != None]

		return self.queued.pop() if len(self.queued) > 0 else self.next()

	def __next__(self):
		return self.next()