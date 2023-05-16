import pygame
import math
class Button:
    def __init__(self, NAME, TAG, DETAILS, minVal, maxVal, visible, x, y, *size):

        self.startX = x  # used to base the range off of this constant, since the actual x/y may vary
        self.startY = y
        self.x = x
        self.y = y
        self.active = False

        self.visible = visible
        self.minVal = minVal  # if the button is a slider, then this value will be the minimum amount the slider can move to the left from its starting X
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

    def is_clicked(self, posx,
                   posy):  # takes 2 positional arguments from a mouse click and checks whether the button would be clicked
        if self.shape == "Circle":  # if the button is circular
            distance = math.sqrt(abs(self.x - posx) ** 2 + abs(self.y - posy) ** 2)
            if distance < self.radius:  # if the distance is less than the radius then the button must be clicked
                return True
            else:
                return False
        if self.shape == "Rectangle":
            if posx > self.x and posx < self.x + self.xLength and posy > self.y and posy < self.y + self.yLength:
                return True
            else:
                return False

def gather_buttons(scaleX, scaleY, scaleSize, screen):
    buttons = []
    buttons.append(
        Button("NewGame", "onTitleScreen", "", 0, 0, False, scaleX * 705, scaleY * 555,
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
        Button("GraphicsSlider", "onSettings", "", 0, 337 * scaleX, True, scaleX * 1062, scaleY * 538,
               28 * scaleSize))
    buttons.append(
        Button("VolumeSlider", "onSettings", "", 0, 337 * scaleX, True, scaleX * 1062, scaleY * 673,
               28 * scaleSize))

    buttons.append(
        Button("BackToTitleScreen", "onNewGame", "", 0, 0, False, scaleX * 684, scaleY * 918,
               917 * scaleX, 163 * scaleY))
    buttons.append(
        Button("StartNewGame1", "onNewGame", "", 0, 0, False, scaleX * 703, scaleY * 556,
               173 * scaleSize))
    buttons.append(
        Button("StartNewGame2", "onNewGame", "", 0, 0, False, scaleX * 1144, scaleY * 556,
               173 * scaleSize))
    buttons.append(
        Button("StartNewGame3", "onNewGame", "", 0, 0, False, scaleX * 1586, scaleY * 556,
               173 * scaleSize))

    buttons.append(
        Button("BackToTitleScreen", "onLoadGame", "", 0, 0, False, scaleX * 684, scaleY * 918,
               917 * scaleX, 163 * scaleY))
    buttons.append(
        Button("StartLoadGame1", "onLoadGame", "", 0, 0, False, scaleX * 703, scaleY * 556,
               173 * scaleSize))
    buttons.append(
        Button("StartLoadGame2", "onLoadGame", "", 0, 0, False, scaleX * 1144, scaleY * 556,
               173 * scaleSize))
    buttons.append(
        Button("StartLoadGame3", "onLoadGame", "", 0, 0, False, scaleX * 1586, scaleY * 556,
               173 * scaleSize))
    return buttons

