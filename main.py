
#imports
import sys
import math
import pygame
from pygame.locals import *

# Colours
BACKGROUND = (5, 10, 51)

# General Variables

gameState = {
    "onTitleScreen": False,
    "onGame": False,
    "onSettings": False,
    "onLoad": False
}


# Pygame Variables and setup
pygame.init()
fps = 60
fpsClock = pygame.time.Clock()

width, height = 640, 480
screen = pygame.display.set_mode((width, height))

# Game loop.
while True:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Update.

    # Draw.
    if gameState.get("onTitleScreen"):
        print("on title screen")
    elif gameState.get("onLoad"):
        print("on load game screen")
    elif gameState.get("onSettings"):
        print("on settings")
    elif gameState.get("onGame"):
        print("playing the main game")


    pygame.display.flip()
    fpsClock.tick(fps)