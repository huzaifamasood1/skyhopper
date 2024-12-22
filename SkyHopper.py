import pygame
from pygame.locals import *
import random

# Initialize pygame
pygame.init()

# Initialize mixer
pygame.mixer.init()

# Clock and FPS
clock = pygame.time.Clock()
fps = 60

# Screen dimensions
screen_width = 600
screen_height = 750

# Set up the display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Define colors
black = (0, 0, 0)  # black color for the score
white = (255, 255, 255)

# Define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 250
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

# Load images
bg = pygame.image.load('bg.png')
dark_bg = pygame.image.load('dark_bg.jpg')
current_bg = bg
ground_img = pygame.image.load('ground.png')
bird_img = pygame.image.load('bird.png')
bomb_img = pygame.image.load('bomb.png')
explosion_img = pygame.image.load('explosion.png')
pipe_img = pygame.image.load('pipes.png')
clouds_img = pygame.image.load('clouds.png')
star_img = pygame.image.load('star.png')

# Resize the clouds image
clouds_img = pygame.transform.scale(clouds_img, (screen_width, 150))

# Load sounds
flap_sound = pygame.mixer.Sound('flap.wav')
score_sound = pygame.mixer.Sound('score.wav')
hit_sound = pygame.mixer.Sound('hit.wav')
bomb_explosion_sound = pygame.mixer.Sound('explosion.wav')
star_collect_sound = pygame.mixer.Sound('star.wav')

# Functions
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    bomb_group.empty()
    star_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    return 0

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bird_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            self.rect.y += int(self.vel)

        if not game_over:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
                flap_sound.play()
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        # Rotate bird
        self.image = pygame.transform.rotate(pygame.transform.scale(bird_img, (50, 50)), self.vel * -2)

# Bomb class
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bomb_img, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.exploding = False
        self.explosion_counter = 0

    def update(self):
        if self.exploding:
            self.image = pygame.transform.scale(explosion_img, (50, 50))
            self.explosion_counter += 1
            if self.explosion_counter > 10:
                self.kill()
        else:
            self.rect.x -= scroll_speed
            if self.rect.right < 0:
                self.kill()

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pipe_img, (60, 300))
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        else:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(star_img, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Sprite groups
bird_group = pygame.sprite.Group()
bomb_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
star_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Main game loop
run = True
while run:
    clock.tick(fps)

    if score >= 10:
        current_bg = dark_bg
    else:
        current_bg = bg

    screen.blit(current_bg, (0, 0))
    screen.blit(clouds_img, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    pipe_group.update()
    bomb_group.draw(screen)
    bomb_group.update()
    star_group.draw(screen)
    star_group.update()

    screen.blit(ground_img, (ground_scroll, screen_height - 70))

    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and \
                bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and not pass_pipe:
            pass_pipe = True
        if pass_pipe and bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
            score += 1
            score_sound.play()
            pass_pipe = False

    draw_text(str(score), font, black, int(screen_width / 2), 20)

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
        hit_sound.play()
        game_over = True

    for bomb in bomb_group:
        if bomb.rect.colliderect(flappy.rect):
            bomb_explosion_sound.play()
            bomb.exploding = True
            game_over = True

    for star in star_group:
        if flappy.rect.colliderect(star.rect):
            star_collect_sound.play()
            score += 3
            star.kill()

    if flappy.rect.bottom >= screen_height - 70:
        hit_sound.play()
        game_over = True
        flying = False

    if not game_over and flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)

            gap_top = int(screen_height / 2) + pipe_height - pipe_gap // 2
            gap_bottom = int(screen_height / 2) + pipe_height + pipe_gap // 2

            place_star = random.randint(0, 1)
            if place_star:
                star_y = random.randint(gap_top + 40, gap_bottom - 40)
                conflict = any(abs(star_y - bomb.rect.center[1]) < 40 for bomb in bomb_group)
                if not conflict:
                    star = Star(screen_width, star_y)
                    star_group.add(star)
            else:
                bomb_y = random.randint(gap_top + 40, gap_bottom - 40)
                conflict = any(abs(bomb_y - star.rect.center[1]) < 40 for star in star_group)
                if not conflict:
                    bomb = Bomb(screen_width, bomb_y)
                    bomb_group.add(bomb)

            last_pipe = time_now

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not flying and not game_over:
                flying = True
            if game_over:
                game_over = False
                score = reset_game()

    pygame.display.update()

pygame.quit()
