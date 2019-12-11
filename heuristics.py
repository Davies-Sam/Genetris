#This file holds functions that will calculate the scores for our heuristics#

"""
We will start by using only 4 Heuristics
1)Total height
2)Bumpiness (jaggedness or lack of flatness)
3)Holes Created
4)Lines Cleared
"""

#returns the height of the board
#we use this method because its faster than getting max from AllHeights.
def TotalHeight(board):
    #we subtract 1 because layer 22 is the base layer used for debugging (all 1's)
    height = len(board) -1
    width = len(board[1])
    #go row by row and check for a non empty board block
    for rowNum, rowElements in enumerate(board):
        for cell in rowElements:
            if cell != 0:
                return height - rowNum 

#returns the heights a single column
def ColumnHeight(board, col):
    height = len(board) -1
    width = len(board[1])
    #for every row in the column check for non empty board block
    for x in range (0, height):
        if(board[x][col] != 0):
            return height - x 

#returns an array of all the column heights
def AllHeights(board):
    heights = []
    height = len(board) -1
    width = len(board[1])
    #for every column get its height
    for x in range (0, width):
        heights.append(ColumnHeight(board, x))
    #initialize the columns with no pieces yet to 0
    for x in range (0, width):
        if heights[x] == None:
            heights[x] = 0
    return heights    

#returns the sum of the column height differences
def Bumpiness(board):
    height = len(board) -1
    width = len(board[1])
    heights = AllHeights(board)
    result = 0
    """
    width-1 because we check adjacent columns and the next would be out of bounds
    i.e, for every column except the last, get the absolute value of the 
    differeces between the columns
    this implementation of bumpiness also considers single column towers or wells to be very bumpy
    Interestingly this implementation also discourages the AI to strategies going for multiple line clears in 1 piece placement
    """
    for x in range (0, width-1):
        result += (abs(heights[x] - heights[x+1]))
    return result

#returns the total number of holes present after a placement
def HolesCreated(board):
    height = len(board) - 1 
    width = len(board[1])
    holes = 0
    for row, rowElements in enumerate(board):
        x=0
        for cell in rowElements:
            #if the height of the column is > height of 0 cell, we know we have a hole
            if cell == 0 and ColumnHeight(board, x) > (height - row):   
                holes += 1
            x += 1
    return holes

#Ponder: LinesCleared might be emergent behavior from following the other heuristics
def LinesCleared(board):
    height = len(board) - 1 
    width = len(board[1])
    cleared = 0
    #if a row has no zeros, it will be cleared
    for x in range(0,height):
        if 0 not in board[x]:
            cleared += 1
    return cleared


#Vertically connected holes
def ConnectedHoles(board):
    height = len(board) - 1 
    width = len(board[1])
    coords = {}
    connected = 0

    for row, rowElements in enumerate(board):
        for x in range(0, len(rowElements)):
            coords[(x,row)] = rowElements[x]

    holes = []
    for row, rowElements in enumerate(board):    
        for x in range(0,len(rowElements)):
            #if the height of the column is > height of 0 cell, we know we have a hole
            if rowElements[x] == 0 and ColumnHeight(board, x) > (height - row):   
                holes.append((x,row))

    for entry in holes:
        x, y = entry
        if coords[(x,y+1)]== 0:
            connected += 1

    return connected


    

#Blockades (number of pieces placed above a hole)
def Blockades(board):
    height = len(board) - 1 
    width = len(board[1])
    coords = {}
    blockades = 0
    for row, rowElements in enumerate(board):
        for x in range(0, len(rowElements)):
            coords[(x,row)] = rowElements[x]

    holes = []
    for row, rowElements in enumerate(board):    
        for x in range(0,len(rowElements)):
            #if the height of the column is > height of 0 cell, we know we have a hole
            if rowElements[x] == 0 and ColumnHeight(board, x) > (height - row):   
                holes.append((x,row))

    for entry in holes:
        x, y = entry
        for z in range(0,y):
            if coords[(x,z)]!= 0:
                blockades += 1
    return blockades
    

#Altitude difference
def AltitudeDelta(board):
    tallest = max(AllHeights(board))
    shortest = min(AllHeights(board))
    return tallest - shortest

##################
#not implemented
#Maximum well depth
#
#Number of wells
##################


#Weighted Blocks (sum of occupied blocks, n-th row counts n times)
def WeightedBlocks(board):
    height = len(board) - 1 
    width = len(board[1])
    blockScore = 0
    for row, rowElements in enumerate(board):
        for cell in rowElements:
            if cell != 0:
                blockScore += 1*(height-row)
    return blockScore
    

#Horizontal Transitions (adjacent blocks arent either both empty or both occupied)
def HorizontalRoughness(board):
    height = len(board) - 1 
    width = len(board[1])
    gaps = 0
    for row, rowElements in enumerate(board):
        for x in range(0, len(rowElements)):
            if (x>0 and x<9) and rowElements[x] == 0 and rowElements[x-1] != 0 and rowElements[x+1] != 0:
                gaps +=1
            elif x == 0 and rowElements[x] == 0 and rowElements[x+1] != 0 :
                gaps +=1
            elif x == 9 and rowElements[x] == 0 and rowElements[x-1] != 0:
                gaps +=1

    return gaps

#Vertical Transitions (adjacent blocks aren't either both empty or both occupied)
def VerticalRoughness(board):
    height = len(board) - 1 
    width = len(board[1])
    coords = {}
    vGaps = 0
    for row, rowElements in enumerate(board):
        for x in range(0, len(rowElements)):
            coords[(x,row)] = rowElements[x]

    for y in range (0, 23):
        for x in range(0,10):
            if y > 1 and y < 22:
                if coords[(x,y)] == 0 and coords[(x,y+1)]!= 0 and coords[(x,y-1)]!= 0:
                    vGaps += 1


    return vGaps

#This is the 'main' function of the file, the only one to be called externally.
#It will return the score of a placement by checking the weighted heuristics
#On the board and weights that is passed to this utility function.
#WE HAVE NOT MADE THE ORGANISM HOLD LABELED WEIGHTS
#THIS FUNCTION HOLDS THE CORRECT ORDER OF THE WEIGHTS
#FOR LEGIBILITY WE WILL ATTACH NAMES TO THE WEIGHTS LATER
def Utility_Function(board, weights):
    #get the heurstics
    height = TotalHeight(board)
    bump = Bumpiness(board)
    holes = HolesCreated(board)
    cleared = LinesCleared(board)
    connectedHoles = ConnectedHoles(board)
    blockades = Blockades(board)
    altituteDelta = AltitudeDelta(board)
    weightedBlocks = WeightedBlocks(board)
    hRoughness = HorizontalRoughness(board)
    vRoughness = VerticalRoughness(board)

    #now we weight the heuristics
    wHeight = height * weights[0]
    wBump = bump * weights[1]
    wHoles = holes * weights[2]
    wCleared = cleared * weights[3]
    wConnectedHoles = connectedHoles * weights[4]
    wBlockades = blockades * weights[5]
    wAltitudeDelta = altituteDelta * weights[6]
    wWeightedBlocks = weightedBlocks * weights[7]
    wHroughness = hRoughness * weights[8]
    wVroughness = vRoughness * weights[9]

    #sum the weighted heurstics to get the score of a piece placement
    score = wHeight + wBump + wHoles + wCleared + wConnectedHoles + wBlockades + wAltitudeDelta + wWeightedBlocks + wHroughness + wVroughness
    return score
