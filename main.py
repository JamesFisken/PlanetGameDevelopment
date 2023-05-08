# imports
import sys
import math
import pygame
from pygame.locals import *
import random
import time

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
running = True
clock = pygame.time.Clock()
dt = 1  # delta time, so that the speed of the game isn't dependant on fps

width, height = 640, 480
screen = pygame.display.set_mode((width, height))


# classes

class Button:
    def __init__(self, x, y, *size):
        self.x = x
        self.y = y

        if len(size) == 1:
            self.shape = "Circle"
            self.radius = size
        elif len(size) == 2:
            self.shape = "Rectangle"
            self.xLength = size[0]
            self.yLength = size[1]


x = 0
# Game loop.
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Update.

    # Draw.
    if gameState.get("onTitleScreen"):
        screen.blit("")
    elif gameState.get("onLoad"):
        print("on load game screen")
    elif gameState.get("onSettings"):
        print("on settings")
    elif gameState.get("onGame"):
        print("playing the main game")

    x += 100 * dt
    pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(x, 50, 50, 50))
    dt = clock.tick(fps) / 1000
    pygame.display.flip()

