import os
import pygame as pg
pg.mixer.pre_init(44100, -16, 2, 512)
pg.mixer.init()

WIDTH = 1920
HEIGHT = 1080
FPS = 120
TITLE = "Hotline Python!"
FLAGS = pg.DOUBLEBUF | pg.HWSURFACE | pg.HWACCEL

ALLOWED_EVENTS = [pg.KEYDOWN, pg.QUIT, pg.MOUSEBUTTONDOWN]

PIXEL_MULT = 4
TILESIZE = 8
BULLET_SPEED = 20
# set up assets path
game_folder = os.path.dirname(__file__)
img_folder = "img"
snd_folder = "snd"

gun_shot = pg.mixer.Sound(os.path.join(snd_folder, "shot1.wav"))
gun_shot.set_volume(0.3)

# player properties
PLAYER_ACCELERATION = 0.9
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

