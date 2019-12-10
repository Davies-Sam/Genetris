"""This file holds code for our AI agent its behavior#
the agent is handed the board, the current and next pieces,
weights, and the game object.
using this information the agent will try every possible rotation
at each column and will choose the column and rotation that yields
the higheest score using the weightings. We wil rotate and sweep over the columns to find the best rotation/column combination"""
#the agent will need duplicated board(s) to play on before sending the correct move back to the tetris app

#The AI will have two for-loops, one for testing each rotation for a piece
#another loop to try each column

#file that holds the heuristic function
#utility_function() will return the heuristic value for the board at that time with
#that piece
import heuristics

#file that holds and initializes our population
#import population
import heuristics
#import functions and the number of columns
from tetris import check_collision, COLS, rotate_clockwise, join_matrixes
from collections import namedtuple
Move = namedtuple('Move', ['x_pos', 'rotation', 'result'])
#pass an organism

class Agent(object):
    #################################################################################
        #################################################################################
    #initialize the AI agent with the current organism's heuristics
    def __init__(self, tetris):
        self.tetris = tetris
        self.best_move = None
        #self.organism = organism
        self.instantPlay = False

        #this var will contain the heuristics of a single organism, will be updated
        #when we work on a different organism
        
        
    #################################################################################
    #finds the best move from all possible moves. calls rotations_per_piece()
    
    def find_best_move(self):
        all_moves = []
        piece = self.tetris.stone

        #want to use the same rotation shape for each column,
        #saves time so we dont have to re-rotate a piece each time
        for rotation in range(self.rotations_per_piece(piece)):
            #now that we have a config of a piece/tetromino/stone,
            #check each column with it
            for x in range( ( COLS - len(piece[0]) ) + 1 ):
                y = self.top_of_column(x, piece)
                #get a new board config after adding the current piece's rotation
                #to the current board. join the current board and place where the
                #piece would be placed
                new_board = join_matrixes(self.tetris.board, piece, (x, y))
                all_moves.append(Move(x, rotation, new_board))
            #checked every config with current configuration,
            #rotate and do it again
            piece = rotate_clockwise(piece)
        
        #at this point, all_moves contains the x_coord, the rotation config of the
        #current piece we are working on, and a representation of how the board looks
        #if we placed the piece in that specific configuration/rotation on the current
        #board

        #now we calculate the utility of each board state and find the max
        #heuristics takes only a board... keep this in mind when calling util_fcn
        max_util = float("-inf")
        best_board_state = None

        #check how good each placement is for each placement
        
        for a_move in all_moves:
            #passing the new_board var into the util function
            #NEEDS TO BE UPDATED!!!! WILL WORK ON LATER.
            pop = self.tetris.genetics.population
            curOrgIndex = self.tetris.genetics.current_organism
            workingOrganism = pop[curOrgIndex]
            temp = heuristics.Utility_Function(a_move[2], workingOrganism.heuristics)
            if temp > max_util:
                max_util = temp
                best_board_state = a_move
        """
        pop = self.tetris.genetics.population
        curOrgIndex = self.tetris.genetics.current_organism
        workingOrganism = pop[curOrgIndex]

        return max(all_moves, key=lambda m: heuristics.Utility_Function(m.result,workingOrganism.heuristics))
        """

        #max_util has the utility of the best board state
        #best_board_state contains x_coord, rotation of the piece, and how the board
        #will look after the piece is placed on the current board
        self.best_move = best_board_state
        return best_board_state

    #################################################################################
    #This def is called by the GA which, in turn, calls the rest of the Agent
    #sub-fcns.
    
    def update_board(self):
        tetris = self.tetris
        
        #calculate the best config for the piece
        #move = [x_coord, rotation, new_board]
        move = self.find_best_move()

        #lock so we are working on something that is running
        tetris.lock.acquire()

        #rotate the piece until it is in the config we want
        for r in range(move[1]):
            tetris.stone = rotate_clockwise(tetris.stone)

        #move the piece over to the correct column
        tetris.move_to(move[0])
        #if we are still playing, not paused
        if self.instantPlay:
            tetris.stone_y = self.top_of_column(move[0], tetris.stone)
        #free the board
        tetris.lock.release()

    #################################################################################
    #this function finds how far down the piece needs to go before a collision
    #uses the def from tetris.py check_collision()
  
    def top_of_column(self, x_coord, piece):
        y_coord = 0

        #go down the column until you hit the end of the board or another piece
        while not check_collision(self.tetris.board, piece, (x_coord, y_coord)):
            y_coord += 1
        #need to go up one so we aren't inside another piece
        return y_coord - 1

    #################################################################################
    #This definition calculates the number of times we can rotate a piece without
    #getting a duplicate configuration, depends on which piece we are looking at
    #good.
    
    def rotations_per_piece(self, piece):
        #pieces contains a list of each configuration
        pieces = [piece]

        while 1:
            new_configuration = rotate_clockwise(piece)
            #checks if the rotation got a different configuration
            #e.g. an "O" piece wont have any rotations, it only have one configuration
            if new_configuration in pieces:
                return len(pieces)
            pieces.append(new_configuration)