import scorescreen
import welcomescreen
import sounds
import maps
import gameobjects
import images
import boxmodels
import ai
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk

import os

#----- Framework -----#

# -- Initialise the display
pygame.init()
pygame.display.set_mode()


# -- Import from the ctf framework

import welcomescreen
import scorescreen

#---- Welcome Screen ----#

# -- Show welcome screen and save the start parameters after
start_param = welcomescreen.show_welcome_screen()
is_multiplayer = start_param[0]
is_liu_vs = start_param[2]

if is_liu_vs:
    images.tanks = images.liu_vs_tanks

# -- Define the current level
current_map = start_param[1]

#---- Initialisation ----#

#-- Constants
FRAMERATE = 50

# -- Initialise the clock
clock = pygame.time.Clock()

# -- Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0, 0.0)

# -- List of all game objects
game_objects_list = []
tanks_list = []
ai_list = []

# -- Resize the screen to the size of the current level
screen = pygame.display.set_mode(current_map.rect().size)

# -- Generate the background
background = pygame.Surface(screen.get_size()).convert_alpha()

# -- Copy the grass tile all over the level area
for x in range(0, current_map.width):
    for y in range(0,  current_map.height):
        # The call to the function "blit" will copy the image
        # contained in "images.grass" into the "background"
        # image at the coordinates given as the second argument
        background.blit(
            images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))

# -- Generate walls for the map
border_body = pymunk.Body(body_type=pymunk.Body.STATIC)
border_lines = [
    pymunk.Segment(
        border_body, (0, 0), (current_map.width, 0), 0
    ),
    pymunk.Segment(
        border_body, (0, 0), (0, current_map.height), 0
    ),
    pymunk.Segment(
        border_body, (0, current_map.height), (current_map.width,
                                               current_map.height), 0
    ),
    pymunk.Segment(
        border_body, (current_map.width, current_map.height), (current_map.width, 0), 0)
]


# Add each segment individually to the space
space.add(border_body)
for line in border_lines:
    space.add(line)


# -- Create the boxes
for x in range(0, current_map.width):
    for y in range(0,  current_map.height):
        # Get the type of boxes
        box_type = current_map.boxAt(x, y)
        box_model = boxmodels.get_model(box_type)
        # If the box model is non null, create a box
        if(box_model != None):
            box = gameobjects.Box(x + 0.5, y + 0.5, box_model, space)
            game_objects_list.append(box)


# -- Create the tanks
# Loop over the starting poistion
for i in range(0, len(current_map.start_positions)):
    # Get the starting position of the tank "i"
    pos = current_map.start_positions[i]

    # Add base at starting position
    base = gameobjects.GameVisibleObject(pos[0], pos[1], images.bases[i])

    # Add the base to the list of objects to display
    game_objects_list.append(base)

    # Create the tank, images.tanks contains the image representing the tank
    tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)

    # Create an AI-instance for all the ai tanks
    if (i != 0 and not is_multiplayer) or (is_multiplayer and (i != 0 and i != 1)):
        ai_tank = ai.Ai(tank, game_objects_list,
                        tanks_list, space, current_map)
        tank.ai = ai_tank
        ai_list.append(ai_tank)

    # Add the tank to the list of objects to display
    game_objects_list.append(tank)

    # Add the tank to the list of tanks
    tanks_list.append(tank)


# -- Create the flag
flag = gameobjects.Flag(
    current_map.flag_position[0], current_map.flag_position[1])
game_objects_list.append(flag)

# -- Play the background music
sounds.play_music("background_1.wav")


#----- Collision detection -----#


def collision_bullet_any(arb, space, data):
    """Removes the bullet."""
    bullet = arb.shapes[0].parent
    game_objects_list.remove(bullet)
    space.remove(arb.shapes[0], arb.shapes[0].body)
    return True


# 1 : Bullet, 0: any
handler_bullet_any = space.add_collision_handler(1, 0)
handler_bullet_any.pre_solve = collision_bullet_any


def collision_bullet_tank(arb, space, data):
    """
    Removes the bullet and the tank from the game aswell as
    respawns the tank.
    """
    pygame.mixer.Sound.play(sounds.tankboom_sound)

    bullet = arb.shapes[0].parent
    tank = arb.shapes[1].parent

    if bullet in game_objects_list:
        game_objects_list.remove(bullet)
        space.remove(arb.shapes[0], arb.shapes[0].body)

    if tank.protection <= 0:
        tank.hp -= 50
        if tank.hp <= 0:
            # Show Explosion
            game_objects_list.append(
                gameobjects.Explosion(
                    bullet.body.position.x, bullet.body.position.y)
            )

            if tank.flag != None:
                bullet.tank.score += 10
            else:
                bullet.tank.score += 5

            tank.reset_position()
            #  If the tank has an AI, reset AI
            if tank.ai != None:
                ai_list.remove(tank.ai)
                ai_tank = ai.Ai(
                    tank, game_objects_list, tanks_list, space, current_map
                )
                tank.ai = ai_tank
                ai_list.append(ai_tank)
    return True


# 1: Bullet, 2: Tank
handler_bullet_tank = space.add_collision_handler(1, 2)
handler_bullet_tank.pre_solve = collision_bullet_tank


def collision_bullet_box(arb, space, data):
    """Removes the bullet and the woodenbox from the game"""
    bullet = arb.shapes[0].parent
    box = arb.shapes[1].parent

    if bullet in game_objects_list:
        game_objects_list.remove(bullet)
        space.remove(arb.shapes[0], arb.shapes[0].body)

    if box.boxmodel == boxmodels.woodbox:
        # Show Explosion
        game_objects_list.append(
            gameobjects.Explosion(bullet.body.position.x,
                                  bullet.body.position.y)
        )

        bullet.tank.score += 1

        game_objects_list.remove(box)
        space.remove(arb.shapes[1], arb.shapes[1].body)
        pygame.mixer.Sound.play(sounds.boxboom_sound)
    return True


# 1: Bullet, 3: Box
handler_bullet_box = space.add_collision_handler(1, 3)
handler_bullet_box.pre_solve = collision_bullet_box


def collision_bullet_bullet(arb, space, data):
    """Removes the two bullets when colliding"""
    bullet_1 = arb.shapes[0].parent
    bullet_2 = arb.shapes[1].parent

    game_objects_list.remove(bullet_1)
    game_objects_list.remove(bullet_2)
    space.remove(arb.shapes[0], arb.shapes[0].body)
    space.remove(arb.shapes[1], arb.shapes[1].body)
    return True


# 1: Bullet, 1: Bullet
handler_bullet_bullet = space.add_collision_handler(1, 1)
handler_bullet_bullet.pre_solve = collision_bullet_bullet


def tank_controller(tank, event, key_up, key_down, key_left, key_right, key_shoot):
    """ Controlls the tank given event and keys. """
    if event.type == KEYDOWN:
        if event.key == key_up:
            tank.accelerate()
        if event.key == key_down:
            tank.decelerate()
        if event.key == key_left:
            tank.turn_left()
        if event.key == key_right:
            tank.turn_right()
        if event.key == key_shoot:
            # Restrict shooting to one per second
            if tank.cooldown == 0:
                game_objects_list.append(tank.shoot(space))
                tank.cooldown = FRAMERATE

    if event.type == KEYUP:
        if event.key == key_up or event.key == key_down:
            tank.stop_moving()
        if event.key == key_left or event.key == key_right:
            tank.stop_turning()


#----- Main Loop -----#

# -- Control whether the game is running
running = True
skip_update = 0

while running:

    # -- Handle the events

    for event in pygame.event.get():
        # Check if we receive a QUIT event (for instance, if the user press the
        # close button of the window) or if the user press the escape key.
        if event.type == QUIT or (event.type == KEYDOWN
                                  and event.key == K_ESCAPE):
            running = False

        # Keeps track of keyboard commands for player 1.
        tank_controller(tanks_list[0], event, K_w, K_s, K_a, K_d, K_SPACE)

        # If hotseat multiplayer keep track of keyboard commands for player 2.
        if is_multiplayer:
            tank_controller(
                tanks_list[1], event, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RETURN
            )

    # -- Update physics
    if skip_update == 0:
        # Loop over all the game objects and update their speed in function of their
        # acceleration
        for obj in game_objects_list:
            obj.update()
        skip_update = 2
    else:
        skip_update -= 1

    #   Check collisions and update the objects position
    space.step(1 / FRAMERATE)

    #   Update object that depends on an other object position
    for obj in game_objects_list:
        obj.post_update()
        if isinstance(obj, gameobjects.Explosion):
            if obj.duration_timer <= 0:
                game_objects_list.remove(obj)

    #   Update ai and decide on every tick
    for ai_tank in ai_list:
        ai_tank.decide()

    #   Update Tanks on every tick and quit the game if the tank has won
    for tank in tanks_list:
        tank.try_grab_flag(flag)
        if tank.has_won():
            pygame.mixer.Sound.play(sounds.win_sound)
            scorescreen.show_score_screen(screen, tanks_list, is_liu_vs)

            # Creates a list for AI
            ai_list = []

            # Reset Tank and Ai
            for i in range(len(tanks_list)):
                tank = tanks_list[i]
                tank.reset_position()
                # Check if tank is ai (Player 1 and 2 in multiplayer)
                if (not is_multiplayer and i != 0) \
                        or (is_multiplayer and i != 1 or i != 0):

                    ai_tank = ai.Ai(
                        tank, game_objects_list, tanks_list, space, current_map
                    )
                    tank.ai = ai_tank
                    ai_list.append(ai_tank)

            # Respawn the flag
            game_objects_list.remove(flag)
            flag = gameobjects.Flag(
                current_map.flag_position[0], current_map.flag_position[1]
            )
            game_objects_list.append(flag)

    # -- Update Display

    # Display the background on the screen
    screen.blit(background, (0, 0))

    # Update the display of the game objects on the screen
    for obj in game_objects_list:
        obj.update_screen(screen)

    # -- Black with hole - Fog of war, Only in singleplayer
    if not is_multiplayer:
        # If Player has flag create a black hole.
        if tanks_list[0].flag != None:
            blackout = pygame.Surface(screen.get_size()).convert_alpha()
            blackout.fill([0, 0, 0, 255])
            pos = tanks_list[0].screen_position()
            pygame.draw.circle(blackout, (0, 0, 0, 0), pos, 100)
            screen.blit(blackout, (0, 0))

    #   Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()

    #   Control the game framerate
    clock.tick(FRAMERATE)
