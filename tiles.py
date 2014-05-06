""" Changes a picture into tiles to use """

import pygame

# Sprite height/width
TILE_WIDTH  = 32
TILE_HEIGHT = 16
IMAGE_DIR = 'images/'

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

def load_tile_table(imagefilename, width, height):
    # Called by tilecacheInstance[file][width][height]
    """Load an image and split it into tiles."""

    image = pygame.image.load(IMAGE_DIR + imagefilename).convert()
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

    def __init__(self,  width=TILE_WIDTH, height=None):
        self.width  = width
        self.height = height or width
        self.cache  = {}

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

