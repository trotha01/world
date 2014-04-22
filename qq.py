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
        self.mapState = gmap.Map("level.map")

    def control(self):
        """Handle the controls of the game."""

        keys = pygame.key.get_pressed()

        def pressed(key):
            """Check if the specified key is pressed."""

            return self.pressed_key == key or keys[key]

        def walk(d):
            """Start walking in specified direction."""

            x, y = self.mapState.player.pos
            self.mapState.player.direction = d
            if not self.mapState.level.is_blocking(x+spr.DX[d], y+spr.DY[d]):
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
            self.metaChangeLevel()
        self.pressed_key = None

    def changeLevel(self, level):
        self.mapState.use_level(gmap.Level(level))
        self.screen.blit(self.mapState.background, (0, 0)) # Blit background on screen
        self.mapState.overlays.draw(self.screen)           # Blit overlays on screen
        pygame.display.flip()                     # Redraw entire display

    def metaChangeLevel(self):
        # Check if player is on a meta-key connecting tile to another level
        for tile in self.mapState.level.metalevelTiles:
            if self.mapState.player._get_pos() == tile:
                newLevel = self.mapState.level.metalevelTiles[tile]['level']
                self.changeLevel(newLevel)

    def autoChangeLevel(self):
        # Check if player is on a connecting tile to another level
        for tile in self.mapState.level.autolevelTiles:
            if self.mapState.player._get_pos() == tile:
                newLevel = self.mapState.level.autolevelTiles[tile]['level']
                self.changeLevel(newLevel)

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
            self.mapState.sprites.clear(self.screen, self.mapState.background)
            self.mapState.sprites.update()
            # If the player's animation is finished, check for keypresses
            if self.mapState.player.animation is None:
                self.control()
                self.mapState.player.update()
            self.mapState.shadows.update()
            # Don't add shadows to dirty rectangles, as they already fit inside
            # sprite rectangles.
            self.mapState.shadows.draw(self.screen)
            dirty = self.mapState.sprites.draw(self.screen)
            # Don't add ovelays to dirty rectangles, only the places where
            # sprites are need to be updated, and those are already dirty.
            self.mapState.overlays.draw(self.screen)
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
