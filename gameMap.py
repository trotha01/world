import ConfigParser
import pygame
import tiles
import sprites as spr

import spanish

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

class Map(object):
    """ The state of the current map """

    def __init__(self, mapfilename="level.map"):
	self.level       = Level(mapfilename)
        self.shadows     = pygame.sprite.RenderUpdates() # sprite Group subclass
        self.sprites     = spr.SortedUpdates()           # sprite RenderUpdates subclass
        self.overlays    = pygame.sprite.RenderUpdates() # sprite Group subclass
	self.background  = None
        self.player      = None

	self.use_level(self.level)

    def use_level(self, level): # level is Level() Class
        """Set the map level."""

        self.shadows  = pygame.sprite.RenderUpdates() # Sprite Group Subclass
        self.sprites  = spr.SortedUpdates()           # sprite RenderUpdates subclass
        self.overlays = pygame.sprite.RenderUpdates() # Sprite Group Subclass
        self.level    = level

        # Set Player Position
        """
        if self.player != None: # If player already exists (i.e., not start of game)
            playerPos = self.player._get_pos()
            for pos, tile in level.autolevelTiles.iteritems():
                if pos[0] == playerPos[0] or pos[1] == playerPos[1]: # Find corresponding tile
                    print "Make new player with pos"
                    print pos
                    sprite = spr.Player(pos)
                    self.player = sprite
            self.sprites.add(sprite)
            self.shadows.add(spr.Shadow(sprite))
            """

        # Populate Game player, sprites, shadows with the level's objects
        for pos, tile in level.items.iteritems(): # pos on map, tile info
            # if self.player == None and tile.get("player") in ('true', '1', 'yes', 'on'): # ??? player usually set to 'true'
            if tile.get("player") in ('true', '1', 'yes', 'on'): # ??? player usually set to 'true'
                sprite = spr.Player(pos) # Player class. Uses "player.png"
                self.player = sprite
            else:
                tileImage = tile["sprite"]
                sprite = spr.Sprite(pos, spr.SPRITE_CACHE[tileImage]) # When is SPRITE_CACHE filled?
            self.sprites.add(sprite)
            self.shadows.add(spr.Shadow(sprite))

        # Render the level map
        self.background, overlays = self.level.render()
        # Add the overlays for the level map
        tWidth  = MAP_TILE_WIDTH
        tHeight = MAP_TILE_HEIGHT
        for (x, y), image in overlays.iteritems():
            overlay = pygame.sprite.Sprite(self.overlays)
            overlay.image = image
            overlay.rect  = image.get_rect().move(x*tWidth, y*tHeight - tHeight)

    def clearSprites(self, screen):
        self.sprites.clear(screen, self.background) # Draw background over sprites
        self.sprites.update() # Calls update() on each sprite

    def updateSprites(self, screen, display):
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

    def __init__(self, mapfilename="level.map"):
        self.tileset = ''
        self.map     = []
        self.items   = {} # Sprites (not walls), mapped to by x,y coords
        self.key     = {}
        self.width   = 0
        self.height  = 0
	self.autolevelTiles = {} # Tiles that auto-transport player to new level
	self.metalevelTiles = {} # Tiles that transport player to new level on meta-key (space)
	self.audioTiles   = {}
        self.load_file(mapfilename)

    def changeCoords(self, coords, direction):
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
                desc = dict(parser.items(section)) # desc = map block info (name, tile, isplayer, doesblock)
                self.key[section] = desc

	# Create item(sprite) tile list, connector tile lists, and audio tile list
        self.width = len(self.map[0])
        self.height = len(self.map)
        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                if not self.is_wall(x, y) and 'sprite' in self.key[c]:
                    self.items[(x, y)] = self.key[c]
		if self.is_autoconnector(x, y):
		    self.autolevelTiles[(x, y)] = self.key[c]
		if self.is_metaconnector(x, y):
		    connectTile = self.changeCoords((x, y), self.key[c]['connectdirection'])
		    self.metalevelTiles[connectTile] = self.key[c]
		if self.is_audio(x, y):
		    speech = self.key[c]['speech']
		    speechTile = self.changeCoords((x, y), self.key[c]['audiodirection'])
		    self.audioTiles[speechTile] = self.key[c]
		    self.audioTiles[speechTile].update(spanish.translate[speech])

    def render(self):
        """Draw the level on the surface."""
	# Returns image: a Surface class
	#         overlays: a dictionary (of walls that obscure things)

        wall  = self.is_wall
        tiles = MAP_CACHE[self.tileset]
        image = pygame.Surface((self.width*MAP_TILE_WIDTH, self.height*MAP_TILE_HEIGHT))
        overlays = {}
        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
                if wall(map_x, map_y):
                    # Draw different tiles depending on neighbourhood
                    if not wall(map_x, map_y+1): # No wall to below
                        if wall(map_x+1, map_y) and wall(map_x-1, map_y): # Wall left and right
                            tile = 1, 2
                        elif wall(map_x+1, map_y): # Wall right
                            tile = 0, 2
                        elif wall(map_x-1, map_y): # Wall left
                            tile = 2, 2
                        else:
                            tile = 3, 2 # No walls
                    else:
                        if wall(map_x+1, map_y+1) and wall(map_x-1, map_y+1):
                            tile = 1, 1
                        elif wall(map_x+1, map_y+1):
                            tile = 0, 1
                        elif wall(map_x-1, map_y+1):
                            tile = 2, 1
                        else:
                            tile = 3, 1
                    # Add overlays if the wall may be obscuring something
                    if not wall(map_x, map_y-1): # No wall above
                        if wall(map_x+1, map_y) and wall(map_x-1, map_y):
                            over = 1, 0
                        elif wall(map_x+1, map_y):
                            over = 0, 0
                        elif wall(map_x-1, map_y):
                            over = 2, 0
                        else:
                            over = 3, 0
                        overlays[(map_x, map_y)] = tiles[over[0]][over[1]]
                else:
                    try:
                        tile = self.key[c]['tile'].split(',')
                        tile = int(tile[0]), int(tile[1])
                    except (ValueError, KeyError):
                        # Default to ground tile
                        tile = 0, 3
                tile_image = tiles[tile[0]][tile[1]]
                image.blit(tile_image,
                            (map_x*MAP_TILE_WIDTH, map_y*MAP_TILE_HEIGHT))
        return image, overlays

    def get_tile(self, x, y):
        """Tell what's at the specified position of the map."""

        try:
            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

    def get_bool(self, x, y, name):
        """Tell if the specified flag is set for position on the map."""

        value = self.get_tile(x, y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

    def is_wall(self, x, y):
        """Is there a wall?"""

        return self.get_bool(x, y, 'wall')

    def is_blocking(self, x, y):
        """Is this place blocking movement?"""

        if not 0 <= x < self.width or not 0 <= y < self.height:
            return True
        return self.get_bool(x, y, 'block')

    def is_autoconnector(self, x, y):
	"""Does tile connect to another level automatically?"""

	value = self.get_tile(x, y).get('connect')
	return (value == 'auto')

    def is_metaconnector(self, x, y):
	"""Does tile connect to another level on meta-key press?"""

	value = self.get_tile(x, y).get('connect')
	return (value == 'metakey')

    def is_audio(self, x, y):
	    """Is this an audio tile?"""
	    return self.get_bool(x, y, 'audio')


