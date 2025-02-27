import json

import pygame as pg
import pytmx

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 80
TILE_SCALE = 2

font = pg.font.Font(None, 36)


class Platform(pg.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super(Platform, self).__init__()

        self.image = pg.transform.scale(image, (width * TILE_SCALE, height * TILE_SCALE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SCALE
        self.rect.y = y * TILE_SCALE


class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()

        self.load_animations()
        self.current_animation = self.idle_animation_right
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.center = (200, 100)  # Начальное положение персонажа

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 200

        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 500

    def load_animations(self):
        tile_size = 32
        tile_scale = 3
        self.idle_animation_right = []
        self.move_animation_right = []
        num_images = 4
        idle_spritesheet = pg.image.load("sprites/Sprite Pack 3/4 - Tommy/Idle_Poses (32 x 32).png")
        move_spritesheet = pg.image.load("sprites/Sprite Pack 3/4 - Tommy/Running (32 x 32).png")

        for i in range(num_images * 2):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = move_spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.move_animation_right.append(image)
        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = idle_spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.idle_animation_right.append(image)

        self.idle_animation_left = [pg.transform.flip(image, True, False) for image in self.idle_animation_right]

    def update(self, platforms):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and not self.is_jumping:
            self.jump()
        if keys[pg.K_a]:
            if self.current_animation != self.move_animation_left:
                self.current_animation = self.move_animation_left
                self.current_image = 0

            self.velocity_x = -10
        elif keys[pg.K_d]:
            if self.current_animation != self.move_animation_right:
                self.current_animation = self.move_animation_right
                self.current_image = 0

            self.velocity_x = 10
        else:
            if self.current_animation == self.move_animation_right:
                self.current_animation = self.idle_animation_right
                self.current_image = 0
            elif self.current_animation == self.move_animation_left:
                self.current_animation = self.idle_animation_left
                self.current_image = 0

            self.velocity_x = 0

        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False

            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                self.velocity_x = 0

            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
                self.velocity_x = 0

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()

    def jump(self):
        self.velocity_y = -25
        self.is_jumping = True

    def get_damage(self):
        if pg.time.get_ticks() - self.damage_timer > self.damage_interval:
            self.hp -= 1
            self.damage_timer = pg.time.get_ticks()


class Crab(pg.sprite.Sprite):
    def __init__(self, map_width, map_height, start_pos, final_pos):
        super(Crab, self).__init__()

        self.load_animations()
        self.current_animation = self.animation
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_edge = start_pos[0]
        self.right_edge = final_pos[0] + self.image.get_width()

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.direction = "right"

    def load_animations(self):
        tile_scale = 3
        tile_size = 32

        self.animation = []

        image = pg.image.load(
            "sprites/Sprite Pack 2/Sprite Pack 2/9 - Snip Snap Crab/Movement_(Flip_image_back_and_forth) (32 x 32).png")
        image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
        self.animation.append(image)
        self.animation.append(pg.transform.flip(image, True, False))

    def update(self, platforms):

        if self.direction == "right":
            self.velocity_x = 5
            if self.rect.right >= self.right_edge:
                self.direction = "left"
        if self.direction == "left":
            self.velocity_x = -5
            if self.rect.left >= self.left_edge:
                self.direction = "right"

        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False

            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                self.velocity_x = 0

            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
                self.velocity_x = 0

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()


class Onion(pg.sprite.Sprite):
    def __init__(self, map_width, map_height, start_pos, final_pos):
        super(Onion, self).__init__()

        self.load_animations()
        self.current_animation = self.move_animation_right
        self.image = self.current_animation[0]
        self.current_image = 0

        self.rect = self.image.get_rect()
        self.rect.bottomleft = start_pos
        self.left_edge = start_pos[0]
        self.right_edge = final_pos[0] + self.image.get_width()

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width * TILE_SCALE
        self.map_height = map_height * TILE_SCALE

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.direction = "right"

    def load_animations(self):
        tile_size = 16
        tile_scale = 3
        self.move_animation_right = []
        num_images = 1
        move_spritesheet = pg.image.load("sprites/Sprite Pack 2/Sprite Pack 2/1 - Onion Lad/Run_&_Jump (16 x 16).png")

        for i in range(num_images * 2):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = move_spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.move_animation_right.append(image)
        self.move_animation_left = [pg.transform.flip(image, True, False) for image in self.move_animation_right]

    def update(self, platforms):

        if self.direction == "right":
            self.velocity_x = 5
            if self.rect.right >= self.right_edge:
                self.direction = "left"
        if self.direction == "left":
            self.velocity_x = -5
            if self.rect.left >= self.left_edge:
                self.direction = "right"

        new_x = self.rect.x + self.velocity_x
        if 0 <= new_x <= self.map_width - self.rect.width:
            self.rect.x = new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False

            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                self.velocity_x = 0

            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
                self.velocity_x = 0

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.current_animation):
                self.current_image = 0
            self.image = self.current_animation[self.current_image]
            self.timer = pg.time.get_ticks()


class Ball(pg.sprite.Sprite):
    def __init__(self, player_rect, direction):
        super(Ball, self).__init__()

        self.direction = direction
        self.speed = 10

        self.timer = pg.time.get_ticks()
        self.interval = 300

        self.image = pg.image.load("sprites/ball.png")
        self.image = pg.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()

        if self.direction == "right":
            self.rect.x = player_rect.right
        else:
            self.rect.x = player_rect.left
        self.rect.y = player_rect.centery

    def update(self):
        if self.direction == "right":
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

        if pg.time.get_ticks() - self.timer == self.interval:
            self.kill()


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        super(Coin, self).__init__()

        self.load_animations()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.current_image = 0
        self.interval = 200
        self.timer = pg.time.get_ticks()

    def load_animations(self):
        tile_size = 16
        tile_scale = 3
        self.images = []
        num_images = 5
        spritesheet = pg.image.load("sprites/Coin_Gems/MonedaD.png")

        for i in range(num_images):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            image = spritesheet.subsurface(rect)
            image = pg.transform.scale(image, (tile_size * tile_scale, tile_size * tile_scale))
            self.images.append(image)

    def update(self):
        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_image += 1
            if self.current_image >= len(self.images):
                self.current_image = 0
            self.image = self.images[self.current_image]
            self.timer = pg.time.get_ticks()


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Платформер")
        self.setup()

    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.clock = pg.time.Clock()
        self.is_running = False
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.balls = pg.sprite.Group()
        self.coins = pg.sprite.Group()

        self.mode = ""

        self.tmx_map = pytmx.load_pygame("maps/lvl1.tmx")

        self.map_pixel_width = self.tmx_map.width * self.tmx_map.tilewidth * TILE_SCALE
        self.map_pixel_height = self.tmx_map.height * self.tmx_map.tileheight * TILE_SCALE

        self.player = Player(self.map_pixel_width, self.map_pixel_height)
        self.all_sprites.add(self.player)

        for layer in self.tmx_map:
            if layer.name == "platforms":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)

                    if tile:
                        platform = Platform(tile, x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight,
                                            self.tmx_map.tilewidth,
                                            self.tmx_map.tileheight)
                        self.all_sprites.add(platform)
                        self.platforms.add(platform)
            elif layer.name == "coins":
                for x, y, gid in layer:
                    tile = self.tmx_map.get_tile_image_by_gid(gid)

                    if tile:
                        coin = Coin(x * self.tmx_map.tilewidth, y * self.tmx_map.tileheight * TILE_SCALE)
                        self.all_sprites.add(coin)
                        self.coins.add(coin)

        with open("maps/level1_enemies.json", "r") as json_file:
            data = json.load(json_file)

        for enemy in data["enemies"]:
            if enemy["name"] == "Crab":

                x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                crab = Crab(self.map_pixel_width, self.map_pixel_height, [x1, y1], [x2, y2])
                self.all_sprites.add(crab)
                self.enemies.add(crab)
            elif enemy["name"] == "Onion":

                x1 = enemy["start_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y1 = enemy["start_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                x2 = enemy["final_pos"][0] * TILE_SCALE * self.tmx_map.tilewidth
                y2 = enemy["final_pos"][1] * TILE_SCALE * self.tmx_map.tilewidth

                onion = Onion(self.map_pixel_width, self.map_pixel_height, [x1, y1], [x2, y2])
                self.all_sprites.add(onion)
                self.enemies.add(onion)

        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 4

        self.run()

    def run(self):
        self.is_running = True
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pg.quit()
        quit()

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    if self.player.current_animation in (
                            self.player.idle_animation_right, self.player.move_animation_right):
                        direction = "right"
                    else:
                        direction = "left"
                    ball = Ball(self.player.rect, direction)
                    self.balls.add(ball)
                    self.all_sprites.add(ball)

            if self.mode == "game over":
                if event.type == pg.KEYDOWN:
                    self.setup()

    def update(self):
        if self.player.hp <= 0:
            self.mode = "game over"
            return

        for enemy in self.enemies.sprites():
            if pg.sprite.collide_mask(self.player, enemy):
                self.player.get_damage()

        self.player.update(self.platforms)
        self.balls.update()
        pg.sprite.groupcollide(self.balls, self.enemies, True, True)
        pg.sprite.groupcollide(self.balls, self.platforms, True, False)

        for enemy in self.enemies.sprites():
            enemy.update(self.platforms)

        self.camera_x = self.player.rect.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.rect.y - SCREEN_HEIGHT // 2

        self.camera_x = max(0, min(self.camera_x, self.map_pixel_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.map_pixel_height - SCREEN_HEIGHT))

    def draw(self):
        self.screen.fill("light blue")

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))

        pg.draw.rect(self.screen, pg.Color("red"), (10, 10, self.player.hp * 10, 10))
        pg.draw.rect(self.screen, pg.Color("black"), (10, 10, 100, 10), 1)

        if self.mode == "game over":
            text = font.render("Вы проиграли", True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)

        pg.display.flip()


if __name__ == "__main__":
    game = Game()
