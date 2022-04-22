from buildhat import Hat, Matrix, Motor, ForceSensor
import time

motor = Motor("C")
matrix_a = Matrix("A")
button = ForceSensor("B")

SECONDS_BETWEEN_BUTTON_PRESSES = 1.5
PLAYER_1 = "orange"
PLAYER_2 = "blue"

WHO_GOES_FIRST = PLAYER_2
ROUNDS_TO_PLAY = 5

player = WHO_GOES_FIRST
cursor = 0
board = [0,0,0,0,0,0,0,0,0]	# Gets filled with color strings or 0

def set_move():
	global board, player, cursor
	if board[cursor] != 0:
		return False
	board[cursor] = player
	if player == PLAYER_1:
		player = PLAYER_2
	else:
		player = PLAYER_1
	refresh_display(cursor, player)
	return True

def addr_to_coord(addr):
	if addr > 8 or addr < 0:
		raise Exception("Invalid matrix address")
	x = addr // 3
	y = addr % 3
	return (x,y)

def board_to_pixel_matrix(board):
	pixm = [[0,0,0],[0,0,0],[0,0,0]]
	i = 0
	for x in range(3):
		for y in range(3):
			pixm[x][y] = (board[i],10)
			i += 1
	return pixm

def refresh_display(cursor, player_color):
	global board
	matrix_a.set_pixels(board_to_pixel_matrix(board), False)
	if board[cursor] != 0:
		matrix_a.set_pixel(addr_to_coord(cursor), ("red",10), True)
	else:
		matrix_a.set_pixel(addr_to_coord(cursor), (player_color,4), True)

# Code winning as a board position (index into board array) in the winning line
# Implicitly indicates the color of the winner
# Only 8 win types and 9 board positions
# Return the unused position 4 (1,1) to indicate tie
# -1 if the game is still running
def check_endgame():
	global board
	# Top left corner wins
	if board[0]:
		# First Row across
		if board[0] == board[1] and board[1] == board[2]:
			return 1	# (1,0)
		# First Column down
		if board[0] == board[3] and board[3] == board[6]:
			return 0	# (0,0)
		# Top LR diagonal
		if board[0] == board[4] and board[4] == board[8]:
			return 8	#(2,2)

	# Top Right corner wins
	if board[2]:
		# Third Column down
		if board[2] == board[5] and board[5] == board[8]:
			return 5	# (2,1)
		# Top RL diagonal
		if board[2] == board[4] and board[4] == board[6]:
			return 2	# (2,0)

	# Second Row across
	if board[3] and board[3] == board[4] and board[4] == board[5]:
		return 3	# (0,1)
	# Third Row across
	if board[6] and board[6] == board[7] and board[7] == board[8]:
		return 6	# (0,2)
	# Second Column down
	if board[1] and board[1] == board[4] and board[4] == board[7]:
		return 7	# (1,2)

	if check_for_stalemate():
		return 4	# (1,1)

	return -1

def check_for_stalemate():
	global board
	for i in range(9):
		if board[i] == 0:
			return False
	return True

def loop_clockwise(clockwise_color, frames=120, frame_delay=0.045, centerpx=(0,0)):
	global matrix_a
	matrix = [
		[(clockwise_color,10),(0,0),(0,0)],
		[(clockwise_color,8),centerpx,(0,0)],
		[(clockwise_color,6),(clockwise_color,4),(clockwise_color,2)]
	]

	loop_count = 1
	while loop_count < frames:

		matrix_a.set_pixels(matrix)
		if matrix[0][0][1] == 10:
			matrix = [
				[(clockwise_color,8),(clockwise_color,10),(0,0)],
				[(clockwise_color,6),centerpx,(0,0)],
				[(clockwise_color,4),(clockwise_color,2),(0,0)]
			]

		elif matrix[0][1][1] == 10:
			matrix = [
				[(clockwise_color,6),(clockwise_color,8),(clockwise_color,10)],
				[(clockwise_color,4),centerpx,(0,0)],
				[(clockwise_color,2),(0,0),(0,0)]
			]
		elif matrix[0][2][1] == 10:
			matrix = [
				[(clockwise_color,4),(clockwise_color,6),(clockwise_color,8)],
				[(clockwise_color,2),centerpx,(clockwise_color,10)],
				[(0,0),(0,0),(0,0)]
			]
		elif matrix[1][2][1] == 10:
			matrix = [
				[(clockwise_color,2),(clockwise_color,4),(clockwise_color,6)],
				[(0,0),centerpx,(clockwise_color,8)],
				[(0,0),(0,0),(clockwise_color,10)]
			]
		elif matrix[2][2][1] == 10:
			matrix = [
				[(0,0),(clockwise_color,2),(clockwise_color,4)],
				[(0,0),centerpx,(clockwise_color,6)],
				[(0,0),(clockwise_color,10),(clockwise_color,8)]
			]
		elif matrix[2][1][1] == 10:
			matrix = [
				[(0,0),(0,0),(clockwise_color,2)],
				[(0,0),centerpx,(clockwise_color,4)],
				[(clockwise_color,10),(clockwise_color,8),(clockwise_color,6)]
			]
		elif matrix[2][0][1] == 10:
			matrix = [
				[(0,0),(0,0),(0,0)],
				[(clockwise_color,10),centerpx,(clockwise_color,2)],
				[(clockwise_color,8),(clockwise_color,6),(clockwise_color,4)]
			]
		elif matrix[1][0][1] == 10:
			matrix = [
				[(clockwise_color,10),(0,0),(0,0)],
				[(clockwise_color,8),centerpx,(0,0)],
				[(clockwise_color,6),(clockwise_color,4),(clockwise_color,2)]
			]

		time.sleep(frame_delay)
		loop_count += 1

def explode(color, frame_delay=0.025):
	global matrix_a

	matrix_a.clear()
	time.sleep(frame_delay)

	center_sequence = [2,4,6,8,10,10,9, 8, 7, 6,5,4,3,2,1,0]
	cross_sequence =  [0,2,4,6,8, 10,10,10,8, 6,4,2,0,0,0,0]
	corner_sequence = [0,0,0,2,4, 6, 8, 10,10,8,6,4,2,0,0,0]

	for x in range(len(center_sequence)):
		matrix = [
			[(color,corner_sequence[x]),(color,cross_sequence[x]),(color,corner_sequence[x])],
			[(color,cross_sequence[x]),(color,center_sequence[x]),(color,cross_sequence[x])],
			[(color,corner_sequence[x]),(color,cross_sequence[x]),(color,corner_sequence[x])]
		]
		matrix_a.set_pixels(matrix)
		time.sleep(frame_delay)

def play_tie_explosion(color="red", frame_delay=0.08):
	global matrix_a

	matrix_a.clear()
	time.sleep(frame_delay)

	center_sequence = [2,4,6,8,10,10,9, 8, 7, 6,5,4,3,2,1,0]
	cross_sequence =  [0,2,4,6,8, 10,10,10,8, 6,4,2,0,0,0,0]
	corner_sequence = [0,0,0,2,4, 6, 8, 10,10,8,6,4,2,0,0,0]

	for x in reversed(range(len(center_sequence))):
		matrix = [
			[(color,corner_sequence[x]),(color,cross_sequence[x]),(color,corner_sequence[x])],
			[(color,cross_sequence[x]),(color,center_sequence[x]),(color,cross_sequence[x])],
			[(color,corner_sequence[x]),(color,cross_sequence[x]),(color,corner_sequence[x])]
		]
		matrix_a.set_pixels(matrix)
		time.sleep(frame_delay)

def play_tie_animation(color="red", frame_delay=0.08):
	global matrix_a

	matrix_a.clear()
	time.sleep(frame_delay)

	x_sequence     = [2,4,6,8,10,10,10,10,9,8,7,6,5,4,3,2,1,0]
	glow_sequence =  [0,0,0,0, 0, 0, 1, 2,3,4,3,2,1,0,0,0,0,0]

	for x in range(len(x_sequence)):
		matrix = [
			[(color,x_sequence[x]),(color,glow_sequence[x]),(color,x_sequence[x])],
			[(color,glow_sequence[x]),(color,x_sequence[x]),(color,glow_sequence[x])],
			[(color,x_sequence[x]),(color,glow_sequence[x]),(color,x_sequence[x])]
		]
		matrix_a.set_pixels(matrix)
		time.sleep(frame_delay)

def blink_pixels(pixels, original_color, blink_color, blink_count=3, frame_delay=0.3):
	global board, matrix_a
	for c in range(blink_count):
		for p in pixels:
			board[p] = blink_color
		matrix_a.set_pixels(board_to_pixel_matrix(board))
		time.sleep(frame_delay)
		for p in pixels:
			board[p] = original_color
		matrix_a.set_pixels(board_to_pixel_matrix(board))
		time.sleep(frame_delay)

def blink_winning_line(gamestate):
	global board
	if gamestate == -1 or gamestate == 4 or gamestate > 8:
		return

	win_color = board[gamestate]
	blink_color = "cyan"
	if win_color == "orange":
		blink_color = "yellow"

	if gamestate == 0:
		# First Column down
		blink_pixels([0,3,6] ,win_color, blink_color)
	if gamestate == 1:
		# First Row across
		blink_pixels([0,1,2] ,win_color, blink_color)
	elif gamestate == 2:
		# Top RL diagonal
		blink_pixels([2,4,6] ,win_color, blink_color)
	elif gamestate == 3:
		# Second Row across
		blink_pixels([3,4,5] ,win_color, blink_color)
	elif gamestate == 5:
		# Third Column down
		blink_pixels([2,5,8] ,win_color, blink_color)
	elif gamestate == 6:
		# Third Row across
		blink_pixels([6,7,8] ,win_color, blink_color)
	elif gamestate == 7:
		# Second Column down
		blink_pixels([1,4,7] ,win_color, blink_color)
	elif gamestate == 8:
		# Top LR diagonal
		blink_pixels([0,4,8] ,win_color, blink_color)

def play_win_animation(gamestate, winner):
	blink_winning_line(gamestate)
	loop_clockwise(winner, 120, 0.025)
	alt_winner = "cyan"
	if winner == PLAYER_1:
		alt_winner = "yellow"

	explode(winner)
	explode(alt_winner)
	explode(winner)
	explode(alt_winner)
	explode(winner)

def reset_game():
	global cursor, board
	cursor = 0
	board = [0,0,0,0,0,0,0,0,0]

def play_game(start_player):
	global cursor, board, player

	player = start_player
	cpos = motor.get_position()
	move = 0
	can_press = True
	game_over = False
	winner_color = None
	bp = time.time()

	while not game_over:
		action = False
		# Set any moves
		if button.is_pressed():
			if can_press:
				action = set_move()
				bp = time.time()
				can_press = False
			else:
				ct = time.time()
				if ct - bp > SECONDS_BETWEEN_BUTTON_PRESSES:
					can_press = True

		# Detect selection movement
		mpos = motor.get_position()
		if mpos > cpos:
			if mpos - cpos > 45:
				cpos = mpos
				move = 1
		else:
			if cpos - mpos > 45:
				cpos = mpos
				move = -1
		if move != 0:
			action = True
			cursor = cursor+move
			if cursor == -1:
				cursor = 8
			elif cursor == 9:
				cursor = 0
			move = 0

		if action:
			gamestate = check_endgame()
			if gamestate == -1:
				refresh_display(cursor, player)
			else:
				if gamestate == 4:
					play_tie_animation()
					game_over = True
				else:
					winner_color = board[gamestate]
					play_win_animation(gamestate, winner_color)
					game_over = True

	return winner_color

# --- Start game ----
refresh_display(cursor, player)

for x in range(ROUNDS_TO_PLAY):
	winner = play_game(player)
	# Winner not allowed to start next game
	if winner == player:
		if winner == PLAYER_1:
			player = PLAYER_2
		else:
			player = PLAYER_1
	reset_game()
	refresh_display(cursor, player)
