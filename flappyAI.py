import pygame, sys
from random import randint
from pygame.constants import DOUBLEBUF, HWSURFACE
import os
from pygame.display import flip
from pygame.transform import get_smoothscale_backend
import neat

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

        if bird_mask.overlap(bottom_mask, bottom_offset) or bird_mask.overlap(top_mask,top_offset):
            return True
        elif bird.rect.top <= -100 or bird.rect.bottom >= 900:
            return True
        return False

def draw_floor():
    global floor_x_pos
    screen.blit(floor_surf, (floor_x_pos, 900))
    screen.blit(floor_surf, (floor_x_pos + 576, 900))
    floor_x_pos -= 10
    if floor_x_pos <= -576:
            floor_x_pos = 0

def display_info(score, gen, birds):
    # score
    score_label = game_font.render("Score: " + str(score),1,(255,255,255))
    screen.blit(score_label, (576 - score_label.get_width() - 15, 10))

    # generations
    score_label = game_font.render("Gen: " + str(gen-1),1,(255,255,255))
    screen.blit(score_label, (10, 10))

    # alive
    score_label = game_font.render("Alive: " + str(len(birds)),1,(255,255,255))
    screen.blit(score_label, (10, 50))

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
gen = 0

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
death_sound.set_volume(0.2)
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
score_sound.set_volume(0.2)

def eval_genomes(genomes, config):
    global gen, score
    nets = []
    ge = []
    birds = []
    pipe_list = [Pipe(700), Pipe(1300)]
    gen += 1
    score = 0

    clock = pygame.time.Clock()

    for _, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird())
        ge.append(genome)

    while len(birds) > 0:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(bg_surface, (0, 0))

        if game_active:
            pipe_ind = 0
            if len(birds) > 0:
                if len(pipe_list) > 1 and birds[0].rect.x > pipe_list[0].top_rect.x + pipe_list[0].top_pipe.get_width():
                    pipe_ind = 1

            for x, bird in enumerate(birds):
                ge[x].fitness += 0.01
                output = nets[x].activate((bird.rect.y, abs(bird.rect.y - pipe_list[pipe_ind].top_rect.bottom), abs(bird.rect.y - pipe_list[pipe_ind].bot_rect.top)))
                if output[0] > 0.5:
                    bird.jump()

            for pipe in pipe_list:
                for x, bird in enumerate(birds):
                    if pipe.collide(bird):
                        ge[x].fitness -= 1
                        nets.pop(x)
                        ge.pop(x)
                        birds.pop(x)
                        death_sound.play()

            if delete_pipes(pipe_list):
                score += 1
                score_sound.play()
                for g in ge:
                    g.fitness += 1

            for pipe in pipe_list:
                pipe.draw_pipes()
                pipe.move_pipes()

        for bird in birds:
            # draw lines from bird to pipe
            try:
                pygame.draw.line(screen, (255,0,0), (bird.rect.x+bird.image.get_width()/2, bird.rect.y + bird.image.get_height()/2), (pipe_list[pipe_ind].top_rect.x + pipe_list[pipe_ind].top_pipe.get_width()/2, pipe_list[pipe_ind].top_rect.bottom), 5)
                pygame.draw.line(screen, (255,0,0), (bird.rect.x+bird.image.get_width()/2, bird.rect.y + bird.image.get_height()/2), (pipe_list[pipe_ind].bot_rect.x + pipe_list[pipe_ind].bottom_pipe.get_width()/2, pipe_list[pipe_ind].bot_rect.top), 5)
            except:
                pass

        display_info(score, gen, birds)

        for bird in birds:
            screen.blit(bird.image, bird.rect)
            bird.update()

        draw_floor()

        pygame.display.update()
        

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes ,50)

    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
