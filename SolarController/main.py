# imports
import sys
import math
import pygame
from pygame.locals import *
import random
import time
import gamebuttons
from sklearn import preprocessing
import numpy as np

# Colours
BACKGROUND = (5, 10, 51)

# General Variables

gameState = {
    "onTitleScreen": False,
    "onGame": False,
    "onSettings": False,
    "onNewGame": False,
    "onLoadGame": False,
    "onPause": False
}

# Pygame Variables and setup
pygame.init()
fps = 500
running = True
clock = pygame.time.Clock()

dt = 1  # delta time, so that the speed of the game isn't dependant on fps
timeMultiplier = 3


width, height = 1600, 900
scaleX, scaleY = width / 1920, height / 1080
scaleSize = min(width / 1920, height / 1080)

# constants
G_CONSTANT = 6.6743 * (10 ** -11)
SOLAR_MASS = 1.989 * 10 ** 30

screen = pygame.display.set_mode((width, height))

# Load sprites
# backgrounds
titleScreen = pygame.image.load('Sprites/BaseScreens/TitleScreen.png').convert_alpha()
settingsScreen = pygame.image.load('Sprites/BaseScreens/Settings.png').convert_alpha()
newGamePage = pygame.image.load('Sprites/BaseScreens/NewGamePage.png').convert_alpha()
loadGamePage = pygame.image.load('Sprites/BaseScreens/LoadGamePage.png').convert_alpha()

# sprites
Earth = pygame.image.load('Sprites/Earth2.png').convert_alpha()
GasGiant = pygame.image.load('Sprites/GasGiant2.png').convert_alpha()

# Transform sprites to the correct size
titleScreen = pygame.transform.scale(titleScreen, (width, height))
settingsScreen = pygame.transform.scale(settingsScreen, (width, height))
newGamePage = pygame.transform.scale(newGamePage, (width, height))
loadGamePage = pygame.transform.scale(loadGamePage, (width, height))


# classes
class CelestialBody:
    def __init__(self, x, y, velX, velY, mass, radius, sprite):
        self.x = x
        self.y = y

        self.velX = velX
        self.velY = velY

        self.forceX = 50
        self.forceY = 0

        self.mass = mass
        self.radius = radius
        self.sprite = pygame.transform.scale(sprite, (
            radius, radius))  # converts the size of the sprite to fit that of the planets true radius



    def update(self):
        accelX = self.forceX / self.mass
        accelY = self.forceY / self.mass

        self.velX += accelX * dt
        self.velY += accelY * dt

        self.x += self.velX * dt
        self.y += self.velY * dt

        self.forceX = 0
        self.forceY = 0
        pixels.append([self.x, self.y])


    def display(self):
        for x in pixels:
            pygame.draw.circle(screen,(255, 0, 0), (x[0], x[1]), 2)
        screen.blit(self.sprite, (self.x - self.sprite.get_width() / 2, self.y - self.sprite.get_height() / 2))
        # pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y),
        # self.radius * 0.3)

    def apply_gravity(self, otherBodies):
        netForceX = 0
        netForceY = 0
        for body in otherBodies:  # loop through all the other planets/suns excluding the planet your looking at
            distance = math.sqrt(((self.x - body.x) ** 2 + (
                    self.y - body.y) ** 2))  # calculate the distance between the 2 planets
            m1 = self.mass
            m2 = body.mass

            # dir = math.atan2(body.x - self.x, body.y - self.y)
            Force = (m1 * m2) / (distance ** 2) * G_CONSTANT  # calculate the total force


            normalizedDir = preprocessing.normalize(np.array([(body.x - self.x), (body.y - self.y)]).reshape(1,
                                                                                                             -1))  # normalize the distances, so that they can act as a direction

            # split the direction into x and y components and then multiply by the force
            netForceX += normalizedDir[0][0] * Force
            netForceY += normalizedDir[0][1] * Force

        self.forceX += netForceX
        self.forceY += netForceY

        return [netForceX, netForceY]


p1 = CelestialBody(400, 450, 0, 40, 100, 200, GasGiant)
p2 = CelestialBody(800, 450, 0, 0, SOLAR_MASS*0.00000000000001, 200, Earth)  # sun
p3 = CelestialBody(1000, 450, 0, 70, 80, 100, Earth)  # sun
pixels = []

def change_scene(newScene, gameState, buttons):
    for key in gameState.keys():
        if key == newScene:
            gameState[key] = True
        else:
            gameState[key] = False
    for button in buttons:
        if button.TAG == newScene:
            button.active = True
        else:
            button.active = False


buttons = gamebuttons.gather_buttons(scaleX, scaleY, scaleSize, screen)  # setups the buttons in the gamebuttons file
change_scene("onTitleScreen", gameState, buttons)  # start the game on the title screen

# Game loop.
while running:

    posx, posy = pygame.mouse.get_pos()  # gets user mouse inputs
    if gameState.get("onTitleScreen"):  # if user is on the title screen
        screen.blit(titleScreen, (0, 0))  # display the title screen
    elif gameState.get("onSettings"):
        screen.blit(settingsScreen, (0, 0))
    elif gameState.get("onGame"):
        screen.fill(BACKGROUND)

        p2.update()
        p2.display()
        p2.apply_gravity([p1])
        p1.update()
        p1.display()
        p1.apply_gravity([p2])

        p3.update()
        p3.display()
        p3.apply_gravity([p2])

        # apply_gravity(p2, [p1])
    elif gameState.get("onLoadGame"):
        screen.blit(loadGamePage, (0, 0))
    elif gameState.get("onNewGame"):
        screen.blit(newGamePage, (0, 0))
    elif gameState.get("onPause"):
        print("Paused")

    for button in buttons:  # loop through all the game buttons
        if button.DETAILS == "LOCKED":
            if posx > button.startX + button.minVal and posx < button.startX + button.maxVal:
                button.x = posx
        if button.active and button.visible:
            if button.shape == "Circle":
                pygame.draw.circle(screen, (0, 0, 255), (button.x, button.y),
                                   button.radius)
            if button.shape == "Rectangle":
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(button.x, button.y, button.xLength, button.yLength))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:  # user clicks
            # print(posx * scaleSize, posy * scaleSize)
            for button in buttons:
                if button.active:
                    if button.is_clicked(posx, posy):

                        if button.NAME == "Settings":
                            change_scene("onSettings", gameState, buttons)
                            break

                        if button.NAME == "ExitSettings":
                            change_scene("onTitleScreen", gameState, buttons)
                            break

                        if button.NAME == "GraphicsSlider":
                            button.DETAILS = "LOCKED"
                            break
                        if button.NAME == "VolumeSlider":
                            button.DETAILS = "LOCKED"
                            break

                        if button.NAME == "NewGame":
                            change_scene("onNewGame", gameState, buttons)
                            break

                        if button.NAME == "LoadGame":
                            change_scene("onLoadGame", gameState, buttons)
                            break

                        if button.NAME == "BackToTitleScreen":
                            change_scene("onTitleScreen", gameState, buttons)
                            break

                        if button.NAME == "StartLoadGame1":
                            change_scene("onGame", gameState, buttons)
                        if button.NAME == "StartLoadGame2":
                            change_scene("onGame", gameState, buttons)
                        if button.NAME == "StartLoadGame3":
                            change_scene("onGame", gameState, buttons)
                        if button.NAME == "StartNewGame1":
                            change_scene("onGame", gameState, buttons)
                        if button.NAME == "StartNewGame2":
                            change_scene("onGame", gameState, buttons)
                        if button.NAME == "StartNewGame3":
                            change_scene("onGame", gameState, buttons)


        elif event.type == MOUSEBUTTONUP:  # user unclicks

            for button in buttons:
                if button.active and button.DETAILS == "LOCKED":
                    button.DETAILS = "UNLOCKED"

    hovering = False
    for button in buttons:
        if button.is_clicked(
                posx, posy
        ) and button.active:  # checks if the mouse cursor is hovering over a button
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            hovering = True
            break
    if hovering is False:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # Update.
    dt = clock.tick(fps) / 1000 * timeMultiplier  # find the amount of time between each frame in seconds,

    print("FPS:", int(clock.get_fps()))

    pygame.display.update()