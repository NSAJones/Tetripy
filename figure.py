#This module has classes for tetriminos (The blocks that fall in Tetris)

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
#(To avoid having to write it out manually)

ROT_MINO_DATA = {
    "I":[[V(0,1),V(1,1),V(2,1),V(3,1)]],
    "J":[[V(0,0),V(0,1),V(1,1),V(2,1)]],
    "L":[[V(0,1),V(1,1),V(2,1),V(2,0)]],
    "O":[[V(1,0),V(2,0),V(1,1),V(2,1)]],
    "S":[[V(0,1),V(1,1),V(1,0),V(2,0)]],
    "T":[[V(1,0),V(0,1),V(1,1),V(2,1)]],
    "Z":[[V(0,0),V(1,0),V(1,1),V(2,1)]],
}

#For every tetrimino
for (mino,data) in BASE_MINO_DATA.items():

    #Get default rotation of tetrimino
    rot_data = list(data)

    #Get center value of Tetrimino to rotate around
    center = None
    if mino in ["J","L","S","Z","T"]:
        center = V(1,1)
    elif mino == "I":
        center = V(1.5,1.5)

    #Rotates each vector around center value 3 times
    for _ in range(3):

        #Check if tetrimino being checked isn't O (all rotations the same)
        if mino != "O":

            #For each block in tetrimino(all have 4)
            for i in range(4):

                #Center vector to (0,0) then rotate it 90 degrees by
                #swapping its x and y values and making one negative
                rot_data[i] = rot_data[i] - center
                rot_data[i] = V(rot_data[i][1]*-1,rot_data[i][0])
                rot_data[i] = rot_data[i] + center
        
        #Add one new rotation data list to ROT_MINO_DATA
        ROT_MINO_DATA[mino].append(list(rot_data))

#Prints out tetrimino rotation data to console, for testing only
def print_rot():
    """Will print out all the possible rotations for each tetrimino"""

    mino_str = None
    
    #For every Tetrimino
    for (mino,rot_data) in ROT_MINO_DATA.items():
        print(mino,"\n")

        #For tetrimino rotation in rot_data
        for data in rot_data:
            
            #Get width of tetrimino
            width = None
            if mino in ["J","L","S","Z","T"]:
                width = 3
            else:
                width = 4

            #Display blocks of single rotation data
            for y in range(width):
                mino_str = ""
                for x in range(width):
                    if V(x,y) in data:
                        mino_str += "██"
                    else:
                        mino_str += "░░"
                print(mino_str)
            print()

#Create function to get mirrored vector
neg_func = lambda vect: vect*-1

"""
Wallkicks are when a tetrimino is rotated but might be inside a placed
block on the grid, a series of translations are tried and if none are
valid no rotation takes place

Wallkick data can be one of two directions, clockwise, or anti-clockwise,
all tetriminos apart from I have symmetrical wallkick data

The key for each wallkick denotes the original rotation and the rotation
to take place, from 0 to 3 with 0 being the starting rotation and 3 being
the starting rotation rotated 3 times clockwise

https://tetris.fandom.com/wiki/SRS
"""

#Calculate symmetrical wall data
WALLKICK_DATA = {
    "0>1":[V(-1,0),V(-1,1),V(0,-2),V(-1,-2)],
    "1>2":[V(1,0),V(1,-1),V(0,2),V(1,2)],
    "2>3":[V(1,0),V(1,1),V(0,-2),V(1,-2)],
    "3>0":[V(-1,0),V(-1,-1),V(0,2),V(-1,2)],

    "1>0":map(neg_func,[V(-1,0),V(-1,1),V(0,-2),V(-1,-2)]),
    "2>1":map(neg_func,[V(1,0),V(1,-1),V(0,2),V(1,2)]),
    "3>2":map(neg_func,[V(1,0),V(1,1),V(0,-2),V(1,-2)]),
    "0>3":map(neg_func,[V(-1,0),V(-1,-1),V(0,2),V(-1,2)])
}

WALLKICK_DATA_I = {
    "0>1":[V(-2,0),V(1,0),V(-2,-1),V(1,2)],
    "1>0":[V(2,0),V(-1,0),V(2,1),V(-1,-2)],

    "1>2":[V(-1,0),V(2,0),V(-1,2),V(2,-1)],
    "2>1":[V(1,0),V(-2,0),V(1,-2),V(-2,1)],

    "2>3":[V(2,0),V(-1,0),V(2,1),V(-1,-2)],
    "3>2":[V(-2,0),V(1,0),V(-2,-1),V(1,2)],

    "3>0":[V(1,0),V(-2,0),V(1,-2),V(-2,1)],
    "0>3":[V(-1,0),V(2,0),V(-1,2),V(2,-1)]
}



class Figure:
    """Class that houses tetrimino functionality"""

    def __init__(self,type,pos,styles) -> None:
        """
        Parameters:
        type(str): The letter of the desired tetrimino (J,L,O,T,Z,S,I)
        pos(pg.Vector2): The position of the figure on the grid
        styles(Styles): Style class to define appearance of figure
        """

        #Rotation Variables
        self.figure_rot_data = ROT_MINO_DATA[type]
        self.rotation = 0

        #Type of tetrimino (J,L,O,T,Z,S,I)
        self.type = type

        #Transparency of tetrimino
        self.alpha = 255

        #Location on grid
        self.pos = pos

        #List of Block objects
        self.block_list = []
        
        #Get images for eack block from style class
        block_imgs = styles.get_blocks(type)

        #For every image
        for (i,v) in enumerate(block_imgs):

            #Create a block using current position and block image
            newpos = V(self.pos)+self.figure_rot_data[0][i]
            self.block_list.append(Block(v,newpos,styles.get_rotation()))

    def update(self,window,sprites,offset=V(0,0)):
        """
        Draws figure to screen and updates block objects

        Parameters:
        window(Window): window class
        sprites(Sprites): sprite class
        offset(pg.Vector2): offset where figure is drawn
        """

        #Update block positions and draw it to screen
        self.update_block_pos()
        self.draw(window,sprites,offset)

    def draw(self,window,sprites,offset=V(0,0),alpha=None):
        """
        Draws figure to screen

        Parameters:
        window(Window): window class
        sprites(Sprites): sprite class
        offset(pg.Vector2): offset where figure is drawn
        alpha(float): override of self.alpha transparency of figure
        """

        #Use default alpha if no override is given
        if alpha is None:
            alpha = self.alpha

        #Update each block
        for block in self.block_list:
            block.update(window,sprites,offset,alpha)
    
    def update_block_pos(self):
        """
        Updates position and rotation of eack block
        """

        #Set position of each block to location in rotation data added
        #to the figure position
        for (i,v) in enumerate(self.figure_rot_data[self.rotation]):
            self.block_list[i].pos = v + self.pos
            self.block_list[i].rotation = self.rotation
    
    def ghost(self,window,sprites,offset,grid_offset,alpha=100):
        """
        Draws figure to screen with a hard coded alpha, used as preview
        to a hard drop

        Parameters:
        window(Window): window class
        sprites(Sprites): sprite class
        offset(pg.Vector2): position to draw to in pixels
        grid_offset:(pg.Vector2): position to draw to in grid increments
        alpha(float): transparency (default 100)
        """
        location = offset+ V(grid_offset[0]*16,grid_offset[1]*16)
        self.draw(window,sprites,location,alpha)


class Block:
    """Class that holds sprite data for each block of tetriminos"""

    def __init__(self,sprite_name,pos,rotation=False) -> None:
        """
        Parameters:
        sprite_name(str): name of sprite to be used with sprite class
        pos(pg.Vector2): position of block on grid
        rotation(bool): if style allows rotation or not
        """

        #Position of Block on the grid
        self.pos = pos

        #Sprite and sprite dimensions of Block
        self.sprite_name = sprite_name
        self.dimensions = V(16,16)

        #Rotation data for when style allows rotation
        self.rotation = rotation
        self.rot_val = 0

    def update(self,window,sprites,offset,alpha=255):
        """
        Draws sprite to window

        Parameters:
        window(Window): window class
        sprites(Sprites): sprites class
        offset(pg.Vector2): draw position before adding grid position
        alpha(float): transparency
        """

        #Create destination Rect for blit
        pos_rect = pg.Rect((V(self.pos)*self.dimensions[0])+offset,self.dimensions)
        
        #Get rotation of image in degrees
        rotation = None
        if self.rotation:
            rotation = self.rot_val*90

        #Get sprite surface from sprite class
        sprite = sprites.get_image(self.sprite_name,alpha,rotation)

        #Draw surface to window class
        window.blit(sprite,pos_rect)

        

        

