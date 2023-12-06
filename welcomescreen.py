
import pygame
from pygame.locals import *
from pygame.color import *
import os

import boxmodels
import images
import maps
import sounds

FRAMERATE = 50

def generate_map_preview(map):
    """ Generates a small preview of the map for the welcome-screen. """
    
    size = round(50/map.height)
    #-- Generate the background
    preview = pygame.Surface((map.width * size, map.height * size)).convert_alpha()

    #-- Create the boxes
    for x in range(0, map.width):
        for y in range(0,  map.height):
            # Get the type of boxes
            box_type  = map.boxAt(x, y)
            box_model = boxmodels.get_model(box_type)

            if box_model != None:
                preview.blit(
                    pygame.transform.scale(box_model.sprite, (size, size)),
                    (x * size, y*size)
                    )
            else:
                preview.blit(
                    pygame.transform.scale(images.grass, (size, size)),
                    (x * size, y*size)
                    )
    return preview


def show_welcome_screen():
    """ Shows the welcome screen when you start the game. """

    #-- Variables
    running = True
    is_multiplayer = False
    is_liu_vs = False
    maps_list = maps.load_all_maps()
    current_map         = maps_list[0]
    current_map_index = 0
    
    #-- Resize the screen to given size
    screen = pygame.display.set_mode((360, 360))

    #-- Initialise the clock
    clock = pygame.time.Clock()

    #-- Imports the font
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    font_file = os.path.join(main_dir, 'data', "Goldman-Regular.ttf")

    #-- Creates a pygame font
    header_font = pygame.font.Font(font_file, 16)
    main_font = pygame.font.Font(font_file, 14)

    #-- Creates text
    map_header = header_font.render("Map: ", True, (0, 0, 0))
    gamemode_header = header_font.render("Mode: ", True, (0, 0, 0))


    #-- Creates a preview map
    preview = generate_map_preview(current_map)

    #-- Main Loop for welcome screen
    while running:
        for event in pygame.event.get():
            # Check if we receive a QUIT event 
            # or if the user press the escape key.
            if event.type == QUIT \
               or (event.type == KEYDOWN and event.key == K_ESCAPE):
                exit()

            if (event.type == KEYDOWN and event.key == K_RETURN):
                running = False
                
            if event.type == KEYDOWN:
                if event.key == K_g:
                    if is_multiplayer:
                        is_multiplayer = False
                    else:
                        is_multiplayer = True
                
                if event.key == K_m:
                    current_map_index += 1
                    if current_map_index > len(maps_list)-1:
                        current_map_index = 0
                    current_map = maps_list[current_map_index]
                    preview = generate_map_preview(current_map)
                
                if event.key == K_l:
                    if is_liu_vs:
                        is_liu_vs = False
                    else:
                        is_liu_vs = True
                        pygame.mixer.Sound.play(sounds.surprise_sound)
                        

        # Checks if game is set to Multiplayer or Singleplayer
        if is_multiplayer:
            gamemode_value = main_font.render("Multiplayer", True, (0, 0, 0))
        else:
            gamemode_value = main_font.render("Singleplayer", True, (0, 0, 0))
        
        map_value = main_font .render(current_map.name, True, (0, 0, 0))

        #-- Update Display
        
        # Display the background on the screen
        if is_liu_vs:
            screen.blit(images.liu_vs_background, (0, 0))
        else:
            screen.blit(images.welcome_background, (0, 0))

        screen.blit(map_header, (100, 267))

        screen.blit(gamemode_header, (100,211))

        screen.blit(gamemode_value, (160, 213))

        screen.blit(map_value, (160, 270))

        screen.blit(preview, ((180-preview.get_width()/2) , 300))

        #   Redisplay the entire screen (see double buffer technique)
        pygame.display.flip()

        #   Control the game framerate
        clock.tick(FRAMERATE)
    
    return [is_multiplayer, current_map, is_liu_vs]
        
