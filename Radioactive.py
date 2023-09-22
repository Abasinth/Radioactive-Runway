import pygame
import time

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

active_sprite_list = pygame.sprite.Group()
bullet_list = pygame.sprite.Group()

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

        image.set_colorkey(BLACK)

        # Return the image
        return image

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()
        width = 40
        height = 40
        self.idles = pygame.image.load("pcidle.png")
        self.life = 10

        self.speed_x = 0
        self.speed_y = 0

        self.clipcounter = 0
        sprite_sheet = SpriteSheet("p1_walk.png")

        self.level = None

        self.touching_y = False
        self.touchingmoveplaty = False
        self.touching_x = False

        self.onwall = False

        self.dashactive = False
        self.dashcounter = 0

        self.ricochet = False
        self.ricochetcounter = 0

        self.moving = False

        self.direction = 0

        # animations
        self.walking_frames_r = []
        self.walking_frames_l = []

        image = sprite_sheet.get_image(0, 0, 66, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(66, 0, 66, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(132, 0, 67, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(0, 93, 66, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(66, 93, 66, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(132, 93, 72, 90)
        self.walking_frames_r.append(image)
        image = sprite_sheet.get_image(0, 186, 70, 90)
        self.walking_frames_r.append(image)

        # Load all the right facing images, then flip them
        # to face left.
        image = sprite_sheet.get_image(0, 0, 66, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(66, 0, 66, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(132, 0, 67, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(0, 93, 66, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(66, 93, 66, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(132, 93, 72, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = sprite_sheet.get_image(0, 186, 70, 90)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)

        self.image = self.walking_frames_r[0]
        self.image = pygame.transform.scale(self.image, (40, 50))
        self.rect = self.image.get_rect()

    def update(self):
        # gravity / walls
        self.clipcounter += 1
        self.calc_grav()

        self.rect.x += self.speed_x

        # dashing
        if self.dashactive:
            self.dashcounter += .5
            if self.dashcounter > 4:
                self.dashactive = False
                self.dashcounter = 0
                # checks for player movement and changes speed
                if self.moving:
                    if self.direction == 1:
                        self.speed_x = 6
                    elif self.direction == -1:
                        self.speed_x = -6
                else:
                    self.speed_x = 0

        if self.ricochet:
            self.ricochetcounter += .5
            if self.ricochetcounter > 8:
                self.ricochet = False
                self.ricochetcounter = 0
                if self.moving:
                    if self.direction == 1:
                        self.speed_x = 6
                    elif self.direction == -1:
                        self.speed_x = -6
                else:
                    self.speed_x = 0



        if self.speed_x == 0:
            if self.direction == 1:
                self.image = self.walking_frames_r[0]
            else:
                self.image = self.walking_frames_l[0]
        else:
            if self.direction == 1:
                frame = self.clipcounter % len(self.walking_frames_r)
                self.image = self.walking_frames_r[frame]
            elif self.direction == -1:
                frame = self.clipcounter % len(self.walking_frames_l)
                self.image = self.walking_frames_l[frame]

        self.image = pygame.transform.scale(self.image, (40, 50))

        # platform contact
        self.onwall = False

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.speed_x > 0:
                self.rect.right = block.rect.left
                self.onwall = True
            elif self.speed_x < 0:
                self.rect.left = block.rect.right
                self.onwall = True
            elif self.speed_x == 0:
                if self.rect.right >= block.rect.left and self.rect.right < block.rect.right:
                    self.rect.right = block.rect.left
                elif self.rect.left <= block.rect.right and self.rect.left > block.rect.left:
                    self.rect.left = block.rect.right

        self.rect.y += self.speed_y

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.speed_y > 0:
                self.rect.bottom = block.rect.top
                if isinstance(block, MovingPlatform):
                    self.rect.x += block.speed_x
                    self.rect.y += block.speed_y
            elif self.speed_y < 0:
                self.rect.top = block.rect.bottom

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
            if not self.touching_y:
                self.life -= 1
                self.spawn()

        for enemy in self.level.enemy_list:
            if enemy.phit:
                enemy.phit = False
                self.life -= 3
                self.spawn()

        # LAZER contact

        lazer_hit_list = pygame.sprite.spritecollide(self, self.level.lazer_list, False)
        for lazer in lazer_hit_list:
            if lazer.color == "RED":
                if self.speed_x >= 0:
                    self.spawn()
                    self.life -= 1
                elif self.speed_x <= 0:
                    self.spawn()
                    self.life -= 1

        if self.rect.y >= screen_height:
            self.spawn()
            self.life -= 1

        # bullet contact

        bullet_hit = pygame.sprite.spritecollide(self, bullet_list, False)
        for bullet in bullet_hit:
            self.life -= 1
            self.spawn()
            bullet_list.remove(bullet)
            active_sprite_list.remove(bullet)

    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        else:
            self.speed_y += .5

    def jump(self):
        self.rect.y += 2
        if self.direction == 1:
            self.rect.x += 4
        else:
            self.rect.x -= 4
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        self.rect.y -= 2
        if self.direction == 1:
            self.rect.x -= 4
        else:
            self.rect.x += 4

        if len(platform_hit_list) > 0:
            # wall jump
            if self.onwall:
                if self.direction == 1:
                    self.speed_x = -2
                else:
                    self.speed_x = 2
                self.speed_y = -11
                self.ricochet = True
            # reg jump
            else:
                self.speed_y = -10

        if len(enemy_hit_list) > 0:
            self.speed_y = -10
        # movement

    def left(self):
        self.speed_x = -6
        self.direction = -1
        self.moving = True

    def right(self):
        self.direction = 1
        self.speed_x = 6
        self.moving = True

    def stop(self):
        self.speed_x = 0
        self.moving = False

    def dash(self):
        self.dashactive = True
        if self.direction == 1:
            self.speed_x = 20
        elif self.direction == -1:
            self.speed_x = -20

    def spawn(self):
        self.rect.x = 50
        self.rect.y = 500 - self.rect.height

# enemy class

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, maxX, minX):
        super(Enemy, self).__init__()
        self.idles = pygame.image.load("enemyidlechp.png")
        self.rights = pygame.image.load("enemyrightchp.png")
        self.lefts = pygame.image.load("enemyleftchp.png")
        self.preattack = pygame.image.load("enemyanticipat.png")
        self.postattack = pygame.image.load("enemyMAW.png")
        self.preattackr = pygame.transform.flip(self.preattack, True, False)
        self.postattackr = pygame.transform.flip(self.postattack, True, False)

        self.attacking = False

        self.width = 40
        self.height = 70

        self.image = self.idles
        self.image = pygame.transform.scale(self.image, (40, 70))
        self.rect = self.image.get_rect()

        self.direction = None
        self.face = 0

        self.player = None

        self.phit = False

        self.rect.x = x
        self.rect.y = y

        self.maxX = maxX
        self.minX = minX

        self.attackdirection = None
        self.set = False

        self.speed_x = 0
        self.speed_y = 0

        self.level = None

        self.attackcounter = 0
        self.attackcooldown = 60

    def update(self):
        # gravity / walls
        self.calc_grav()

        playerdistance = self.player.rect.x - self.rect.x
        playerydistance = self.player.rect.y - self.rect.y

        if -90 < playerdistance < 90 and -90 < playerydistance < 90 and self.attackcooldown >= 60:
            self.attacking = True
            if not self.set:
                if playerdistance <= 0:
                    self.attackdirection = "l"
                else:
                    self.attackdirection = "r"
                self.set = True

        if self.attacking:
            self.attackcounter += 1
            self.speed_x = 0
            if self.attackcounter <= 30:
                if self.attackdirection == "l":
                    self.image = self.preattack
                else:
                    self.image = self.preattackr
            elif 60 >= self.attackcounter > 30:
                if self.attackdirection == "l":
                    self.image = self.postattack
                    if -90 <= playerdistance <= 0 and -90 <= playerydistance <= 90:
                        self.phit = True
                else:
                    self.image = self.postattackr
                    if 0 <= playerdistance <= 90 and -90 <= playerydistance <= 90:
                        self.phit = True

            elif 90 >= self.attackcounter > 60:
                if self.attackdirection == "l":
                    self.image = self.preattack
                else:
                    self.image = self.preattackr

            elif self.attackcounter > 90:
                self.attacking = False
                self.set = False
                self.attackcounter = 0
                self.attackcooldown = 0

        else:
            if self.face == 0:
                self.image = self.idles
            elif self.face == 1:
                self.image = self.rights
            elif self.face == -1:
                self.image = self.lefts

            if self.attackcooldown <= 60:
                self.attackcooldown += 1



        self.image = pygame.transform.scale(self.image, (40, 70))

        # platform contact
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.speed_x > 0:
                self.rect.right = block.rect.left
            elif self.speed_x < 0:
                self.rect.left = block.rect.right
            elif self.speed_x == 0:
                if self.rect.right >= block.rect.left and self.rect.right < block.rect.right:
                    self.rect.right = block.rect.left
                elif self.rect.left <= block.rect.right and self.rect.left > block.rect.left:
                    self.rect.left = block.rect.right

        self.rect.y += self.speed_y

        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.speed_y > 0:
                self.rect.bottom = block.rect.top
                if isinstance(block, MovingPlatform):
                    self.rect.x += block.speed_x
                    self.rect.y += block.speed_y

            elif self.speed_y < 0:
                self.rect.top = block.rect.bottom

            self.speed_y = 0

        # player contact

        player_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        for guy in player_hit_list:
            self.face = 0
            self.stop()

        if not self.attacking:
            if self.player.rect.x > self.rect.x:
                self.direction = "right"
                self.face = 1
                self.right()

            elif self.player.rect.x < self.rect.x:
                self.direction = "left"
                self.face = -1
                self.left()



        if self.rect.x >= self.maxX-self.width and self.direction == "right":
            self.stop()
        elif self.rect.x <= self.minX and self.direction == "left":
            self.stop()

        if self.speed_x == 0:
            self.face = 0

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

    def left(self):
        self.speed_x = -1

    def right(self):
        self.speed_x = 1

    def stop(self):
        self.speed_x = 0

class GunEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, bulletup, bulletside, timer, bspeed):
        super(GunEnemy, self).__init__()
        width = 50
        height = 50
        self.image = pygame.image.load("VeryGoodLookingEnemy.png")

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

        self.timer = timer
        self.bulletside = bulletside
        self.bulletup = bulletup

        self.bspeed = bspeed

        self.counter = 0
        self.player = None
        level = None

    # shoot every cooldown
    def update(self):
        self.counter += 1

        if self.counter == self.timer:
            self.counter = 0
            if self.bulletup:
                bullet = Bullet("vert", self.bspeed)
                bullet.rect.x = self.rect.centerx
                bullet.rect.y = self.rect.centery
                active_sprite_list.add(bullet)
                bullet_list.add(bullet)

                bullet = Bullet("vert", -self.bspeed)
                bullet.rect.x = self.rect.centerx
                bullet.rect.y = self.rect.centery
                active_sprite_list.add(bullet)
                bullet_list.add(bullet)

            if self.bulletside:
                bullet = Bullet("horiz", self.bspeed)
                bullet.rect.x = self.rect.centerx
                bullet.rect.y = self.rect.centery
                active_sprite_list.add(bullet)
                bullet_list.add(bullet)

                bullet = Bullet("horiz", -self.bspeed)
                bullet.rect.x = self.rect.centerx
                bullet.rect.y = self.rect.centery
                active_sprite_list.add(bullet)
                bullet_list.add(bullet)

class Bullet(pygame.sprite.Sprite):

    def __init__(self, way, speed):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([7, 7])
        self.image.fill(RED)

        self.rect = self.image.get_rect()

        self.way = way
        self.speed = speed

    def update(self):
        if self.way == "horiz":
            self.rect.x += self.speed
        elif self.way == "vert":
            self.rect.y += self.speed

class Lazer(pygame.sprite.Sprite):
    def __init__(self, x, timer):
        super(Lazer, self).__init__()
        width = 50
        height = 600
        self.image = pygame.Surface([width, height])
        self.image.fill(LIME_GREEN)

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = 0

        self.color = "GREEN"
        self.timer = timer

        self.counter = 0

        level = None

    def update(self):
        self.counter += 1

        if self.counter == self.timer * 2:
            self.counter = 0
            self.color = "GREEN"
            self.image.fill(LIME_GREEN)

        if self.counter > self.timer:
            self.color = "RED"
            self.image.fill(RED)

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super(Platform, self).__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, type, width, height, max, min, speed, player):
        super(MovingPlatform, self).__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        self.player = player

        self.rect = self.image.get_rect()
        self.xdirection = 1
        self.ydirection = 1

        self.max = max
        self.min = min
        self.speed = speed
        self.speed_x = 0
        self.speed_y = 0

        self.level = None
        self.type = type

    def update(self):
        # x movement
        if self.type == "horiz":
            self.rect.x += self.speed_x
            if self.xdirection == 1:
                self.speed_x = self.speed
            elif self.xdirection == -1:
                self.speed_x = -self.speed

            # wall collision
            if self.rect.right >= self.max and self.xdirection == 1:
                self.xdirection = -1
            elif self.rect.left <= self.min and self.xdirection == -1:
                self.xdirection = 1

        # y movement
        if self.type == "vert":
            self.rect.y += self.speed_y
            if self.ydirection == 1:
                self.speed_y = self.speed
            elif self.ydirection == -1:
                self.speed_y = -self.speed

            if self.rect.bottom >= self.max and self.ydirection == 1:
                self.ydirection = -1
            elif self.rect.top <= self.min and self.ydirection == -1:
                self.ydirection = 1

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
        self.gunenemy_list = pygame.sprite.Group()
        self.lazer_list = pygame.sprite.Group()
        self.player = player

        self.background = None

        self.world_shift = 0
      # updates when called

    def update_lvl(self):
        self.platform_list.update()
        self.enemy_list.update()
        self.gunenemy_list.update()
        self.lazer_list.update()
        bullet_list.update()

    def draw(self, screen):
        screen.fill(PASTEL_RED)
        bullet_list.draw(screen)
        self.gunenemy_list.draw(screen)
        self.platform_list.draw(screen)
        self.object_list.draw(screen)
        self.lazer_list.draw(screen)
        self.enemy_list.draw(screen)

class Level_1(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1000

        # width, height ,x, y of plat
        levelstatic = [[400, 100, 0, 500],
                 [300, 100, 600, 500],
                       # columns
                       [40, 400, 300, 200],
                       [20, 500, 600, 200]]

        # type(horiz/vert), width, height, x, y, max, min, speed
        levelmove = [["horiz", 200, 10, 350, 400, 700, 120, 4]]

        #x, y ,max, min
        enemies = []

        # static platforms
        for platform in levelstatic:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)
        # moving platforms
        for platform in levelmove:
            # specify max, min x
            block = MovingPlatform(platform[0], platform[1], platform[2], platform[5], platform[6], platform[7], self.player)
            block.player = self.player
            block.rect.x = platform[3]
            block.rect.y = platform[4]
            block.level = self
            self.platform_list.add(block)

        for enemy in enemies:
            sprite = Enemy(enemy[0], enemy[1], enemy[2], enemy[3])
            sprite.player = self.player
            sprite.level = self
            self.enemy_list.add(sprite)

class Level_2(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        self.level_limit = -1000
        # width height x y
        level = [[200, 100, 0, 500],
                 [400, 100, 300, 500],
                 [10, 400, 350, 200]]

        # x, y, max x, min x
        enemies = []

        levelmove = [["horiz", 100, 5, 350, 400, 700, 200, 4]]

        # x, timer
        lazers = []

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

        for platform in levelmove:
            # specify max, min x
            block = MovingPlatform(platform[0], platform[1], platform[2], platform[5], platform[6], platform[7],
                                   self.player)
            block.player = self.player
            block.rect.x = platform[3]
            block.rect.y = platform[4]
            block.level = self
            self.platform_list.add(block)

        for enemy in enemies:
            sprite = Enemy(enemy[0], enemy[1], enemy[2], enemy[3])
            sprite.player = self.player
            sprite.level = self
            self.enemy_list.add(sprite)

        for lazer in lazers:
            lazer = Lazer(lazer[0], lazer[1])
            lazer.player = self.player
            lazer.level = self
            self.lazer_list.add(lazer)

class Level_3(Level):
    def __init__(self,player):
        Level.__init__(self,player)
        self.level_limit = -1000

        level = [[100, 100, 0, 500],
                 [300, 100, 200, 500],
                 [200, 100, 600, 500]]

        # type(horiz/vert), width, height, x, y, max, min, speed
        levelmove = []

        enemies = []

        # x, y, bulletup, bulletside, timer, bspeed
        gunenemies = [[400, 400, False, True, 100, 5]]

        lazers = []

        for platform in level:
            block = Platform(platform[0], platform[1])
            block.player = self.player
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            self.platform_list.add(block)

        for platform in levelmove:
            # specify max, min x
            block = MovingPlatform(platform[0], platform[1], platform[2], platform[5], platform[6], platform[7], self.player)
            block.player = self.player
            block.rect.x = platform[3]
            block.rect.y = platform[4]
            block.level = self
            self.platform_list.add(block)

        for enemy in enemies:
            sprite = Enemy(enemy[0], enemy[1], enemy[2], enemy[3])
            sprite.player = self.player
            sprite.level = self
            self.enemy_list.add(sprite)

        for gun in gunenemies:
            gunner = GunEnemy(gun[0], gun[1], gun[2], gun[3], gun[4], gun[5])
            gunner.player = self.player
            gunner.level = self
            self.gunenemy_list.add(gunner)

        for lazer in lazers:
            lazer = Lazer(lazer[0], lazer[1])
            lazer.player = self.player
            lazer.level = self
            self.lazer_list.add(lazer)

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
        self.lvl_list.append(Level_1(self.player))
        self.lvl_list.append(Level_2(self.player))
        self.lvl_list.append(Level_3(self.player))
        self.lvl_list.append(Level_4(self.player))
        self.lvl_list.append(Level_5(self.player))
        self.lvl_list.append(Level_6(self.player))
        self.lvl_list.append(Level_7(self.player))
        self.lvl_list.append(Level_8(self.player))

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
                if 700 > mouse[0] > 100 and 500 > mouse[1] > 400:
                    pygame.draw.rect(self.screen, PINK, (100, 400, 600, 100))
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        menu_done = True
                        self.on_screen = LVL_SELECT


                else:
                    pygame.draw.rect(self.screen, MAGENTA_RED, (100, 400, 600, 100))

                lvl_select_text = self.lvl_select_text_font.render("LEVEL SELECT", True, WHITE)
                lvl_select_text_rect = lvl_select_text.get_rect()
                lvl_select_text_rect.centerx = 400
                lvl_select_text_rect.centery = 450


                self.screen.blit(title_text, title_text_rect)
                self.screen.blit(start_text, start_text_rect)
                self.screen.blit(lvl_select_text, lvl_select_text_rect)

                self.clock.tick(60)

                pygame.display.flip()

    def game_loop(self):
        game_done = False

        self.player = Player()
        self.initializeLevels()

        active_sprite_list = pygame.sprite.Group()

        current_lvl = self.lvl_list[self.current_lvl_num]
        self.player.level = current_lvl

        self.player.speed_x = 0
        self.player.speed_y = 0

        self.player.spawn()
        active_sprite_list.add(self.player)

        while not game_done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                            game_done = True
                            self.on_screen = QUIT_GAME

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player.left()
                    if event.key == pygame.K_RIGHT:
                        self.player.right()
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_ESCAPE:
                        self.on_screen = GAME_MENU
                        game_done = True
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_r:
                        self.initializeLevels()
                    if event.key == pygame.K_f:
                        self.player.life += 1

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and self.player.speed_x < 0:
                        self.player.stop()
                    if event.key == pygame.K_RIGHT and self.player.speed_x > 0:
                        self.player.stop()

            active_sprite_list.update()
            current_lvl.update_lvl()

            if self.player.rect.left < 0:
                self.player.rect.left = 0

            if self.player.life <= 0:
                game_done = True
                self.on_screen = GAME_OVER

            # deletes bullets if leave screen
            for bullet in bullet_list:
                if bullet.rect.y > 600 or bullet.rect.y < 0 or bullet.rect.x > 800 or bullet.rect.x < 0:
                    bullet_list.remove(bullet)
                    active_sprite_list.remove(bullet)

            # If the player gets to the end of the level, go to the next level
            if self.player.rect.x >= self.death_zone:
                self.player.spawn()
                if self.current_lvl_num < len(self.lvl_list) - 1:
                    self.current_lvl_num += 1
                    current_lvl = self.lvl_list[self.current_lvl_num]
                    self.player.level = current_lvl

            if self.player.rect.x <= 0 and self.current_lvl_num > 0:
                self.player.spawn()
                if self.current_lvl_num < len(self.lvl_list) + 1:
                    self.current_lvl_num -= 1
                    current_lvl = self.lvl_list[self.current_lvl_num]
                    self.player.level = current_lvl

            # drawing code

            current_lvl.draw(self.screen)
            active_sprite_list.draw(self.screen)

            lvl_text = self.font.render("Level: " + str(self.current_lvl_num + 1), True, GREEN)
            lvl_text_rect = lvl_text.get_rect()
            lvl_text_rect.centerx = 400
            lvl_text_rect.centery = 50

            life_text = self.font.render("Lives: " + str(self.player.life), True, SKY_BLUE)
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

        self.player = Player()
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
                    self.player.life = 3
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
