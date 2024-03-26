#This module has classes for tetriminos

import pygame

pygame.init()

V = pygame.Vector2

#Tetrimino data based off the SRS - https://tetris.fandom.com/wiki/SRS

BASE_MINO_DATA = {
    "I":[V(0,1),V(1,1),V(2,1),V(3,1)],
    "J":[V(0,0),V(0,1),V(1,1),V(2,1)],
    "L":[V(0,1),V(1,1),V(2,1),V(2,0)],
    "O":[V(1,0),V(2,0),V(1,1),V(2,1)],
    "S":[V(0,1),V(1,1),V(1,0),V(2,0)],
    "T":[V(1,0),V(0,1),V(1,1),V(2,1)],
    "Z":[V(0,0),V(1,0),V(1,1),V(2,1)],
}

#Create tetrimino rotation data
#(to avoid having to write it out lol)

ROT_MINO_DATA = {
    "I":[[V(0,1),V(1,1),V(2,1),V(3,1)]],
    "J":[[V(0,0),V(0,1),V(1,1),V(2,1)]],
    "L":[[V(0,1),V(1,1),V(2,1),V(2,0)]],
    "O":[[V(1,0),V(2,0),V(1,1),V(2,1)]],
    "S":[[V(0,1),V(1,1),V(1,0),V(2,0)]],
    "T":[[V(1,0),V(0,1),V(1,1),V(2,1)]],
    "Z":[[V(0,0),V(1,0),V(1,1),V(2,1)]],
}

for (mino,data) in BASE_MINO_DATA.items():
    rot_data = list(data)

    center = None
    if mino in ["J","L","S","Z","T"]:
        center = V(1,1)
    elif mino == "I":
        center = V(1.5,1.5)

    #Rotates each vector around center value 3 times, excluding O
        
    for _ in range(3):
        if mino != "O":
            for i in range(4):
                rot_data[i] = rot_data[i] - center
                rot_data[i] = V(rot_data[i][1]*-1,rot_data[i][0])
                rot_data[i] = rot_data[i] + center

        ROT_MINO_DATA[mino].append(list(rot_data))

#Prints out tetrimino rotation data to console, for testing only
        
def print_rot():
    mino_str = None
    for (mino,rot_data) in ROT_MINO_DATA.items():
        print(mino,"\n")
        for data in rot_data:

            width = None
            if mino in ["J","L","S","Z","T"]:
                width = 3
            else:
                width = 4

            for y in range(width):
                mino_str = ""
                for x in range(width):
                    if V(x,y) in data:
                        mino_str += "██"
                    else:
                        mino_str += "░░"
                print(mino_str)
            print()


class Figure:
    """Class that houses tetrimino functionality"""

    def __init__(self,type,pos) -> None:
        """
        - Pick any of the following for type parameter
        : I, J, L, O, S, T, Z
        - pos parameter is short for position, use vector input
        """
        self.figure_rot_data = ROT_MINO_DATA[type]
        self.rotation = 0

        self.pos = pos

    def update(self,dt):
        pass

        
        

