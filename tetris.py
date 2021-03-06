import random
import pygame, sys
from copy import deepcopy
import numpy

CELL_SIZE =	30
COLS =		10
ROWS =		22
MAXFPS = 	30
PIECELIMIT = float("inf")
DROP_TIME = 60
DRAW = True

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

colors = [
(0,   0,   0  ),
(255, 85,  85),
(100, 200, 115),
(120, 108, 245),
(255, 140, 50 ),
(50,  120, 52 ),
(146, 202, 73 ),
(150, 161, 218 ),
(35,  35,  35) # Helper color for background grid
]

#rotates the pieces clockwise
def rotate_clockwise(shape):
	return [ [ shape[y][x] for y in range(len(shape)) ] for x in range(len(shape[0]) - 1, -1, -1) ]

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
	return [[0 for i in range(COLS)]] + board

#adds a placed piece to the board
def join_matrixes(mat1, mat2, mat2_off):
	mat3 = deepcopy(mat1)
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat3[cy+off_y-1][cx+off_x] += val
	return mat3

#create the board
def new_board():
	board = [ [ 0 for x in range(COLS) ] for y in range(ROWS) ]
	#next line not needed, just there for clarity (adds a base row to the grid)
	board += [[ 1 for x in range(COLS)]]
	return board
class TetrisApp(object):
	def __init__(self, genetics):
		self.DROPEVENT = pygame.USEREVENT + 1
		pygame.init()
		pygame.display.set_caption("Final Project")
		pygame.key.set_repeat(250,25)
		self.width = CELL_SIZE * (COLS+10)
		self.height = CELL_SIZE * ROWS
		self.rlim = CELL_SIZE * COLS
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in range(COLS)] for y in range(ROWS)]
		self.default_font = pygame.font.Font(pygame.font.get_default_font(), 11)
		if DRAW:
			self.screen = pygame.display.set_mode((self.width, self.height))
		self.next_stone = tetris_shapes[5]
		self.linesCleared = 0
		self.gameover = False
		self.genetics = genetics
		self.ai = None
		self.limit = PIECELIMIT
		self.piecesPlayed = 0
		if self.genetics.sequenceType == "fixed":
			self.init_game(self.genetics.seed)
		elif self.genetics.sequenceType == "random":
			self.init_game(numpy.random.random())
	
	def new_stone(self):
		self.stone = self.next_stone
		nextStone = random.randint(0, len(tetris_shapes)-1)
		self.next_stone = tetris_shapes[nextStone]
		self.stone_x = COLS//2 - len(self.stone[0])//2
		self.stone_y = 0
		self.score += 1
		self.piecesPlayed += 1
		
		if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
			self.gameover = True
			if self.genetics:
				#print(self.linesCleared)
				self.genetics.GameOver(self.linesCleared)
		

	def init_game(self,seed):
		random.seed(seed)	
		self.board = new_board()
		self.score = 0	
		self.linesCleared = 0
		#start every game with a flat piece
		self.next_stone = tetris_shapes[6]
		self.new_stone()
		pygame.time.set_timer(self.DROPEVENT, DROP_TIME)
	
	def disp_msg(self, msg, topleft):
		x,y = topleft
		for line in msg.splitlines():
			self.screen.blit(self.default_font.render(line, False, (255,255,255), (0,0,0)), (x,y))
			y+=14
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  self.default_font.render(line, False,
				(255,255,255), (0,0,0))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (
			  self.width // 2-msgim_center_x,
			  self.height // 2-msgim_center_y+i*22))
		
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					#corrupt board exception from https://tinyurl.com/wu7gl48
					try:
						pygame.draw.rect(self.screen, colors[val], 
							pygame.Rect((off_x+x)*CELL_SIZE, (off_y+y)*CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
					except IndexError:
						pass
						#print("Corrupted board") 
						#self.print_board()
						
	
	def add_cl_lines(self, n):
		linescores = [0, 40, 100, 300, 1200]
		self.score += linescores[n]
		self.linesCleared += n
	
	def move_to(self, x):
		self.move(x - self.stone_x)

	def move(self, delta_x):
		if not self.gameover:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > COLS - len(self.stone[0]):
				new_x = COLS - len(self.stone[0])
			if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
				self.stone_x = new_x
	
	def drop(self):	
		if not self.gameover:
			self.stone_y += 1
			if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
				self.board = join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y))
				self.new_stone()
				cleared_rows = 0
				for i, row in enumerate(self.board[:-1]):
					if 0 not in row:
						self.board = remove_row(self.board, i)
						cleared_rows += 1
				self.add_cl_lines(cleared_rows)

								
				if self.ai:
					self.ai.update_board()

				return True
		return False
	
	def insta_drop(self):
		if not self.gameover:
			while not self.drop():
				pass
	
	def rotate_stone(self):
		if not self.gameover:
			new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
				self.stone = new_stone

	def start_game(self,seed):
		if self.gameover:
			self.init_game(seed)
			self.gameover = False

	def quit(self):
		self.center_msg("exiting...")
		pygame.display.update()
		""" make sure fitnesses are recorded
		for a in self.genetics.population:
			print(a.fitness)
			print("\n")
		"""
		sys.exit()

	def ai_toggle_instantPlay(self):
		if self.ai:
			self.ai.instantPlay = not self.ai.instantPlay
	
	def print_board(self):
		i=0
		for row in self.board:	
			print(self.board[i])
			print('\n')
			i+=1
		"""for testing
		import heuristics
		print("height %s" % heuristics.TotalHeight(self.board))
		print("bump %s" % heuristics.Bumpiness(self.board))
		print("holes %s" % heuristics.HolesCreated(self.board))
		print("linesc %s" % heuristics.LinesCleared(self.board))
		print("connectedholes %s" % heuristics.ConnectedHoles(self.board))
		print("blockade %s" % heuristics.Blockades(self.board))
		print("altDelta %s" % heuristics.AltitudeDelta(self.board))
		print("WeighteBlocks %s" % heuristics.WeightedBlocks(self.board))
		print("Horiz R %s" % heuristics.HorizontalRoughness(self.board))
		print("Vert R %s" % heuristics.VerticalRoughness(self.board))
		print("wells %s" % heuristics.Wells(self.board))
		print("max well %s" % heuristics.MaxWell(self.board))
		""" 
	def run(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT': lambda: self.move(-1),
			'RIGHT': lambda: self.move(+1),
			'DOWN': self.drop,
			'UP': self.rotate_stone,
			'RETURN': self.insta_drop,
			'p': self.ai_toggle_instantPlay,
			't' : self.print_board
		}
		
		clock = pygame.time.Clock()
		while True:
			if DRAW:		
				self.screen.fill((0,0,0))
				if self.gameover:
					self.center_msg("Game Over!\nYour score: %d\nPress space to continue" % self.score)
				else:
					pygame.draw.line(self.screen, (255,255,255), 
						(self.rlim+1, 0), (self.rlim+1, self.height-1))
					self.disp_msg("Next:", (self.rlim+CELL_SIZE, 2))
					self.disp_msg("Score: %d" % self.score, (self.rlim+CELL_SIZE, CELL_SIZE*5))
					if self.ai and self.genetics:
						chromosome = self.genetics.population[self.genetics.current_organism]
						self.disp_msg("Generation: %s" % self.genetics.current_generation, (self.rlim+CELL_SIZE, CELL_SIZE*5))				
						self.disp_msg("\n %s: %s\n %s: %s\n  %s: %s\n  %s: %s\n  %s: %s\n %s: %s\n %s: %s\n  %s: %s\n  %s: %s\n  %s: %s\n %s: %s\n %s: %s\n  %s: %s\n %s: %s\n %s: %s\n  %s: %s\n  %s: %s\n  %s: %s\n"  % (
							"Organism #", self.genetics.current_organism,
							"Name", chromosome.name,
							"Played", chromosome.played,
							"Fitness", chromosome.fitness,
							"Age", chromosome.age,
							"Height", chromosome.heuristics[0],
							"Bumpiness", chromosome.heuristics[1],
							"Holes", chromosome.heuristics[2],
							"Lines", chromosome.heuristics[3],
							"Connected Holes", chromosome.heuristics[4],
							"Blockades", chromosome.heuristics[5],
							"Altitude Delta", chromosome.heuristics[6],
							"Weighted Blocks", chromosome.heuristics[7],
							"Horizonal Roughness", chromosome.heuristics[8],
							"Vertical Roughness", chromosome.heuristics[9],
							"Wells", chromosome.heuristics[10],
							"Biggest Well", chromosome.heuristics[11],
							"Lines Cleared", self.linesCleared
						), (self.rlim+CELL_SIZE, CELL_SIZE*7))
					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone, (COLS+1,2))
				pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == self.DROPEVENT:
					self.drop()
				elif event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_" + key):
							key_actions[key]()
			if self.piecesPlayed > PIECELIMIT:
				self.gameover = True
				if self.genetics:
				#print(self.linesCleared)
					self.genetics.GameOver(self.linesCleared)
			clock.tick(145)

if __name__ == "__main__":
	from agent import Agent
	app = TetrisApp()
	app.ai = Agent(app)
	app.ai.instantPlay = True
	app.run()
