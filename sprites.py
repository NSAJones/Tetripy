import os
import pygame as pg

V = pg.Vector2

SPRITE_DIR = "sprites/"
SPRITESHEETS = [
    "fonts/charmap-cellphone.png",
    "fonts/charmap-futuristic.png",
    "fonts/charmap-oldschool.png"
]

#creates a list of subsurfaces from a spritesheet
def split_spritesheet(surface,cell_dims):
    surface_dims = V(surface.get_size())
    surface_list = []

    columns = surface_dims[0]//cell_dims[0]
    rows = surface_dims[1]//cell_dims[1]

    for y in range(rows):
        for x in range(columns):
            new_rect = pg.Rect(V(x*cell_dims[0],y*cell_dims[1]),cell_dims)
            new_surf = surface.subsurface(new_rect)
            surface_list.append(new_surf)
    
    return surface_list


class Fonts:
    def __init__(self) -> None:
        self.spritesheets = {
            "cellphone":pg.image.load("sprites/fonts/charmap-cellphone.png"),
            "futuristic":pg.image.load("sprites/fonts/charmap-futuristic.png"),
            "oldschool":pg.image.load("sprites/fonts/charmap-oldschool.png")
        }
        self.chars_cellphone = {}
        self.futuristic_cellphone = {}
        self.oldschool_cellphone = {}

        char_order = list("!\"#$%&'()*+,-./0123456789:;<=>?"+
                      r"@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_"+
                      "`abcdefghijklmnopqrstuvwxyz{}~")
        
        surf_list = split_spritesheet(self.spritesheets["cellphone"],V(7,9))[1:]
        for (i,v) in char_order:
            self.chars_cellphone[v] = surf_list[i]