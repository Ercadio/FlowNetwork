
from manim import *
from itertools import product
import math

"""
@todo:  Implement this animation to showcase how a Map with roads and blocks in Cytopia
        translates to the transport network
"""
class MapToGraph(Scene):
    def construct(self):
        l = math.sqrt(2) / 4
        grid_objects = [ Polygon([l*(i-j), l*(i+j)/2, 0], [l*(i+1-j), l*(j+i+1)/2, 0], [l*(i-j), l*(i+j+2)/2, 0], [l*(i-j-1), l*(i+j+1)/2, 0]) for (i, j) in product(range(10), repeat=2) ]
        grid = Group(*grid_objects)
        #grid.set_fill('#707070', opacity=1)
        #grid.set_style(stroke_color='#FFFFFF')
        
        self.add(grid)
        self.wait(3)
        self.play(FadeOut(grid))

"""
@todo:  Implement this animation to showcase traffic simulation for a whole
        day with the transport network in MapToGraph
"""
class TransportSim(Scene):
    def construct(self):
        pass
