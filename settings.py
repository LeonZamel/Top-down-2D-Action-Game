import os

WIDTH = 800
HEIGHT = 800
FPS = 60
TITLE = "Hotline Python!"

# set up assets path
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")

# player properties
PLAYER_ACC = 1
PLAYER_FRICTION = -0.2

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# keys for tile position
KEY = {
    'S': (0, 0),
    'W': (32, 0),
    'G': (0, 32),
    'N': (32, 32)
}

