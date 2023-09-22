import random
import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PASTEL_RED = (255, 105, 97)
MAGENTA_RED = (194, 30, 86)
TOMATO = (255,99,71)
SCARLET = (86, 3, 25)
PINK = (255, 105, 180)
BLUE = (0, 0, 255)
LIME_GREEN = (50, 205, 50)
SKY_BLUE = (135, 206, 235)
TURQUOISE = (175, 238, 238)

screen_width = 800
screen_height = 600

#graphics
def imgcolorkey(image, colorkey):
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image

class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """

    def __init__(self, file_name):
        """ Constructor. Pass in the file name of the sprite sheet. """

        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """

        # Create a new blank image
        image = pygame.Surface([width, height]).convert()

        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))

        colorkey = -1

        # Return the image
        return imgcolorkey(image, colorkey)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        width = 40
        height = 40
        self.image = pygame.Surface([width, height])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.life = 3

        self.speed_x = 0
        self.speed_y = 0

        self.level = None

        self.touching_y = False
        self.touching_x = False

    def update(self):
        # gravity / walls
        self.calc_grav()

        self.rect.x += self.speed_x

        # platform contact
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.speed_x > 0:
                self.rect.right = block.rect.left
            elif self.speed_x < 0:
                self.rect.left = block.rect.right

        self.rect.y += self.speed_y

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.speed_y > 0:
                self.rect.bottom = block.rect.top
            elif self.speed_y < 0:
                self.rect.top = self.rect.bottom

            self.speed_y = 0

        # object contact
        object_hit_list = pygame.sprite.spritecollide(self, self.level.object_list, False)
        for object in object_hit_list:
            self.level.object_list.remove(object)
            self.life += 1

        # ENEMY contact
        self.touching_y = False

        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for enemy in enemy_hit_list:
            if self.speed_y > 0:
                self.rect.bottom = enemy.rect.top
                self.touching_y = True
            elif self.speed_y < 0:
                self.rect.top = self.rect.bottom
                self.touching_y = True

            self.speed_y = 0

        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for enemy in enemy_hit_list:
            if self.touching_y == False:
                if self.speed_x >= 0:
                    self.rect.right = enemy.rect.left
                    self.spawn()
                    self.life -= 1
                elif self.speed_x <= 0:
                    self.rect.left = enemy.rect.right
                    self.spawn()
                    self.life -= 1

        if self.rect.y >= screen_height - 40:
            self.spawn()
            self.life -= 1

    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        else:
            self.speed_y += .5
        if self.rect.y >= screen_height - self.rect.height and self.speed_y >= 0:
            self.speed_y = 0
            self.rect.y = screen_height - self.rect.height

    def jump(self):
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        self.rect.y -= 2

        if len(platform_hit_list) > 0:
            self.speed_y = -10

        if len(enemy_hit_list) > 0:
            self.speed_y = -10
        # movement

    def left(self):
        self.speed_x = -6

    def right(self):
        self.speed_x = 6

    def stop(self):
        self.speed_x = 0

    def spawn(self):
        self.rect.x = 50
        self.rect.y = 500 - self.rect.height

# enemy class

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, maxX, minX):
        super(Enemy, self).__init__()
        width = 80
        height = 60
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect()

        self.direction = None

        self.player = None

        self.rect.x = x
        self.rect.y = y

        self.maxX = maxX
        self.minX = minX

        self.speed_x = 0
        self.speed_y = 0

        self.level = None

    def update(self):
        # gravity / walls
        self.calc_grav()

        self.rect.x += self.speed_x

        # platform contact
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.speed_x > 0:
                self.rect.right = block.rect.left
            elif self.speed_x < 0:
                self.rect.left = block.rect.right
            self.jump()

            self.speed_x = 0

        self.rect.y += self.speed_y

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.speed_y > 0:
                self.rect.bottom = block.rect.top
            elif self.speed_y < 0:
                self.rect.top = self.rect.bottom

            self.speed_y = 0

        if self.player.rect.x > self.rect.x:
            self.speed_x += .03
            self.direction = "right"
        elif self.player.rect.x < self.rect.x:
            self.speed_x -= .03
            self.direction = "left"

        if self.rect.x >= self.maxX and self.direction == "right":
            self.speed_x = 0
        elif self.rect.x <= self.minX and self.direction == "left":
            self.speed_x = 0

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        else:
            self.speed_y += .5
        if self.rect.y >= screen_height - self.rect.height and self.speed_y >= 0:
            self.speed_y = 0
            self.rect.y = screen_height - self.rect.height
        # movement


    def jump(self):
        self.rect.y += .5
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        self.rect.y -= .5

        if len(platform_hit_list) > 0:
            self.speed_y = -10

        if len(enemy_hit_list) > 0:
            self.speed_y = -10

    def left(self):
        self.speed_x = -6

    def right(self):
        self.speed_x = 6

    def stop(self):
        self.speed_x = 0

class spriteAnims(pygame.sprite.Sprite):
    playerleft = []


class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super(Platform, self).__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()

class LifeBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(LifeBlock, self).__init__()

        self.image = pygame.Surface([10, 10])
        self.image.fill(RED)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
# levels

class Level(object):
    def __init__(self, player):

        self.platform_list = pygame.sprite.Group()
        self.object_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player

        self.background = None

        self.world_shift = 0
      # updates when called

    def update_lvl(self):
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):

        screen.fill(BLACK)
        self.platform_list.draw(screen)
        self.object_list.draw(screen)
        self.enemy_list.draw(screen)


class Level_1(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1000

        # width, height ,x, y of plat
        level = [[400, 100, 0, 500],
                 [300, 100, 600, 500]]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)


class Level_2(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1000
        # width height x y
        level = [[200, 100, 0, 500],
                 [400, 100, 300, 500]]

        enemies = [[400, 500]]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

        for enemy in enemies:
            sprite = Enemy(enemy[0], enemy[1], 600, 300)
            sprite.player = self.player
            sprite.level = self
            self.enemy_list.add(sprite)

class Level_3(Level):
    def __init__(self,player):
        Level.__init__(self,player)
        self.level_limit = -1000

        level = [[100, 100, 0, 500],
                 [300, 100, 200, 500],
                 [200, 100, 600, 500]]

        enemies = [[210, 500],
                   [280, 500]]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

        for enemy in enemies:
            sprite = Enemy(enemy[0], enemy[1], 500, 200)
            sprite.player = self.player
            sprite.level = self
            self.enemy_list.add(sprite)


class Level_4(Level):
    def __init__(self,player):
        Level.__init__(self,player)
        self.level_limit = -1000

        level = [[400, 100, 0, 500],
                 [30, 30, 450, 400],
                 #lifeblock
                 [20, 20, 465, 550],
                 [30, 30, 600, 350],
                 [100, 100, 700, 500]]

        lifeblocks = [[465, 520]]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

        for life in lifeblocks:
            object = LifeBlock(life[0], life[1])
            object.player = self.player
            self.object_list.add(object)

class Level_5(Level):
    def __init__(self,player):
        Level.__init__(self,player)
        self.level_limit = -1000

        level = [[50, 50, 50, 500],
                 [40, 40, 190, 400],
                 [50, 50, 330, 500],
                 [40, 40, 480, 480],
                 [60, 50, 680, 400]]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

class Level_6(Level):
    def __init__(self,player):
        Level.__init__(self,player)
        self.level_limit = -1000
        # width, height, x, y
        level = [[100, 100, 0, 500],
                 [20, 20, 200, 400],
                 [10, 10, 350, 300],
                 [5, 5, 430, 200],
                 # lifeblock
                 [8, 8, 250, 200],
                 [100, 100, 700, 500]]

        # x, y - given width/height
        lifeblocks = [[250, 170]]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

        for life in lifeblocks:
            object = LifeBlock(life[0], life[1])
            object.player = self.player
            self.object_list.add(object)

class Level_7(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1000

        # width, height ,x, y of plat
        level = [[400, 100, 0, 500],
                 [5, 100, 500, 500],
                 [5, 440, 500, 0],
                [300, 100, 600, 500]]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

class Level_8(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1000

        # width, height ,x, y of plat
        level = [[100, 100, 0, 500],
                 # col 1
                 [5, 100, 300, 500],
                 [5, 400, 300, 0],
                 # col 2
                 [5, 200, 400, 500],
                 [5, 400, 400, 0],
                 # col 3
                 [5, 300, 500, 500],
                 [5, 400, 500, 0],
                [200, 100, 600, 500]]

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

player = Player()

GAME_MENU = 1
GAME_LOOP = 2
LVL_SELECT = 3
GAME_OVER = 4
QUIT_GAME = -1

class Game:
    def __init__(self):
        self.on_screen = GAME_MENU
        self.current_lvl_num = 0
        self.death_zone = 800

    def initializeGame(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.size = [screen_width, screen_height]
        self.screen = pygame.display.set_mode(self.size)

        pygame.display.set_caption("The Floor Is A Radioactive Hellscape")

        self.font = pygame.font.SysFont("TimesNewRoman", 40)
        self.title_text_font = pygame.font.SysFont("TimesNewRoman", 90)
        self.start_text_font = pygame.font.SysFont("TimesNewRoman", 75)
        self.lvl_select_text_font = pygame.font.SysFont("TimesNewRoman", 75)
        self.back_text_font = pygame.font.SysFont("TimeNewRoman", 50)
        self.lvl_text_font = pygame.font.SysFont("TimesNewRoman", 40)
        self.game_over_text_font = pygame.font.SysFont("TimesNewRoman", 100)

    def initializeLevels(self):

        self.lvl_list = []
        self.lvl_list.append(Level_1(player))
        self.lvl_list.append(Level_2(player))
        self.lvl_list.append(Level_3(player))
        self.lvl_list.append(Level_4(player))
        self.lvl_list.append(Level_5(player))
        self.lvl_list.append(Level_6(player))
        self.lvl_list.append(Level_7(player))
        self.lvl_list.append(Level_8(player))

    def game_menu(self):
        menu_done = False

        title_text = self.title_text_font.render("Radioactive Runway", True, PASTEL_RED)
        title_text_rect = title_text.get_rect()
        title_text_rect.centerx = 400
        title_text_rect.centery = 100

        start_text = self.start_text_font.render("START!", True, WHITE)
        start_text_rect = start_text.get_rect()
        start_text_rect.centerx = 400
        start_text_rect.centery = 250

        while not menu_done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_done = True
                    self.on_screen = QUIT_GAME

                self.screen.fill(BLACK)

                    # x, y, width, height

                mouse = pygame.mouse.get_pos()

                # start button
                if 600 > mouse[0] > 200 and 300 > mouse[1] > 200:
                    pygame.draw.rect(self.screen, GREEN, (200, 200, 400, 100))
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        menu_done = True
                        self.current_lvl_num = 0
                        self.on_screen = GAME_LOOP

        # x, y, width, height
                else:
                    pygame.draw.rect(self.screen, LIME_GREEN, (200, 200, 400, 100))

                # width + x > mouse[0] > x and vice versa
                # button for controls menu
                if 700 > mouse[0] > 100 and 500 > mouse[1] > 400:
                    pygame.draw.rect(self.screen, PINK, (100, 400, 600, 100))
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        menu_done = True
                        self.on_screen = LVL_SELECT


                else:
                    pygame.draw.rect(self.screen, MAGENTA_RED, (100, 400, 600, 100))

                controls_text = self.lvl_select_text_font.render("CONTROLS", True, WHITE)
                controls_text_rect = controls_text.get_rect()
                controls_text_rect.centerx = 400
                controls_text_rect.centery = 450


                self.screen.blit(title_text, title_text_rect)
                self.screen.blit(start_text, start_text_rect)
                self.screen.blit(controls_text, controls_text_rect)

                self.clock.tick(60)

                pygame.display.flip()

    def lvl_select_loop(self):

        lvl_select_done = False

        self.initializeLevels()

        back_text = self.back_text_font.render("Back", True, WHITE)
        back_text_rect = back_text.get_rect()
        back_text_rect.centerx = 675
        back_text_rect.centery = 525

        while not lvl_select_done:
            mouse_down = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    lvl_select_done = True
                    self.on_screen = QUIT_GAME
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True

            self.screen.fill(BLACK)

            mouse = pygame.mouse.get_pos()

            lvl_count = 0

            for level in self.lvl_list:
                button_y = 20 + lvl_count * 60

                if 500 > mouse[0] > 200 and 50 + button_y > mouse[1] > button_y:
                    pygame.draw.rect(self.screen, TURQUOISE, (100, button_y, 400, 50))
                    if mouse_down == True:
                        lvl_select_done = True
                        self.current_lvl_num = lvl_count
                        self.on_screen = GAME_LOOP

                        # x, y, width, height
                else:
                    pygame.draw.rect(self.screen, SCARLET, (100, button_y, 400, 50))

                lvl_text = self.lvl_text_font.render("Level " + str(lvl_count + 1), True, WHITE)
                lvl_text_rect = lvl_text.get_rect()
                lvl_text_rect.centerx = 300
                lvl_text_rect.centery = (60 * lvl_count) + 40

                lvl_count += 1
                self.screen.blit(lvl_text, lvl_text_rect)

            if 750 > mouse[0] > 600 and 550 > mouse[1] > 500:
                pygame.draw.rect(self.screen, PASTEL_RED, (600, 500, 150, 50))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    lvl_select_done = True
                    self.on_screen = GAME_MENU

                    # to calc center x & y, width or  height / 2 + x or y
            else:
                pygame.draw.rect(self.screen, SCARLET, (600, 500, 150, 50))

            if lvl_select_done == False:
                self.screen.blit(back_text, back_text_rect)
                self.clock.tick(60)
                pygame.display.flip()

    def game_loop(self):
        game_done = False

        self.initializeLevels()

        current_lvl = self.lvl_list[self.current_lvl_num]
        active_sprite_list = pygame.sprite.Group()
        player.level = current_lvl

        player.speed_x = 0
        player.speed_y = 0

        player.spawn()
        active_sprite_list.add(player)

        while not game_done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                            game_done = True
                            self.on_screen = QUIT_GAME

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.left()
                    if event.key == pygame.K_RIGHT:
                        player.right()
                    if event.key == pygame.K_UP:
                        player.jump()
                    if event.key == pygame.K_ESCAPE:
                        self.on_screen = GAME_MENU
                        game_done = True
                    if event.key == pygame.K_r:
                        self.initializeLevels()
                    if event.key == pygame.K_f:
                        player.life += 1

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and player.speed_x < 0:
                        player.stop()
                    if event.key == pygame.K_RIGHT and player.speed_x > 0:
                        player.stop()

            active_sprite_list.update()
            current_lvl.update_lvl()

            if player.rect.left < 0:
                player.rect.left = 0

            if player.life == 0:
                game_done = True
                self.on_screen = GAME_OVER

            # If the player gets to the end of the level, go to the next level
            if player.rect.x >= self.death_zone:
                player.spawn()
                if self.current_lvl_num < len(self.lvl_list) - 1:
                    self.current_lvl_num += 1
                    current_lvl = self.lvl_list[self.current_lvl_num]
                    player.level = current_lvl

            if player.rect.x <= 0 and self.current_lvl_num > 0:
                player.spawn()
                if self.current_lvl_num < len(self.lvl_list) + 1:
                    self.current_lvl_num -= 1
                    current_lvl = self.lvl_list[self.current_lvl_num]
                    player.level = current_lvl

            # drawing code

            current_lvl.draw(self.screen)
            active_sprite_list.draw(self.screen)

            lvl_text = self.font.render("Level: " + str(self.current_lvl_num + 1), True, GREEN)
            lvl_text_rect = lvl_text.get_rect()
            lvl_text_rect.centerx = 400
            lvl_text_rect.centery = 50

            life_text = self.font.render("Lives: " + str(player.life), True, PINK)
            life_text_rect = life_text.get_rect()
            life_text_rect.centerx = 400
            life_text_rect.centery = 100

            self.screen.blit(lvl_text, lvl_text_rect)
            self.screen.blit(life_text, life_text_rect)
            # anims go here

            self.clock.tick(60)

            pygame.display.flip()

    def lvl_select_loop(self):

        lvl_select_done = False

        self.initializeLevels()

        back_text = self.back_text_font.render("Back", True, WHITE)
        back_text_rect = back_text.get_rect()
        back_text_rect.centerx = 675
        back_text_rect.centery = 525

        while not lvl_select_done:
            mouse_down = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    lvl_select_done = True
                    self.on_screen = QUIT_GAME
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True

            self.screen.fill(BLACK)

            mouse = pygame.mouse.get_pos()

            lvl_count = 0

            for level in self.lvl_list:
                button_y = 20 + lvl_count*60

                if 500 > mouse[0] > 200 and 50+button_y > mouse[1] > button_y:
                    pygame.draw.rect(self.screen, TURQUOISE, (100, button_y, 400, 50))
                    if mouse_down == True:
                        lvl_select_done = True
                        self.current_lvl_num = lvl_count
                        self.on_screen = GAME_LOOP

                        # x, y, width, height
                else:
                    pygame.draw.rect(self.screen, SCARLET, (100, button_y, 400, 50))

                lvl_text = self.lvl_text_font.render("Level "+str(lvl_count+1), True, WHITE)
                lvl_text_rect = lvl_text.get_rect()
                lvl_text_rect.centerx = 300
                lvl_text_rect.centery = (60*lvl_count)+40

                lvl_count += 1
                self.screen.blit(lvl_text, lvl_text_rect)

            if 750 > mouse[0] > 600 and 550 > mouse[1] > 500:
                pygame.draw.rect(self.screen, PASTEL_RED, (600, 500, 150, 50))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    lvl_select_done = True
                    self.on_screen = GAME_MENU

                    # to calc center x & y, width or  height / 2 + x or y
            else:
                pygame.draw.rect(self.screen, SCARLET, (600, 500, 150, 50))

            if lvl_select_done == False:
                self.screen.blit(back_text, back_text_rect)
                self.clock.tick(60)
                pygame.display.flip()

    def game_over_screen(self):
        game_over_done = False

        game_over_text = self.game_over_text_font.render("GAME OVER!", True, PASTEL_RED)
        game_over_text_rect = game_over_text.get_rect()
        game_over_text_rect.centerx = 400
        game_over_text_rect.centery = 300

        click_spawn_text = self.font.render("Try Again?", True, WHITE)
        click_spawn_text_rect = click_spawn_text.get_rect()
        click_spawn_text_rect.centerx = 400
        click_spawn_text_rect.centery = 405

        while not game_over_done:
            mouse_click = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over_done = True
                    self.on_screen = QUIT_GAME
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_click = 1

            mouse = pygame.mouse.get_pos()

            self.screen.fill(BLACK)

            if 550 > mouse[0] > 250 and 430 > mouse[1] > 380:
                pygame.draw.rect(self.screen, GREEN, (250, 380, 300, 50))
                if mouse_click == 1:
                    game_over_done = True
                    player.life = 3
                    self.on_screen = GAME_MENU

                    # x, y, width, height
            else:
                pygame.draw.rect(self.screen, LIME_GREEN, (250, 380, 300, 50))


            self.screen.blit(game_over_text, game_over_text_rect)
            self.screen.blit(click_spawn_text, click_spawn_text_rect)
            self.clock.tick(60)
            pygame.display.flip()

    # runs entire game, determines which loop to run
    def main_loop(self):
        self.initializeGame()
        done = False
        while not done:
            if self.on_screen == GAME_MENU:
                self.game_menu()

            elif self.on_screen == GAME_LOOP:
                self.game_loop()

            elif self.on_screen == LVL_SELECT:
                self.lvl_select_loop()

            elif self.on_screen == GAME_OVER:
                self.game_over_screen()

            elif self.on_screen == QUIT_GAME:
                done = True

game = Game()
game.main_loop()























