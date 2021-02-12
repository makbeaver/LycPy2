import pygame
import random
import time
from os import path

img_dir = path.join(path.dirname(__file__), 'data/img')
snd_dir = path.join(path.dirname(__file__), 'data/snd')
explode_dir = path.join(path.dirname(__file__), 'data/explodes')

background = None

# Экран

# WIDTH = 1200
# HEIGHT = 500
FPS = 30
# Сколько захватчиков
ufos = 20

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Создаем игру и окно
pygame.init()
WIDTH = pygame.display.Info().current_w
HEIGHT = pygame.display.Info().current_h
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN | pygame.DOUBLEBUF)
pygame.display.set_caption("[Название игры]")
pygame.display.set_icon(pygame.image.load(path.join(img_dir, "main.png")))
clock = pygame.time.Clock()

# font_name = pygame.font.match_font('Sergoe')
font_platypus = pygame.font.Font(
    path.join(path.dirname(__file__), 'data/game_font.ttf'), 90)
font_text = pygame.font.Font(path.join(path.dirname(__file__), 'data/pl_font.ttf'), 40)
font_text18 = pygame.font.Font(path.join(path.dirname(__file__), 'data/pl_font.ttf'), 18)

def draw_text(surf, font, text, x, y):
    # font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, YELLOW)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (70, 45))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centery = HEIGHT / 2
        self.rect.left = 10
        self.speedy = 0
        self.speedx = 0
        self.shield = 100

    def update(self):
        self.speedy = 0
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_UP]:
            self.speedy = -8
            self.rect.y += self.speedy
        if keystate[pygame.K_DOWN]:
            self.speedy = 8
            self.rect.y += self.speedy
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
            self.rect.x += self.speedx
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
            self.rect.x += self.speedx
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def shoot(self):
        bullet = Bullet(self.rect.right, self.rect.centery)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shot.play()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        im = random.randint(1, 13)
        self.image_orig = ufo_images[im - 1]
        self.image_orig.set_colorkey(-1)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        if im in [1, 4, 9, 10]:
            self.type = 1
        else:
            self.type = 2
        self.rect.x = WIDTH + 150
        self.speedy = random.randrange(-1, 1)
        self.dy = 1
        self.vy = 0
        self.rect.y = random.randrange(HEIGHT - self.rect.height)
        self.speedx = random.randrange(-12, -1)
        self.last_update = pygame.time.get_ticks()
        self.tick = time.time()

    def update(self):
        self.rect.x += self.speedx
        if self.type == 1:
            self.vy += self.dy
            if self.vy > 10 or self.vy < -10:
                self.dy *= -1
            self.rect.y += self.vy
            if time.time() - self.tick > 2:
                self.shoot()
                self.tick = time.time()
        else:
            self.rect.y += self.speedy

        if self.rect.x < -10 or self.rect.y < -25 or self.rect.bottom > HEIGHT + 20:
            self.rect.x = WIDTH + 150
            self.rect.y = random.randrange(HEIGHT - self.rect.height)
            self.speedx = random.randrange(-12, -1)

    def shoot(self):
        mob_shot = Mob_shot(self.rect.left, self.rect.centery)
        all_sprites.add(mob_shot)
        mob_shots.add(mob_shot)
        # shot.play()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (60, 30))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speedy = 10

    def update(self):
        self.rect.x += self.speedy
        # убить, если он заходит за правую часть экрана
        if self.rect.x > WIDTH:
            self.kill()


class Mob_shot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(mob_shot_img, (90, 20))
        # self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speedx = 30

    def update(self):
        self.rect.x -= self.speedx
        # убить, если он заходит за правую часть экрана
        if self.rect.right < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


def HP(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 70
    BAR_HEIGHT = 6
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 1)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def scrollBackground():
    background_rect1.x -= 5
    background_rect2.x -= 5
    if background_rect1.right < 0:
        background_rect1.x = WIDTH
    if background_rect2.right < 0:
        background_rect2.x = WIDTH


def start_screen():
    background_rect1.x = 0
    background_rect2.x = WIDTH + 1
    screen.blit(background1, background_rect1)
    draw_text(screen, font_platypus, "[Название ]", WIDTH / 2, HEIGHT / 4 - 80)
    draw_text(screen, font_text, f'Лучший результат {best_score}',
              WIDTH / 2, HEIGHT / 4 + 50)
    draw_text(screen, font_text, "Стрелками двигай пробелом стреляй",
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, font_text, "ESC - Выход",
              WIDTH / 2, HEIGHT / 2 + 50)

    draw_text(screen, font_text18, "Нажми любую клавишу для игры (кроме ESC)",
              WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    time.sleep(2)
    pygame.event.clear()
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


def Game_over():
    global game_over, best_score
    game_over = True
    if score > best_score:
        best_score = score


# Загрузка всей игровой графики
background1 = pygame.transform.scale(pygame.image.load(
    path.join(img_dir, "stars_background.png")).convert(), (WIDTH, HEIGHT))
background_rect1 = background1.get_rect()
background2 = pygame.transform.scale(pygame.image.load(
    path.join(img_dir, "stars_background.png")).convert(), (WIDTH, HEIGHT))
background_rect2 = background2.get_rect()
background_rect2.x = WIDTH + 1

player_img = pygame.image.load(path.join(img_dir, "main.png")).convert()
bullet_img = pygame.image.load(path.join(img_dir, "lazer.png")).convert()
mob_shot_img = pygame.image.load(path.join(img_dir, "mob_shot.gif")).convert()
# Захватчики
ufo_images = []
for i in range(1, 14):
    ufo_images.append(
        pygame.transform.scale(pygame.image.load(path.join(img_dir, 'ufo{}.png'.format(i))).convert(), (70, 50)))
# Взрывы
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(explode_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
# Звуки
shot = pygame.mixer.Sound(path.join(snd_dir, 'shot.wav'))
explode = pygame.mixer.Sound(path.join(snd_dir, 'explode.wav'))
explode_player = pygame.mixer.Sound(path.join(snd_dir, 'explode_player.wav'))

pygame.mixer.music.load(path.join(snd_dir, 'fon_music.ogg'))
pygame.mixer.music.set_volume(0.4)

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
mob_shots = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(ufos):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

score = 0
ufo = 0
best_score = 0
# Цикл игры
pygame.mixer.music.play(loops=-1)
game_over = True
start = True
image_game_over = pygame.image.load(
    path.join(img_dir, "gameover.png")).convert()
image_game_over = pygame.transform.scale(image_game_over, (WIDTH, HEIGHT))
game_over_x = - WIDTH

running = True

while running:
    if game_over:
        pygame.event.clear
        if start == False:
            while game_over_x < 0:
                clock.tick(FPS)
                game_over_x += 15
                screen.blit(image_game_over, (game_over_x, 1))
                pygame.display.update()
            time.sleep(2)
            game_over_x = - WIDTH
        start = False
        start_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        # powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(ufos):
            newmob()
        score = 0
        ufo = 0
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # проверка для закрытия окна
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Обновление
    all_sprites.update()

    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        ufo += 1
        m = Mob()
        all_sprites.add(m)
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        mobs.add(m)
        explode.play()

    # Проверка, не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(
        player, mobs, False, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 20
        explode_player.play()
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        hit.kill()
        newmob()
        if player.shield <= 0:
            Game_over()
            game_over = True
            if score > best_score:
                best_score = score

    # Проверка, попал ли выстрел моба игрока
    hits = pygame.sprite.spritecollide(
        player, mob_shots, False, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= 20
        explode_player.play()
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        hit.kill()
        if player.shield <= 0:
            game_over = True
            if score > best_score:
                best_score = score

    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background1, background_rect1)
    screen.blit(background2, background_rect2)
    scrollBackground()
    all_sprites.draw(screen)
    draw_text(
        screen, font_text18, f'Сбито захватчиков {ufo}, Счёт {str(score)}, Лучший результат {best_score}', WIDTH / 2, 10)

    HP(screen, player.rect.x, player.rect.y + 45, player.shield)
    pygame.display.flip()

pygame.quit()
