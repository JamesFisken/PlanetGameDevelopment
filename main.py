#imports
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
fps = 10000000
running = True
clock = pygame.time.Clock()
dt = 1  #delta time, so that the speed of the game isn't dependant on fps

width, height = 1920, 1080
scaleX, scaleY = width / 1920, height / 1080
scaleSize = min(width / 1920, height / 1080)

screen = pygame.display.set_mode((width, height))

# Load sprites
titleScreen = pygame.image.load('Sprites/BaseScreens/TitleScreen.png').convert_alpha()
settingsScreen = pygame.image.load('Sprites/BaseScreens/Settings.png').convert_alpha()
# Transform sprites to the correct size
titleScreen = pygame.transform.scale(titleScreen, (width, height))
settingsScreen = pygame.transform.scale(settingsScreen, (width, height))
#classes


class Button:

    def __init__(self, NAME, TAG, DETAILS, minVal, maxVal, visible, x, y, *size):

        self.startX = x
        self.startY = y
        self.x = x
        self.y = y
        self.active = False

        self.visible = visible
        self.minVal = minVal
        self.maxVal = maxVal

        self.NAME = NAME
        self.TAG = TAG
        self.DETAILS = DETAILS

        if len(size) == 1:
            self.shape = "Circle"
            self.radius = size[0]
        elif len(size) == 2:
            self.shape = "Rectangle"
            self.xLength = size[0]
            self.yLength = size[1]

    def is_clicked(self, posx, posy):  # takes 2 positional arguments from a mouse click and checks whether the button would be clicked
        if self.shape == "Circle":  # if the button is circular
            distance = math.sqrt(abs(self.x - posx)**2 + abs(self.y - posy)**2)
            if distance < self.radius:  #if the distance is less than the radius then the button must be clicked
                return True
            else:
                return False
        if self.shape == "Rectangle":
            if posx > self.x and posx < self.x + self.xLength and posy > self.y and posy < self.y + self.yLength:
                return True
            else:
                return False

    def display(self):
        if self.visible:
            if self.shape == "Circle":
                pygame.draw.circle(screen, (0, 0, 255), (self.x, self.y),
                                   self.radius)
            if self.shape == "Rectangle":
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(self.x, self.y, self.xLength, self.yLength))



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


buttons = []  # will contain a list of all buttons in a particular scene
buttons.append(
    Button("PlayGame", "onTitleScreen", "", 0, 0, False, scaleX * 705, scaleY * 555,
           170 * scaleSize))
buttons.append(
    Button("LoadGame", "onTitleScreen", "", 0, 0, False, scaleX * 1487, scaleY * 568,
           115 * scaleSize))
buttons.append(
    Button("Settings", "onTitleScreen", "", 0, 0, False, scaleX * 1127, scaleY * 938,
           130 * scaleSize))

buttons.append(
    Button("ExitSettings", "onSettings", "", 0, 0, False, scaleX * 771, scaleY * 883,
           673 * scaleX, 155 * scaleY))
buttons.append(
    Button("GraphicsSlider", "onSettings", "", 0, 337*scaleX, True, scaleX * 1062, scaleY * 538,
           28 * scaleSize))
buttons.append(
    Button("VolumeSlider", "onSettings", "", 0, 337*scaleX, True, scaleX * 1062, scaleY * 673,
           28 * scaleSize))
print(gameState)
change_scene("onTitleScreen", gameState, buttons)
print(gameState)


#Game loop.
while running:

    posx, posy = pygame.mouse.get_pos()  # gets user mouse inputs
    if gameState.get("onTitleScreen"):  # if user is on the title screen
        screen.blit(titleScreen, (0, 0))  # display the title screen
    elif gameState.get("onLoad"):
        print("on load game screen")
    elif gameState.get("onSettings"):
        screen.blit(settingsScreen, (0, 0))
    elif gameState.get("onGame"):
        print("playing the main game")

    for button in buttons:
        if button.DETAILS == "LOCKED":
            if posx > button.startX + button.minVal and posx < button.startX + button.maxVal:
                button.x = posx
        if button.active:
            button.display()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:  # user clicks
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

    # Draw.

    dt = clock.tick(fps) / 1000
    print(dt)
    pygame.display.update()