# Hotline Python

from mobs import *


class Game:
    def __init__(self):
        # initialize game, pg and create window
        self.running = True
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), FLAGS | pg.FULLSCREEN)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.playing = True
        self.all_events = pg.event.get()

        # using ordered updates so player will rendered last (on top)
        self.all_sprites = pg.sprite.OrderedUpdates()
        self.map = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.player = None

    def new(self):
        # start new game
        # SPRITE GROUPS
        # using ordered updates so player will rendered last (on top)
        self.all_sprites = pg.sprite.OrderedUpdates()
        self.map = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        # OBJECTS
        l = Level(self, "level.txt", 60, 34)
        l.build()
        self.player = Player(self, (500, 700))
        Enemy.seeing_player = False
        e1 = Enemy(self, (40, 40))
        e1.current_weapon = pistol1 = Pistol(self, False)
        e2 = Enemy(self, (1200, 700))
        e2.current_weapon = pistol2 = Pistol(self, False)
        self.player.current_weapon = pistol3 = Pistol(self, False)
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
        pg.display.set_caption(TITLE + str(self.clock.get_fps()))
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
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False
                elif event.key == pg.K_F11:
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
