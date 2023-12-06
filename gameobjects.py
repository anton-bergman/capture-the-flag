import images
import pygame
import pymunk
import math
import sounds
import ctf

# Change this to set it in debug mode 
DEBUG = False 


def physics_to_display(x):
    """ Convert physics engine coordinates into the display coordinates. """
    return x * images.TILE_SIZE


class GameObject:
    """ Handles all of objects in the game. """

    def __init__(self, sprite):
        self.sprite         = sprite


    def update(self):
        """ Placeholder, supposed to be implemented in a subclass.
            Should update the current state (after a tick) of the object."""
        return


    def post_update(self):
        """ Should be implemented in a subclass. Make updates that depend on
            other objects than itself.""" 
        return
        

    def update_screen(self, screen):
        """ 
        Updates the visual part of the game. Should NOT need to be changed
        by a subclass.
        """
        sprite = self.sprite
        
        # Get the position of the object (pygame coordinates)
        p = self.screen_position() 
        
        # Rotate the sprite using the rotation of the object
        sprite = pygame.transform.rotate(sprite, self.screen_orientation()) 
        
        # Offsets the coordinates to the upper left corner
        offset = pymunk.Vec2d(sprite.get_size()[0], sprite.get_size()[1]) / 2.
        p = p - offset

        # Copy the sprite on the screen
        screen.blit(sprite, p) 
        


class GamePhysicsObject(GameObject):
    """ 
    This class extends GameObject and it is used for objects which have a
    physical shape (such as tanks and boxes). This class handle the physical
    interaction of the objects.
    """
        
    def __init__(self, x, y, orientation, sprite, space, movable):
        """ Takes as parameters the starting coordinate (x,y),
            the orientation, the sprite (aka the image
            representing the object), the physic engine object (space)
            and whether the object can be moved (movable).
        """

        super().__init__(sprite)

        # Half dimensions of the object converted from screen coordinates 
        # to physic coordinates
        half_width          = 0.5 * self.sprite.get_width() / images.TILE_SIZE
        half_height         = 0.5 * self.sprite.get_height() / images.TILE_SIZE

        # Physical objects have a rectangular shape, the points correspond 
        # to the corners of that shape.
        points              = [[-half_width, -half_height],
                            [-half_width, half_height],
                            [half_width, half_height],
                            [half_width, -half_height]]
        self.points = points
        # Create a body (which is the physical representation of this 
        # game object in the physic engine)
        if(movable):
            mass = 10
            moment = pymunk.moment_for_poly(mass, points)
            self.body         = pymunk.Body(mass, moment)
        else:
            self.body         = pymunk.Body(body_type=pymunk.Body.STATIC)
            
        self.body.position  = x, y
        self.body.angle     = math.radians(orientation)
        self.shape          = pymunk.Poly(self.body, points)

        # Set value for friction and elasticity
        self.shape.friction = 0.5
        self.shape.elasticity = 0.1

        # Add the object to the physic engine
        if(movable):
            ctf.space.add(self.body, self.shape)
        else:
            ctf.space.add(self.body, self.shape)
    

    def screen_position(self):
        """ 
        Converts the body's position in the 
        physics engine to screen coordinates. 
        """
        return physics_to_display(self.body.position)
    
    
    def screen_orientation(self):
        """ Angles are reversed from the engine to the display. """
        return -math.degrees(self.body.angle)


    def update_screen(self, screen):
        """ Updates the screen. """
        super().update_screen(screen)
        # debug draw 
        if DEBUG:
            ps = [self.body.position+p for p in self.points]

            ps = [physics_to_display(p) for p in ps]
            ps += [ps[0]]
            pygame.draw.lines(
                screen, pygame.color.THECOLORS["red"], False, ps, 1
            )

def clamp (minval, val, maxval):
    """ Convenient helper function to bound a value to a specific interval. """
    if val < minval: return minval
    if val > maxval: return maxval
    return val


class Tank(GamePhysicsObject):
    """ 
    Extends GamePhysicsObject and 
    handles aspects which are specific to our tanks. 
    """

    # Constant values for the tank, acessed like: Tank.ACCELERATION
    ACCELERATION = 0.4
    NORMAL_MAX_SPEED = 2.0
    FLAG_MAX_SPEED = NORMAL_MAX_SPEED * 0.5
    
    def __init__(self, x, y, orientation, sprite, space):
        super().__init__(x, y, orientation, sprite, space, True)
        # Define variable used to apply motion to the tanks
        self.acceleration         = 0.0
        self.velocity             = 0.0
        self.angular_acceleration = 0.0
        self.angular_velocity     = 0.0

        self.ai = None

        self.score                = 0
        self.flag                 = None                      
        self.maximum_speed        = Tank.NORMAL_MAX_SPEED
        self.start_position       = pymunk.Vec2d(x, y)
    
        self.cooldown = 0
        self.protection = 100
        self.hp = 100

        # Collision detection
        self.start_orientation = orientation
        self.shape.collision_type = 2
        self.shape.parent = self

    def accelerate(self):
        """ Call this function to make the tank move forward. """
        self.acceleration = Tank.ACCELERATION
    

    def decelerate(self):
        """ Call this function to make the tank move backward. """
        self.acceleration = -Tank.ACCELERATION
    
    # 
    def turn_left(self):
        """ Makes the tank turn left (counter clock-wise). """
        self.angular_acceleration = -Tank.ACCELERATION


    def turn_right(self):
        """ Makes the tank turn right (clock-wise). """
        self.angular_acceleration = Tank.ACCELERATION
    
    def update(self):
        """ A function to update the objects coordinates.
            Gets called at every tick of the game. 
        """
        
        # Update the velocity of the tank in function of the physic simulation
        if(math.fabs(self.velocity) > 0 ):
            self.velocity *= self.body.velocity.length / math.fabs(self.velocity)
            
        if(math.fabs(self.angular_velocity) > 0 ):
            self.angular_velocity *= math.fabs(
                self.body.angular_velocity / self.angular_velocity
            )
        
        # Update the velocity in function of the acceleration
        self.velocity         += self.acceleration
        self.angular_velocity += self.angular_acceleration
        
        # Make sure the velocity is not larger than a maximum speed
        self.velocity = clamp(
            -self.maximum_speed, self.velocity, self.maximum_speed
            )
        self.angular_velocity = clamp(
            -self.maximum_speed, self.angular_velocity, self.maximum_speed
        )
        
        # Update the physic velocity
        self.body.velocity = pymunk.Vec2d(
            0, self.velocity).rotated(self.body.angle
            )
        self.body.angular_velocity = self.angular_velocity
    
    
    def stop_moving(self):
        """ Call this function to make the tank stop moving. """
        self.velocity     = 0
        self.acceleration = 0
    
    
    def stop_turning(self):
        """ Call this function to make the tank stop turning. """
        self.angular_velocity     = 0
        self.angular_acceleration = 0
    
    
    def post_update(self):
        """ 
        Updates the position of the flag and 
        ensures that the tank has its normal speed. 
        """
        # If the tank carries the flag, then update the positon of the flag
        if(self.flag != None):
            self.flag.x           = self.body.position[0]
            self.flag.y           = self.body.position[1]
            self.flag.orientation = -math.degrees(self.body.angle)
        # Else ensure that the tank has its normal max speed 
        else:
            self.maximum_speed = Tank.NORMAL_MAX_SPEED
        
        if self.cooldown > 0:
            self.cooldown -= 1

        if self.protection > 0:
            self.protection -= 1


    def try_grab_flag(self, flag):
        """ 
        Call this function to try to grab the flag, 
        if the flag is not on other tank
        and it is close to the current tank, 
        then the current tank will grab the flag.
        """
        # Check that the flag is not on other tank
        if(not flag.is_on_tank):
            # Check if the tank is close to the flag
            flag_pos = pymunk.Vec2d(flag.x, flag.y)
            if((flag_pos - self.body.position).length < 0.5):
                # Grab the flag !
                pygame.mixer.Sound.play(sounds.pickup_sound)
                self.flag           = flag
                flag.is_on_tank     = True
                self.maximum_speed  = Tank.FLAG_MAX_SPEED


    def has_won(self):
        """ 
        Check if the current tank has won 
        (if it is has the flag and it is close to its start position). 
        """
        if self.flag != None and \
            (self.start_position - self.body.position).length < 0.2:
            self.score += 100
            return True
        return False


    def shoot(self, space):
        """ Call this function to shoot a bullet. """
        pygame.mixer.Sound.play(sounds.shoot_sound)
        return Bullet(
                self.body.position[0], 
                self.body.position[1], 
                self.body.angle, space, 
                self
                )


    def reset_position(self):
        """ Resets the tanks position. """
        self.body.position = self.start_position
        self.body.angle = math.radians(self.start_orientation)
        self.hp = 100
        self.protection = 100
        
        if self.flag != None:
            self.flag.is_on_tank = False
        self.flag = None


class Bullet(GamePhysicsObject):
     """ Extends the GamePhysicsObject to handle bullets. """
     VELOCITY = 3
     
     def __init__(self, x, y, rotation, space, tank):
        super().__init__(
            x+math.cos(rotation + math.pi/2)*0.4,
            y+math.sin(rotation + math.pi/2)*0.4,
            rotation, images.bullet, space, True
            )
        self.body.velocity = pymunk.Vec2d(0, self.VELOCITY).rotated(rotation)
        self.body.angle = rotation
        self.shape.collision_type = 1
        self.shape.parent = self
        self.tank = tank


class Box(GamePhysicsObject):
    """ This class extends the GamePhysicsObject to handle box objects. """

    def __init__(self, x, y, boxmodel, space):
        """ 
        It takes as arguments the coordinate of the starting position 
        of the box (x,y) and the box model (boxmodel). 
        """
        self.boxmodel = boxmodel
        super().__init__(
            x, y, 0,
            self.boxmodel.sprite, space, self.boxmodel.movable
            )

        # Collision detection
        self.shape.collision_type = 3
        self.shape.parent = self
    
    
    def update(self):
        """ Updates the friction of the movable boxes. """
        self.body.velocity *= 0.9
        self.body.angular_velocity *= 0.9


class GameVisibleObject(GameObject):
    """ 
    This class extends GameObject for object that are visible on screen 
    but have no physical representation (bases and flag).
    """

    def __init__(self, x, y, sprite):
        """ It takes argument the coordinates (x,y) and the sprite. """
        self.x            = x
        self.y            = y
        self.orientation  = 0
        super().__init__(sprite)


    def screen_position(self):
        """ Returns the screen position of object """
        return physics_to_display(pymunk.Vec2d(self.x, self.y))


    def screen_orientation(self):
        """ Returns the orientation of object. """
        return self.orientation


class Flag(GameVisibleObject):
    """ This class extends GameVisibleObject for representing flags."""

    def __init__(self, x, y):
        super().__init__(x, y,  images.flag)
        self.is_on_tank   = False


class Explosion(GameVisibleObject):
    """ This class extends GameVisibleObject for repressenting Explosions. """
    def __init__(self, x, y):
        """ Takes the coordinates of the explosion. """
        super().__init__(x, y,  images.explosion)
        self.duration_timer = 25


    def post_update(self):
        """ Decreases the timer by one. """
        self.duration_timer -= 1

        

        

        

        

        

        

        

        

        

        

        

        

        

        

        

        

        

        

        

        

        

        

