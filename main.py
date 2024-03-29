#The main file where everything is run

import pygame as pg
import timer as t
import sprites as s
import figure,easing

V = pg.Vector2
V3 = pg.Vector3
class Window:
    #Class that manages window resizing, scale and clock dt

    def __init__(self) -> None:
        
        self.window_dims = V(640,360)
        self.fullscreen_dims = pg.display.list_modes()[0]
        self.game_dims = V(100,100)

        self.scale = None
        self.game_rect = None

        self.window = pg.display.set_mode(self.window_dims)
        self.mode = None

        self.fps = 60
        self.clock = pg.time.Clock()
        self.dt = None

        self.update_scale()
        self.windowed()
        self.update()
    
    def update_scale(self):
        """
        Updates the scale and game_rect attributes based on the size
        of the window, use after changing the size of the display
        """

        window_surf_size = self.window.get_size()

        self.scale = min(window_surf_size[0]//self.game_dims[0],
                         window_surf_size[1]//self.game_dims[1])
        
        self.game_rect = pg.Rect(V(0),self.game_dims * self.scale)
        self.game_rect.center = self.window.get_rect().center
    
    def scale_rect(self,rect,in_game_rect=True):
        """
        - Scales a rect using scale attribute,
        - If in_game_rect is true offsets it using game_rect attribute
        """

        topleft = V(rect.topleft)

        rect.scale_by(self.scale)
        
        rect.topleft = topleft * self.scale

        if in_game_rect:
            rect.topleft = (rect.topleft + 
                            V(self.game_rect.topleft))

        return rect
    
    def windowed(self):
        #Sets the display to a resizeable window


        self.window = pg.display.set_mode(self.window_dims,pg.RESIZABLE)
        self.mode = "windowed"

        self.update_scale()
    
    def fullscreen(self):
        #Sets the display to fullscreen

        self.window = pg.display.set_mode(self.fullscreen_dims,
                                          pg.FULLSCREEN)
        self.mode = "fullscreen"

        self.update_scale()

    def blit(self,surf,dest,offset=V(0,0),scale_rect=True,special_flags=0):
        """
        Shorthand for drawing to the window, also scaled to draw to
        the window

        """

        surf = pg.transform.scale_by(surf,self.scale)
        if scale_rect:
            dest = self.scale_rect(dest)

        self.window.blit(surf,dest,None,special_flags)
    
    def update(self):
        #Updates dt and flips display as well as drawing a background

        self.dt = self.clock.tick(self.fps)
        pg.display.flip()

        self.window.fill(V3(0,0,0))
        self.window.fill(V3(0,0,200),self.game_rect)


class Events:
    #Class that manages inputs

    def __init__(self) -> None:
        self.held_keys = []
        self.held_keys_time = {}
        self.pressed_keys = []
        self.key_map = {"up":["w","up arrow"],
                        "down":["s","down arrow"],
                        "left":["a","left arrow"],
                        "right":["d","right arrow"],
                        "rotate_clock":["w","up arrow"],
                        "rotate_anti_clock":["z",
                                             "right control",
                                             "left control"],
                        "hard_drop":["space"],
                        "hold_block":["c",
                                      "right shift",
                                      "left shift"],
                        "pause":["escape"]}
    
    def update(self,dt):
        self.pressed_keys = []

        for event in pg.event.get():

            if event.type == pg.QUIT:
                exit()

            if event.type == pg.KEYDOWN:
                key = pg.key.name(event.key)
                if key not in self.held_keys:
                    self.held_keys.append(key)
                    self.held_keys_time[key] = 0
                else:
                    self.held_keys_time[key] += dt
                
                self.pressed_keys.append(key)

            if event.type == pg.KEYUP:
                key = pg.key.name(event.key)
                if key in self.held_keys:
                    self.held_keys.remove(key)
                    del self.held_keys_time[key]
            
            if event.type == pg.VIDEORESIZE and window.mode == "windowed":
                window.update_scale()
    
    def key_held(self,key_map_id):
        #Check if keys in keymap are pressed based on id

        key_held = False

        for key in self.key_map[key_map_id]:
            if key in self.held_keys:
                key_held = True
        
        return key_held
    
    def key_pressed(self,key_map_id):
        #Check if keys in keymap are pressed based on id

        key_pressed = False

        for key in self.key_map[key_map_id]:
            if key in self.pressed_keys:
                key_pressed = True
        
        return key_pressed


pg.init()

window = Window()
events = Events()
timer = t.Timers()

sprites = s.Sprites()
styles = s.Styles(sprites)
fonts = s.Fonts()


letters = ["I","O","J","L","S","Z","T"]
test_figure = figure.Figure("I",(1,1),styles)

while True:
    window.update()
    events.update(window.dt)
    timer.update(window.dt)

    fonts.draw_font("stuff and things",
                      pg.Rect(V(0,0),V(70,50)),
                      window)

    test_figure.update(window.dt,window,sprites)

    if events.key_pressed("hard_drop"):
        letters.append(letters.pop(0))
        test_figure = figure.Figure(letters[0],(1,1),styles)



    
    



