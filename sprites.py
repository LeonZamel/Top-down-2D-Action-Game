# Sprite classes for HP
import math
from settings import *
vec = pg.math.Vector2


class Spritesheet(object):
    # utility class for loading and parsing sprite sheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, img_x, img_y, img_width, img_height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((img_width, img_height))
        image.blit(self.spritesheet, (0, 0), (img_x, img_y, img_width, img_height))
        image = pg.transform.scale(image, (img_width * PIXEL_MULT, img_height * PIXEL_MULT))
        return image


class Tile(pg.sprite.Sprite):
    def __init__(self, is_wall):
        pg.sprite.Sprite.__init__(self)
        self.is_wall = is_wall
        self.image = None
        # adding to groups etc. is handled by Level class


class Level(object):
    # loads a level and makes its tiles
    def __init__(self, game, level_file):
        self.level_file = level_file
        self.game = game
        self.spritesheet = Spritesheet(os.path.join(img_folder, "spritesheet.png"))

    # adds all level tiles to group as sprites
    def build(self):
        with open(self.level_file, 'r') as f:
            for ln, line in enumerate(f.readlines()):
                for cn, char in enumerate(line):
                    try:
                        pos = KEY[char][0]
                        wall = KEY[char][1]
                        t = Tile(wall)
                        t.image = self.spritesheet.get_image(pos[0], pos[1], TILESIZE, TILESIZE)
                        t.rect = t.image.get_rect()
                        t.rect.x = cn * TILESIZE * PIXEL_MULT
                        t.rect.y = ln * TILESIZE * PIXEL_MULT
                        self.game.map_tiles.add(t)
                        self.game.all_sprites.add(t)
                        if wall:
                            self.game.walls.add(t)
                    except KeyError:
                        pass


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, rot):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((1 * PIXEL_MULT, 1 * PIXEL_MULT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.vel = vec(0, 0)
        self.pos = vec(self.rect.center)
        # convert back to radians
        self.dir = math.radians(rot+90)
        # set pos to "front mid" of player sprite
        # spawn away far enough so it won't count as hit
        self.pos = vec(x + (self.game.player.rect_orig.height / 2 + BULLET_SPEED) * math.cos(self.dir),
                       y - (self.game.player.rect_orig.height / 2 + BULLET_SPEED) * math.sin(self.dir))
        # calculates speed for given direction
        self.vel = vec(BULLET_SPEED * math.cos(self.dir), -(BULLET_SPEED * math.sin(self.dir)))
        self.rect.center = self.pos

        # add to groups
        self.game.all_sprites.add(self)
        self.game.bullets.add(self)

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.rect.center = self.pos
        if self.rect.x > WIDTH or self.rect.right < 0 or self.rect.top > HEIGHT or self.rect.y < 0:
            self.kill()
        if pg.sprite.spritecollide(self, self.game.walls, False):
            self.kill()


class Weapon(pg.sprite.Sprite):
    def __init__(self, game, m_ammo, s_delay):
        # ONLY parent class, cant create Weapon() instance
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.spritesheet = Spritesheet(os.path.join(img_folder, "Weapon_sheet.png"))
        self.max_ammo = m_ammo
        self.ammo = self.max_ammo
        self.delay = s_delay
        self.last_shot = pg.time.get_ticks()
        self.game.all_sprites.add(self)
        self.game.items.add(self)

    def shoot(self, x, y, rot):
        now = pg.time.get_ticks()
        if self.ammo > 0:
            if now - self.last_shot > self.delay:
                self.ammo -= 1
                self.last_shot = now
                Bullet(self.game, x, y, rot)

    def reload(self):
        self.ammo = self.max_ammo


class Pistol(Weapon):
    def __init__(self, game):
        super(Pistol, self).__init__(game, 20, 150)
        self.image = self.spritesheet.get_image(0, 0, 8, 6)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()


