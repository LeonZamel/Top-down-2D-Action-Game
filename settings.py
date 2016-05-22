import os
import configparser
import pygame as pg


pg.mixer.pre_init(44100, -16, 2, 512)
pg.mixer.init()

# CUSTOM SETTINGS (by user)
config = configparser.ConfigParser()
config.read("settings.cfg")
move_up = getattr(pg, "K_" + (config.get("CONTROLS", "up")).lower())
move_down = getattr(pg, "K_" + (config.get("CONTROLS", "down")).lower())
move_left = getattr(pg, "K_" + (config.get("CONTROLS", "left")).lower())
move_right = getattr(pg, "K_" + (config.get("CONTROLS", "right")).lower())

WIDTH = int(config.get("WINDOW", "width"))
HEIGHT = int(config.get("WINDOW", "height"))

volume = float(config.get("SOUND", "volume"))

FPS = 120
TITLE = "Hotline Python!"
FLAGS = pg.DOUBLEBUF | pg.HWSURFACE | pg.HWACCEL

ALLOWED_EVENTS = [pg.KEYDOWN, pg.QUIT, pg.MOUSEBUTTONDOWN]

PIXEL_MULT = 4
TILESIZE = 8
BULLET_SPEED = 20
# set up assets path
game_folder = os.path.dirname(__file__)
resource_folder = "resources"
map_folder = os.path.join(resource_folder, "maps")
img_folder = os.path.join(resource_folder, "img")
snd_folder = os.path.join(resource_folder, "snd")

gun_shot = pg.mixer.Sound(os.path.join(snd_folder, "shot1.wav"))
gun_shot.set_volume(volume)
punch = pg.mixer.Sound(os.path.join(snd_folder, "punch.wav"))
punch.set_volume(0.3 * volume)
hit = pg.mixer.Sound(os.path.join(snd_folder, "hit.wav"))
hit.set_volume(volume)

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

