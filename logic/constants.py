""" Game Constants """
from . import tiles

# Dimensions of the map tiles
MAP_TILE_WIDTH, MAP_TILE_HEIGHT = 24, 16
# Cache of map tiles
MAP_CACHE = tiles.TileCache(MAP_TILE_WIDTH, MAP_TILE_HEIGHT)
# Directory of map files
MAP_DIR = 'resources/maps/'
# Map to use if none specified
DEFAULT_MAP = MAP_DIR + "level.map"
# Walking Directions
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3
# Motion offsets for particular directions
#     N  E  S   W
DX = [0, 1, 0, -1] # Moves left and right
DY = [-1, 0, 1, 0] # Moves up   and down


