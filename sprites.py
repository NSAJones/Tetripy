# This file contains classes that manage sprites

import configparser,json,os
import pygame as pg
from random import shuffle
import easing

V = pg.Vector2

SPRITE_DIR = "sprites/"
SPRITESHEETS = [
    "fonts/charmap-cellphone.png",
    "fonts/charmap-futuristic.png",
    "fonts/charmap-oldschool.png"
]

def split_spritesheet(surface,cell_dims):
    # Creates a list of subsurfaces from a spritesheet based on cell dims

    # Calculate the number of columns+rows based on cell_dims

    surface_dims = V(surface.get_size())
    surface_list = []

    columns = int(surface_dims[0]//cell_dims[0])
    rows = int(surface_dims[1]//cell_dims[1])

    # Create subsurfaces using pygame Rect objects

    for y in range(rows):
        for x in range(columns):
            pos = V(x*cell_dims[0],y*cell_dims[1])

            new_rect = pg.Rect(pos,cell_dims)
            new_surf = surface.subsurface(new_rect)

            surface_list.append(new_surf)

    return surface_list



class Font:
    """This class stores information about a Font"""
    def __init__(self,spritesheet:pg.Surface,char_order:str
                 ,name:str,char_dims:V) -> None:
        
        self.spritesheet = spritesheet
        self.name = name
        self.char_dims = char_dims
        self.letter_images = {}


        letter_list = split_spritesheet(spritesheet,
                                            self.char_dims)

        for (i,v) in enumerate(char_order):
            self.letter_images[v] = letter_list[i]



class Fonts:
    """This class stores and draws pixel perfect(i.e. pixelart) fonts"""

    def __init__(self) -> None:
        # Gets sprites for all 3 fonts and cuts up the spritesheets

        self.path = "sprites/fonts/"
        self.spritesheets= {
            "cellphone":pg.image.load(self.path + "charmap-cellphone.png"),
            "futuristic":pg.image.load(self.path + "charmap-futuristic.png"),
            "oldschool":pg.image.load(self.path + "charmap-oldschool.png")
        }

        self.fonts = {}

        self.char_dims = V(7,9)

        # Create a list of every character in order in the font spritesheets
        char_order = list(" !\"#$%&'()*+,-./0123456789:;<=>?"+
                      r"@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_"+
                      "`abcdefghijklmnopqrstuvwxyz{}~")
        
        # Split up the spritesheets for each font
        for (ss_name,spritesheet) in self.spritesheets.items():
            self.fonts[ss_name] = Font(spritesheet,char_order,ss_name,V(7,9))

    def draw_font(self,text,rect,window,type="oldschool",center=False):        # Draws text within a rect
        if type not in self.fonts.keys():
            raise ValueError("type parameter is not the name of a font")

        

        draw_pos = V(rect.topleft)
        word_list = list(text.split(" "))
        line_list = []

        font = self.fonts[type]
        char_dims = font.char_dims

        while len(word_list) > 0 or len(line_list) > 0:

            draw_line = False

            if len(word_list) > 0:
                word = word_list[0]
                word_dims = V(self.char_dims[0]*len(word),)
                word_rect = pg.Rect(draw_pos,word_dims)
                max_word_len = int(rect.width//char_dims[0])

                
                if rect.right < word_rect.right:
                    draw_line = True
            
            if len(word_list) == 0:
                draw_line = True

            if draw_line:
                line_rect = pg.Rect(V(0,draw_pos[1]),
                                    V(len(" ".join(line_list))*char_dims[0],
                                      char_dims[1]))

                if center:
                    line_rect.centerx = rect.centerx
                else:
                    line_rect.left = rect.left

                draw_rect = pg.Rect(line_rect.topleft,char_dims)
                for (i,w) in enumerate(line_list):

                    for c in w:
                        image = font.letter_images[c]
                        window.blit(image,draw_rect)
                        draw_rect.left += char_dims[0]
                    
                    if i < len(line_list)-1:
                        draw_rect.left += char_dims[0]
                
                draw_pos = V(rect.topleft[0],draw_pos[1]+self.char_dims[1])
                line_list = []

            if len(word_list) > 0:
                if max_word_len < len(word):
                    # If word is too long for rect width, split it between
                    # lines with a hyphen

                    word_list = [word[max_word_len-1:]] + word_list
                    word = word[:max_word_len-1]+"-"

                line_list.append(word_list.pop(0))

                # Draw letters to window
                for _ in word:
                    draw_pos = draw_pos + V(self.char_dims[0],0)
                
                if len(word_list) != 1 and word[-1:] != "-":
                    draw_pos = draw_pos + V(self.char_dims[0],0)




class Sprites:
    """
    This class stores images so they can be reused and stored centrally
    instead of an object instance importing the image every time
    """

    def __init__(self) -> None:
        self.sprites = {}
        self.split_sprites = {}

    def get_sprite(self,path,name):
        """
        Fetches image at path, if it is already in self.sprites,
        reuse it

        Parameters:
        path(str): file path to image
        name(str): the assigned name to sprite in self.sprites
        """

        if path in self.sprites.keys():
            return self.sprites[name]
        else:
            self.sprites[name] = pg.image.load(path).convert()
            return self.sprites[name]
    
    def split_spritesheet(self,name,dims):
        """
        Split a spritesheet by name, if it is already in
        self.split_sprites, reuse it
        The split images are put into self.sprites with the affix
        sprite_1, sprite_2, sprite_3, ...

        Parameters:
        name(str): name of sprite in self.sprites
        dims(pg.Vector2): dimension to cut out of sprite

        Returns:
        list: a list of the sprite names of the newly created sprites
        """

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
        """Returns image surface with options to make transparent or rotate it"""

        image = self.sprites[name]
        image.set_alpha(alpha)
        if rotation:
            image = pg.transform.rotate(image,rotation)
        return image


class Styles:
    """This class manages different tilesets for the tetriminos to pick from"""

    def __init__(self,sprites) -> None:
        """
        Parameters:
        sprites(Sprites): sprite class
        """

        # Dictionary to store Style objects
        self.style_list = {}

        # Set default style
        self.current_style = "Cracked Tiles"
        self.bg_timer = V(0,0)
        self.bg_timer_max = V(5,11)

        self.switch_alternate = False

        # Read all folders in directory and create a Style object from each
        cfg_file = None
        for f in os.listdir("sprites/styles"):
            cfg_file = os.path.join("sprites","styles",f,"style.cfg")
            style = Style(cfg_file,sprites)
            self.style_list[style.name] = style

    def get_blocks(self,letter):
        """
        Gets a list of sprite names for a new figure in current style

        Parameters:
        letter(str): tetrimino name - choose from (J,L,O,T,Z,S,I)
        """

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
    
    def get_score_anim(self):
        return self.style_list[self.current_style].score_animation
    
    def get_anim_delay(self):
        return self.style_list[self.current_style].animation_delay
    
    def draw_background(self,dt,window,sprites):
        sprite_name = self.style_list[self.current_style].bg_image
        sprite = sprites.get_image(sprite_name)

        starting_pos = V(sprite.get_size()) * -1

        self.bg_timer[0] = (self.bg_timer[0]+dt)%self.bg_timer_max[0]
        self.bg_timer[1] = self.bg_timer[1]+dt

        if self.bg_timer[1] > self.bg_timer_max[1]:
            self.bg_timer[1] = 0
            self.switch_alternate = not self.switch_alternate

        tx = self.bg_timer[0]/self.bg_timer_max[0]
        ty = self.bg_timer[1]/self.bg_timer_max[1]
        offset_vector = V(0,0)
        offset_vector[0] = easing.lerp(tx,0,sprite.get_width())
        offset_vector[1] = easing.lerp(ty,0,sprite.get_height())
        

        iterations = V((window.game_dims[0]//sprite.get_width())+3,
                       (window.game_dims[1]//sprite.get_height())+3)

        for x in range(int(iterations[0])):
            for y in range(int(iterations[1])):
                draw_pos = V(starting_pos)
                draw_pos += V(x*sprite.get_width(),y*sprite.get_height())

                """
                offset_value = 0
                if (x % 2 == 1 and self.switch_alternate):

                    draw_pos += V(0,offset_vector[1])
                    
                elif (x % 2 == 1 and not self.switch_alternate):

                    draw_pos += V(0,-offset_vector[1])
                
                elif self.switch_alternate:
                    draw_pos += V(0,-offset_vector[1])
                
                elif not self.switch_alternate:
                    draw_pos += V(0,offset_vector[1])"""


                draw_pos += offset_vector

                window.blit_precise(sprite,draw_pos,V(sprite.get_size()))



class Style:
    """This class reads style data from cfg file for tetrimino sprites"""

    def __init__(self,cfg_file,sprites) -> None:
        """
        Parameters:
        cfg_file(str): path to cfg file
        sprites(Sprites): sprite class
        """

        """
        There are 4 different styles types:
        * separate - tetriminos pick a random tile from img files each
          time, tiles are not joined
        * separate_c - there is a tile for every type of tetrimino
          which is picked every time, tiles are not joined
        * joined - tiles are joined and there is a specific image for 
          each tetrimino
        """

        style_path = cfg_file.replace("style.cfg","")

        config = configparser.ConfigParser()
        config.read(cfg_file)

        self.name = config["Metadata"]["name"]
        self.creator = config["Metadata"]["creator"]
        self.type = config["Metadata"]["type"]

        self.blocks = json.loads(config["Images"]["blocks"])
        self.score = config["Images"]["score"]
        self.background = config["Images"]["background"]
        self.rotation = bool(config["Images"]["rotation"])
        self.animation_delay = float(config["Images"]["animation_delay"])

        score_name = f"{self.name}_{self.score}"
        sprites.get_sprite(os.path.join(style_path,self.score),score_name)
        self.score_animation = sprites.split_spritesheet(score_name,V(16,16))
        
        bg_name = f"{self.name}_{self.background}"
        sprites.get_sprite(os.path.join(style_path,self.background),bg_name)
        self.bg_image = bg_name

        # Each image file is for a seperate piece, the x axis is for
        # animation and the y axis is for variants in the same figure

        self.variants = {}

        for img_name in self.blocks:
            self.variants[img_name[:-4]] = {}

            location = os.path.join(style_path,img_name)
            spritesheet_name = f"{self.name}_{img_name[:-4]}"
            sprites.get_sprite(location,spritesheet_name)

            dims = V(sprites.sprites[spritesheet_name].get_size()[0],16)
            var_list = sprites.split_spritesheet(spritesheet_name,dims)

            for var in var_list:
                self.variants[img_name[:-4]][var] = sprites.split_spritesheet(var,V(16,16))
        

        
        
            
            


            




            
        



    
            


            



        
        