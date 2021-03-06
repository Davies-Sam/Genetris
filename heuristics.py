#This file holds functions that will calculate the scores for our heuristics#

"""
We will start by using only 4 Heuristics
1)Total height
2)Bumpiness (jaggedness or lack of flatness)
3)Holes Created
4)Lines Cleared
"""

#returns the height of the board

def TotalHeight(board):
    """returns the heighest column height"""
    #we subtract 1 because layer 22 is the base layer  (all 1's)
    height = len(board) -1
    width = len(board[1])
    #go row by row and check for a non empty board block
    for rowNum, rowElements in enumerate(board):
        for cell in rowElements:
            if cell != 0:
                return height - rowNum 


def ColumnHeight(board, col):
    """#returns the heights a single column"""
    height = len(board) -1
    width = len(board[1])
    #for every row in the column check for non empty board block
    for x in range (0, height):
        if(board[x][col] != 0):
            return height - x 
    return 0


def AllHeights(board):
    """returns an array of all the column heights"""
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

def AggregateHeigh(board):
    """returns the sum of the column heights"""
    return sum(AllHeights(board))   

def Bumpiness(board):
    """returns the sum of the column height differences"""
    height = len(board) -1
    width = len(board[1])
    heights = AllHeights(board)
    result = 0
    for x in range (0, width-1):
        result += (abs(heights[x] - heights[x+1]))
    return result

def HolesCreated(board):
    """returns the total number of holes present"""
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

def LinesCleared(board):
    """returns the number of lines cleared"""
    height = len(board) - 1 
    width = len(board[1])
    cleared = 0
    #if a row has no zeros, it will be cleared
    for x in range(0,height):
        if 0 not in board[x]:
            cleared += 1
    return cleared


#
def ConnectedHoles(board):
    """returns number of vertically connected holes"""
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

def Blockades(board):
    """returns number of pieces placed above holes"""
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
    

def AltitudeDelta(board):
    """returns the difference in height between the tallest and shortest column"""
    tallest = max(AllHeights(board))
    shortest = min(AllHeights(board))
    return tallest - shortest

def MaxWell(board):
    """returns the depth of the biggest well"""
    height = len(board) - 1 
    width = len(board[1])
    coords = {}

    for row, rowElements in enumerate(board):
        for x in range(0, len(rowElements)):
            coords[(x,row)] = rowElements[x]
    wellMap = {0 : 0, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0}
    wells = 0
    for row, rowElements in enumerate(board):    
        for x in range(0,len(rowElements)):
            #if the height of the column is > height of 0 cell, we know we have a hole
            if rowElements[x] == 0:
                if x > 0 and x < 9:
                    if (rowElements[x-1] != 0 and rowElements[x+1] != 0) and ColumnHeight(board, x) < (height - row):   
                        wells +=1
                        wellMap[x] += 1
                elif x==0:
                    if rowElements[x+1] != 0 and ColumnHeight(board, x) < (height - row):
                        wells +=1
                        wellMap[x] += 1
                elif x==9:
                    if rowElements[x-1] != 0 and ColumnHeight(board, x) < (height - row):
                        wells +=1
                        wellMap[x] += 1
    return max(wellMap.values())

def Wells(board):
    """returns the number of wells"""
    height = len(board) - 1 
    width = len(board[1])
    coords = {}

    for row, rowElements in enumerate(board):
        for x in range(0, len(rowElements)):
            coords[(x,row)] = rowElements[x]

    wells = 0
    for row, rowElements in enumerate(board):    
        for x in range(0,len(rowElements)):
            #if the height of the column is > height of 0 cell, we know we have a hole
            if rowElements[x] == 0:
                if x > 0 and x < 9:
                    if (rowElements[x-1] != 0 and rowElements[x+1] != 0) and ColumnHeight(board, x) < (height - row) :   
                        wells +=1
                elif x==0:
                    if rowElements[x+1] != 0 and ColumnHeight(board, x) < (height - row):
                        wells +=1
                elif x==9:
                    if rowElements[x-1] != 0 and ColumnHeight(board, x) < (height - row):
                        wells +=1
    return wells

def WeightedBlocks(board):
    """returns the sum of occupied blocks, n-th row counts n times"""
    height = len(board) - 1 
    width = len(board[1])
    blockScore = 0
    for row, rowElements in enumerate(board):
        for cell in rowElements:
            if cell != 0:
                blockScore += 1*(height-row)
    return blockScore
    


def HorizontalRoughness(board):
    """returns the number of horizontal transitions (adjacent blocks arent either both empty or both occupied)"""
    height = len(board) - 1 
    width = len(board[1])
    gaps = 0
    for row, rowElements in enumerate(board):
        for x in range(0, len(rowElements)):
            if (x>0 and x<9) and rowElements[x] != 0 and rowElements[x-1] == 0 and rowElements[x+1] == 0:
                gaps +=1
            elif x == 0 and rowElements[x] == 0 and rowElements[x+1] != 0 and rowElements[x+2] == 0:
                gaps +=1
            elif x == 9 and rowElements[x] == 0 and rowElements[x-1] != 0 and rowElements[x-2] == 0:
                gaps +=1

    return gaps

#
def VerticalRoughness(board):
    """return the number of vertical transitions (adjacent blocks aren't either both empty or both occupied)"""
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
                if coords[(x,y)] != 0 and coords[(x,y+1)]== 0 and coords[(x,y-1)]== 0:
                    vGaps += 1


    return vGaps

#This is the 'main' function of the file, the only one to be called externally.
#It will return the score of a placement by checking the weighted heuristics
#On the board and weights that is passed to this utility function.
#WE HAVE NOT MADE THE ORGANISM HOLD LABELED WEIGHTS
#THIS FUNCTION HOLDS THE CORRECT ORDER OF THE WEIGHTS
#FOR LEGIBILITY WE WILL ATTACH NAMES TO THE WEIGHTS LATER
def Utility_Function(board, weights):
    """returns the utility score of a board state"""
    #get the heurstics
    aggHeight = AggregateHeigh(board)
    bump = Bumpiness(board)
    holes = HolesCreated(board)
    cleared = LinesCleared(board)
    
    connectedHoles = ConnectedHoles(board)
    blockades = Blockades(board)
    altituteDelta = AltitudeDelta(board)
    weightedBlocks = WeightedBlocks(board)
    hRoughness = HorizontalRoughness(board)
    vRoughness = VerticalRoughness(board)
    wells = Wells(board)
    biggestWell = MaxWell(board)
    
    #totalHeight = TotalHeight(board)
   
    #now we weight the heuristics
    wHeight = aggHeight * weights[0]
    wBump = bump * weights[1]
    wHoles = holes * weights[2]
    wCleared = cleared * weights[3]
    wConnectedHoles = connectedHoles * weights[4]
    wBlockades = blockades * weights[5]
    wAltitudeDelta = altituteDelta * weights[6]
    wWeightedBlocks = weightedBlocks * weights[7]
    wHroughness = hRoughness * weights[8]
    wVroughness = vRoughness * weights[9]
    wWells = wells * weights[10]
    wbiggestWell = biggestWell * weights[11]
    #wTotalHeight = totalHeight * weights[12]S
   

    #sum the weighted heurstics to get the score of a piece placement
    #score = (wHeight + wBump + wHoles + wCleared + wTotalHeight)
    score = (wHeight + wBump + wHoles + wCleared + wConnectedHoles + wBlockades + wAltitudeDelta + wWeightedBlocks + wHroughness + wVroughness + wWells + wbiggestWell)
    return score
