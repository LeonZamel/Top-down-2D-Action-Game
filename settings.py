import os

WIDTH = 1000
HEIGHT = 1000
FPS = 60
TITLE = "Hotline Python!"

PIXEL_MULT = 4
TILESIZE = 8
# set up assets path
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")

# player properties
PLAYER_ACCELERATION = 1
PLAYER_FRICTION = -0.18

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# keys for tile position
KEY = {
    'S': [(0, TILESIZE), True],
    'W': [(0, 0), False],
    'G': [(TILESIZE, 0), False],
    'N': [(32, 32), False]
}

