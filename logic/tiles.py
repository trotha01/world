""" Changes a picture into tiles to use """

import pygame

from logic import constants as const

GROUND_TILE = 0, 3

WALL_TILES = {
# You can see front of wall
    'FRONT' : {
        'MIDDLE'   : (1, 2),
        'RIGHT'    : (2, 2),
        'LEFT'     : (0, 2),
        'ISOLATED' : (3, 2),
    },

# There is a wall in front, only see top
    'TOP' : {
        'MIDDLE'   : (1, 1),
        'RIGHT'    : (2, 1),
        'LEFT'     : (0, 1),
        'ISOLATED' : (3, 1),
    },

# There is something behind the wall (these are overlays)
    'OVERLAY' : {
        'MIDDLE'   : (1, 0),
        'RIGHT'    : (2, 0),
        'LEFT'     : (0, 0),
        'ISOLATED' : (3, 0)
    }
}

def wall_img_coords(wall, map_coords, overlays, map_tiles):
    """ wall       : function that determines if a tile is a wall
        map_coords : Where the wall will go on the map
        overlays   : An overlay dictionary to add to
        map_tiles  : tiles to choose from
        returns (x, y) for a wall from image set """

    map_x, map_y = map_coords
    # wall  = self.is_wall

    def wall_coords_from_set((map_x, map_y), wall_set):
        """ Returns relevant wall image coords, from the set of walls given """

        # If walls on left and right
        if wall(map_x+1, map_y) and wall(map_x-1, map_y):
            coords = wall_set['MIDDLE']

        # If wall only on right
        elif wall(map_x+1, map_y):
            coords = wall_set['LEFT']

        # If wall only on left
        elif wall(map_x-1, map_y):
            coords = wall_set['RIGHT']

        # If no walls on left or right
        else:
            coords = wall_set['ISOLATED']
        return coords

    # Draw different tiles depending on neighbourhood
    if not wall(map_x, map_y+1): # No wall below
        coords = wall_coords_from_set(map_coords, WALL_TILES['FRONT'])
    else: # else if wall below
        # (We add 1 to y, cuz this case depends on the walls below)
        coords = wall_coords_from_set((map_x, map_y+1), WALL_TILES['TOP'])
        
    # Add overlays if the wall may be obscuring something
    if not wall(map_x, map_y-1): # No wall above
        over = wall_coords_from_set(map_coords, WALL_TILES['OVERLAY'])
        overlays[(map_x, map_y)] = map_tiles[over[0]][over[1]]

    return coords


def load_tile_table(imagefilename, width, height):
    # Called by tilecacheInstance[file][width][height]
    """Load an image and split it into tiles."""

    image = pygame.image.load(const.IMAGE_DIR + imagefilename).convert()
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_x in range(0, image_width/width):
        line = []
        tile_table.append(line)
        for tile_y in range(0, image_height/height):
            rect = (tile_x*width, tile_y*height, width, height)
            line.append(image.subsurface(rect))
    return tile_table

class TileCache(object):
    """Load the tilesets lazily into global cache"""

    def __init__(self, width=const.TILE_WIDTH, height=None):
        self.width = width
        self.height = height or width
        self.cache = {}

    def __getitem__(self, imagefilename):
        """Return a table of tiles, load it from disk if needed."""
        # Called by tilecacheInstance[file]

        key = (imagefilename, self.width, self.height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = load_tile_table(imagefilename, self.width,
                                         self.height)
            self.cache[key] = tile_table
            return tile_table

    # Functions not necessary
    def __setitem__(self, imagefilename):
        pass
    def __delitem__(self, imagefilename):
        pass
    def __len__(self, imagefilename):
        pass

# Cache of map tiles
MAP_CACHE = TileCache(const.MAP_TILE_WIDTH, const.MAP_TILE_HEIGHT)

