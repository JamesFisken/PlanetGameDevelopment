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

running = True
clock = pygame.time.Clock()

# time keeping variables
averageFPS = 1
fps = 10000
buffering = False
FPS = []
dt = 1  # delta time, so that the speed of the game isn't dependant on fps
timeMultiplier = 5000000

width, height = 1600, 900
scaleX, scaleY = width / 1920, height / 1080
scaleSize = min(width / 1920, height / 1080)


zoom = 1  # the higher the value the more zoomed in you are

#where the mouse is relative to the screen
relMouseX = width / 2
relMouseY = height / 2

# where in space the screen is observing
relScreenX = 0
relScreenY = 0


# constants
G_CONSTANT = 6.6743 * (10 ** -11)
SOLAR_MASS = 1.989 * 10 ** 30
TRUE_PIXEL_DISTANCE = 1515000000  # this number was calculated by taking the distance from the true sun to the earth and diving by 100, this means that 100 pixels will equate to the distance from earth to the sun

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

#GUI
PlanetSelectionLock = pygame.image.load('Sprites/PlanetSelectionlock.png').convert_alpha()
PlanetSelectionUnlock = pygame.image.load('Sprites/PlanetSelectionUnlock.png').convert_alpha()


# Transform sprites to the correct size
titleScreen = pygame.transform.scale(titleScreen, (width, height))
settingsScreen = pygame.transform.scale(settingsScreen, (width, height))
newGamePage = pygame.transform.scale(newGamePage, (width, height))
loadGamePage = pygame.transform.scale(loadGamePage, (width, height))

PlanetSelectionLock = pygame.transform.scale(PlanetSelectionLock, (110, 40))
PlanetSelectionUnlock = pygame.transform.scale(PlanetSelectionUnlock, (110, 40))

lockOffsetX = 0
lockOffsetY = 0
# classes
class CelestialBody:
    objs = []  # registrar

    def __init__(self, x, y, velX, velY, mass, radius, sprite, locked):
        CelestialBody.objs.append(self)

        self.x = x
        self.y = y
        self.trueX = x
        self.trueY = y

        self.velX = velX
        self.velY = velY

        self.forceX = 0
        self.forceY = 0

        self.zoom = zoom
        self.relMouseX = width/2
        self.relMouseY = height/2

        self.mass = mass
        self.radius = radius
        self.old_sprite = sprite
        self.sprite = pygame.transform.scale(sprite, (
            self.radius * self.zoom * 2.85,
            self.radius * self.zoom * 2.85))  # converts the size of the sprite to fit that of the planet's true radius

        self.locked = locked
        self.showOptions = False


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
        global lockOffsetX, lockOffsetY
        # Calculate the blit position based on the zoom
        blit_x = (self.x - (self.relMouseX*1)) * self.zoom + width/2
        blit_y = (self.y - (self.relMouseY*1)) * self.zoom + height/2

        if self.locked:
            lockOffsetX = blit_x - width/2
            lockOffsetY = blit_y - height/2

        # Blit the sprite to the screen
        self.trueX = blit_x - lockOffsetX
        self.trueY = blit_y - lockOffsetY
        screen.blit(self.sprite, (self.trueX - self.sprite.get_width() / 2, self.trueY - self.sprite.get_height() / 2))
        if self.showOptions:
            screen.blit(PlanetSelectionLock, (self.trueX - PlanetSelectionLock.get_width()/2, self.trueY - PlanetSelectionLock.get_height()/2))


        #pygame.draw.circle(screen, (255, 0, 0), (self.trueX, self.trueY), self.radius*self.zoom)


    def apply_gravity(self, otherBodies):
        netForceX = 0
        netForceY = 0
        for body in otherBodies:
            distance = math.sqrt((self.x - body.x) ** 2 + (self.y - body.y) ** 2) * TRUE_PIXEL_DISTANCE

            m1 = self.mass
            m2 = body.mass
            Force = (m1 * m2) / (distance ** 2) * G_CONSTANT

            normalizedDir = [(body.x - self.x) / distance, (body.y - self.y) / distance]

            netForceX += normalizedDir[0] * Force
            netForceY += normalizedDir[1] * Force

        self.forceX += netForceX
        self.forceY += netForceY
        return [netForceX, netForceY]

    def is_clicked(self, posx, posy):
        distance = math.sqrt(abs(self.trueX - posx) ** 2 + abs(self.trueY - posy) ** 2)
        if distance < self.radius*self.zoom:  # if the distance is less than the radius then the planet must be clicked
            return True
        else:
            return False

    @classmethod
    def change_zoom(cls, new_zoom, mouseX, mouseY):
        for obj in cls.objs:  # loop through all instances
            obj.relMouseX = mouseX
            obj.relMouseY = mouseY

            obj.zoom = obj.zoom + obj.zoom * new_zoom   # update zoom in a non-linear fashion
            obj.sprite = obj.old_sprite

            obj.sprite = pygame.transform.scale(obj.sprite, (
                obj.radius * obj.zoom * 2.85,
                obj.radius * obj.zoom * 2.85))  # converts the size of the sprite to fit that of the planet's true radius
    @classmethod
    def change_lock(cls, body):
        for obj in cls.objs:
            obj.locked = False
        body.locked = True


celestialBodies = []  # create a list to contain all planets
celestialBodies.append(CelestialBody(650, 450, 0, 0.00001280198, SOLAR_MASS * 0.000003, 30, Earth, True))
celestialBodies.append(CelestialBody(850, 450, 0, 0, SOLAR_MASS, 80, GasGiant, False))

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

def get_button(name, buttons):
    for button in buttons:
        if button.NAME == name:
            return button
    return False

buttons = gamebuttons.gather_buttons(scaleX, scaleY, scaleSize, screen)  # setups the buttons in the gamebuttons file
change_scene("onTitleScreen", gameState, buttons)  # start the game on the title screen

# Game loop.
while running:
    frameFPS = clock.get_fps()
    dt = clock.tick(fps) / 1000 * timeMultiplier  # find the amount of time between each frame in seconds,

    mouseX, mouseY = pygame.mouse.get_pos()  # gets user mouse inputs
    if gameState.get("onTitleScreen"):  # if user is on the title screen
        screen.blit(titleScreen, (0, 0))  # display the title screen
    elif gameState.get("onSettings"):
        screen.blit(settingsScreen, (0, 0))
    elif gameState.get("onGame"):
        screen.fill(BACKGROUND)

        for i, body in enumerate(celestialBodies):
            otherBodies = [x for j, x in enumerate(celestialBodies) if j != i]  # append planets excluding self
            body.apply_gravity(otherBodies)
            body.update()
            body.display()
            if body.showOptions:  # selected onto a planet
                button = get_button("lockToPlanet", buttons)
                button.x = body.trueX - 55
                button.y = body.trueY - 20

                button = get_button("upgradePlanet", buttons)
                button.x = body.trueX - 19
                button.y = body.trueY - 20

                button = get_button("deletePlanet", buttons)
                button.x = body.trueX + 18
                button.y = body.trueY - 20


        # CelestialBody.change_zoom(body.zoom + body.zoom*0.001)  # test to change the zoom each iteration

        # apply_gravity(p2, [p1])
    elif gameState.get("onLoadGame"):
        screen.blit(loadGamePage, (0, 0))
    elif gameState.get("onNewGame"):
        screen.blit(newGamePage, (0, 0))
    elif gameState.get("onPause"):
        print("Paused")

    for button in buttons:  # loop through all the game buttons
        if button.DETAILS == "LOCKED":
            if mouseX > button.startX + button.minVal and mouseX < button.startX + button.maxVal:
                button.x = mouseX
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
            if gameState.get("onGame"):  # if on the main game tab
                if event.button == 3:  # right click
                    #check to see if any planets have been clicked
                    for body in celestialBodies:
                        if body.is_clicked(mouseX, mouseY):
                            if body.showOptions:  # alternate whether the planets options are showing
                                body.showOptions = False
                                for button in buttons:
                                    if button.NAME == "lockToPlanet":
                                        button.active = False
                                    if button.NAME == "upgradePlanet":
                                        button.active = False
                                    if button.NAME == "deletePlanet":
                                        button.active = False
                            else:
                                for oBody in celestialBodies:  # turn all planet options off
                                    oBody.showOptions = False

                                body.showOptions = True  # turn selected planet option on
                                for button in buttons:
                                    if button.NAME == "lockToPlanet":
                                        button.active = True
                                    if button.NAME == "upgradePlanet":
                                        button.active = True
                                    if button.NAME == "deletePlanet":
                                        button.active = True
                            #body.showOptions = not body.showOptions


                elif event.button == 4:  # Scroll wheel up
                    CelestialBody.change_zoom(0.2, mouseX, mouseY)  # zoom increases
                elif event.button == 5:  # Scroll wheel down
                    CelestialBody.change_zoom(-0.2, mouseX, mouseY)  # zoom decreases

            # print(mouseX * scaleSize, mouseY * scaleSize)
            if event.button == 1:
                for button in buttons:
                    if button.active:
                        if button.is_clicked(mouseX, mouseY):

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

                            if button.NAME == "lockToPlanet":
                                for body in celestialBodies:
                                    if body.showOptions:
                                        body.change_lock(body)
                            if button.NAME == "deletePlanet":
                                for body in celestialBodies:
                                    if body.showOptions:
                                        celestialBodies.remove(body)


        elif event.type == MOUSEBUTTONUP:  # user unclicks
            for button in buttons:
                if button.active and button.DETAILS == "LOCKED":
                    button.DETAILS = "UNLOCKED"

    hovering = False
    for button in buttons:
        if button.is_clicked(
                mouseX, mouseY
        ) and button.active:  # checks if the mouse cursor is hovering over a button
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            hovering = True
            break
    if hovering is False:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    FPS.append(frameFPS)
    '''
    if (averageFPS - frameFPS)/averageFPS * 100 > 50:
        dt = -10 / 1000 * timeMultiplier
        print("here")
    '''

    if len(FPS) > 5000:
        averageFPS = sum(FPS) / len(FPS)
        print(averageFPS)
        FPS = []
    pygame.display.update()