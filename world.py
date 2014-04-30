#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Some code was taken from:
    http://qq.readthedocs.org/en/latest/tiles.html
    @copyright: 2008, 2009 Radomir Dopieralski <qq@sheep.art.pl>
    @license: BSD, see COPYING for details
"""

import sys
import pygame
import pygame.locals as pg
import gameMap as gmap

GAME_FRAMERATE = 50 # Frames per second
class Game(object):
    """The main game object."""

    def __init__(self, language):
        self.screen      = pygame.display.get_surface()
        self.pressed_key = None
        self.game_over   = False
        self.mapState = gmap.Map(language, "level.map")

    def control(self):
        """Handle the controls of the game."""

        keys = pygame.key.get_pressed()

        mods = pygame.key.get_mods()
        if mods & pg.KMOD_LSHIFT:
            GAME_FRAMERATE = 100 # Frames per second
        else:
            GAME_FRAMERATE = 50 # Frames per second

        def pressed(key):
            """Check if the specified key is pressed."""

            return self.pressed_key == key or keys[key]

        def walk(d):
            """Start walking in specified direction."""

            x, y = self.mapState.player.pos
            self.mapState.player.direction = d
            if not self.mapState.level.is_blocking(x+gmap.DX[d], y+gmap.DY[d]):
                self.mapState.player.animation = self.mapState.player.walk_animation() # moves player in direction d

            # Change level?
            self.autoChangeLevel()


        if pressed(pg.K_UP):
            walk(gmap.NORTH)
        elif pressed(pg.K_DOWN):
            walk(gmap.SOUTH)
        elif pressed(pg.K_LEFT):
            walk(gmap.WEST)
        elif pressed(pg.K_RIGHT):
            walk(gmap.EAST)
        # Play audio?
        if pressed(pg.K_SPACE):
            self.playAudio()
        # Change  Level?
        self.metaChangeLevel(pressed)
        self.pressed_key = None

    def changeLevel(self, level, newPlayerPos=(-1, -1)):
        # self.mapState.use_level(level, newPlayerPos)
        self.mapState.use_level(level)
        self.screen.blit(self.mapState.background, (0, 0)) # Blit background on screen
        self.mapState.overlays.draw(self.screen)           # Blit overlays on screen
        pygame.display.flip()                     # Redraw entire display

    def posParse(self, position):
        # Convert position string "(x, y)" to a tuple (x, y)
        item = 0
        items = []
        items.append("")
        for s in position:
            if s == " ":
                item += 1
                items.append("")
            items[item] += s
        return (str.strip(items[0]), str.strip(items[1]))

    def metaChangeLevel(self, pressed):
        # Check if player is on a meta-key connecting tile to another level
        for tile in self.mapState.level.metalevelTiles:
            if self.mapState.player._get_pos() == tile:
                metaKey = self.mapState.level.metalevelTiles[tile]['metakey']
                key = getattr(pg, metaKey)
                if pressed(key):
                    newLevel = self.mapState.level.metalevelTiles[tile]['level']
                    if 'nextpos' in self.mapState.level.metalevelTiles[tile]:
                        newPos   = self.mapState.level.metalevelTiles[tile]['nextpos']
                        newPos = self.posParse(newPos)
                    else:
                        newPos = (-1, -1)
                    self.changeLevel(newLevel, newPos)

    def autoChangeLevel(self):
        # Check if player is on a connecting tile to another level
        for tile in self.mapState.level.autolevelTiles:
            if self.mapState.player._get_pos() == tile:
                newLevel = self.mapState.level.autolevelTiles[tile]['level']
                if 'nextpos' in self.mapState.level.autolevelTiles[tile]:
                    newPos   = self.mapState.level.autolevelTiles[tile]['nextpos']
                    newPos = self.posParse(newPos)
                else:
                    newPos = (-1, -1)
                self.changeLevel(newLevel, newPos)

    def playAudio(self):
        for tile in self.mapState.level.audioTiles:
            if self.mapState.player._get_pos() == tile:
                audioFile = self.mapState.level.audioTiles[tile]['audiofile']
                start     = self.mapState.level.audioTiles[tile]['start']
                length    = self.mapState.level.audioTiles[tile]['length']
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
        # Draw the whole screen initially
        self.screen.blit(self.mapState.background, (0, 0)) # Blit background on screen
        self.mapState.overlays.draw(self.screen)           # Blit overlays on screen
        pygame.display.flip()                     # Redraw entire display

        # The main game loop
        while not self.game_over:
            # Don't clear shadows and overlays, only sprites.
            self.mapState.clearSprites(self.screen)

            # If the player's animation is finished, check for keypresses
            if self.mapState.player.animation is None:
                self.control()
                self.mapState.player.update()

            # Update sprites, shadows, and overlays
            self.mapState.updateSprites(self.screen, pygame.display)

            # Wait for one tick of the game clock
            clock.tick(GAME_FRAMERATE)

            # Process pygame events
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    self.game_over = True
                elif event.type == pg.KEYDOWN:
                    self.pressed_key = event.key

def use_error():
        print "Usage: "
        print sys.argv[0] + " [language]"
        print
        print "language can be spanish, ..."
        sys.exit(1)

if __name__ == "__main__":
    # Get language to use
    if len(sys.argv) < 2:
        use_error()
    language = sys.argv[1].lower()

    # Intitialize Pygame
    pygame.init()
    screenWidth  = gmap.MAP_TILE_WIDTH*15
    screenHeight = gmap.MAP_TILE_HEIGHT*15 # Screen Width, Height
    pygame.display.set_mode((screenWidth, screenHeight)) # Screen Width, Height

    # Initialize and start the game!
    Game(language).main()
