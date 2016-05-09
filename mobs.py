from sprites import *


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


class Enemy(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
