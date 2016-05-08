# Sprite classes for HP
from settings import *
import pygame as pg
import math
vec = pg.math.Vector2


# player class
class Player(pg.sprite.Sprite):
    def __init__(self, game, img_x, img_y, img_width, img_height):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        self.player_spritesheet = Spritesheet(os.path.join(img_folder, "gunguy.png"))
        self.image_orig = self.player_spritesheet.get_image(img_x, img_y, img_width, img_height)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig
        self.rect_orig = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.hitbox = pg.rect.Rect(self.rect.x, self.rect.y, (img_width - 2) * PIXEL_MULT,
                                   (img_height - 2) * PIXEL_MULT)
        self.hitbox.center = self.rect_orig.center

        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0
        self.mouse_offset = 0

        self.current_weapon = None
        # add to group
        self.game.all_sprites.add(self)

    def update(self):
        self.rotate()
        self.move()
        self.act()

    def move(self):
        # set acc to 0 when not pressing so it will stop accelerating
        self.acc = vec(0, 0)

        # move on buttonpress
        key_state = pg.key.get_pressed()
        if key_state[pg.K_w]:
            self.vel.y -= PLAYER_ACCELERATION
        if key_state[pg.K_a]:
            self.vel.x -= PLAYER_ACCELERATION
        if key_state[pg.K_s]:
            self.vel.y += PLAYER_ACCELERATION
        if key_state[pg.K_d]:
            self.vel.x += PLAYER_ACCELERATION

        # apply friction
        self.acc += self.vel * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc

        # first move x then y for better collision detection

        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.check_collision('x')

        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.check_collision('y')

        # constrain to screen
        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 0
        if self.pos.y > HEIGHT:
            self.pos.y = HEIGHT

        # set rect to new calculated pos
        self.rect.center = self.pos
        self.hitbox.center = self.pos

    def check_collision(self, axis):
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall):
                if axis == 'x':
                    if self.vel.x < 0:
                        self.hitbox.left = wall.rect.right
                    elif self.vel.x > 0:
                        self.hitbox.right = wall.rect.left
                    self.pos.x = self.hitbox.centerx
                    self.rect.centerx = self.hitbox.centerx
                else:
                    if self.vel.y < 0:
                        self.hitbox.top = wall.rect.bottom
                    elif self.vel.y > 0:
                        self.hitbox.bottom = wall.rect.top
                    self.pos.y = self.hitbox.centery
                    self.rect.centery = self.hitbox.centery

    def rotate(self):
        # turns sprite to face towards mouse
        mouse = pg.mouse.get_pos()
        # calculate relative offset from mouse and angle
        self.mouse_offset = (mouse[1] - self.rect.centery, mouse[0] - self.rect.centerx)
        self.rot = 180 + round(math.degrees(math.atan2(self.mouse_offset[1], self.mouse_offset[0])), 1)

        # make sure image keeps center
        old_center = self.rect.center
        self.image = pg.transform.rotate(self.image_orig, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def act(self):
        for event in self.game.all_events:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.attack()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    if self.current_weapon is not None:
                        self.current_weapon.reload()
                if event.key == pg.K_e:
                    hits = pg.sprite.spritecollide(self, self.game.items, False)
                    if hits:
                        self.current_weapon = hits[0]
                        hits[0].kill()

    def attack(self):
        if self.current_weapon is not None:
            self.current_weapon.shoot(self.rect.centerx, self.rect.centery, self.rot)
        else:
            self.punch()

    def punch(self):
        pass


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
        self.pos = vec(x + (self.game.player.rect_orig.height / 2) * math.cos(self.dir),
                       y - (self.game.player.rect_orig.height / 2) * math.sin(self.dir))
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


class Gun(Weapon):
    def __init__(self, game):
        super(Gun, self).__init__(game, 20, 300)

        self.image = self.spritesheet.get_image(0, 0, 8, 6)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()


