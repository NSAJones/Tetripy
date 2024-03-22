import easing

class Timers:
    """
    Class that manages interpolation of values using Timer objects
    """
    def __init__(self) -> None:
        self.timers = {}

    def add_timer(self,timer,id):
        """
        Pass in Timer object with its id
        """
        self.timers[id] = timer

    def update(self,dt):
        for timer in self.timers:
            timer.update(dt)
    
    def val(self,id):
        """
        Get interpolated value at given id
        """
        return self.timers[id].val(id)

class Timer:
    def __init__(self,id,end_time,easing_func,val1,val2) -> None:
        self.id = id
        self.passed_time = 0
        self.end_time = end_time
        self.easing_func = easing_func
        
        self.val1 = val1
        self.val2 = val2

    def update(self,dt):
        self.passed_time += dt
    
    def val(self):
        lerp_perc = self.end_time/self.passed_time
        return self.lerp(self.easing_func(lerp_perc),
                    self.val1,
                    self.val2
                    )
    
    @staticmethod
    def lerp(perc,val1,val2):
        return val1+(perc*(val1-val2))
