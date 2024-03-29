#This module has classes for tetriminos

import pygame as pg

pg.init()

V = pg.Vector2

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

    def __init__(self,type,pos,styles) -> None:
        """
        - Pick any of the following for type parameter
        : I, J, L, O, S, T, Z
        - pos parameter is short for position, use vector input
        """
        self.figure_rot_data = ROT_MINO_DATA[type]
        self.rotation = 0

        self.pos = pos
        self.block_list = []

        block_imgs = styles.get_blocks(type)
        for (i,v) in enumerate(block_imgs):
            newpos = V(self.pos)+self.figure_rot_data[0][i]
            self.block_list.append(Block(v,newpos,styles.get_rotation()))

    def update(self,dt,window,sprites,offset=V(0,0)):
        for block in self.block_list:
            block.update(window,sprites,offset)

    def update_block_pos(self):
        for (i,v) in enumerate(self.figure_rot_data[self.rotation]):
            self.block_list[i].pos = v + self.pos



class Block:
    """Class that holds sprite data for each block of tetriminos"""

    def __init__(self,sprite_name,pos,rotation=False) -> None:
        self.pos = pos
        self.sprite_name = sprite_name
        self.dimensions = V(16,16)
        self.rotation = rotation

    def update(self,window,sprites,offset):
        pos_rect = pg.Rect((V(self.pos)*self.dimensions[0])+offset,self.dimensions)
        window.blit(sprites.sprites[self.sprite_name],pos_rect)

        

        

