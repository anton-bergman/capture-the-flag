import images
import pygame
import json
import os


class Map:
  """ An instance of Map is a blueprint for how the game map will look. """

  def __init__(self, name, width, height, boxes, start_positions, flag_position):
    """ 
    Takes as argument the size of the map (width, height), 
    an array with the boxes type, the start position of tanks (start_positions) 
    and the position of the flag (flag_position).
    """
    self.name               = name
    self.width              = width
    self.height             = height
    self.boxes              = boxes
    self.start_positions    = start_positions
    self.flag_position      = flag_position


  def rect(self):
    """ Returns rectangle object of map. """
    return pygame.Rect(
      0, 0, images.TILE_SIZE*self.width, images.TILE_SIZE*self.height
    )
  
  
  def boxAt(self, x, y):
    """ Return the type of the box at coordinates (x, y). """
    return self.boxes[y][x]


#--Reference to current directory.
main_dir = os.path.split(os.path.abspath(__file__))[0]
  
def save_map(map):
  """
  Saves map as json, in maps/map_name.
  """
  json_data = json.dumps(map.__dict__)
  file_path = os.path.join(main_dir, 'maps', map.name + ".txt")
  file = open(file_path, "w")
  file.write(json_data)
  file.close()


def load_map(file_name):
  """
  Loads maps with name from maps, returns map object.
  """
  file_path = os.path.join(main_dir, 'maps', file_name )
  file = open(file_path, "r")
  json_data = json.load(file)
  file.close()

  map = Map(
    json_data["name"], 
    json_data["width"], 
    json_data["height"],
    json_data["boxes"], 
    json_data["start_positions"],
    json_data["flag_position"])
  return map


def load_all_maps():
  """
  Loads all maps from maps folder and returns list of maps
  """
  folder_path = os.path.join(main_dir, "maps")
  maps_list = []
  for file in sorted(os.listdir(folder_path)):
      if file.endswith(".txt"):
        try: 
          maps_list.append(load_map(file))
        except:
          continue
  return maps_list
