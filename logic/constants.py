""" Game Constants """

# Dimensions of the map tiles
MAP_TILE_WIDTH, MAP_TILE_HEIGHT = 24, 16

# Sprite height/width
TILE_WIDTH = 32
TILE_HEIGHT = 16
IMAGE_DIR = 'resources/images/'

# Make screen 15 tiles wide and 15 tiles high
SCREEN_WIDTH = MAP_TILE_WIDTH*15
SCREEN_HEIGHT = MAP_TILE_HEIGHT*15

# Directory of map files
MAP_DIR = 'resources/maps/'
# The starting map
INITIAL_MAP = MAP_DIR + "house.map"

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


SUPPORTED_LANGUAGES = ["Spanish", "French"]
