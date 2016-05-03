import os

WIDTH = 1000
HEIGHT = 1000
FPS = 60
TITLE = "Hotline Python!"

# set up assets path
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")

# player properties
PLAYER_ACCELERATION = 0.5
PLAYER_FRICTION = -0.12

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# keys for tile position
KEY = {
    'S': [(0, 0), True],
    'W': [(32, 0), False],
    'G': [(0, 32), False],
    'N': [(32, 32), False]
}

