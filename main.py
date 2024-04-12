#The main file where everything is run

import pygame as pg
import timer as t
import sprites as s
import grid as g
import figure,easing

V = pg.Vector2
V3 = pg.Vector3
class Window:
    """Class that manages window resizing, scale and clock dt"""

    def __init__(self) -> None:
        
        #Dimensions of the window and game. Game dimensinons will be
        #scaled to fit into the center of the window and will be the
        #size of the game in pixels
        self.window_dims = V(640*2,360*2)
        self.fullscreen_dims = pg.display.list_modes()[0]
        self.game_dims = V(640,360)

        #Variables to help with scaling
        self.scale = None
        self.game_rect = None

        #Variables used to access the display surface and it's state
        self.window = pg.display.set_mode(self.window_dims)
        self.mode = None

        #Variables about the clock and the games FPS
        self.fps = 60
        self.clock = pg.time.Clock()
        self.dt = None

        #Update scale to newly sized window
        self.update_scale()

        #Set mode to windowed mode
        self.windowed()

        #Get first delta time from clock to avoid any zero division
        self.update()
    
    def update_scale(self):
        """
        Updates the scale and game_rect attributes based on the size
        of the window, use after changing the size of the display
        """

        #Get current dimensions of display surface
        window_surf_size = self.window.get_size()

        #Calculate int scale to fit game dimensions into window dimensions
        self.scale = min(window_surf_size[0]//self.game_dims[0],
                         window_surf_size[1]//self.game_dims[1])
        
        #Create new game rect using new scale and center it
        self.game_rect = pg.Rect(V(0),self.game_dims * self.scale)
        self.game_rect.center = self.window.get_rect().center
    
    def scale_rect(self,rect,in_game_rect=True):
        """
        Scales a rect using scale attribute,
        If in_game_rect is true offsets it using game_rect attribute

        Parameters:
        rect(pg.Rect): Rect to be resized
        in_game_rect(bool): If rect should be offset by game dimensions

        Returns
        pg.Rect: Scaled Rect
        """

        topleft = V(rect.topleft)

        rect = rect.scale_by(self.scale)
        
        rect.topleft = topleft * self.scale

        if in_game_rect:
            rect.topleft = (rect.topleft + 
                            V(self.game_rect.topleft))

        return rect
    
    def windowed(self):
        """Sets the display to a resizeable window"""

        #Modify pygame display to enable resizeable windowed mode
        self.window = pg.display.set_mode(self.window_dims,pg.RESIZABLE)
        self.mode = "windowed"

        #Update scale as window dimensions might have changed
        self.update_scale()
    
    def fullscreen(self):
        """Sets the display to fullscreen"""

        #Modify pygame display to enable fullscreen mode
        self.window = pg.display.set_mode(self.fullscreen_dims,
                                          pg.FULLSCREEN)
        self.mode = "fullscreen"

        #Update scale as window dimensions might have changed
        self.update_scale()

    def blit(self,surf,dest,offset=V(0,0),scale_rect=True,special_flags=0):
        """
        Shorthand for drawing to the window, also scaled to draw to
        the window

        Parameters:
            surf (pg.Surface): The surface to be drawn
            dest (pg.Rect): The rect position for the surface to be drawn
            to, this will be used to scale the surface to the window scale
            offset (pg.Vector2): The offset from the scaled game screen
            scale_rect(bool): If the dest rect will be scaled
            special_flags(pygame flags): special flags used in pg blits

        """

        #Scale the surface and rect based on scale_rect
        if scale_rect:
            surf = pg.transform.scale_by(surf,self.scale)
            dest = self.scale_rect(dest)

        #Draw surface to window
        self.window.blit(surf,dest,None,special_flags)
    
    def update(self):
        """Updates dt and flips display as well as filling the background"""

        self.dt = self.clock.tick(self.fps)/1000
        if self.dt > 1:
            self.dt = 1/60

        pg.display.flip()

        self.window.fill(V3(0,0,0))
        self.window.fill(V3(0,0,80),self.game_rect)


class Events:
    """Class that manages key inputs and key names"""

    def __init__(self) -> None:

        #Variables to store key states
        self.held_keys = []
        self.held_keys_time = {}
        self.pressed_keys = []

        #Key map id assignments, one key map id can have multiple keys,
        #key names are at https://www.pygame.org/docs/ref/key.html
        self.key_map = {"up":["w","up arrow"],
                        "down":["s","down arrow"],
                        "left":["a","left arrow"],
                        "right":["d","right arrow"],
                        "rotate_clock":["w","up arrow"],
                        "rotate_anti_clock":["z",
                                             "right control",
                                             "left control"],
                        "hard_drop":["space","1"],
                        "hold_block":["c",
                                      "right shift",
                                      "left shift"],
                        "pause":["escape"]}
    
    def update(self,dt):
        """
        Reads pygame events to get pressed/held keys

        Parameters:
        dt (float): delta time in seconds, obtained from window class
        """

        #Reset pressed keys every frame, pressed keys are active for
        #only one frame
        self.pressed_keys = []

        #Loop through pygame events
        for event in pg.event.get():
            
            #Allow exit when the x button is pressed on the window
            if event.type == pg.QUIT:
                exit()

            #Event for when any key if pressed
            if event.type == pg.KEYDOWN:

                #Get key name
                key = pg.key.name(event.key)

                #Add key name to held_keys if it isn't there
                #Add time to record how long key is pressed
                if key not in self.held_keys:
                    self.held_keys.append(key)
                    self.held_keys_time[key] = dt
                else:
                    self.held_keys_time[key] += dt
                
                #Add key name to pressed_keys
                self.pressed_keys.append(key)

            #Event for when any key is let go
            if event.type == pg.KEYUP:

                #Get key name
                key = pg.key.name(event.key)

                #Remove key name if it is in held_keys
                if key in self.held_keys:
                    self.held_keys.remove(key)
                    del self.held_keys_time[key]
            
            if event.type == pg.VIDEORESIZE and window.mode == "windowed":
                window.update_scale()
    
    def key_held(self,key_map_id):
        """
        Check if keys in keymap are held based on id
        
        Parameters:
        key_map_id (str): The name given to an input in self.key_map

        Returns:
        bool: Returns True if key is held
        """

        key_held = False

        #Multiple keys can be in one key map id, check held keys for
        #each key in given key map id
        for key in self.key_map[key_map_id]:
            if key in self.held_keys:
                key_held = True
        
        return key_held
    
    def key_pressed(self,key_map_id):
        """
        Check if keys in keymap are pressed based on id
        
        Parameters:
        key_map_id (str): The name given to an input in self.key_map

        Returns:
        bool: Returns True if key is held
        """

        key_pressed = False

        #Multiple keys can be in one key map id, check pressed keys for
        #each key in given key map id
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

grid = g.Grid(window,styles)

while True:
    window.update()
    events.update(window.dt)
    timer.update(window.dt)
    grid.update(window.dt,window,styles,events,sprites,fonts)

    fonts.draw_font("stuff and things",
                      pg.Rect(V(0,0),V(70,50)),
                      window)


    
    



