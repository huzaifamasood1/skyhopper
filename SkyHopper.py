import pygame
from pygame.locals import *
import random

# Initialize pygame
pygame.init()

# Initialize mixer for sound effects
pygame.mixer.init()

# Clock and FPS
clock = pygame.time.Clock()
fps = 60

# Screen dimensions
screen_width = 600
screen_height = 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Define colours
WHITE = (255, 255, 255)

# Define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Game variables
ground_scroll = 0
scroll_speed = 4
pipe_gap = 275
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
flying = False

# Load images
bg = pygame.image.load('bg.png')  # Default background
dark_bg = pygame.image.load('dark_bg.jpg')  # Dark background
current_bg = bg  # Current background being displayed
ground_img = pygame.image.load('ground.png')
bird_img = pygame.image.load('bird.png')
pipe_img = pygame.image.load('pipes.png')
bomb_img = pygame.image.load('bomb.png')  # Bomb image
star_img = pygame.image.load('star.png')  # Star image

# Load sounds
flap_sound = pygame.mixer.Sound('flap.wav')  # Flap sound
score_sound = pygame.mixer.Sound('score.wav')  # Score sound
hit_sound = pygame.mixer.Sound('hit.wav')  # Hit sound
bomb_explosion_sound = pygame.mixer.Sound('explosion.wav')  # Bomb explosion sound
star_collect_sound = pygame.mixer.Sound('star.wav')  # Star collect sound

# Draw text function
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(bird_img, (50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 0

    def update(self):
        global flying
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            self.rect.y += int(self.vel)

        if pygame.mouse.get_pressed()[0] == 1:
            self.vel = -5
            flap_sound.play()  # Play flap sound when bird flaps

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.transform.scale(pipe_img, (60, 300))
        if position == 1:  # Top pipe
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(bottomleft=(x, y - pipe_gap // 2))
        else:  # Bottom pipe
            self.rect = self.image.get_rect(topleft=(x, y + pipe_gap // 2))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# PipePair class to manage top and bottom pipes as a single pair
class PipePair:
    def __init__(self, x, y):
        self.top_pipe = Pipe(x, y, 1)  # Top pipe
        self.bottom_pipe = Pipe(x, y, -1)  # Bottom pipe
        self.passed = False  # Track if the bird has passed this pair

    def update(self):
        self.top_pipe.update()
        self.bottom_pipe.update()

    def draw(self, screen):
        screen.blit(self.top_pipe.image, self.top_pipe.rect)
        screen.blit(self.bottom_pipe.image, self.bottom_pipe.rect)

# Bomb class
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(bomb_img, (40, 40))  # Load and scale bomb image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed  # Move bomb to the left
        if self.rect.right < 0:  # Remove bomb if off-screen
            self.kill()

# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(star_img, (30, 30))  # Load and scale star image
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= scroll_speed  # Move star to the left
        if self.rect.right < 0:  # Remove star if off-screen
            self.kill()

# Groups
bird_group = pygame.sprite.Group()
pipe_pairs = []  # List to store pipe pairs
bomb_group = pygame.sprite.Group()
star_group = pygame.sprite.Group()
flappy = Bird(screen_width // 2, screen_height // 2)
bird_group.add(flappy)

# Reset game
def reset_game():
    global flying, score, pass_pipe
    pipe_pairs.clear()
    bomb_group.empty()
    star_group.empty()
    flappy.rect.center = (screen_width // 2, screen_height // 2)
    flappy.vel = 0
    flying = False
    score = 0
    pass_pipe = False

# Main loop
running = True
while running:
    clock.tick(fps)
    screen.blit(current_bg, (0, 0))  # Draw current background

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if not flying:
                flying = True

    # Update and draw sprites
    bird_group.update()
    bird_group.draw(screen)
    for pipe_pair in pipe_pairs:
        pipe_pair.update()
        pipe_pair.draw(screen)
    bomb_group.update()
    bomb_group.draw(screen)
    star_group.update()
    star_group.draw(screen)
    screen.blit(ground_img, (ground_scroll, screen_height - 70))

    # Collision detection
    for pipe_pair in pipe_pairs:
        if flappy.rect.colliderect(pipe_pair.top_pipe.rect) or flappy.rect.colliderect(pipe_pair.bottom_pipe.rect) or flappy.rect.top < 0:
            hit_sound.play()  # Play hit sound
            reset_game()  # Reset the game

    # Check for collisions with bombs
    for bomb in bomb_group:
        if bomb.rect.colliderect(flappy.rect):
            bomb_explosion_sound.play()  # Play explosion sound
            reset_game()  # Reset the game

    # Check for collisions with stars
    for star in star_group:
        if star.rect.colliderect(flappy.rect):
            star_collect_sound.play()  # Play star collect sound
            score += 3  # Increase score by 3
            star.kill()  # Remove star

    # Check for passing pipes
    for pipe_pair in pipe_pairs:
        if not pipe_pair.passed and flappy.rect.left > pipe_pair.top_pipe.rect.right:
            pipe_pair.passed = True
            score += 1  # Increase score by 1
            score_sound.play()  # Play score sound

    # Remove off-screen pipe pairs
    pipe_pairs = [pair for pair in pipe_pairs if pair.top_pipe.rect.right > 0]

    # Change background when score reaches 10
    if score >= 10:
        current_bg = dark_bg

    # Pipe spawning
    time_now = pygame.time.get_ticks()
    if time_now - last_pipe > pipe_frequency:
        pipe_height = random.randint(-100, 100)
        pipe_pair = PipePair(screen_width, screen_height // 2 + pipe_height)
        pipe_pairs.append(pipe_pair)

        # Spawn bombs and stars in the gap between pipes
        gap_top = screen_height // 2 + pipe_height - pipe_gap // 2
        gap_bottom = screen_height // 2 + pipe_height + pipe_gap // 2

        # Randomly decide to spawn a bomb or star
        if random.randint(0, 1) == 0:
            # Spawn a bomb
            bomb_y = random.randint(gap_top + 40, gap_bottom - 40)  # Random Y position in the gap
            bomb = Bomb(screen_width, bomb_y)
            bomb_group.add(bomb)
        else:
            # Spawn a star
            star_y = random.randint(gap_top + 40, gap_bottom - 40)  # Random Y position in the gap
            star = Star(screen_width, star_y)
            star_group.add(star)

        last_pipe = time_now

    # Draw score
    draw_text(str(score), font, WHITE, screen_width // 2, 20)

    pygame.display.update()

pygame.quit()