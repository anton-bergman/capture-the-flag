import math
import pymunk
from pymunk import Vec2d
import gameobjects
import boxmodels
from collections import defaultdict, deque

# 3 degrees, a bit more than we can turn each tick
MIN_ANGLE_DIF = math.radians(3) 

def angle_between_vectors(vec1, vec2):
    """ 
        Since Vec2d operates in a cartesian coordinate space we have to
        convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2 
    vec = vec.perpendicular()
    return vec.angle


def periodic_difference_of_angles(angle1, angle2): 
    """ Returns the periodic difference between two angles. """
    return  ((angle1% (2*math.pi)) - (angle2% (2*math.pi))) % (2*math.pi)


class Ai:
    """ 
    A simple ai that finds the shortest path to the target using 
    a breadth first search. Also capable of shooting other tanks 
    and or wooden boxes. 
    """

    def __init__(self, tank, game_objects_list, tanks_list, space, currentmap):
        self.tank               = tank
        self.game_objects_list  = game_objects_list
        self.tanks_list         = tanks_list
        self.space              = space
        self.currentmap         = currentmap
        self.flag = None
        self.MAX_X = currentmap.width - 1 
        self.MAX_Y = currentmap.height - 1

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()

        self.move_cycle = self.move_cycle_gen()


    def update_grid_pos(self):
        """ 
        This should only be called in the beginning,
        or at the end of a move_cycle. 
        """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    
    def decide(self):
        """ 
        Main decision function that gets called on 
        every tick of the game. 
        """
        self.maybe_shoot()
        next(self.move_cycle)


    def maybe_shoot(self):
        """ 
        Makes a raycast query in front of the tank. If another tank
        or a wooden box is found, then we shoot. 
        """
        angle = self.tank.body.angle + math.pi/2
        start = self.tank.body.position + (math.cos(angle)*0.4, math.sin(angle)*0.4)
        end = self.tank.body.position + (math.cos(angle)*self.currentmap.width,\
              math.sin(angle)*self.currentmap.height)

        res = self.space.segment_query_first(start, end, 0, pymunk.ShapeFilter())
        
        if hasattr(res, "shape") and hasattr(res.shape, "parent"):
            if isinstance(res.shape.parent, gameobjects.Box):
                if res.shape.parent.boxmodel == boxmodels.get_model(2) \
                and self.tank.cooldown == 0:
                    self.game_objects_list.append(self.tank.shoot(self.space))
                    self.tank.cooldown = 50
                        
            elif isinstance(res.shape.parent, gameobjects.Tank) \
            and self.tank.cooldown == 0:
                self.game_objects_list.append(self.tank.shoot(self.space))
                self.tank.cooldown = 50


    def move_cycle_gen(self):
        """ 
        A generator that iteratively goes through all the required steps
        to move to our goal.
        """ 
        while True:
            # Search for shortest path to target
            path = self.find_shortest_path()
            if not path:
                # Search for shortest path to target, allow metal boxes
                path = self.find_shortest_path(True)
                if not path:
                    # No path to target, try again.
                    yield
                    continue 
            # Moves on to the next coordinte and aligns from upper left to center of coordinate.
            next_coord = path.popleft() + (0.5, 0.5)
            yield
            
            # Get tank target angle to next position
            target_angle = angle_between_vectors(
                self.tank.body.position, next_coord
            )
            
            # Get difference between current tank angle and target
            angle_diff = periodic_difference_of_angles(
                self.tank.body.angle, target_angle
            )
            
            # Turn left or right depending on the difference between the angles
            if not (angle_diff <= MIN_ANGLE_DIF \
                or angle_diff >= math.pi*2 - MIN_ANGLE_DIF):
                self.tank.stop_moving()
                if angle_diff >= math.pi:
                    self.tank.turn_right()
                else:
                    self.tank.turn_left()

            # Updates the difference between angles while the tank is turning
            while not (angle_diff <= MIN_ANGLE_DIF \
                or angle_diff >= math.pi*2 - MIN_ANGLE_DIF):
                
                angle_diff = periodic_difference_of_angles(
                    self.tank.body.angle, target_angle
                )
                yield
            
            # Stop turning
            self.tank.stop_turning()

            # Get distance to next coordinate and save current position.
            current_distance = self.tank.body.position.get_distance(next_coord)
            last_distance = current_distance

            # Accelerate
            self.tank.accelerate()
            
            # Keep moving until next coord is reached.
            while not last_distance < current_distance:
                last_distance = current_distance
                current_distance = self.tank.body.position.get_distance(next_coord)
                yield 

            # Update the position of the AI.
            self.update_grid_pos()
            

    def find_shortest_path(self, allow_metal = False):
        """ 
        A simple Breadth First Search using integer coordinates as our nodes.
        Edges are calculated as we go, using an external function.
        """

        # Get the current position.
        start_node = (self.grid_pos[0], self.grid_pos[1])
        
        # Create queue and add the start position.
        queue = deque()
        queue.append(start_node)
        
        # Create a set of visited nodes.
        visited = set()

        # Create a dictionary of all tested paths
        paths = {}

        # Gets the Vec2d coordinates for the starting position.
        paths[start_node] = [Vec2d(start_node[0], start_node[1])]

        # Runs while we have a queue.
        while queue:
            # The position we're currently looking at
            node = queue.popleft()  

            # Check if current node is target
            if node == self.get_target_tile():
                # Return the path taken to the target node.
                result = deque(paths[node])
                result.popleft()
                return result

            # Looks at all the neighbouring coordinates
            for neighbour in self.get_tile_neighbors(node, allow_metal):
                if (neighbour[0], neighbour[1]) not in visited:

                    # If the neighbour hasn't been visited
                    neighbour = (neighbour[0], neighbour[1])
                    # Add neighbour to queue and visited
                    queue.append(neighbour) 
                    visited.add(neighbour) 
                    # Create a copy of paths
                    paths[neighbour] = paths[node].copy() 
                    # Add neighbour to paths
                    paths[neighbour].append(Vec2d(neighbour[0], neighbour[1])) # 
                    
        # Returns an empty deque if no path is found
        return deque([])
            
            
    def get_target_tile(self):
        """
        Returns position of the flag if we don't have it. 
        If we do have the flag, return the position of our home base.
        """
        if self.tank.flag != None:
            x, y = self.tank.start_position
        else:
            self.get_flag() # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))


    def get_flag(self):
        """ 
        This has to be called to get the flag, since we don't know
        where it is when the Ai object is initialized.
        """
        if self.flag == None:
        # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag


    def get_tile_of_position(self, position_vector):
        """ 
        Converts and returns the float position 
        of our tank to an integer position.
        """
        x, y = position_vector
        return Vec2d(int(x), int(y))


    def get_tile_neighbors(self, coord_vec, allow_metal = False):
        """ 
        Returns all bordering grid squares of the input coordinate.
        A bordering square is only considered accessible if it is grass
        or a wooden box. If allow_metal is true metal boxes will be accepted.
        """
        coord_vec = Vec2d(coord_vec[0], coord_vec[1])
        # Find the coordinates of the tiles' four neighbors
        neighbors = [
            coord_vec + delta for delta in [(1, 0), (0, 1), (-1, 0), (0, -1)]
        ] 
        if allow_metal:
            return filter(self.filter_tile_neighbors_metalbox, neighbors)
        else:
            return filter(self.filter_tile_neighbors, neighbors)


    def filter_tile_neighbors (self, coord):
        """ Checks if selected tile is either free or a wooden box. """
        if  coord[0] <= self.MAX_X \
            and coord[1] <= self.MAX_Y \
            and coord[0] >= 0 \
            and coord[1] >= 0 \
            and (self.currentmap.boxAt(coord[0], coord[1]) == 0
            or self.currentmap.boxAt(coord[0], coord[1]) == 2):

            return True
        else:
            return False


    def filter_tile_neighbors_metalbox (self, coord):
        """ 
        Checks if selected tile is either grass, wooden box or metal box. 
        """
        if coord[0] <= self.MAX_X \
            and coord[1] <= self.MAX_Y \
            and coord[0] >= 0 \
            and coord[1] >= 0 \
            and (self.filter_tile_neighbors(coord) \
            or self.currentmap.boxAt(coord[0], coord[1]) == 3):
        
            return True
        else:
            return False
            