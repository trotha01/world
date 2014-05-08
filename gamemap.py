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
        level = Level(self.language, level_file)

        # Initialize sprites, shadows and overlays as their respective classes
        self.shadows  = pygame.sprite.RenderUpdates()
        self.sprites  = spr.SortedUpdates()
        self.overlays = pygame.sprite.RenderUpdates()
        self.level    = level

        # Set Player position if position was passed to method
        """
        if nextPlayerPos != (-1, -1):
            print "unpack: "
            print nextPlayerPos[0]
            print nextPlayerPos[1]
            x, y = nextPlayerPos
            currentX, currentY = self.player._get_pos()
            if x == 'x':
                nextPlayerPos = (currentX, nextPlayerPos[1])
            elif x == 'left':
                nextPlayerPos = (1, nextPlayerPos[1])
            elif x == 'right':
                nextPlayerPos = (level.width-1, nextPlayerPos[1])

            if y == 'y':
                nextPlayerPos = (nextPlayerPos[0], currentY)
            elif y == 'top':
                nextPlayerPos = (nextPlayerPos[0], 1)
            elif y == 'bottom':
                nextPlayerPos = (nextPlayerPos[0], level.height-1)

            print "New Pos: "
            print nextPlayerPos
            sprite = spr.Player(nextPlayerPos)
            self.player = sprite
            self.sprites.add(sprite)
            self.shadows.add(spr.Shadow(sprite))
            """

        # Populate player, sprites, shadows with in the level
        for pos, tile in level.items.iteritems(): # pos on map, tile info
            # if nextPlayerPos == (-1, -1) and \
            #    tile.get("player") in ('true', '1', 'yes', 'on'):
            if tile.get("player") in ('true', '1', 'yes', 'on'):
                print "Adding player in level-defined position"
                sprite = spr.Player(pos) # Player class. Uses "player.png"
                self.player = sprite
            else:
                tile_image = tile["sprite"]
                sprite = spr.Sprite(pos, spr.SPRITE_CACHE[tile_image])
            self.sprites.add(sprite)
            self.shadows.add(spr.Shadow(sprite))

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

	# Create item(sprite) tile list, connector tile lists, and audio tile list
        self.width = len(self.map[0])
        self.height = len(self.map)
        for y, line in enumerate(self.map):
            for x, tile in enumerate(line):
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

    def wall_img_coords(self, map_coords, overlays, map_tiles):
        """ returns (x, y) for a wall from image set """

        map_x, map_y = map_coords
        wall  = self.is_wall

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
            coords = wall_coords_from_set(map_coords, tiles.WALL_TILES['FRONT'])
        else: # else if wall below
            # (We add 1 to y, cuz this case depends on the walls below)
            coords = wall_coords_from_set((map_x, map_y+1), tiles.WALL_TILES['TOP'])
            
        # Add overlays if the wall may be obscuring something
        if not wall(map_x, map_y-1): # No wall above
            over = wall_coords_from_set(map_coords, tiles.WALL_TILES['OVERLAY'])
            overlays[(map_x, map_y)] = map_tiles[over[0]][over[1]]

        return coords


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
                if wall(map_x, map_y):
                    # Gets coords in image to use
                    img_coords = self.wall_img_coords((map_x, map_y), overlays, map_tiles)
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


