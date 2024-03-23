import pygame as pg
import timer, easing

#test
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
        self.update_scale()

        self.window = pg.display.set_mode(self.window_dims)
        self.mode = None

        self.windowed()

        self.fps = 60
        self.clock = pg.time.Clock()
        self.dt = None

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
        self.window = pg.diplay.set_mode(self.window_dims,pg.RESIZABLE)
        self.mode = "windowed"

        self.update_scale()
    
    def fullscreen(self):
        """
        sets the display to fullscreen
        """
        self.window = pg.display.set_mode(self.fullscreen_dims,pg.FULLSCREEN)
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

pg.init()


V = pg.Vector2
V3 = pg.Vector3

window = Window()

while True:
    window.update()
    



