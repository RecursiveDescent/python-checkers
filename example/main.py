import checkers
import checkers.svg

import os

# board = checkers.Board("-p-k-p-k/k-p-k-p-/-----P--/8/-----P--/--p-----/-K-K-K-K/P-P-----")

board = checkers.Board("""
-P-P-P-P/
P-P-P-P-/
-P-P-P-P/
--------/
--------/
p-p-p-p-/
-p-p-p-p/
p-p-p-p-""")

# Bug D6B4D2 and D6F4D2

# Visualize checkers board in console

def print_board():
	i = 0

	rows = "ABCDEFGH"

	row = 7

	print("   ", end="")

	for c in range(8):
		print(rows[c], end=" ")

	print()

	print()

	for square in board.squares:
		if i % 8 == 0:
			print(row + 1, end="  ")
		
		if square & checkers.KING:
			print("k" if square & checkers.RED else "K", end=" ")
		elif square & checkers.PIECE:
			print("p" if square & checkers.RED else "P", end=" ")
		else:
			print(".", end=" ")
	
		i += 1
	
		if i % 8 == 0:
			print(row + 1, end=" ")
			
			print()
			
			row -= 1

	print()

	print("   ", end="")

	for c in range(8):
		print(rows[c], end=" ")

	print()

file = open("board.svg", "w")

file.write(checkers.svg.board(board))

file.close()

last = None

while True:
	input()
	os.system("clear")
	
	print_board()
	
	print()

	print(f"It is {'reds turn' if board.turn else 'blacks turn'}!")

	file = open("board.svg", "w")

	file.write(checkers.svg.board(board, last))

	file.close()

	move = input("Enter move: ")

	if move == "undo":
		board.pop()

		os.system("clear")

		print_board()
	
		print()

		continue

	if move == "quit":
		break

	if move == "svg":
		break

	# print(board.is_legal(checkers.Move.from_uci(move)))

	try:
		last = board.parse_uci(move)
		
		board.play_move(board.parse_uci(move))
	except Exception as e:
		print("Invalid move!", e)

		raise e

		continue

	if board.is_game_over():
		os.system("clear")

		file = open("board.svg", "w")

		file.write(checkers.svg.board(board, last))

		file.close()

		print_board()
	
		print()
	
		if board.winner() == checkers.RED:
			print("Red wins!")
		else:
			print("Black wins!")
		
		break

exit()



print_board()

print()
"""
generator = checkers.LegalMoveGenerator(board)

list = [move for move in generator]

for move in checkers.LegalMoveGenerator(board):
	print(move)"""

board.play_move(checkers.Move.from_uci("E5D4"))

print_board()

print()

board.play_move(checkers.Move.from_uci("B6C5"))

print_board()

print()

print(board.is_game_over())

print(board.winner())