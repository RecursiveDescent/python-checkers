import checkers

class Move:
	def __init__(self, from_square, to_square, drops = None, last = None):
		self.from_square = from_square
		
		self.to_square = to_square

		self.drops = drops or []

		self.dropped = []

		self.last = last

	def __eq__(self, other):
		return self.uci() == other.uci()
		
	# Convenience for getting tile from the index
	def source(self, board):
		return board[self.from_square[0]][self.from_square[1]]
	
	def target(self, board):
		return board[self.to_square[0]][self.to_square[1]]

	def squares(self):
		return [self.from_square, self.to_square]

		#self.promotion = (to_square >= 0 and to_square < 8) or (to_square >= 56 and to_square < 64)

	def uci(self):
		rows = "ABCDEFGH"
		
		return rows[self.from_square[0]] + str(self.from_square[1] + 1) + rows[self.to_square[0]] + str(self.to_square[1] + 1)

	def contains(self, square):
		return self.from_square == square or self.to_square == square

	def from_uci(uci_string):
		if len(uci_string) % 2 != 0 or len(uci_string) < 4:
			raise checkers.InvalidMoveError("Invalid uci string: %s" % uci_string)

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
				if not checkers.parse_square(ucistr[:2].upper()) == lastsq:
					moves.append(Move(lastsq, checkers.parse_square(ucistr[:2].upper())))

				return MultiJump(moves)
			except:
				raise checkers.InvalidMoveError("Invalid uci string: %s" % uci_string)
				
		
		try:
			from_square = checkers.parse_square(uci_string[0:2].upper())
	
			to_square = checkers.parse_square(uci_string[2:4].upper())

			return Move(from_square, to_square)
		except KeyError:
			raise checkers.InvalidMoveError("Invalid move: " + uci_string)

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

	def squares(self):
		sqrs = []

		for move in self.moves:
			sqrs.append(*move.squares())

		return sqrs

	def uci(self):
		uci = ""

		c = 0
				
		for move in self.moves:
			uci += move.uci() if c % 2 == 0 else checkers.index_to_square(move.to_square)

			c += 1

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




class Piece:
	def __init__(self, color, type):
		self.color = color

		self.type = type

	def __repr__(self):
		repr = "K" if self.type == checkers.KING else "P"

		if self.color == checkers.RED:
			repr = repr.lower()

		return repr



				
class Tile:
	def __init__(self, x, y, piece = None):
		self.x = x
		
		self.y = y
		
		self.piece = piece

		self.old_piece = None

		self.upper_left = None

		self.upper_right = None

		self.lower_left = None

		self.lower_right = None

	def index(self):
		return (self.x, self.y)

	def ascii(self):
		return self.piece or "-"

	def follow_jump(self, square):
		jump = None

		square = checkers.parse_square(square)

		if self.upper_left and (self.upper_left.x, self.upper_left.y) == square:
			jump = self.upper_left

		if self.upper_right and (self.upper_right.x, self.upper_right.y) == square:
			jump = self.upper_right

		if self.lower_left and (self.lower_left.x, self.lower_left.y) == square:
			jump = self.lower_left

		if self.lower_right and (self.lower_right.x, self.lower_right.y) == square:
			jump = self.lower_right

		if jump.piece:
			return jump

		return None
	
	def get_moves(self):
	    moves = []
		
	    if self.piece is None:
	        return moves
	    
	    # Check for moves to the upper left
	    if self.upper_left is not None and self.upper_left.piece is None:
	        if self.piece.color == checkers.RED or self.piece.type == checkers.KING:
	            moves.append((self, self.upper_left))
	    
	    # Check for moves to the upper right
	    if self.upper_right is not None and self.upper_right.piece is None:
	        if self.piece.color == checkers.RED or self.piece.type == checkers.KING:
	            moves.append((self, self.upper_right))
	    
	    # Check for moves to the lower left
	    if self.lower_left is not None and self.lower_left.piece is None:
	        if self.piece.color == checkers.BLACK or self.piece.type == checkers.KING:
	            moves.append((self, self.lower_left))
	    
	    # Check for moves to the lower right
	    if self.lower_right is not None and self.lower_right.piece is None:
	        if self.piece.color == checkers.BLACK or self.piece.type == checkers.KING:
	            moves.append((self, self.lower_right))
	    
	    return moves


	def get_jumps(self):
		jumps = []
		
		if self.piece is None:
			return jumps
	    
	    # Check for jumps to the upper left
		if self.upper_left is not None and self.upper_left.piece is not None and self.upper_left.piece.color != self.piece.color and self.upper_left.upper_left is not None and self.upper_left.upper_left.piece is None:
			if self.piece.color == checkers.RED or self.piece.type == checkers.KING:
				jumps.append((self, self.upper_left, self.upper_left.upper_left))
	    
	    # Check for jumps to the upper right
		if self.upper_right is not None and self.upper_right.piece is not None and self.upper_right.piece.color != self.piece.color and self.upper_right.upper_right is not None and self.upper_right.upper_right.piece is None:
			if self.piece.color == checkers.RED or self.piece.type == checkers.KING:
				jumps.append((self, self.upper_right, self.upper_right.upper_right))
	    
	    # Check for jumps to the lower left
		if self.lower_left is not None and self.lower_left.piece is not None and self.lower_left.piece.color != self.piece.color and self.lower_left.lower_left is not None and self.lower_left.lower_left.piece is None:
			if self.piece.color == checkers.BLACK or self.piece.type == checkers.KING:
				jumps.append((self, self.lower_left, self.lower_left.lower_left))
	    
	    # Check for jumps to the lower right
		if self.lower_right is not None and self.lower_right.piece is not None and self.lower_right.piece.color != self.piece.color and self.lower_right.lower_right is not None and self.lower_right.lower_right.piece is None:
			if self.piece.color == checkers.BLACK or self.piece.type == checkers.KING:
				jumps.append((self, self.lower_right, self.lower_right.lower_right))

		return jumps
	
	def jumped(frm, to):
		return (frm.x + int((to.x - frm.x) / 2), frm.y + int((to.y - frm.y) / 2))

		return False

	def get_all_multijumps(self):
		def dfs(cur, path, paths, piece = None):
			path.append(cur)
	
			original = cur.piece
	
			cur.piece = piece or original
	
			jumps = cur.get_jumps()
	
			if not any(jumps) and len(path) > 1:
				paths.append(path.copy())
			else:
				for jump in jumps:
					if jump:
						branch = path.copy()
						
						branch.append(jump[1])
						
						dfs(jump[2], branch, paths, jump[0].piece)
	
			cur.piece = original

		paths = []
	
		dfs(self, [], paths)
	
		return paths
	
	def get_move(self, direction):
		if direction == "upper_left":
			move = Move((self.x, self.y), (self.upper_left.x, self.upper_left.y))

			if self.upper_left and self.upper_left.piece and self.upper_left.piece.color != self.piece.color and self.upper_left.upper_left and self.upper_left.upper_left.piece == None:
				move.drops.append((self.upper_left.x, self.upper_left.y))

				move.to_square = (self.upper_left.upper_left.x, self.upper_left.upper_left.y)

				return move

			if self.upper_left.piece == None:
				return move

		if direction == "upper_right":
			move = Move((self.x, self.y), (self.upper_right.x, self.upper_right.y))

			if self.upper_right and self.upper_right.piece and self.upper_right.piece.color != self.piece.color and self.upper_right.upper_right and self.upper_right.upper_right.piece == None:
				move.drops.append((self.upper_right.x, self.upper_right.y))

				move.to_square = (self.upper_right.upper_right.x, self.upper_right.upper_right.y)

				return move

			if self.upper_right.piece == None:
				return move

		if direction == "lower_left":
			move = Move((self.x, self.y), (self.lower_left.x, self.lower_left.y))

			if self.lower_left and self.lower_left.piece and self.lower_left.piece.color != self.piece.color and self.lower_left.lower_left and self.lower_left.lower_left.piece == None:
				move.drops.append((self.lower_left.x, self.lower_left.y))

				move.to_square = (self.lower_left.lower_left.x, self.lower_left.lower_left.y)

				return move

			if self.lower_left.piece == None:
				return move

		if direction == "lower_right":
			move = Move((self.x, self.y), (self.lower_right.x, self.lower_right.y))

			if self.lower_right and self.lower_right.piece and self.lower_right.piece.color != self.piece.color and self.lower_right.lower_right and self.lower_right.lower_right.piece == None:
				move.drops.append((self.lower_right.x, self.lower_right.y))

				move.to_square = (self.lower_right.lower_right.x, self.lower_right.lower_right.y)

				return move

			if self.lower_right.piece == None:
				return move

			return None
	
	def uci(self):
		rows = "ABCDEFGH"

		return rows[self.x] + str(self.y + 1)

	def __str__(self):
		 return self.uci()

	def __repr__(self):
		return f"<{self.uci()} [{self.piece or '-'}]>"


class Board:
	def __init__(self, fen = "-P-P-P-P/P-P-P-P-/-P-P-P-P/--------/--------/p-p-p-p-/-p-p-p-p/p-p-p-p-"):
		self.squares = []

		for x in range(8):
			col = []

			for y in range(8):
				col.append(Tile(x, y))

			self.squares.append(col)

		self.turn = checkers.RED

		self.move_number = 1

		self.move_stack = []

		self.require_jumps = True

		self.require_all_jumps = True

		self.red_pieces = []

		self.black_pieces = []

		self.load_fen(fen)

		self.refresh_tiles()

		self.legal_moves = LegalMoveGenerator(self)

	# Implementation of pseudo-FEN for checkers, only suitable for setting starting state

	def create_tile(self, x, y, piece):
		tile = Tile(x, y, piece)

		return tile

	
	def scan_tile(self, x, y):
		tile = self.squares[x][y]

		if x - 1 >= 0 and y - 1 >= 0:
			tile.lower_left = self.squares[x - 1][y - 1]

		if x + 1 < 8 and y - 1 >= 0:
			tile.lower_right = self.squares[x + 1][y - 1]

		if x - 1 >= 0 and y + 1 < 8:
			tile.upper_left = self.squares[x - 1][y + 1]

		if x + 1 < 8 and y + 1 < 8:
			tile.upper_right = self.squares[x + 1][y + 1]

		return tile

	
	
	def refresh_tiles(self):
		for x in range(8):
			for y in range(8):
				self.scan_tile(x, y)
				

	# Pseudo-fen
	
	def load_fen(self, fen):
		spl = fen.replace("\n", "").split("/")

		i = 0

		x = 0

		y = 0
		
		for row in spl:
			if len(row) < 1 or (len(row) < 8 and len(row) > 1) or len(row) > 8:
				raise Exception("Invalid FEN")

			if len(row) < 8:
				try:
					i += int(row[0]) - 1
				except:
					raise Exception("Invalid FEN")

			x = 0
			
			for column in row:
				if column == "p" or column == "k":
					self.squares[x][y] = self.create_tile(x, y, Piece(checkers.RED, checkers.PIECE if column == "p" else checkers.KING))

					self.red_pieces.append(self.squares[x][y])

				if column == "P" or column == "K":
					self.squares[x][y] = self.create_tile(x, y, Piece(checkers.BLACK, checkers.PIECE if column == "P" else checkers.KING))

					self.black_pieces.append(self.squares[x][y])

				i += 1

				x += 1

			y += 1
			

	
	#def do_move(self, move):

	def update_pieces(self):
		self.red_pieces = []

		self.black_pieces = []

		for y in range(8):
			for x in range(8):
				if self.squares[x][y].piece:
					tile = self.squares[x][y]

					if self.turn == tile.piece.color == checkers.RED:
						self.red_pieces.append(tile)
					else:
						self.black_pieces.append(tile)
		
	
	def undo_move(self, move):
		self.squares[move.from_square[0]][move.from_square[1]].piece = self.squares[move.to_square[0]][move.to_square[1]].piece
		
		self.squares[move.to_square[0]][move.to_square[1]].piece = None

		for drop in move.drops:
			self.squares[drop[0]][drop[1]].piece = self.squares[drop[0]][drop[1]].old_piece

		self.update_pieces()

	def do_move(self, move):
		self.squares[move.to_square[0]][move.to_square[1]].piece = self.squares[move.from_square[0]][move.from_square[1]].piece

		self.squares[move.from_square[0]][move.from_square[1]].piece = None

		for drop in move.drops:
			self.squares[drop[0]][drop[1]].old_piece = self.squares[drop[0]][drop[1]].piece
			
			self.squares[drop[0]][drop[1]].piece = None

		self.update_pieces()
	
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
	
	def is_legal(self, move):
		return move in self.legal_moves
	
	def parse_uci(self, uci):
		move = checkers.Move.from_uci(uci)
		
		if type(move) == MultiJump:
			for m in move.moves:
				tile = Tile.jumped(self.squares[m.from_square[0]][m.from_square[1]], self.squares[m.to_square[0]][m.to_square[1]])

				if self.squares[tile[0]][tile[1]].piece:
					m.drops.append(tile)
					
					move.drops.append(tile)
		else:
			tile = Tile.jumped(self.squares[move.from_square[0]][move.from_square[1]], self.squares[move.to_square[0]][move.to_square[1]])

			if self.squares[tile[0]][tile[1]].piece and (tile[0] != move.from_square[0] and tile[1] != move.from_square[1]) :
				move.drops.append(tile)
			
		return move

	def play_move(self, move):
		if not self.is_legal(move):
			pieces = self.red_pieces if self.turn == checkers.RED else self.black_pieces

			for tile in pieces:
				if len(tile.get_all_multijumps()) > 0:
					raise checkers.IllegalMoveError(f"Illegal move. A jump is available and must be taken.\nFirst legal move: \"{next(iter(self.legal_moves)).uci()}\"")
			
			raise checkers.IllegalMoveError("Illegal move.")

		if self.is_game_over():
			raise checkers.IllegalMoveError("Game has ended.")

		
		self.push(move)
	
	def is_game_over(self):
		return len(self.red_pieces) == 0 or len(self.black_pieces) == 0
	
	def winner(self):
		if len(self.black_pieces) == 0:
			return checkers.RED

		if len(self.red_pieces) == 0:
			return checkers.BLACK

		return None

							   



class LegalMoveGenerator:
	def __init__(self, board, any = False):
		self.board = board

		self.piece_index = 0

		self.pieces = [*self.board.red_pieces, *self.board.black_pieces]

		# If true, then the generator will return valid moves that either player can make instead of just the current turn
		self.any = any

	def count(self):
		return len(list(self))
    
	def __iter__(self):
		pieces = self.pieces if self.any else (self.board.red_pieces if self.board.turn == checkers.RED else self.board.black_pieces)

		has_jump = False
		
		for tile in pieces:
			paths = tile.get_all_multijumps()

			if len(paths) > 0:
				has_jump = True

			for path in paths:
				#print("PATH: ", path)
				if len(path) == 3:
					yield Move(path[0].index(), path[2].index(), [path[1].index()])

					continue
				
				jump = MultiJump([])

				iterator = path.__iter__()

				try:
					last = None
					
					while True:
						move = Move(None, None, [])
						
						move.from_square = last.to_square if last else next(iterator).index()

						drop = next(iterator).index()

						move.drops = [drop] # [*board.legal_moves]

						try:
							move.to_square = next(iterator).index()

							jump.drops.append(drop)
	
							jump.moves.append(move)

							last = move
						except StopIteration:
							jump.moves.append(Move(last.to_square, drop, [move.from_square]))
				except StopIteration:
					pass

				yield jump



		if not has_jump:
			for tile in pieces:
				for move in tile.get_moves():
					yield Move(move[0].index(), move[1].index(), [])
		
		return