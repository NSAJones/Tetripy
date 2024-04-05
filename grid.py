import pygame as pg
from random import shuffle
import figure,easing

V = pg.Vector2

class Grid:
    """
    This is a class that controls how figures are moved/dropped
    as well as rotation translation from the SRS
    """

    def __init__(self,window,styles) -> None:
        """
        Parameters:
        window(Window): window class
        styles(Styles): style class
        """

        self.block_dims = V(16,16)
        self.grid_dims = V(10,22)
        self.rect = None
        self.update_rect(window)

        self.drop_pos = V(3,0)

        self.active_figure = None
        self.held_figure = None
        self.last_move_rotation = False

        self.next_figures = []
        self.figure_bag = []
        self.shown_pieces = 6

        self.ghost_pos = V(0,0)
        self.used_swap = False

        self.lock_time = 0
        self.lock_time_max = 1
        self.gravity_time = 0
        self.gravity_time_max = 0.8
        self.gravity_time_max_held = 0.1

        self.dir_held_time = 0
        self.dir_held_max = 0.25
        self.dir_held_skip = 0.17

        self.block_dict = {}

        self.update_bag(styles)
        self.next_piece(styles)
    
    def update_rect(self,window):
        #Update rect to size of window.game_dims

        rect_dims = V(self.grid_dims[0]*self.block_dims[0],
                      self.grid_dims[1]*self.block_dims[1])
        self.rect = pg.Rect(V(0,0),rect_dims)
        
        small_game_rect = pg.Rect((0,0),window.game_dims)
        self.rect.center = small_game_rect.center
    
    def update_gravity(self,dt,events,styles):
        #Updates gravity and checks if figure should lock

        #If down key is held, gravity progresses faster

        if ((events.key_held("down") and 
            self.gravity_time > self.gravity_time_max_held)
            or (self.gravity_time > self.gravity_time_max)):

            self.gravity_time = 0

            if self.valid_pos(V(0,1)):
                self.active_figure.pos += V(0,1)
                self.lock_time = 0

        else:
            self.gravity_time += dt
        
        #Play animation if figure has started locking

        if not self.valid_pos(V(0,1)):
            t = self.lock_time/self.lock_time_max
            self.active_figure.alpha = easing.lerp(t,255,100)
            
            self.lock_time += dt

            if self.lock_time > self.lock_time_max:
                self.lock_time = 0
                self.set_figure(styles)
        else:
            self.active_figure.alpha = 255

        #Get ghost pos (hard drop translation)

        ghost_check = V(0,0)
        while self.valid_pos(ghost_check + V(0,1)):
            ghost_check += V(0,1)
        
        self.ghost_pos = V(ghost_check)
    
    def set_figure(self,styles):
        #Destroy current figure and put it into block_list

        for block in self.active_figure.block_list:
            row_num = int(block.pos[1])
            if row_num not in self.block_dict.keys():
                self.block_dict[row_num] = []
            self.block_dict[row_num].append(block)

        self.score_update()
        self.next_piece(styles)
        
    def get_blocks(self,pos_only=False):
        block_list = []
        for (row_num,row) in self.block_dict.items():
            
            for b in row:
                if pos_only:
                    block_list.append(b.pos)
                else:
                    block_list.append(b)
        
        return block_list

    def update_input(self,dt,events,styles):
        #Gandles the different inputs into the game

        if events.key_pressed("left") and self.valid_pos(V(-1,0)):
            self.last_move_rotation = False
            self.lock_time = 0
            self.active_figure.pos += V(-1,0)

        elif events.key_held("left"):

            if self.dir_held_time > self.dir_held_max and self.valid_pos(V(-1,0)):
                self.active_figure.pos += V(-1,0)
                self.dir_held_time = self.dir_held_skip

            elif self.dir_held_time < self.dir_held_max :
                self.dir_held_time += dt
        
        elif events.key_pressed("right") and self.valid_pos(V(1,0)):
            self.last_move_rotation = False
            self.lock_time = 0
            self.active_figure.pos += V(1,0)

        elif events.key_held("right"):

            if self.dir_held_time > self.dir_held_max  and self.valid_pos(V(1,0)):
                self.active_figure.pos += V(1,0)
                self.dir_held_time = self.dir_held_skip

            elif self.dir_held_time < self.dir_held_max :
                self.dir_held_time += dt
        
        else:
            self.dir_held_time = 0
        
        if events.key_pressed("rotate_clock"):
            self.last_move_rotation = True
            self.lock_time = 0
            self.rotate()
        elif events.key_pressed("rotate_anti_clock"):
            self.last_move_rotation = True
            self.lock_time = 0
            self.rotate(False)
        
        if events.key_pressed("hard_drop"):
            self.last_move_rotation = False
            self.active_figure.pos += self.ghost_pos
            self.active_figure.update_block_pos()
            self.set_figure(styles)
        
        if events.key_pressed("hold_block") and not self.used_swap:
            if self.held_figure is None:
                self.held_figure = self.active_figure
                self.next_piece(styles)
            else:
                temp = self.held_figure
                self.held_figure = self.active_figure
                self.active_figure = temp
                self.active_figure.pos = V(self.drop_pos)
            
            self.used_swap = True
            self.held_figure.pos = V(0,0)

    def rotate(self,clockwise=True):
        #Rotates active figure and uses wall kick data when needed

        origin_rot= int(self.active_figure.rotation)

        #rotate clockwise or counter-clockwise

        new_rot = None
        if clockwise:
            new_rot = int((origin_rot+1)%4)
        else:
            new_rot = origin_rot-1
            if new_rot < 0:
                new_rot = 3
        
        change_key = f"{origin_rot}>{new_rot}"
        wallkick_trans = figure.WALLKICK_DATA[change_key]
        if self.active_figure.type == "I":
            wallkick_trans = figure.WALLKICK_DATA_I[change_key]

        self.active_figure.rotation = new_rot
        self.active_figure.update_block_pos()

        #use wallkick data to check if rotation is possible

        if not self.valid_pos():
            valid_translation = None
            for translation in wallkick_trans:
                if self.valid_pos(translation):
                    valid_translation = translation
                    break
            
            if valid_translation is None:
                self.active_figure.rotation = origin_rot
            else:
                self.active_figure.pos += translation

    def valid_pos(self,offset=V(0,0)):
        #check if offset/rotation is valid

        for block_move in self.active_figure.block_list:
            new_pos = V(block_move.pos) + V(offset)

            for block_set in self.get_blocks():
                if new_pos == block_set.pos:
                    return False
            
            if (new_pos[0] < 0 or 
                new_pos[0] > self.grid_dims[0]-1 or
                new_pos[1] > self.grid_dims[1]-1):
                return False
        
        return True

    def update_bag(self,styles):
        #update figure_bag and next_figures

        while len(self.figure_bag) == 0 or len(self.next_figures) < self.shown_pieces:

            if len(self.figure_bag) == 0:
                for type in ["I","O","J","L","S","Z","T"]:
                    self.figure_bag.append(figure.Figure(type,
                                                         V(0,0),
                                                         styles))
                shuffle(self.figure_bag)
            
            if len(self.next_figures) < self.shown_pieces:
                self.next_figures.append(self.figure_bag.pop(0))

    def next_piece(self,styles):
        #change to the next figure

        self.active_figure = self.next_figures.pop(0)
        self.active_figure.pos = V(self.drop_pos)
        self.update_bag(styles)

        self.used_swap = False
    
    def draw_widgets(self,dt,window,sprites):

        side_stuff_rect = pg.Rect(V(0,0),V(16*4,16*3))
        side_stuff_rect.top = self.rect.top
        side_stuff_rect.right = self.rect.left
        if not self.held_figure is None:
            self.held_figure.update(dt,window,sprites,side_stuff_rect.topleft)
        
        side_stuff_rect.left = self.rect.right
        for f in self.next_figures:
            f.update(dt,window,sprites,side_stuff_rect.topleft)
            side_stuff_rect.top += side_stuff_rect.height

    def score_update(self):
        #checks if grid can score

        scored_lines = []

        for row_num in range(int(self.grid_dims[1])):
            if row_num in self.block_dict.keys():
                row = self.block_dict[row_num]
                #if score move all previous rows down

                scored_lines.append(row_num)

        #check for t spins
        if self.active_figure.type == "T" and self.last_move_rotation:
            t_origin = V(self.active_figure.pos)
            corner_pos = [t_origin,
                          t_origin+V(2,0),
                          t_origin+V(2,2),
                          t_origin+V(0,2)
                          ]
            facing_corner_pos = corner_pos[self.active_figure.rotation,
                                           int((self.active_figure.rotation+1
                                                )%4)]
            block_list = self.get_blocks(True)

            active_corners = 0
            facing_corners = 0
            for b in block_list:
                if b in corner_pos:
                    active_corners += 1
                if b in facing_corner_pos:
                    facing_corner_pos += 1
            
            if active_corners >= 3:
                if facing_corners == 2:
                    pass
                    #t spin
                else:
                    #t spin mini
                    pass

        for row_num in scored_lines:
            if len(row) >= self.grid_dims[0]:
                    del self.block_dict[row_num]

                    for i in range(row_num,-1,-1):
                        if i in self.block_dict.keys():
                            for block in self.block_dict[i]:
                                block.pos += V(0,1)
        #update rows dictionary if blocks have moved
                                
        if len(scored_lines)>1:
            self.update_rows()

        return len(scored_lines)>1

    def update_rows(self):
        #moves blocks to their proper row in block_dict

        block_list = self.get_blocks()
        self.block_dict = {}

        for block in block_list:
            row_num = int(block.pos[1])
            if row_num not in self.block_dict.keys():
                self.block_dict[row_num] = []
            self.block_dict[row_num].append(block)
        
    def update(self,dt,window,styles,events,sprites):
        fill_surf = pg.Surface(self.rect.size)
        fill_surf.fill((0,0,10))
        window.blit(fill_surf,self.rect)

        self.update_input(dt,events,styles)
        self.update_gravity(dt,events,styles)

        for block in self.get_blocks():
            block.update(window,sprites,self.rect.topleft)
        
        self.active_figure.ghost(window,sprites,self.rect.topleft,self.ghost_pos)
        self.active_figure.update(window,sprites,self.rect.topleft)
        
        self.draw_widgets(dt,window,sprites)



class Score:
    def __init__(self) -> None:
        self.score = 0

        self.single = 100
        self.double = 300
        self.triple = 500
        self.quad = 800

        self.m_spin_single = 200
        self.m_spin_double = 400

        self.spin_single = 800
        self.spin_double = 1200
        self.spin_triple = 1600

        self.combo = 50


            

                

    

