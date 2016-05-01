# Sprite classes for HP
from settings import *
import pygame as pg
import math
vec = pg.math.Vector2


# player class
class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.playerspritesheet = Spritesheet(os.path.join(img_folder, "gunguy.png"))
        self.image_orig = self.playerspritesheet.get_image(0, 0, 16, 16)
        self.image_orig = pg.transform.scale(self.image_orig, (64, 64))
        self.image = self.image_orig
        self.rect = self.image.get_rect()
        # self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        # self.acc = vec(0, 0)
        self.rot = 0
        self.mouse_offset = 0

    def update(self):
        self.move()
        self.rotate()

    def move(self):
        # set vel to 0 when not pressing so it will stop moving
        self.vel = vec(0, 0)

        # move on buttonpress
        keystate = pg.key.get_pressed()
        if keystate[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
        if keystate[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
        if keystate[pg.K_s]:
            self.vel.y = PLAYER_SPEED
        if keystate[pg.K_d]:
            self.vel.x = PLAYER_SPEED

        # apply friction
        # self.acc += self.vel * PLAYER_FRICTION
        # equations of motion
        # self.vel += self.acc
        # self.pos += self.vel + 0.5 * self.acc
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        # constrain to screen
        if self.rect.x > WIDTH:
            self.rect.x = WIDTH
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > HEIGHT:
            self.rect.y = HEIGHT

        # set rect to new calculated pos
        # self.rect.center = self.pos

    def rotate(self):
        # turns sprite to face towards mouse
        mouse = pg.mouse.get_pos()
        # calculate relative offset from mouse and angle
        self.mouse_offset = (mouse[1] - self.rect.centery, mouse[0] - self.rect.centerx)
        self.rot = round(-90-math.degrees(math.atan2(*self.mouse_offset)))

        # make sure image keeps center
        old_center = self.rect.center
        self.image = pg.transform.rotate(self.image_orig, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = old_center


class Spritesheet(object):
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        # image = pg.transform.scale(image, (width * 4, height * 4))
        return image


class Tile(pg.sprite.Sprite):
    size = 32

    def __init__(self, is_wall):
        pg.sprite.Sprite.__init__(self)
        self.is_wall = is_wall
        self.image = pg.Surface((Tile.size, Tile.size))
        self.rect = self.image.get_rect()


class Level(object):
    # loads a level and makes its tiles
    def __init__(self, game, level_file):
        self.level_file = level_file
        self.game = game

    # adds all level tiles to group as sprites
    def build(self):
        with open(self.level_file, 'r') as f:
            for ln, line in enumerate(f.readlines()):
                for cn, char in enumerate(line):
                    try:
                        pos = KEY[char][0]
                        wall = KEY[char][1]
                        t = Tile(wall)
                        t.image = self.game.spritesheet.get_image(pos[0], pos[1], Tile.size, Tile.size)
                        t.rect.x = cn * Tile.size
                        t.rect.y = ln * Tile.size
                        self.game.map_tiles.add(t)
                        self.game.all_sprites.add(t)
                        if wall:
                            self.game.walls.add(t)
                    except KeyError:
                        pass
