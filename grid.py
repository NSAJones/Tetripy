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
        self.last_figure = None

        self.next_figures = []
        self.figure_bag = []
        self.shown_pieces = 2

        self.ghost_pos = V(0,0)
        self.used_swap = False

        self.lock_time = 0
        self.lock_time_max = 1
        self.gravity_time = 0
        self.gravity_time_max = 0.8
        self.gravity_time_max_held = 0.05

        self.dir_held_time = 0
        self.dir_held_max = 0.25
        self.dir_held_skip = 0.17

        self.animate_time = 0
        self.scored_lines = []

        self.block_dict = {}

        self.score = Score()

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
    
    def set_figure(self,styles,soft_drop=True):
        #Destroy current figure and put it into block_list

        for block in self.active_figure.block_list:
            row_num = int(block.pos[1])
            if row_num not in self.block_dict.keys():
                self.block_dict[row_num] = []
            self.block_dict[row_num].append(block)

        self.score_update()
        self.score.score_drop(self.active_figure.pos[1],soft_drop)

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
        #  Handles the different inputs into the game

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
            
            hard_check = V(0,0)
            while self.valid_pos(hard_check + V(0,1)):
                hard_check += V(0,1)
            
            self.last_move_rotation = False
            self.active_figure.pos += hard_check
            self.active_figure.update_block_pos()
            self.set_figure(styles,False)

        
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
        # Change to the next figure

        self.last_figure = self.active_figure

        self.active_figure = self.next_figures.pop(0)
        self.active_figure.pos = V(self.drop_pos)
        self.update_bag(styles)

        self.used_swap = False
    
    def draw_widgets(self,dt,window,sprites,fonts):

        side_stuff_rect = pg.Rect(V(0,0),V(16*4,16*3))
        side_stuff_rect.top = self.rect.top
        side_stuff_rect.right = self.rect.left
        if not self.held_figure is None:
            self.held_figure.update(window,sprites,side_stuff_rect.topleft)
        
        side_stuff_rect.left = self.rect.right
        for f in self.next_figures:
            f.update(window,sprites,side_stuff_rect.topleft)
            side_stuff_rect.top += side_stuff_rect.height
        
        self.score.update(dt,window,fonts,V(side_stuff_rect.topleft))

    def score_update(self):
        # Checks if grid can score

        for row_num in range(int(self.grid_dims[1])):
            if row_num in self.block_dict.keys():
                row = self.block_dict[row_num]
                #If score move all previous rows down
                if len(row) >= self.grid_dims[0]:
                    self.scored_lines.append(row_num)

    def score_lines(self):
        # Score lines

        # Check for t spins
        if self.last_figure.type == "T" and self.last_move_rotation and(
            not(self.last_figure.pos[0] < 0 and 
                self.last_figure.pos[0] > self.grid_dims[0])):
            
            t_origin = V(self.last_figure.pos)
            corner_pos = [t_origin,
                          t_origin+V(2,0),
                          t_origin+V(2,2),
                          t_origin+V(0,2)]
            
            facing_corner_pos = [corner_pos[self.last_figure.rotation],
                                 corner_pos[int((self.last_figure.rotation+1)%4)]]
            
            block_list = self.get_blocks(True)

            active_corners = 0
            facing_corners = 0

            for b in block_list:
                if b in corner_pos:
                    active_corners += 1
                if b in facing_corner_pos:
                    facing_corners += 1
            
            if active_corners >= 3:
                if facing_corners == 2:
                    #t spin mini
                    self.score.score_spin(len(self.scored_lines),True)
                else:
                    #t spin 
                    self.score.score_spin(len(self.scored_lines),False)
        elif len(self.scored_lines)>0:
            self.score.score_lines(len(self.scored_lines))

        
        # Delete blocks in full rows
        for row_num in self.scored_lines:
            del self.block_dict[row_num]
            for i in range(row_num,-1,-1):
                if i in self.block_dict.keys():
                    for block in self.block_dict[i]:
                        block.pos += V(0,1)

        # Update rows dictionary if blocks have moved
        self.update_rows()
        self.scored_lines = []

    def animate_scoring(self,dt,window,styles,sprites):
        self.animate_time += dt

        score_anim = styles.get_score_anim()
        anim_len = len(score_anim)

        delay = 0.6/anim_len
        single_delay = delay * anim_len
        offset = 0.02
        max_delay_all = (single_delay * offset) * self.grid_dims[0]

        start_time = 0
        
        for x in range(int(self.grid_dims[0])):

            end_time = start_time + single_delay
            
            


            if self.animate_time < start_time:
                for row in self.scored_lines:
                    
                    block_rect = pg.Rect(V(self.rect.topleft)+V(x*16,row*16),
                                V(16,16))
                    sprite = sprites.get_image(score_anim[sprite_index])
                    window.blit(sprite,block_rect)

            elif self.animate_time < end_time:
                t = (self.animate_time-start_time)/single_delay
                sprite_index = int(easing.lerp(t,0,anim_len))
                sprite_index = min(sprite_index,anim_len-1)               
                
                for row in self.scored_lines:
                    
                    block_rect = pg.Rect(V(self.rect.topleft)+V(x*16,row*16),
                                V(16,16))
                    sprite = sprites.get_image(score_anim[sprite_index])
                    window.blit(sprite,block_rect)
            
            start_time += single_delay*offset

                
                    
        if self.animate_time >= end_time:
            self.score_lines()
            self.animate_time = 0

    def update_rows(self):
        #moves blocks to their proper row in block_dict

        block_list = self.get_blocks()

        self.block_dict = {}

        for block in block_list:
            row_num = int(block.pos[1])
            if row_num not in self.block_dict.keys():
                self.block_dict[row_num] = []
            self.block_dict[row_num].append(block)
        
    def update(self,dt,window,styles,events,sprites,fonts):
        fill_surf = pg.Surface(self.rect.size)
        fill_surf.fill((0,0,10))
        window.blit(fill_surf,self.rect)

        if len(self.scored_lines) == 0:
            self.update_input(dt,events,styles)
            self.update_gravity(dt,events,styles)

            
            
            self.active_figure.ghost(window,sprites,self.rect.topleft,self.ghost_pos)
            self.active_figure.update(window,sprites,self.rect.topleft)
        else:
            self.animate_scoring(dt,window,styles,sprites)

        for (row,blocks) in self.block_dict.items():
                if row not in self.scored_lines:
                    for block in blocks:
                        block.update(window,sprites,self.rect.topleft)

        self.draw_widgets(dt,window,sprites,fonts)



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

        self.combo_score = 50

        self.pending_scores = []
        self.pending_timer = 0
        self.pending_timer_max = 4

        self.level = 1
        self.combo = 0


    def score_lines(self,lines):
        """Score a normal line from 1 to 4"""

        score_add = 0

        match lines:
            case 1:
                score_add = self.single
            case 2:
                score_add = self.double
            case 3:
                score_add = self.triple
            case 4:
                score_add = self.quad
        
        score_add = score_add * self.level
        self.pending_scores.append(score_add)
    
    def score_spin(self,lines,t_spin_mini=False):
        """Score a t-spin or mini t-spin"""

        score_add = 0

        if t_spin_mini:
            match lines:
                case 1:
                    score_add = self.m_spin_single
                case 2:
                    score_add = self.m_spin_double

        else:
            match lines:
                case 1:
                    score_add = self.spin_single
                case 2:
                    score_add = self.spin_double
                case 3:
                    score_add = self.spin_triple
        
        score_add = score_add * self.level
        self.pending_scores.append(score_add)
    
    def score_drop(self,cells,soft_drop=False):
        if soft_drop:
            self.pending_scores.append(int(cells))
        else:
            self.pending_scores.append(int(cells*2))


    def update(self,dt,window,fonts,offset=V(0,0)):
        font_height = fonts.char_dims[1]
        font_rect = pg.Rect(offset,V(1000,font_height))

        fonts.draw_font("SCORE",font_rect,window)
        font_rect.topleft += V(0,font_height)

        animation_time_total = (self.pending_timer_max/
                                (1+(len(self.pending_scores)/2)))

        #Do animation with lerp using easing library
        if len(self.pending_scores) != 0:
            self.pending_timer += dt
            t = easing.ease_in_out_cubic(self.pending_timer/animation_time_total)

            add_score = self.score + int(easing.lerp(t,0,self.pending_scores[0]))
            fonts.draw_font(str(add_score),font_rect,window)

            for i,score in enumerate(self.pending_scores):
                font_rect.topleft += V(0,font_height)

                if i == 0:
                    new_score = int(easing.lerp(t,score,0))
                    fonts.draw_font(f"+{new_score}",font_rect,window)

                    if self.pending_timer >= animation_time_total:
                        self.score += self.pending_scores.pop(0)
                        self.pending_timer = 0
                else:
                    fonts.draw_font(f"+{score}",font_rect,window)
        else:
            fonts.draw_font(str(self.score),font_rect,window)
            self.pending_timer = 0
        
        








        
        


            

                

    

