import pygame
import os

# --Reference to current directory.
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    """ Load an image from the data directory. """
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' %
                         (file, pygame.get_error()))
    return surface.convert_alpha()


TILE_SIZE = 40  # Define the default size of tiles

explosion = pygame.image.load('data/explosion.png')  # Image of an explosion


grass = pygame.image.load('data/grass.png')  # Image of a grass tile

rockbox = pygame.image.load('data/rockbox.png')  # Image of a rock box (wall)

metalbox = pygame.image.load('data/metalbox.png')  # Image of a metal box

woodbox = pygame.image.load('data/woodbox.png')  # Image of a wood box

flag = pygame.image.load('data/flag.png')  # Image of flag

bullet = pygame.image.load('data/bullet.png')
bullet = pygame.transform.scale(bullet, (10, 10))
bullet = pygame.transform.rotate(bullet, -90)

# List of image of tanks of different colors
tanks = [
    pygame.image.load('data/tank_orange.png'),
    pygame.image.load('data/tank_blue.png'),
    pygame.image.load('data/tank_white.png'),
    pygame.image.load('data/tank_yellow.png'),
    pygame.image.load('data/tank_red.png'),
    pygame.image.load('data/tank_gray.png')]

# List of image of bases corresponding to the color of each tank
bases = [
    pygame.image.load('data/base_orange.png'),
    pygame.image.load('data/base_blue.png'),
    pygame.image.load('data/base_white.png'),
    pygame.image.load('data/base_yellow.png'),
    pygame.image.load('data/base_red.png'),
    pygame.image.load('data/base_gray.png')]

liu_vs_tanks = [
    pygame.transform.scale(pygame.image.load('data/liu.jpg'), (20, 20)),
    pygame.transform.scale(pygame.image.load('data/kth.png'), (20, 20)),
    pygame.transform.scale(pygame.image.load('data/chalmers.png'), (20, 20)),
    pygame.transform.scale(pygame.image.load('data/skovde.png'), (20, 20)),
    pygame.transform.scale(pygame.image.load('data/uppsala.jpg'), (20, 20)),
    pygame.transform.scale(pygame.image.load('data/lund.png'), (20, 20))
]

# Image of welcome screen background
welcome_background = pygame.image.load('data/welcome_background.png')

# Image of welcome screen background, easteregg
liu_vs_background = pygame.image.load('data/liu_vs_background.jpg')

# Image of score screen background
score_background = pygame.image.load('data/score_background.jpg')
