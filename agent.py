"""This file holds code for our AI agent its behavior#
the agent is handed the board, the current and next pieces,
weights, and the game object.
using this infomration the agent will try every possible rotation
at each column and will choose the column and rotation that yields
the higheest score using the weightings. We must consider the moving into the
last colum with each possible rotation as well, due to situational rotation lock at the edge columns"""