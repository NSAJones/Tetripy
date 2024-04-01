#Small module that has functions used for interpolation

def lerp(t,a,b):
        return a + (b-a) * t

#Sasing functions for use with lerp

def ease_in_cubic(x):
    return x**3

def ease_out_cubic(x):
    return 1 - pow(1 - x, 3)

def ease_in_out_cubic(x):
    if x < 0.5:
        return 4 * (x**3)
    else:
       return 1 - pow(-1 * x + 2, 3) / 2