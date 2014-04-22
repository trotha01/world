#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This is sample of how you can implement a tile-based game, not unlike
the RPG games known from consoles, in pygame. It's not a playable game,
but it can be turned into one. Care has been taken to comment it clearly,
so that you can use it easily as a starting point for your game.

The program reads a level definition from a "level.map" file, and uses the
graphics referenced for that file to display a tiled map on the screen and
let you move an animated player character around it.

Note that a lot of additional work is needed to turn it into an actual game.

@copyright: 2008, 2009 Radomir Dopieralski <qq@sheep.art.pl>
@license: BSD, see COPYING for details

"""


import pygame
import pygame.locals as pg
import gameMap as gmap
import sprites as spr

GAME_FRAMERATE = 50 # Frames per second
class Game(object):
    """The main game object."""

    def __init__(self):
        self.screen      = pygame.display.get_surface()
        self.pressed_key = None
        self.game_over   = False
        self.shadows     = pygame.sprite.RenderUpdates() # sprite Group subclass
        self.sprites     = spr.SortedUpdates()           # sprite RenderUpdates subclass
        self.overlays    = pygame.sprite.RenderUpdates() # sprite Group subclass
        self.player      = None

        self.use_level(gmap.Level("level.map"))

    def use_level(self, level): # level is Level() Class
        """Set the level as the current one."""

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
        tWidth  = gmap.MAP_TILE_WIDTH
        tHeight = gmap.MAP_TILE_HEIGHT
        for (x, y), image in overlays.iteritems():
            overlay = pygame.sprite.Sprite(self.overlays)
            overlay.image = image
            overlay.rect  = image.get_rect().move(x*tWidth, y*tHeight - tHeight)

    def control(self):
        """Handle the controls of the game."""

        keys = pygame.key.get_pressed()

        def pressed(key):
            """Check if the specified key is pressed."""

            return self.pressed_key == key or keys[key]

        def walk(d):
            """Start walking in specified direction."""

            x, y = self.player.pos
            self.player.direction = d
            if not self.level.is_blocking(x+spr.DX[d], y+spr.DY[d]):
                self.player.animation = self.player.walk_animation() # moves player in direction d

            # Change level?
            self.autoChangeLevel()


        if pressed(pg.K_UP):
            walk(0)
        elif pressed(pg.K_DOWN):
            walk(2)
        elif pressed(pg.K_LEFT):
            walk(3)
        elif pressed(pg.K_RIGHT):
            walk(1)
        # Play audio?
        if pressed(pg.K_SPACE):
            self.playAudio()
            self.metaChangeLevel()
        self.pressed_key = None

    def changeLevel(self, level):
        self.use_level(gmap.Level(level))
        self.screen.blit(self.background, (0, 0)) # Blit background on screen
        self.overlays.draw(self.screen)           # Blit overlays on screen
        pygame.display.flip()                     # Redraw entire display

    def metaChangeLevel(self):
        # Check if player is on a meta-key connecting tile to another level
        for tile in self.level.metalevelTiles:
            if self.player._get_pos() == tile:
                newLevel = self.level.metalevelTiles[tile]['level']
                self.changeLevel(newLevel)

    def autoChangeLevel(self):
        # Check if player is on a connecting tile to another level
        for tile in self.level.autolevelTiles:
            if self.player._get_pos() == tile:
                newLevel = self.level.autolevelTiles[tile]['level']
                self.changeLevel(newLevel)

    def playAudio(self):
        for tile in self.level.audioTiles:
            if self.player._get_pos() == tile:
                audioFile = self.level.audioTiles[tile]['audiofile']
                start     = self.level.audioTiles[tile]['start']
                length    = self.level.audioTiles[tile]['length']
                lengthSecs = float(length) * 1000

                pygame.mixer.music.load('sound/' + audioFile)
                pygame.mixer.music.play(0, float(start))
                while pygame.mixer.music.get_pos() < lengthSecs:
                    pygame.time.Clock().tick(10)
                    continue
                pygame.mixer.music.stop()

    def main(self):
        """Run the main loop."""

        clock = pygame.time.Clock()
        mapState = gmap.Map("level.map")
        # Draw the whole screen initially
        self.screen.blit(mapState.background, (0, 0)) # Blit background on screen
        mapState.overlays.draw(self.screen)           # Blit overlays on screen
        pygame.display.flip()                     # Redraw entire display
        # The main game loop
        while not self.game_over:
            # Don't clear shadows and overlays, only sprites.
            self.sprites.clear(self.screen, self.background)
            self.sprites.update()
            # If the player's animation is finished, check for keypresses
            if self.player.animation is None:
                self.control()
                self.player.update()
            self.shadows.update()
            # Don't add shadows to dirty rectangles, as they already fit inside
            # sprite rectangles.
            self.shadows.draw(self.screen)
            dirty = self.sprites.draw(self.screen)
            # Don't add ovelays to dirty rectangles, only the places where
            # sprites are need to be updated, and those are already dirty.
            self.overlays.draw(self.screen)
            # Update only the dirty areas of the screen
            pygame.display.update(dirty)
            # Wait for one tick of the game clock
            clock.tick(GAME_FRAMERATE)
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    self.game_over = True
                elif event.type == pg.KEYDOWN:
                    self.pressed_key = event.key


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((424, 320)) # Screen Height, Width
    Game().main()
