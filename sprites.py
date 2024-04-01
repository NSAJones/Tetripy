#This file contains classes that manage sprites

import os
import configparser
import pygame as pg
from random import shuffle

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
                draw_pos = draw_pos + V(self.char_dims[0],0)




class Sprites:
    #Stores sprites so they can be reused

    def __init__(self) -> None:
        self.sprites = {}
        self.split_sprites = {}

    def get_sprite(self,path,name):
        #Fetches image at path, if it is already in self.sprites,
        #reuse it

        if path in self.sprites.keys():
            return self.sprites[name]
        else:
            self.sprites[name] = pg.image.load(path).convert()
            return self.sprites[name]
    
    def split_spritesheet(self,name,dims):
        #Split a spritesheet by name, if it is already in
        #self.split_sprites, reuse it
        #The split images are put into self.sprites with the affix
        #sprite_1, sprite_2, sprite_3, ...

        split_sprites = []

        if name in self.split_sprites.keys():
            
            for s in self.split_sprites[name]:
                split_sprites.append(s)
            
        else:
            split_sprites_imgs = split_spritesheet(self.sprites[name],dims)
            for (i,v) in enumerate(split_sprites_imgs):
                child_name = f"{name}_{i}"
                self.sprites[child_name] = v.convert()
                split_sprites.append(child_name)
            
        return split_sprites
    
    def get_image(self,name,alpha=255,rotation=None):
        image = self.sprites[name]
        image.set_alpha(alpha)
        if rotation:
            image = pg.transform.rotate(image,rotation)
        return image


class Styles:
    #Manages different tilesets for the tetriminos to pick from

    def __init__(self,sprites) -> None:
        #Get all tetris styles using cfg files

        self.style_list = {}
        self.current_style = "Cracked Tiles"

        cfg_file = None
        for f in os.listdir("sprites/styles"):
            cfg_file = os.path.join("sprites","styles",f,"style.cfg")
            style = Style(cfg_file,sprites)
            self.style_list[style.name] = style

    def get_blocks(self,letter):
        #get a list of 4 sprite names for a tetrimino from a style

        style = self.style_list[self.current_style]
        sprites = []

        if style.type in ["separate","separate_c"]:
            variants = None

            if style.type == "separate_c":
                variants = list(style.variants[letter])
            elif style.type == "separate":
                keys = style.variants.keys()
                shuffle(keys)
                
                variants = list(style.variants[keys[0]])

            for i in range(4):
                shuffle(variants)
                sprites.append(variants[0])
        
        return sprites
    
    def get_rotation(self):
        return self.style_list[self.current_style].rotation



class Style:
    def __init__(self,cfg_file,sprites) -> None:
        #this class fetches and stores data from cfg files

        """
        There are 4 different styles types:
        * separate - tetriminos pick a random tile from img files each
          time, tiles are not joined
        * separate_c - there is a tile for every type of tetrimino
          which is picked every time, tiles are not joined
        * joined - tiles are joined and there is a specific image for 
          each tetrimino
        * tileset - tetriminos pick a random tile, uses a tileset to
          support all possible tetriminos
        """

        """
        There are 3 different animation types:
        * none - no animation
        * 
        """

        style_path = cfg_file.replace("style.cfg","")

        config = configparser.ConfigParser()
        config.read(cfg_file)

        self.name = config["Style"]["name"]
        self.creator = config["Style"]["creator"]
        self.type = config["Style"]["type"]
        self.images = config["Style"]["images"].split(",")
        self.rotation = bool(config["Style"]["rotation"])

        #each type has a 2d list for variants, then animations
        self.variants = {}

        for img_name in self.images:
            self.variants[img_name[:-4]] = {}

            location = os.path.join(style_path,img_name)
            spritesheet_name = f"{self.name}_{img_name[:-4]}"
            sprites.get_sprite(location,spritesheet_name)

            dims = V(sprites.sprites[spritesheet_name].get_size()[0],16)
            var_list = sprites.split_spritesheet(spritesheet_name,dims)

            for var in var_list:
                self.variants[img_name[:-4]][var] = sprites.split_spritesheet(var,V(16,16))
            
            


            




            
        



    
            


            



        
        