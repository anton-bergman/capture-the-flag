import pygame
import os
import images
import ctf

tank_colours = ["Orange", "Blue", "White", "Yellow", "Red", "Gray"]
tank_uni = ["LiU", "KTH", "Chalmers", "Skövde", "Uppsala", "Lund"]

# -- Imports the font
main_dir = os.path.split(os.path.abspath(__file__))[0]
font_file = os.path.join(main_dir, 'data', "Goldman-Regular.ttf")

# -- Creates a pygame font
header_font = pygame.font.Font(font_file, 16)
main_font = pygame.font.Font(font_file, 14)

#header_font = pygame.font.Font(None, 16)
#main_font = pygame.font.Font(None, 14)


def show_score_screen(screen, tanks_list, is_liu_vs):
    """ Shows the score screen when a player gains a point. """

    if is_liu_vs:
        tank_names = tank_uni
    else:
        tank_names = tank_colours

    initial_size = screen.get_size()
    screen = pygame.display.set_mode((360, 360))

    # Create white background for score screen
    score_surface = pygame.Surface(screen.get_size()).convert_alpha()
    score_surface.fill([255, 255, 255, 255])
    screen.blit(score_surface, (0, 0))
    screen.blit(images.score_background, (0, 0))

    for i in range(len(tanks_list)):
        player_text = main_font.render(
            "Player " + tank_names[i] + ": ", True, (0, 0, 0)
        )
        score_text = main_font.render(
            str(tanks_list[i].score), True, (0, 0, 0)
        )
        screen.blit(player_text, (110, 120 + 30*i))
        screen.blit(score_text, (230, 120 + 30*i))

    # Redisplay the screen and then pause for 4 seconds
    pygame.display.flip()
    pygame.time.delay(4000)

    screen = pygame.display.set_mode(initial_size)