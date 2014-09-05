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
from logic.gamemap import Map
import logic.gamemap as gmap

GAME_FRAMERATE = 70 # Frames per second
SUPPORTED_LANGUAGES = ["Spanish", "French"]
INITIAL_MAP = gmap.MAP_DIR + "house.map"

class Game(object):
    """The main game object."""

    def __init__(self, lang, initial_map, screen_width, screen_height):
        # Intitialize Pygame
        pygame.init()
        pygame.display.set_mode((screen_width, screen_height))

        self.screen = pygame.display.get_surface()
        self.pressed_key = None
        self.game_over = False
        self.map_state = Map(lang, initial_map)

    def control(self):
        """Handle the controls of the game."""

        keys = pygame.key.get_pressed()

        """
        mods = pygame.key.get_mods()
        if mods & pg.KMOD_LSHIFT:
            GAME_FRAMERATE = 100 # Frames per second
        else:
            GAME_FRAMERATE = 50 # Frames per second
            """

        def pressed(key):
            """Check if the specified key is pressed."""

            return self.pressed_key == key or keys[key]

        def walk(direction):
            """Start walking in specified direction."""

            # Get current player coordinates
            x_coord, y_coord = self.map_state.player.pos
            # Set player direction
            self.map_state.player.direction = direction


            # If not walking into a wall
            if not self.map_state.level.is_blocking(x_coord+gmap.DX[direction],
                                                    y_coord+gmap.DY[direction]):
                # Walking animation and actual coord movement
                walking = self.map_state.player.walk()
                # Walk in specified direction
                self.map_state.player.animation = walking

            # Change level?
            self.auto_change_level()

        if pressed(pg.K_UP):
            walk(gmap.NORTH)
        elif pressed(pg.K_DOWN):
            walk(gmap.SOUTH)
        elif pressed(pg.K_LEFT):
            walk(gmap.WEST)
        elif pressed(pg.K_RIGHT):
            walk(gmap.EAST)
        # Possibly play audio
        if pressed(pg.K_SPACE):
            self.play_audio()
        # Possibly change level
        self.meta_change_level(pressed)
        self.pressed_key = None

    # def change_level(self, level, new_player_pos=(-1, -1)):
    def change_level(self, level, from_tile=None):
        """ Change level, and update background and player position """

        # self.map_state.use_level(level, new_player_pos)
        self.map_state.use_level(gmap.MAP_DIR + level, from_tile)
        # Blit background and overlays on screen
        self.screen.blit(self.map_state.background, (0, 0))
        self.map_state.overlays.draw(self.screen)
        # Redraw entire display
        pygame.display.flip()

    def meta_change_level(self, pressed):
        """ Move player if on a meta-key tile connecting to another level"""
        level_state = self.map_state.level
        for tile in level_state.metaleveltiles:
            if self.map_state.player.pos == tile:
                meta_tile = level_state.metaleveltiles[tile]
                # Get the metakey required for the tile
                metakey = meta_tile['metakey']
                key = getattr(pg, metakey)
                # If player has pressed required key:
                if pressed(key):
                    new_level = meta_tile['level']
                    self.change_level(new_level, meta_tile)

    def auto_change_level(self):
        """ Check if player is on a connecting tile to another level """
        level_state = self.map_state.level
        for tile in level_state.autoleveltiles:
            if self.map_state.player.pos == tile:
                auto_tile = level_state.autoleveltiles[tile]
                new_level = auto_tile['level']
                self.change_level(new_level, auto_tile)

    def play_audio(self):
        """ Play audio if player on audio tile """
        for tile in self.map_state.level.audio_tiles:
            if self.map_state.player.pos == tile:
                audio_file = self.map_state.level.audio_tiles[tile]['audiofile']
                start = self.map_state.level.audio_tiles[tile]['start']
                length = self.map_state.level.audio_tiles[tile]['length']
                length_mili_secs = float(length) * 1000

                pygame.mixer.music.load('resources/sound/' + audio_file)
                pygame.mixer.music.play(0, float(start))
                while pygame.mixer.music.get_pos() < length_mili_secs:
                    pygame.time.Clock().tick(10)
                    continue
                pygame.mixer.music.stop()

    def main(self):
        """Run the main loop."""

        clock = pygame.time.Clock()

        # Draw the whole screen initially
        # Blit background and overlays on screen
        self.screen.blit(self.map_state.background, (0, 0))
        self.map_state.overlays.draw(self.screen)
        # Redraw entire display
        pygame.display.flip()

        # The main game loop
        while not self.game_over:
            # Don't clear shadows and overlays, only sprites.
            self.map_state.clear_sprites(self.screen)

            # If the player's animation is finished, check for keypresses
            if self.map_state.player.animation is None:
                self.control()
                self.map_state.player.update()

            # Update sprites, shadows, and overlays
            self.map_state.update_sprites(self.screen, pygame.display)

            # Wait for one tick of the game clock
            clock.tick(GAME_FRAMERATE)

            # Process pygame events
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    self.game_over = True
                elif event.type == pg.KEYDOWN:
                    self.pressed_key = event.key

def use_error():
    """ Prints error message if this is used incorrectly """
    print "Usage: "
    print sys.argv[0] + " [language]"
    print
    print "language can be:"
    print SUPPORTED_LANGUAGES
    sys.exit(1)

if __name__ == "__main__":
    print sys.modules
    # Get language to use
    if len(sys.argv) < 2:
        use_error()
    LANGUAGE = sys.argv[1].lower()

    # Make screen 15 tiles wide and 15 tiles high
    SCREEN_WIDTH = gmap.MAP_TILE_WIDTH*15
    SCREEN_HEIGHT = gmap.MAP_TILE_HEIGHT*15

    # Initialize and start the game!
    Game(LANGUAGE, INITIAL_MAP, SCREEN_WIDTH, SCREEN_HEIGHT).main()
