from Tkinter import *
import tkFont
import os
import sys
from subprocess import Popen, PIPE

import random
import time
# The board is represented as an array of arrays, with 10 rows and 10 columns.

UNMOVABLE=2

SQUARE_SIZE=50
SCREEN_WIDTH=800
SCREEN_HEIGHT=800

LEFT_ARROW_KEY=65361
UP_ARROW_KEY=65362
RIGHT_ARROW_KEY=65363
DOWN_ARROW_KEY=65364

ENTER=65293
SPACE=32

def keyDown(e, app):
        print e.keysym_num
        if app.game.is_game_ongoing:
                if e.keysym_num==UP_ARROW_KEY:
                        app.game.update_board("up")
                if e.keysym_num==LEFT_ARROW_KEY:
                        app.game.update_board("left")
                if e.keysym_num==RIGHT_ARROW_KEY:
                        app.game.update_board("right")
                if e.keysym_num==DOWN_ARROW_KEY:
                        app.game.update_board("down")
                if e.keysym_num==SPACE:
                        app.game.teleport_down()
        elif e.keysym_num==ENTER:
                app.game=GameClass()

class MainApp(Tk):
        def __init__(self):
                Tk.__init__(self)

                self.game=GameClass()
                width=SQUARE_SIZE*self.game.board_size["x"]
                height=SQUARE_SIZE*self.game.board_size["y"]
                self.canvas=Canvas(self, width=width, height=height)
                self.canvas.configure(background="black")
                self.canvas.pack()

                self.canvas.bind("<KeyPress>", lambda e: keyDown(e, self))
                self.canvas.focus_set()
                self.time_move=time.time()
                self.draw()

        def draw(self):
                self.canvas.delete(ALL)
                for row in range(self.game.board_size["y"]):
                        for col in range(self.game.board_size["x"]):
                                x1=col*SQUARE_SIZE
                                y1=row*SQUARE_SIZE
                                x2=x1+SQUARE_SIZE
                                y2=y1+SQUARE_SIZE
                                if not self.game.board[row][col]==0:
                                        self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue")

                if not self.game.is_game_ongoing:
                        self.draw_game_over()

                if time.time()-self.time_move>self.game.move_frequency and self.game.is_game_ongoing:
                        self.game.move_piece_down()
                        self.time_move=time.time()

                self.after(1, self.draw)

        def draw_game_over(self):
                canvas_width=self.canvas.winfo_width()
                canvas_height=self.canvas.winfo_height()
                rect_width=0.5*canvas_width
                rect_height=0.5*rect_width
                x1=canvas_width/2-rect_width/2
                y1=rect_height
                x2=x1+rect_width
                y2=y1+rect_height
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")
                font=tkFont.Font(family='Helvetica', size=10, weight='bold')
                padding=20
                self.canvas.create_text((x1+x2)/2, y1+padding, font=font, text="GAME OVER") 
                self.canvas.create_text((x1+x2)/2, y1+2*padding, font=font, text="PRESS ENTER FOR NEW GAME")
                
class GameClass:
        def __init__(self):
                self.is_game_ongoing=True
                self.move_frequency=2.0
                self.board_size = { "x": 10, "y": 10 }
                self.board = []
                self.piece_pos=[0, 5]
                self.piece_type = "I"

                self.row_move={ "up": -1, "down": 1, "right": 0, "left": 0}
                self.col_move={ "up": 0, "down": 0, "right": 1, "left": -1}
                
                self.pieces={"I": [[0, 0], [0, 1], [0, 2], [0, 3]],
                                "J": [[0, 0], [0, 1], [-1, 1], [-2, 1]], 
                                "L": [[0, 0], [0, 1], [-1, 0], [-2, 0]],
                                "O": [[0, 0], [0, 1], [-1, 0], [-1, 1]],
                                "S": [[0, 0], [0, 1], [-1, 1], [-1, 2]],
                                "T": [[0, 1], [-1, 0], [-1, 1], [-1, 2]],
                                "Z": [[0, 0], [0, 1], [-1, 1], [-1, 2]]}
                
                self.cur_piece=[[0, 0], [0, 1], [0, 2], [0, 3]]

                # Setup the board.
                for i in range(0, self.board_size["y"]):
                        self.board.append([0 for i in range(0, self.board_size["x"])])

        def remove_piece(self):
                for i in range(len(self.cur_piece)):
                        row=self.piece_pos[0]+self.cur_piece[i][0]
                        col=self.piece_pos[1]+self.cur_piece[i][1]
                        if row>=0 and row<self.board_size["x"] and col>=0 and col<self.board_size["y"]:
                                self.board[row][col]=0

        def add_piece(self):
                for i in range(len(self.cur_piece)):
                        row=self.piece_pos[0]+self.cur_piece[i][0]
                        col=self.piece_pos[1]+self.cur_piece[i][1]
                        if row>=0 and row<self.board_size["x"] and col>=0 and col<self.board_size["y"]:
                                self.board[row][col]=1

        def has_clash(self, temp):
                for i in range(len(temp)):
                        row=self.piece_pos[0]+temp[i][0]
                        col=self.piece_pos[1]+temp[i][1]
                        if row>=self.board_size["x"] or col<0 or col>=self.board_size["y"] or self.board[row][col]==UNMOVABLE:
                                return True
                return False

        def rotate_piece(self):
                temp=['?']*len(self.cur_piece)
                for i in range(len(self.cur_piece)):
                        temp[i]=[0, 0]

                for i in range(len(self.cur_piece)):
                        temp[i][0]=self.cur_piece[i][1]
                        temp[i][1]=-self.cur_piece[i][0]

                clash=self.has_clash(temp)

                if not clash:
                        for i in range(len(self.cur_piece)):
                                self.cur_piece[i]=[temp[i][0], temp[i][1]]

        def is_piece_at_bottom(self):
                for i in range(len(self.cur_piece)):
                        row=self.piece_pos[0]+self.cur_piece[i][0]
                        col=self.piece_pos[1]+self.cur_piece[i][1]
                        if col>=len(self.board[0]) or col<0:
                                return False
                        #print "row= ", row
                        #print "col= ", col
                        if row>=self.board_size["y"]-1 or (row>=0 and self.board[row+1][col]==UNMOVABLE):
                                return True
                return False

        def is_piece_at_left(self):
                for i in range(len(self.cur_piece)):
                        row=self.piece_pos[0]+self.cur_piece[i][0]
                        col=self.piece_pos[1]+self.cur_piece[i][1]
                        if col<=0 or (row>=0 and self.board[row][col-1]==UNMOVABLE):
                                return True
                return False

        def is_piece_at_right(self):
                for i in range(len(self.cur_piece)):
                        row=self.piece_pos[0]+self.cur_piece[i][0]
                        col=self.piece_pos[1]+self.cur_piece[i][1]
                        if col>=self.board_size["x"]-1 or (row>=0 and self.board[row][col+1]==UNMOVABLE):
                                return True
                return False

        def spawn_new_piece(self):
                self.piece_type=random.sample(self.pieces, 1)[0]
                col=random.randint(0, len(self.board[0])-5)
                self.piece_pos=[0, col]
                for i in range(len(self.pieces[self.piece_type])):
                        self.cur_piece[i][0]=self.pieces[self.piece_type][i][0]
                        self.cur_piece[i][1]=self.pieces[self.piece_type][i][1]

        def set_piece_unmovable(self):
                for i in range(len(self.cur_piece)):
                        row=self.piece_pos[0]+self.cur_piece[i][0]
                        col=self.piece_pos[1]+self.cur_piece[i][1]
                        self.board[row][col]=UNMOVABLE

        def check_line(self, row):
                for i in range(len(self.board[0])):
                        if not self.board[row][i]==UNMOVABLE:
                                return False

                return True

        def move_lines_down(self, row):
                for i in range(row, 0, -1):
                        for j in range(len(self.board[0])):
                                self.board[i][j]=self.board[i-1][j]

        def clear_lines(self):
                for i in range(len(self.board)):
                        clear=self.check_line(i)
                        if clear:
                                for j in range(len(self.board[0])):
                                        self.board[i][j]=0
                                self.move_lines_down(i)

        def check_game_over(self):
                if self.is_piece_at_bottom():
                        self.is_game_ongoing=False

        def update_board(self, input):
                self.remove_piece()
                bottom=self.is_piece_at_bottom()
                if input=="down" and not bottom:
                        self.piece_pos[0]+=self.row_move[input]
                        self.piece_pos[1]+=self.col_move[input]
                elif input=="right" and not self.is_piece_at_right():
                        self.piece_pos[0]+=self.row_move[input]
                        self.piece_pos[1]+=self.col_move[input]
                elif input=="left" and not self.is_piece_at_left():
                        self.piece_pos[0]+=self.row_move[input]
                        self.piece_pos[1]+=self.col_move[input]
                elif input=="up":
                        self.rotate_piece()
                self.add_piece()
                if self.is_piece_at_bottom():
                        self.set_piece_unmovable()
                        self.spawn_new_piece()
                        self.check_game_over()
                        self.clear_lines()
                        return False
                
                self.clear_lines()
                return True

        def move_piece_down(self):
                self.update_board("down")

        def teleport_down(self):
                while self.update_board("down"):
                        pass
                        
# Draws the contents of the board with a border around it.
        def draw_board(self):
                os.system("clear")
                board_border = "".join(["*" for i in range(0, self.board_size["x"] + 2)])
                print(board_border)
                for y in range(0, self.board_size["y"]):
                        line = "|"
                        for x in range(0, self.board_size["x"]):
                                line += ("#" if not self.board[y][x] == 0 else " ")
                        line += "|"
                        print(line)
                print(board_border)

if __name__=="__main__":
        app=MainApp()
        app.geometry(str(SCREEN_WIDTH)+"x"+str(SCREEN_HEIGHT))
        app.mainloop()
