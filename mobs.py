from sprites import *
import random
# Moving objects (technically sprites)


class Mob(pg.sprite.Sprite):
    def __init__(self, game, img_x, img_y, img_width, img_height, spritesheet_file, stop_game, spawn=(0, 0)):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        # stop game if hit
        self.stop_game = stop_game

        self.spritesheet = Spritesheet(os.path.join(img_folder, spritesheet_file))
        self.image_orig = self.spritesheet.get_image(img_x, img_y, img_width, img_height)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig
        self.rect_orig = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.hitbox = pg.rect.Rect(self.rect.x, self.rect.y, self.rect_orig.width - 2 * PIXEL_MULT,
                                   self.rect_orig.height - 2 * PIXEL_MULT)
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
        self.rotate()
        self.check_hit(self.stop_game)

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

    def check_hit(self, stop_playing):
        for bullet in self.game.bullets:
            if self.hitbox.colliderect(bullet):
                bullet.kill()
                self.kill()
                if self.current_weapon is not None:
                    self.current_weapon.toggle_item()
                    self.current_weapon.rect.center = self.pos
                    self.current_weapon = None
                if stop_playing:
                    self.game.playing = False

    def attack(self):
        if self.current_weapon is not None:
            self.current_weapon.shoot(self.rect.centerx, self.rect.centery, self.rot)
        else:
            self.punch()

    def punch(self):
        pass


class Player(Mob):
    def __init__(self, game, spawn):
        super(Player, self).__init__(game, 0, 0, 11, 13, "gunguy.png", True, spawn)
        self.mouse_offset = 0

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


class Enemy(Mob):
    seeing_player = False
    last_seen_player = pg.time.get_ticks()

    def __init__(self, game, spawn):
        super(Enemy, self).__init__(game, 0, 0, 11, 13, "gunguy.png", False, spawn)
        self.player_offset = 0

    def move(self):
        # set acc to 0 when not pressing so it will stop accelerating
        self.acc = vec(0, 0)

        if Enemy.seeing_player is True:
            if self.game.player.pos.x > self.pos.x and self.game.player.pos.x > self.pos.x + 200:
                self.vel.x += PLAYER_ACCELERATION
            if self.game.player.pos.x < self.pos.x and self.game.player.pos.x < self.pos.x - 200:
                self.vel.x -= PLAYER_ACCELERATION
            if self.game.player.pos.y > self.pos.y and self.game.player.pos.y > self.pos.y + 200:
                self.vel.y += PLAYER_ACCELERATION
            if self.game.player.pos.y < self.pos.y and self.game.player.pos.y < self.pos.y - 200:
                self.vel.y -= PLAYER_ACCELERATION

        else:
            choice = random.randrange(1, 5)
            if choice == 1:
                self.vel.x += PLAYER_ACCELERATION
            elif choice == 2:
                self.vel.x -= PLAYER_ACCELERATION
            elif choice == 3:
                self.vel.y += PLAYER_ACCELERATION
            elif choice == 4:
                self.vel.y -= PLAYER_ACCELERATION
            else:
                pass

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

    def rotate(self):
        # turns sprite to face towards player
        # calculate relative offset from player and angle
        if Enemy.seeing_player:
            self.player_offset = (self.game.player.pos.y - self.rect.centery, self.game.player.pos.x - self.rect.centerx)
            self.rot = 180 + round(math.degrees(math.atan2(self.player_offset[1], self.player_offset[0])), 1)

        # make sure image keeps center
        old_center = self.rect.center
        self.image = pg.transform.rotate(self.image_orig, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def act(self):
        if self.current_weapon.ammo == 0:
            self.current_weapon.reload()
        self.look_for_player()
        if Enemy.seeing_player and abs(self.pos.x - self.game.player.pos.x) <= 400 and abs(self.pos.y - self.game.player.pos.y) <= 400:
            self.attack()

    def look_for_player(self):
        if abs(self.pos.x - self.game.player.pos.x) <= 500 and abs(self.pos.y - self.game.player.pos.y) <= 500:
            Enemy.last_seen_player = pg.time.get_ticks()
            Enemy.seeing_player = True
        elif Enemy.last_seen_player + 2000 < pg.time.get_ticks():
            Enemy.seeing_player = False
