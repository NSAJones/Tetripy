#This file contains classes that manage sprites

import os
import pygame as pg

V = pg.Vector2

SPRITE_DIR = "sprites/"
SPRITESHEETS = [
    "fonts/charmap-cellphone.png",
    "fonts/charmap-futuristic.png",
    "fonts/charmap-oldschool.png"
]

def split_spritesheet(surface,cell_dims):
    #Creates a list of subsurfaces from a spritesheet based on cell dims

    #Calculate the number of columns+rows based on cell_dims

    surface_dims = V(surface.get_size())
    surface_list = []

    columns = int(surface_dims[0]//cell_dims[0])
    rows = int(surface_dims[1]//cell_dims[1])

    #create subsurfaces using pygame Rect objects

    for y in range(rows):
        for x in range(columns):
            pos = V(x*cell_dims[0],y*cell_dims[1])

            new_rect = pg.Rect(pos,cell_dims)
            new_surf = surface.subsurface(new_rect)

            surface_list.append(new_surf)

    return surface_list


class Fonts:
    def __init__(self) -> None:
        #Gets sprites for all 3 fornts and cuts up the spritesheets

        self.path = "sprites/fonts/"
        self.spritesheets = {
            "cellphone":pg.image.load(self.path + "charmap-cellphone.png"),
            "futuristic":pg.image.load(self.path + "charmap-futuristic.png"),
            "oldschool":pg.image.load(self.path + "charmap-oldschool.png")
        }

        self.chars_cellphone = {}
        self.chars_futuristic = {}
        self.chars_oldschool = {}
        self.fonts = {}

        self.char_dims = V(7,9)

        #Create a list of ever character in order in the font spritesheets

        char_order = list(" !\"#$%&'()*+,-./0123456789:;<=>?"+
                      r"@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_"+
                      "`abcdefghijklmnopqrstuvwxyz{}~")
        
        #Split up the spritesheets for each font

        for (ss_name,spritesheet) in self.spritesheets.items():
            letter_list = split_spritesheet(spritesheet,
                                              self.char_dims)
            self.fonts[ss_name] = {}

            for (i,v) in enumerate(char_order):
                self.fonts[ss_name][v] = letter_list[i]

        # cellphone = split_spritesheet(self.spritesheets["cellphone"],
        #                               self.char_dims)
        # futuristic = split_spritesheet(self.spritesheets["futuristic"],
        #                               self.char_dims)
        # oldschool = split_spritesheet(self.spritesheets["oldschool"],
        #                               self.char_dims)

        # for (i,v) in enumerate(char_order): 
        #     self.chars_cellphone[v] = cellphone[i]
        #     self.chars_futuristic[v] = futuristic[i]
        #     self.chars_oldschool[v] = oldschool[i]
    
    def draw_font(self,text,rect,window,type="oldschool"):
        #Draws text within a rect

        #rect.bottom += 500

        if type not in self.fonts.keys():
            raise ValueError("type parameter is not the name of a font")

        draw_pos = V(rect.topleft)
        word_list = text.split(" ")

        while len(word_list) > 0:

            word = word_list.pop(0)
            word_dims = V(self.char_dims[0]*len(word),)
            word_rect = pg.Rect(draw_pos,word_dims)
            max_word_len = int(rect.width//self.char_dims[0])

            if max_word_len < len(word):
                #If word is too long, split it between lines

                word_list = [word[max_word_len-1:]] + word_list
                word = word[:max_word_len-1]+"-"

                draw_pos = V(rect.topleft[0],draw_pos[1]+self.char_dims[1])
                
            elif rect.right < word_rect.right:
                #If word goes past rect, word wrap

                draw_pos = V(rect.topleft[0],draw_pos[1]+self.char_dims[1])

            #Draw letters to window
            for letter in word:
                letter_rect = pg.Rect(draw_pos,self.char_dims)

                window.blit(self.fonts[type][letter],letter_rect)

                draw_pos = draw_pos + V(self.char_dims[0],0)
            
            if len(word_list) != 1 and word[-1:] != "-":
                sdraw_pos = draw_pos + V(self.char_dims[0],0)
            


            



        
        