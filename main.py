# Hotline Python

import pygame as pg
import random
import math
from settings import *
from sprites import *
import os


class Game:
    def __init__(self):
        # initialize game, pg and create window
        self.running = True
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), FLAGS)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.playing = True
        self.all_events = pg.event.get()

        # using ordered updates so player will rendered last (on top)
        self.all_sprites = pg.sprite.OrderedUpdates()
        self.map_tiles = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.player = None

    def new(self):
        # start new game
        # SPRITE GROUPS
        # using ordered updates so player will rendered last (on top)
        self.all_sprites = pg.sprite.OrderedUpdates()
        self.map_tiles = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()

        # OBJECTS
        l = Level(self, "level.txt")
        l.build()
        self.player = Player(self, 0, 0, 11, 13)
        Gun(self)
        # ADD TO SPRITE GROUP IN RIGHT ORDER, init player last

        # run game AFTER everything is set up
        self.run()

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def update(self):
        # game loop - update
        self.all_sprites.update()
        # collision detected by sprites

    def handle_events(self):
        # game loop - events
        # sprites do event handling their selves, they iterate through self.all_events
        self.all_events = pg.event.get()
        for event in self.all_events:
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False
                if event.key == pg.K_F11:
                    if self.screen.get_flags() & pg.FULLSCREEN:
                        pg.display.set_mode((WIDTH, HEIGHT), FLAGS)
                    else:
                        pg.display.set_mode((WIDTH, HEIGHT), FLAGS | pg.FULLSCREEN)

    def draw(self):
        # game loop - draw/ render
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)

        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # show splash/ start screen
        pass

    def show_go_screen(self):
        # show game over screen
        pass

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
