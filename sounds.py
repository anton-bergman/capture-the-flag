import pygame
import os

#--Initialise mixer
pygame.mixer.init()

#--Reference to current directory.
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_sound(file):
    """ Load a sound from the data directory. """
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
    except pygame.error:
        raise SystemExit('Could not load sound "%s" %s'%(file, pygame.get_error()))
    return sound


def play_music(file):
    """ Plays a given music """
    file = os.path.join(main_dir, 'data', file)
    try:
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.load(file)
        pygame.mixer.music.play(-1)
    except pygame.error:
        raise SystemExit('Could not load music "%s" %s'%(file, pygame.get_error()))


#--Loads sounds and sets volume.
shoot_sound = load_sound("shoot.flac")
shoot_sound.set_volume(0.05)
 
boxboom_sound = load_sound("boxboom.wav")
boxboom_sound.set_volume(0.15)

tankboom_sound = load_sound("tankboom.wav")
tankboom_sound.set_volume(0.15)

pickup_sound = load_sound("pick_up.wav")
pickup_sound.set_volume(0.15)

win_sound = load_sound("win.wav")
win_sound.set_volume(0.15)
    
surprise_sound = load_sound("surprise.wav")
surprise_sound.set_volume(0.15)