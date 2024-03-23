import pygame as pg
import timer as t
import figure,easing

class Window:
    """
    Class that manages window resizing, scale and clock dt
    """
    def __init__(self) -> None:
        
        self.window_dims = V(640,360)
        self.fullscreen_dims = pg.display.list_modes()[0]
        self.game_dims = V(320,180)

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
        updates the scale and game_rect attributes based on the size
        of the window, use after changing the size of the display
        """
        self.scale = min(self.window_dims[0]/self.game_dims[0],
                         self.window_dims[1]/self.game_dims[1])
        
        self.game_rect = pg.Rect(V(0),self.game_dims*self.scale)
        self.game_rect.center = V(self.window.get_rect().size) / 2
    
    def scale_rect(self,rect,in_game_rect=True):
        """
        - scales a rect using scale attribute,
        - if in_game_rect is true offsets it using game_rect attribute
        """
        scaled_rect = pg.Rect(V(rect.topleft)*self.scale,
                              V(rect.size)*self.scale)
        
        if in_game_rect:
            scaled_rect.topleft = (scaled_rect.topleft + 
                                self.game_rect.topleft)
        
        return scaled_rect
    
    def windowed(self):
        """
        sets the display to a resizeable window
        """
        self.window = pg.display.set_mode(self.window_dims,pg.RESIZABLE)
        self.mode = "windowed"

        self.update_scale()
    
    def fullscreen(self):
        """
        sets the display to fullscreen
        """
        self.window = pg.display.set_mode(self.fullscreen_dims,
                                          pg.FULLSCREEN)
        self.mode = "fullscreen"

        self.update_scale()

    def blit(self,source,dest,special_flags=0):
        """
        shorthand for drawing to the window
        """
        self.window.blit(source,dest,special_flags)
    
    def update(self):
        """
        updates dt and flips display as well as drawing a background
        """
        self.dt = self.clock.tick(self.fps)
        pg.display.flip()

        self.window.fill(V3(0,0,0))

class Events:
    "class that manages inputs"
    def __init__(self) -> None:
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
    
    def update(self):
        for event in pg.event.get():

            if event.type == pg.QUIT:
                exit()

            if event.type == pg.KEYDOWN:
                key = pg.key.name(event.key)
                if key not in self.pressed_keys:
                    self.pressed_keys.append(key)

            if event.type == pg.KEYUP:
                key = pg.key.name(event.key)
                if key in self.pressed_keys:
                    self.pressed_keys.remove(key)
            
            if event.type == pg.VIDEORESIZE and window.mode == "windowed":
                window.update_scale()
    
    def key_event(self,key_map_id):
        """
        check if keys in keymap are pressed based on id
        """
        key_pressed = True

        for key in self.key_map[key_map_id]:
            if key in self.pressed_keys:
                key_pressed = False
        
        return key_pressed

pg.init()

V = pg.Vector2
V3 = pg.Vector3

window = Window()
events = Events()
timer = t.Timers()

while True:
    window.update()
    events.update()
    timer.update()
    



