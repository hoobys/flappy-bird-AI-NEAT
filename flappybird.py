import pygame, sys
from random import randint
from pygame.constants import DOUBLEBUF, HWSURFACE
import os
from pygame.display import flip
from pygame.transform import get_smoothscale_backend

class Bird:
    def __init__(self):
        self.index = 0
        self.image = bird_frames[self.index]
        self.rect = self.image.get_rect(center = (100, 512))
        self.movement = 0
        self.gravity = 1

    def rotate_bird(self):
        self.image = pygame.transform.rotozoom(self.image, -self.movement * 4  , 1)

    def bird_animation(self):
        if self.index < 2:
                self.index += 0.2
        else:
                self.index = 0
        self.image = bird_frames[int(self.index)]
        self.rect = self.image.get_rect(center = (100, self.rect.centery))

    def jump(self):
        self.movement = 0
        self.movement = -20
        flap_sound.play()

    def move(self):
        self.movement += self.gravity
        self.rect.y += self.movement

    def update(self):
        self.bird_animation()
        self.rotate_bird()
        self.move()

class Pipe():
    def __init__(self, x_pos):
        self.top_pipe = pygame.transform.flip(pipe_surf, False, True)
        self.bottom_pipe = pipe_surf
        self.random_xpos = randint(400, 800)
        self.top_rect = self.top_pipe.get_rect(midbottom = (x_pos, self.random_xpos - 300))
        self.bot_rect = self.bottom_pipe.get_rect(midtop = (x_pos, self.random_xpos))

    def draw_pipes(self):
            screen.blit(self.top_pipe, self.top_rect)
            screen.blit(self.bottom_pipe, self.bot_rect)
    
    def move_pipes(self):
        self.top_rect.x -= 10
        self.bot_rect.x -= 10

    def collide(self, bird):
        bird_mask = pygame.mask.from_surface(bird.image)
        top_mask = pygame.mask.from_surface(self.top_pipe)
        bottom_mask = pygame.mask.from_surface(self.bottom_pipe)
        top_offset = (self.top_rect.x - bird.rect.x, self.top_rect.y - round(bird.rect.y))
        bottom_offset = (self.bot_rect.x - bird.rect.x, self.bot_rect.y - round(bird.rect.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True
        elif bird.rect.top <= -100 or bird.rect.bottom >= 900:
            return True
        return False

def draw_floor(game_active):
    global floor_x_pos
    screen.blit(floor_surf, (floor_x_pos, 900))
    screen.blit(floor_surf, (floor_x_pos + 576, 900))
    if game_active: floor_x_pos -= 10
    if floor_x_pos <= -576:
            floor_x_pos = 0

def score_display(game_state):
    if game_state == 'main_game':
        score_surf = game_font.render(str(int(score)), False, 'White')
        score_rect = score_surf.get_rect(center = (288, 100))
        screen.blit(score_surf, score_rect)
    if game_state == 'game_over':
        high_score_surf = game_font.render(f'High score: {int(high_score)}', False, 'White')
        high_score_rect = high_score_surf.get_rect(center = (288, 850))
        screen.blit(high_score_surf, high_score_rect)

def update_score(score, high_score):
    if score > high_score:
	    high_score = score
    return high_score

def delete_pipes(pipes):
    for pipe in pipes:
        if pipe.top_rect.x <= -100:
            pipes.remove(pipe)
            pipes.append(Pipe(1100))
            return True


pygame.init()
screen = pygame.display.set_mode((576, 1024), pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.TTF',40)

game_active = True
score = 0
high_score = 0

bg_surface = pygame.image.load('assets/background-day.png').convert()
bg_surface = pygame.transform.scale2x(bg_surface)

floor_surf = pygame.image.load('assets/base.png').convert()
floor_surf = pygame.transform.scale2x(floor_surf)
floor_x_pos = 0

bird_downflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-downflap.png').convert_alpha())
bird_midflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-midflap.png').convert_alpha())
bird_upflap = pygame.transform.scale2x(pygame.image.load('assets/bluebird-upflap.png').convert_alpha())
bird_frames = [bird_downflap, bird_midflap, bird_upflap]


pipe_surf = pygame.image.load('assets/pipe-green.png').convert()
pipe_surf = pygame.transform.scale2x(pipe_surf)

game_over_surf = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())
game_over_rect = game_over_surf.get_rect(center = (288, 512))

flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
flap_sound.set_volume(0.2)
death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')


bird = Bird()
pipe_list = [Pipe(700), Pipe(1300)]

clock = pygame.time.Clock()

while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird.jump()
            if event.key == pygame.K_SPACE and game_active == False:
                game_active = True
                pipe_list = [Pipe(700), Pipe(1300)]
                bird.movement = -10
                bird.rect.center = (100, 512)
                score = 0



    screen.blit(bg_surface, (0, 0))

    if game_active:
        for pipe in pipe_list:
            if pipe.collide(bird):
                game_active = False
                death_sound.play()

        if delete_pipes(pipe_list):
            score += 1
            score_sound.play()

        for pipe in pipe_list:
            pipe.draw_pipes()
            pipe.move_pipes()

        bird.update()
        score_display('main_game')


    else:
        if bird.rect.y < 830:
            bird.update()
        for pipe in pipe_list:
            pipe.draw_pipes()
        screen.blit(game_over_surf, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')


    draw_floor(game_active)
    screen.blit(bird.image, bird.rect)


    pygame.display.update()