#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Tool to view the game maps """

import sys
sys.path.append('../')
sys.path.append('../languages')

import pygame
import pygame.locals as pg
from logic import gamemap as gmap

def use_error():
    """ Prints error message if tool is used incorrectly """
    print "Usage: "
    print sys.argv[0] + " <map>"


if __name__ == "__main__":
    if len(sys.argv) < 1:
        use_error()

    MAP = sys.argv[1]

    SCREEN_WIDTH = gmap.MAP_TILE_WIDTH*15
    SCREEN_HEIGHT = gmap.MAP_TILE_HEIGHT*15
    LANGUAGE = "spanish"

    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    SCREEN = pygame.display.get_surface()
    MAP_STATE = gmap.Map(LANGUAGE, MAP)

    while True:
        SCREEN.blit(MAP_STATE.background, (0, 0))
        MAP_STATE.overlays.draw(SCREEN)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pg.QUIT:
                sys.exit()
