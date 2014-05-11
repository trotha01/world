""" The state of the current map """
import ConfigParser
import pygame
import tiles
import sprites as spr
import importlib
import sys
sys.path.append('languages')

# Dimensions of the map tiles
MAP_TILE_WIDTH, MAP_TILE_HEIGHT = 24, 16
# Cache of map tiles
MAP_CACHE = tiles.TileCache(MAP_TILE_WIDTH, MAP_TILE_HEIGHT)
# Directory of map files
MAP_DIR = 'maps/'
# Walking Directions
NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3
# Motion offsets for particular directions
#     N  E  S   W
DX = [0, 1, 0, -1] # Moves left and right
DY = [-1, 0, 1, 0] # Moves up   and down

def change_coords(coords, direction):
    """Change the coordinates North, East, South, or West."""
    x, y = coords
    if direction == 'North':
        return (x, y-1)
    elif direction == 'South':
        return (x, y+1)
    elif direction == 'East':
        return (x+1, y)
    elif direction == 'West':
        return (x-1, y)
    else:
        return (x, y)
            
class Map(object):
    """ The state of the current map """

    def __init__(self, language, mapfilename="level.map"):
        self.language    = language # the language as a string
        self.level       = Level(language, mapfilename)

        # Initialize sprites, shadows and overlays as their respective classes
        self.shadows     = pygame.sprite.RenderUpdates()
        self.sprites     = spr.SortedUpdates()
        self.overlays    = pygame.sprite.RenderUpdates()
        self.background  = None
        self.player      = None

        self.use_level(mapfilename)

    # def use_level(self, level_file, nextPlayerPos=(-1, -1)):
    def use_level(self, level_file):
        """Set the map level."""
        level = Level(self.language, level_file) #TODO: rename to new_level

        # Figure out where player goes on the level (if changing levels)
        new_pos = None
        old_dir = None
        connects_by = None # Auto connecting tile, or meta-key
        if self.player is not None:
            old_dir = self.player.direction
            current_pos = self.player.pos
            # Which char to put player on in next level
            connect_char = self.level.get_tile(current_pos[0], current_pos[1]).get('connectchar')
            connects_by = self.level.get_tile(current_pos[0], current_pos[1]).get('connect')

            # Get all tiles with that char
            if connect_char is not None:
                coords = level.key[connect_char]['locations']
                if len(coords) == 1:
                    new_pos = coords[0]
                else:
                    coord1 = coords[0]
                    coord2 = coords[1]
                    # If x's are the same (all vertical)
                    if coord1[0] == coord2[0]:
                        # Use y from the old position
                        new_pos = (coord1[0], current_pos[1])
                    else: # y's are the same (all horizontal)
                        # Use x from the old position
                        new_pos = (current_pos[0], coord1[1])

        # Initialize sprites, shadows and overlays as their respective classes
        self.shadows  = pygame.sprite.RenderUpdates()
        self.sprites  = spr.SortedUpdates()
        self.overlays = pygame.sprite.RenderUpdates()
        self.level    = level

        # Populate player, sprites, shadows with in the level
        for pos, tile in level.items.iteritems(): # pos on map, tile info
            if tile.get("player") in ('true', '1', 'yes', 'on'):
                if new_pos is not None:
                    sprite = spr.Player(new_pos) # Player class. Uses "player.png"
                    sprite.direction = old_dir
                else:
                    sprite = spr.Player(pos) # Player class. Uses "player.png"
                self.player = sprite
            else:
                tile_image = tile["sprite"]
                sprite = spr.Sprite(pos, spr.SPRITE_CACHE[tile_image])
            self.sprites.add(sprite)
            self.shadows.add(spr.Shadow(sprite))

        # If autoconnects (transports player) move off transporting tile
        if connects_by == 'auto':
            # Get current player coordinates
            x_coord, y_coord = self.player.pos
            walking = self.player.walk_animation()
            # If not walking into a wall
            if not self.level.is_blocking(x_coord+DX[old_dir],
                                          y_coord+DY[old_dir]):
                # Walk in specified direction
                self.player.animation =  walking

        # Render the level map
        self.background, overlays = self.level.render()

        # Add the overlays for the level map
        twidth  = MAP_TILE_WIDTH
        theight = MAP_TILE_HEIGHT
        for (x, y), image in overlays.iteritems():
            overlay = pygame.sprite.Sprite(self.overlays)
            overlay.image = image
            overlay.rect  = image.get_rect().move(x*twidth, y*theight - theight)

    def clear_sprites(self, screen):
        """ Clears all the sprites from screen and updates them """
        self.sprites.clear(screen, self.background)
        self.sprites.update() # Calls update() on each sprite

    # Faster than clear_sprites
    def update_sprites(self, screen, display):
        """ Update and redraw all the sprites on the screen """
        self.shadows.update()
        # Don't add shadows to dirty rectangles, as they already fit inside
	# sprite rectangles.
        self.shadows.draw(screen) # Blit the shadows
        dirty = self.sprites.draw(screen) # Blit the sprites

	# Don't add overlays to dirty rectangles, only the places where
	# sprites are need to be updated, and those are already dirty.
        self.overlays.draw(screen) # Blit the overlays
	# Update only the dirty areas of the screen
        display.update(dirty) # Update dirty portions of display

class Level(object):
    """Load and store the map of the level, together with all the items."""

    def __init__(self, language, mapfilename="level.map"):
        # 'language' is a module to import
        self.lang    = importlib.import_module(language)
        self.tileset = ''
        self.map     = []
        self.items   = {} # Sprites (not walls), mapped to by x,y coords
        self.key     = {}
        self.width   = 0
        self.height  = 0
        # Tiles that auto-transport player to new level
        self.autoleveltiles = {}
        # Tiles that transport player to new level on meta-key press (space)
        self.metaleveltiles = {}
        self.audio_tiles    = {}
        self.load_file(mapfilename)

    def load_file(self, mapfilename="level.map"):
        """Load the level from specified file."""

        parser = ConfigParser.ConfigParser()
        parser.read(MAP_DIR + mapfilename)
	# get(section, option), returns value from 'option = value'
        self.tileset = parser.get("level", "tileset") 
        self.map = parser.get("level", "map").split("\n")

	# Load section block descriptions into 'key' dictionary
        for section in parser.sections():
            if len(section) == 1: # If section is a map block
                # desc = map block info (name, tile, isplayer, doesblock)
                desc = dict(parser.items(section))
                self.key[section] = desc
                self.key[section]['locations'] = [] # Coordinates that have this key

        # Create item(sprite) tile list, connector tile lists, and audio tile list
        self.width = len(self.map[0])
        self.height = len(self.map)
        for y, line in enumerate(self.map):
            for x, tile in enumerate(line):
                self.key[tile]['locations'].append((x, y))
                if not self.is_wall(x, y) and 'sprite' in self.key[tile]:
                    self.items[(x, y)] = self.key[tile]
                if self.is_autoconnector(x, y):
                    self.autoleveltiles[(x, y)] = self.key[tile]
                if self.is_metaconnector(x, y):
                    if('connectlocation' in self.key[tile]):
                        connect_pos = self.key[tile]['connectlocation']
                        connect_tile = change_coords((x, y), connect_pos)
                    else:
                        connect_tile = (x, y)
                    self.metaleveltiles[connect_tile] = self.key[tile]
                if self.is_audio(x, y):
                    speech = self.key[tile]['speech']
                    audio_dir = self.key[tile]['audiodirection']
                    speech_tile = change_coords((x, y), audio_dir)
                    speech = self.lang.TRANSLATE[speech]
                    self.audio_tiles[speech_tile] = self.key[tile]
                    self.audio_tiles[speech_tile].update(speech)

    def render(self):
        """Draw the level on the surface."""
	# Returns (image, overlays)
        #    image: a Surface class
	#    overlays: a dictionary (of walls that obscure things)

        wall  = self.is_wall
        map_tiles = MAP_CACHE[self.tileset]
        surface_pos = (self.width*MAP_TILE_WIDTH, self.height*MAP_TILE_HEIGHT)
        image = pygame.Surface(surface_pos)
        overlays = {}

        for map_y, line in enumerate(self.map):
            for map_x, tile_char in enumerate(line):
                # Gets coords in image to use
                if wall(map_x, map_y):
                    img_coords = tiles.wall_img_coords(wall, (map_x, map_y), overlays, map_tiles)
                else:
                    try:
                        img_coords = self.key[tile_char]['tile'].split(',')
                        img_coords = int(img_coords[0]), int(img_coords[1])
                    except (ValueError, KeyError):
                        # Default to ground image tile
                        img_coords = tiles.GROUND_TILE
                tile_image = map_tiles[img_coords[0]][img_coords[1]]
                image.blit(tile_image,
                            (map_x*MAP_TILE_WIDTH, map_y*MAP_TILE_HEIGHT))
        return image, overlays

    def get_tile(self, tile_x, tile_y):
        """Tell what's at the specified position of the map."""

        try:
            char = self.map[tile_y][tile_x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

    def get_bool(self, tile_x, tile_y, name):
        """Tell if the specified flag is set for position on the map."""

        value = self.get_tile(tile_x, tile_y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

    def is_wall(self, tile_x, tile_y):
        """Is there a wall?"""

        return self.get_bool(tile_x, tile_y, 'wall')

    def is_blocking(self, tile_x, tile_y):
        """Is this place blocking movement?"""

        if not 0 <= tile_x < self.width or not 0 <= tile_y < self.height:
            return True
        return self.get_bool(tile_x, tile_y, 'block')

    def is_autoconnector(self, tile_x, tile_y):
        """Does tile connect to another level automatically?"""

        value = self.get_tile(tile_x, tile_y).get('connect')
        return (value == 'auto')

    def is_metaconnector(self, tile_x, tile_y):
        """Does tile connect to another level on meta-key press?"""

        value = self.get_tile(tile_x, tile_y).get('connect')
        return (value == 'metakey')

    def is_audio(self, tile_x, tile_y):
        """Is this an audio tile?"""
        return self.get_bool(tile_x, tile_y, 'audio')


