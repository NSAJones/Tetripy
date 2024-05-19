import easing
import pygame as pg

V = pg.Vector2
V3 = pg.Vector3
class Button:
    def __init__(self,text:str,rect:pg.Rect,padding:pg.Vector2 = V(0,0)) -> None:
        self.text = text
        self.rect = rect
        self.draw_rect = self.rect.copy()
        self.padding = padding

        self.base_colour = pg.Color(0,0,0,0)
        self.hover_colour = pg.Color(150,150,150,100)
        self.pressed_colour = pg.Color(150,150,150,255)

        self.pressed = False
        self.activated = False

        self.focused = False
        self.focused_pressed = False
        self.focused_pressed_last = False
        self.focused_activated = False

        self.transition_time = 0
        self.transition_time_max = 0.25

    def lerp_colour(self,t:float,colour1:pg.Color,colour2:pg.Color):
        # Lerp alpha and rgb of colour separately

        t = self.transition_time/self.transition_time_max
        alpha = easing.lerp(t,colour1.a,colour2.a)
        rgb_1 = V3(colour1.r,colour1.g,colour1.b)
        rgb_2 =  V3(colour2.r,colour2.g,colour2.b)
        rgb = easing.lerp(t,rgb_1,rgb_2)
        

        return pg.Color(*rgb,alpha)

    def update(self,dt,window,fonts,events):
        self.activated = False
        self.focused_activated = False
        current_colour = self.base_colour

        # Button activation happens on key release rather than press

        # Mouse collision code
        if (self.draw_rect.collidepoint(events.get_mouse_pos(window)) and
            events.mouse_focus):
            
            if events.mouse_down:
                self.pressed = True

            if events.mouse_up:
                self.pressed = False
                self.activated = True

            self.transition_time = min(self.transition_time_max,
                                       self.transition_time+dt)

            if self.pressed:
                t = self.transition_time/self.transition_time_max
                current_colour = self.lerp_colour(t,self.hover_colour,
                                                  self.pressed_colour)
            
            else:
                t = self.transition_time/self.transition_time_max                
                current_colour = self.lerp_colour(t,self.base_colour,
                                                  self.hover_colour)
            

        # Keyboard only code
        elif self.focused:
            self.transition_time = min(self.transition_time_max,
                                       self.transition_time+dt)
            
            t = self.transition_time/self.transition_time_max
            current_colour = self.lerp_colour(t,self.base_colour,self.hover_colour)

            current_colour = self.lerp_colour(t,self.base_colour,
                                              self.hover_colour)
        
            if self.focused_pressed:
                if not self.focused_pressed_last:
                    self.focused_pressed_last = True
                    

                self.transition_time = min(self.transition_time_max,
                                        self.transition_time+dt)

                t = self.transition_time/self.transition_time_max
                current_colour = self.lerp_colour(t,self.hover_colour,
                                                self.pressed_colour)
            elif not self.focused_pressed and self.focused_pressed_last:
                self.focused_activated = True
                self.focused_pressed_last = False
            
        # No animation if uh um uhhe uhhhhhhhhhhhhhhhhhhhhhhhh
        else:
            self.transition_time = 0
            self.pressed = False
        
        self.pressed_response(dt,window,fonts,events)

        self.focused_pressed = False
        
        # Draw rect
        self.draw_rect = self.rect.copy()
        self.draw_rect.width += self.padding[0]*2
        self.draw_rect.height += self.padding[1]*2
        self.draw_rect.center = self.rect.center

        surf = pg.Surface(self.draw_rect.size).convert()
        surf.fill(current_colour)
        surf.set_alpha(current_colour.a)

        window.blit(surf,self.draw_rect,window)

        # Draw font
        fonts.draw_font(self.text,self.rect,window,center=True)

    # Functions used for keyboard only controls
    def focus(self):
        self.focused = True
    
    def unfocus(self):
        self.focused = False
    
    def hold(self):
        self.focused_pressed = True

    def get_pressed(self):
        if self.activated or self.focused_activated:
            return True
        return False

    # Blank function used for inheritance
    def pressed_response(self,dt,window,fonts,events):
        pass

    def __repr__(self) -> str:
        return f"Button({self.text},{self.rect})"

class OptionButton(Button):
    def __init__(self,text:str,option_list:list,rect:pg.Rect,
                 padding:pg.Vector2 = V(0,0)) -> None:
        
        super().__init__(text,rect,padding)
        self.option_list = option_list

        self.original_text = str(self.text)

        self.option_select = 0
    
    def pressed_response(self,dt,window,fonts,events):
        selected = self.option_list[self.option_select]
        self.text = f"{self.original_text}:{selected}"

        if self.get_pressed():
            self.next_option()

    def next_option(self):
        self.option_select = int((self.option_select+1)%len(self.option_list))
    
    def select_option(self,object):
        self.option_select = self.option_list.index(object)

        
        

class Button_List:
    def __init__(self,button_names:dict,rect:pg.Rect
                 ,gap:float = 0,padding=2)-> None:
        
        self.button_dict = {}
        self.button_order = []

        self.rect = rect
        self.pos = V(self.rect.topleft)
        self.gap = gap

        self.focused = None

        self.dir_held_timer = 0
        self.dir_held_max = 0.5
        self.dir_held_skip = 0.3

        for (name,text) in button_names.items():
            self.button_dict[name] = Button(text,
                                            pg.Rect(V(0,0),
                                                    V(self.rect.width,9)),
                                                    V(padding))
            self.button_order.append(name)

    def up(self):
        self.focused = max(0,self.focused-1)
        
    def down(self):
        self.focused = min(len(self.button_dict.keys())-1,self.focused+1)

    def update(self,dt,window,fonts,events):

        # keyboard only controls
        if events.mouse_focus == False:
            
            if self.focused == None:
                self.focused = 0
            
            if events.key_pressed("up"):
                self.up()
                self.dir_held_timer = 0
            elif events.key_pressed("down"):
                self.down()
                self.dir_held_timer = 0
            
            # If direction is held for given time, keep going in that
            # direction instead of just once
            if events.key_held("up") or events.key_held("down"):
                self.dir_held_timer += dt

                if self.dir_held_timer > self.dir_held_max:
                    self.dir_held_timer = self.dir_held_skip
                    if events.key_held("up"):
                        self.up()
                    elif events.key_held("down"):
                        self.down()

        draw_pos = V(self.pos)    
        for (name,button) in self.button_dict.items():
            
            if not self.focused is None:
                focused_name = self.button_order[self.focused]
                if name == focused_name and not events.mouse_focus:
                    button.focused = True

                    if events.key_held("enter"):
                        button.focused_pressed = True

                else:
                    button.focused = False

            button.rect.topleft = V(draw_pos)
            button.update(dt,window,fonts,events)

            draw_pos += V(0,button.rect.height+(button.padding[1]*2)+self.gap)

    def set_option_btn(self,id,option_list,selected=None):
        base_btn = self.button_dict[id]
        self.button_dict[id] = OptionButton(base_btn.text,option_list,
                                            base_btn.rect,base_btn.padding)
        
        if not selected is None:
            self.button_dict[id].select_option(selected)
        
    
    def get_pressed(self):
        for (name,button) in self.button_dict.items():
            if button.get_pressed():
                return name

        return None
        
    def center_to(self,center_pos):
        self.rect.center = center_pos
        self.pos = V(self.rect.topleft)
    
    def change_text(self,id,new_text):
        button = self.button_dict[id]
        if type(button) is OptionButton:
            button.original_text = new_text
        else:
            button.text = new_text

        


            
        
        
        


    
