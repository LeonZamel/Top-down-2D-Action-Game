import random
import os
import math
import pygame as pg
import settings as s
import sprites

vec = pg.math.Vector2

# Moving objects (technically sprites)


class Mob(pg.sprite.Sprite):
    def __init__(self, game, img_x, img_y, img_width, img_height, spritesheet_file, stop_game, spawn=(0, 0)):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        # stop game if hit
        self.stop_game = stop_game

        self.spritesheet = sprites.Spritesheet(os.path.join(s.img_folder, spritesheet_file))
        self.image_orig = self.spritesheet.get_image(img_x, img_y, img_width, img_height)
        self.image_orig.set_colorkey(s.BLACK)
        self.image = self.image_orig
        self.rect_orig = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.hitbox = pg.rect.Rect(self.rect.x, self.rect.y, self.rect_orig.width - 2 * s.PIXEL_MULT,
                                   self.rect_orig.height - 2 * s.PIXEL_MULT)
        self.hitbox.center = self.rect_orig.center

        self.pos = vec(spawn[0], spawn[1])
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0

        self.current_weapon = None
        # add to group
        self.game.all_sprites.add(self)
        self.game.mobs.add(self)

    def update(self):
        self.act()
        self.move()
        # move also includes rotating
        self.check_hit()

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

    def check_hit(self):
        for bullet in self.game.bullets:
            if self.hitbox.colliderect(bullet):
                bullet.kill()
                self.kill()

    def attack(self):
        if self.current_weapon is not None:
            self.current_weapon.shoot(self.rect.centerx, self.rect.centery, self.rot)
        else:
            self.punch()

    def punch(self):
        for mob in self.game.mobs:
            if mob is not self:
                if self.hitbox.colliderect(mob):
                    mob.kill()

    def rotate(self, point):
        # turns sprite to face towards player
        # calculate relative offset from point
        offset = (point[0] - self.pos.x, point[1] - self.pos.y)
        # rotate
        self.rot = 180 + round(math.degrees(math.atan2(offset[0], offset[1])), 1)
        # make sure image keeps center
        old_center = self.rect.center
        self.image = pg.transform.rotate(self.image_orig, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def kill(self):
        super().kill()
        if self.stop_game:
            self.game.playing = False

        if self.current_weapon is not None:
            self.current_weapon.toggle_item()
            self.current_weapon.rect.center = self.pos
            self.current_weapon = None


class Player(Mob):
    def __init__(self, game, spawn):
        super(Player, self).__init__(game, 0, 0, 11, 13, "gunguy.png", True, spawn)
        self.mouse_offset = 0

    def move(self):
        self.rotate(pg.mouse.get_pos())
        # set acc to 0 when not pressing so it will stop accelerating
        self.acc = vec(0, 0)

        # move on buttonpress
        key_state = pg.key.get_pressed()
        if key_state[pg.K_w]:
            self.vel.y -= s.PLAYER_ACCELERATION
        if key_state[pg.K_a]:
            self.vel.x -= s.PLAYER_ACCELERATION
        if key_state[pg.K_s]:
            self.vel.y += s.PLAYER_ACCELERATION
        if key_state[pg.K_d]:
            self.vel.x += s.PLAYER_ACCELERATION

        # apply friction
        self.acc += self.vel * s.PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc

        # first move x then y for better collision detection

        self.pos.x += round(self.vel.x + 0.5 * self.acc.x, 1)
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.check_collision('x')

        self.pos.y += round(self.vel.y + 0.5 * self.acc.y, 1)
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.check_collision('y')

        # constrain to screen
        if self.pos.x > s.WIDTH:
            self.pos.x = s.WIDTH
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 0
        if self.pos.y > s.HEIGHT:
            self.pos.y = s.HEIGHT

        # set rect to new calculated pos
        self.rect.center = self.pos
        self.hitbox.center = self.pos

    def act(self):
        for event in self.game.all_events:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.attack()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    if self.current_weapon is not None:
                        self.current_weapon.reload()
                if event.key == pg.K_e:
                    if self.current_weapon is None:
                        # pick up weapon
                        hits = pg.sprite.spritecollide(self, self.game.items, False)
                        if hits:
                            self.current_weapon = hits[0]
                            self.current_weapon.toggle_item()
                            # will kill() itself if not an item
                    else:
                        # throw away weapon
                        self.current_weapon.toggle_item()
                        self.current_weapon.rect.center = self.pos
                        self.current_weapon = None

                if event.key == pg.K_t:
                    print(str(self.game.clock.get_fps()))


class Enemy(Mob):
    seeing_player = False
    last_seen_player = pg.time.get_ticks()

    def __init__(self, game, spawn):
        super(Enemy, self).__init__(game, 0, 0, 11, 13, "gunguy.png", False, spawn)
        self.player_offset = 0

    def move(self):
        if Enemy.seeing_player:
            self.rotate(self.game.player.pos)
        # set acc to 0 when not pressing so it will stop accelerating
        self.acc = vec(0, 0)

        if Enemy.seeing_player is True:
            if self.game.player.pos.x > self.pos.x and self.game.player.pos.x > self.pos.x + 200:
                self.vel.x += s.PLAYER_ACCELERATION
            if self.game.player.pos.x < self.pos.x and self.game.player.pos.x < self.pos.x - 200:
                self.vel.x -= s.PLAYER_ACCELERATION
            if self.game.player.pos.y > self.pos.y and self.game.player.pos.y > self.pos.y + 200:
                self.vel.y += s.PLAYER_ACCELERATION
            if self.game.player.pos.y < self.pos.y and self.game.player.pos.y < self.pos.y - 200:
                self.vel.y -= s.PLAYER_ACCELERATION

        else:
            choice = random.randrange(1, 5)
            if choice == 1:
                self.vel.x += s.PLAYER_ACCELERATION
            elif choice == 2:
                self.vel.x -= s.PLAYER_ACCELERATION
            elif choice == 3:
                self.vel.y += s.PLAYER_ACCELERATION
            elif choice == 4:
                self.vel.y -= s.PLAYER_ACCELERATION
            else:
                pass

        # apply friction
        self.acc += self.vel * s.PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc

        # first move x then y for better collision detection

        self.pos.x += round(self.vel.x + 0.5 * self.acc.x, 1)
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.check_collision('x')

        self.pos.y += round(self.vel.y + 0.5 * self.acc.y, 1)
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.check_collision('y')

        # constrain to screen
        if self.pos.x > s.WIDTH:
            self.pos.x = s.WIDTH
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 0
        if self.pos.y > s.HEIGHT:
            self.pos.y = s.HEIGHT

        # set rect to new calculated pos
        self.rect.center = self.pos
        self.hitbox.center = self.pos

    def act(self):
        if self.current_weapon is not None:
            if self.current_weapon.ammo == 0:
                self.current_weapon.reload()
        self.look_for_player()
        if Enemy.seeing_player and abs(self.pos.x - self.game.player.pos.x) <= 400 and abs(self.pos.y - self.game.player.pos.y) <= 400:
            self.attack()

    def look_for_player(self):
        if abs(self.pos.x - self.game.player.pos.x) <= 200 and abs(self.pos.y - self.game.player.pos.y) <= 200:
            Enemy.last_seen_player = pg.time.get_ticks()
            Enemy.seeing_player = True
        elif Enemy.last_seen_player + 2000 < pg.time.get_ticks():
            Enemy.seeing_player = False
