from random import randrange as rand
from gui import Gui
import pygame, sys
import heuristics
import population

cell_size =	18
cols =		10
rows =		22
maxfps = 	30

tetris_shapes = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]
]

#rotates the pieces clockwise
def rotate_clockwise(shape):
	return [ [ shape[y][x] for y in xrange(len(shape)) ] for x in xrange(len(shape[0]) - 1, -1, -1) ]

#checks that no pieces are overlapping
def check_collision(board, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]:
					return True
			except IndexError:
				return True
	return False

#removes a row from the board
def remove_row(board, row):
	del board[row]
	return [[0 for i in xrange(cols)]] + board

#adds a placed piece to the board
def join_matrixes(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1	][cx+off_x] += val
	return mat1

#create the board
def new_board():
	board = [ [ 0 for x in xrange(cols) ] for y in xrange(rows) ]
	#next line not needed, just there for clarity (adds a base row to the grid)
	board += [[ 1 for x in xrange(cols)]]
	return board

class TetrisApp(object):
	def __init__(self,visuals):
		pygame.init()
		pygame.key.set_repeat(250,25)
		#cell_size is the height and the width of our squares.
		#set width of our window, with 6 extra columns for the HUD info
		self.width = cell_size*(cols+6)
		#set height of our window 
		self.height = cell_size*rows
		#set the right edge of our playing board
		self.rlim = cell_size*cols
		#create a grey&black checkerboard. grey if x,y are the same after %2. black otherwise
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in xrange(cols)] for y in xrange(rows)]
		#sets font for the HUD
		self.default_font =  pygame.font.Font(pygame.font.get_default_font(), 12)
		#next line not needed, gui will create the window for us
		#self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.event.set_blocked(pygame.MOUSEMOTION) # We do not need
		                                             # mouse movement
		                                             # events, so we
		                                             # block them.
		#our next shape is randomly selected from our shapes list
		self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
		#set the gui boolean to the initialization value
		self.visuals = visuals
		#create a gui object to allow visualization
		if self.visuals:
			self.gui = Gui()
		#this is for step checking purposes
		self.printed=False
		#create the board
		self.init_game()
	
	def new_stone(self):
		#set the new stone to a shallow copy of next stone
		self.stone = self.next_stone[:]
		#randomize a new next stone
		self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
		#set the x coord of the shape (top left corner) to the center of a row
		self.stone_x = int(cols / 2 - len(self.stone[0])/2)
		#set the y coord of the shape to the top row
		self.stone_y = 0
		#if a new piece can't fit on the board - game over
		if check_collision(self.board,self.stone,(self.stone_x, self.stone_y)):
			self.gameover = True
	
	#initialize the game values
	def init_game(self):
		self.board = new_board()
		self.new_stone()
		self.level = 1
		self.score = 0
		self.lines = 0
		
		pygame.time.set_timer(pygame.USEREVENT+1, 1000)

	#manages scoring for line clears and level
	def add_cl_lines(self, n):
		linescores = [0, 40, 100, 300, 1200]
		self.lines += n
		self.score += linescores[n] * self.level
		if self.lines >= self.level*6:
			self.level += 1
			newdelay = 1000-50*(self.level-1)
			newdelay = 100 if newdelay < 100 else newdelay
			pygame.time.set_timer(pygame.USEREVENT+1, newdelay)

	#manages shifting pieces to the left or right
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > cols - len(self.stone[0]):
				new_x = cols - len(self.stone[0])
			if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
				self.stone_x = new_x
	# ESC ends the game
	def quit(self):
		self.gui.center_msg("Exiting...")
		pygame.display.update()
		sys.exit()

	#manages the falling of the pieces
	def drop(self, manual):
		if not self.gameover and not self.paused:
			self.score += 1 if manual else 0
			self.stone_y += 1
			if check_collision(self.board,self.stone,(self.stone_x, self.stone_y)):
				self.board = join_matrixes( self.board, self.stone, (self.stone_x, self.stone_y))
				self.new_stone()
				cleared_rows = 0
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							print("\nlines cleared:") 
							print(heuristics.LinesCleared(self.board))
							self.board = remove_row(self.board, i)
							cleared_rows += 1
							break
					else:
						break
				self.add_cl_lines(cleared_rows)
				return True
		return False

	#manages instant piece placement
	def insta_drop(self):
		if not self.gameover and not self.paused:
			while(not self.drop(True)):
				pass

	#executes a valid piece rotation
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
				self.stone = new_stone

	#for planning purposes
	def print_board(self):
		i=0
		if not self.printed:
			for row in self.board:	
				print(self.board[i])
				print('\n')
				i+=1
			print("\nTotal Height:") 
			print(heuristics.TotalHeight(self.board))
			print("\nBumpiness:") 
			print(heuristics.Bumpiness(self.board))
			#print(heuristics.AllHeights(self.board))
			print("\nHole created:") 
			print(heuristics.HolesCreated(self.board))
			"""
			test = population.InitPop(2)
			for i in test:
				for num in i:
					print(bin(num))
				print("NEXT")
				"""
			print(int(-0b1101111))
			
	#P to pause
	def toggle_pause(self):
		self.paused = not self.paused

	#Start a game
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False

	#Contains keybindings and the game loop
	def run(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			'RETURN':	self.insta_drop
		}
		
		self.gameover = False
		self.paused = False
		
		dont_burn_my_cpu = pygame.time.Clock()
		while 1:
			if self.visuals:
				self.gui.nextFrame(self)
			#print(self.stone_x, self.stone_y) 
			#print(len(self.stone[0]))
			#pause the game to get a printout of the board
			if self.paused:
				self.print_board()
				#print(list(enumerate(self.board)))
				#for x in range(0, 23):
				#	print(self.board[x])
				#print(len(self.board[1]))
				self.printed = True
			else:
				self.printed = False
			if self.gameover:
				return
			## pass the ai class our board, stone, next stone, stone location, weights, and self #
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.drop(False)
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_" +key):
							key_actions[key]()
					
			dont_burn_my_cpu.tick(maxfps)

if __name__ == '__main__':
	#give tetrisapp true for visuals, false for none
	App = TetrisApp(True)
	App.run()
