#!/usr/bin/env python

import atexit
from tetrislib import *

import threading

original_terminal_state = set_terminal_mode()
atexit.register(restore_terminal, original_terminal_state)

# This example code draws a horizontal bar 4 squares long.
game=GameClass()

row = 0
game.board[row][5] = 1
game.board[row][6] = 1
game.board[row][7] = 1
game.board[row][8] = 1

game.draw_board()
#q=queue.Queue()
# This code waits for input until the user hits a keystroke. getinput() returns one of "left", "up", "right",
# "down".

#loop=asyncio.get_event_loop()
#tasks= [
#                asyncio.ensure_future(input
#        ]
threads=[]
t=threading.Thread(target=game.move_piece_down)
threads.append(t)
t.start()

#s=threading.Thread(target=play_game, args=(game,))
#s.start()

game.play_game()

