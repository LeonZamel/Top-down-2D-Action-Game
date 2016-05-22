# Sprite classes for HP
import math
import os
import pygame as pg
import settings as s

vec = pg.math.Vector2


class Spritesheet(object):
    # utility class for loading and parsing sprite sheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, img_pos, img_dim):
        # grab an image out of a larger spritesheet
        image = pg.Surface((img_dim[0], img_dim[1]))
        image.blit(self.spritesheet, (0, 0), (img_pos, img_dim))
        image = pg.transform.scale(image, (img_dim[0] * s.PIXEL_MULT, img_dim[1] * s.PIXEL_MULT))
        return image


class Tile(pg.sprite.Sprite):
    def __init__(self, is_wall):
        super().__init__()
        self.is_wall = is_wall
        self.image = None
        # adding to groups etc. is handled by Level class


class Level(pg.sprite.Sprite):
    # loads a level and makes its tiles
    def __init__(self, game, level_file, t_width, t_height):
        super().__init__()
        self.level_file = level_file
        self.game = game
        self.spritesheet = Spritesheet(os.path.join(s.img_folder, "spritesheet.png"))
        self.image = pg.Surface((t_width * s.TILESIZE * s.PIXEL_MULT, t_height * s.TILESIZE * s.PIXEL_MULT))
        self.rect = self.image.get_rect()

    # adds all level tiles to group as sprites
    def build(self):
        with open(self.level_file, 'r') as f:
            for ln, line in enumerate(f.readlines()):
                for cn, char in enumerate(line):
                    try:
                        pos = s.KEY[char][0]
                        wall = s.KEY[char][1]
                        t = Tile(wall)
                        t.image = self.spritesheet.get_image(pos, (s.TILESIZE, s.TILESIZE))
                        t.rect = t.image.get_rect()
                        t.rect.x = cn * s.TILESIZE * s.PIXEL_MULT
                        t.rect.y = ln * s.TILESIZE * s.PIXEL_MULT
                        self.image.blit(t.image, (t.rect.x, t.rect.y))
                        if wall:
                            self.game.walls.add(t)
                    except KeyError:
                        pass

            self.game.map.add(self)
            self.game.all_sprites.add(self)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, rot):
        super().__init__()
        self.game = game
        self.image = pg.Surface((1 * s.PIXEL_MULT, 1 * s.PIXEL_MULT))
        self.image.fill(s.YELLOW)
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(self.rect.center)
        # convert back to radians
        self.rot = math.radians(rot+90)
        # set pos to "front mid" of player sprite
        # spawn away far enough so it won't count as hit
        self.pos = vec(x + round((self.game.player.rect_orig.height / 2 + s.BULLET_SPEED) * math.cos(self.rot), 1),
                       y - round((self.game.player.rect_orig.height / 2 + s.BULLET_SPEED) * math.sin(self.rot), 1))
        # calculates speed for given direction
        self.vel = vec(round(s.BULLET_SPEED * math.cos(self.rot), 1), - round(s.BULLET_SPEED * math.sin(self.rot), 1))
        self.rect.center = self.pos

        # add to groups
        self.game.all_sprites.add(self)
        self.game.bullets.add(self)

        if pg.sprite.spritecollide(self, self.game.walls, False):
            self.kill()

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.rect.center = self.pos
        if self.rect.x > s.WIDTH or self.rect.right < 0 or self.rect.top > s.HEIGHT or self.rect.y < 0:
            self.kill()
        if pg.sprite.spritecollide(self, self.game.walls, False):
            self.kill()


class Weapon(pg.sprite.Sprite):
    def __init__(self, game, m_ammo, delay, is_item, sound):
        # ONLY parent class, can't create Weapon() instance
        super().__init__()
        self.game = game
        self.spritesheet = Spritesheet(os.path.join(s.img_folder, "Weapon_sheet.png"))
        # is_item needed to know if should be rendered or not
        self.sound = sound
        self.is_item = is_item
        self.max_ammo = m_ammo
        self.ammo = self.max_ammo
        self.delay = delay
        self.last_shot = pg.time.get_ticks()
        if self.is_item:
            self.game.all_sprites.add(self)
            self.game.items.add(self)

    def shoot(self, x, y, rot):
        if self.ammo == 0:
            self.reload()
        now = pg.time.get_ticks()
        if self.ammo > 0:
            if now - self.last_shot > self.delay:
                self.sound.play()
                self.ammo -= 1
                self.last_shot = now
                Bullet(self.game, x, y, rot)
                return True

    def reload(self):
        if self.ammo != self.max_ammo:
            self.ammo = self.max_ammo
            self.last_shot += 20 * self.delay

    def toggle_item(self):
        # will toggle between sprite and weapon for Mob
        if not self.is_item:
            self.is_item = True
            self.game.all_sprites.add(self)
            self.game.items.add(self)
        else:
            self.is_item = False
            self.kill()


class Pistol(Weapon):
    def __init__(self, game, is_item):
        super().__init__(game, 20, 200, is_item, s.gun_shot)
        self.image = self.spritesheet.get_image((0, 0), (8, 6))
        self.image.set_colorkey(s.BLACK)
        self.rect = self.image.get_rect()


class VisionRay(pg.sprite.Sprite):
    # debugging for now
    def __init__(self, game, mob):
        super().__init__(self)
        self.game = game
        self.mob = mob
        self.length = 500
        self.image = pg.Surface((s.WIDTH, s.HEIGHT))
        self.image.set_colorkey(s.BLACK)
        self.image.set_alpha(50)

        self.rect = self.image.get_rect()
        self.rot = self.mob.rot
        self.angle = 90

        self.game.all_sprites.add(self)

    def update(self):
        self.rot = math.radians(self.mob.rot + 90)
        self.make_ray()

    def make_ray(self):
        self.image.fill(s.BLACK)
        pg.draw.line(self.image, s.YELLOW, self.mob.pos, (500 * math.cos(self.rot) + self.mob.pos.x,
                                                          - (500 * math.sin(self.rot)) + self.mob.pos.y), 5)

