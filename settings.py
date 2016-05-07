import os
import pygame as pg

WIDTH = 1000
HEIGHT = 1000
FPS = 120
TITLE = "Hotline Python!"
FLAGS = pg.DOUBLEBUF | pg.HWSURFACE

PIXEL_MULT = 4
TILESIZE = 8
BULLET_SPEED = 16
# set up assets path
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")

# player properties
PLAYER_ACCELERATION = 0.8
PLAYER_FRICTION = -0.2

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# keys for tile position
KEY = {
    'S': [(0, TILESIZE), True],
    'W': [(0, 0), False],
    'G': [(TILESIZE, 0), False],
    'N': [(32, 32), False]
}

