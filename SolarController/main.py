# imports
import sys
import math
import pygame
from pygame.locals import *
import gamebuttons

# Colours
BACKGROUND = (5, 10, 51)

# General Variables
game_state = {
    "on_title_screen": False,
    "on_game": False,
    "on_settings": False,
    "on_new_game": False,
    "on_load_game": False,
    "on_pause": False
}

# Pygame Variables and setup
pygame.init()

running = True
clock = pygame.time.Clock()

# time keeping variables
average_fps = 1
fps = 10000
buffering = False
fps_list = []
dt = 1  # delta time, so that the speed of the game isn't dependent on fps
time_multiplier = 5000000

width, height = 1600, 900
scale_x, scale_y = width / 1920, height / 1080
scale_size = min(width / 1920, height / 1080)

zoom = 1  # the higher the value the more zoomed in you are

# where the mouse is relative to the screen
rel_mouse_x = width / 2
rel_mouse_y = height / 2

panning = False
# where in space the screen is observing
rel_screen_x = 0
rel_screen_y = 0

# constants
G_CONSTANT = 6.6743 * (10 ** -11)
SOLAR_MASS = 1.989 * 10 ** 30
TRUE_PIXEL_DISTANCE = 1515000000  # this number was calculated by taking the distance from the true sun to the earth and dividing by 100, this means that 100 pixels will equate to the distance from earth to the sun

screen = pygame.display.set_mode((width, height))

# Load sprites
# backgrounds
title_screen = pygame.image.load('Sprites/BaseScreens/TitleScreen.png').convert_alpha()
settings_screen = pygame.image.load('Sprites/BaseScreens/Settings.png').convert_alpha()
new_game_page = pygame.image.load('Sprites/BaseScreens/NewGamePage.png').convert_alpha()
load_game_page = pygame.image.load('Sprites/BaseScreens/LoadGamePage.png').convert_alpha()

# sprites
earth = pygame.image.load('Sprites/Earth2.png').convert_alpha()
gas_giant = pygame.image.load('Sprites/GasGiant2.png').convert_alpha()

# GUI
shop_panel = pygame.image.load('Sprites/Shop/ShopPanel.png').convert_alpha()
open_shop = pygame.image.load('Sprites/Shop/OpenShop.png').convert_alpha()
planet_selection_lock = pygame.image.load('Sprites/PlanetSelectionlock.png').convert_alpha()
planet_selection_unlock = pygame.image.load('Sprites/PlanetSelectionUnlock.png').convert_alpha()


# Transform sprites to the correct size
title_screen = pygame.transform.scale(title_screen, (width, height))
settings_screen = pygame.transform.scale(settings_screen, (width, height))
new_game_page = pygame.transform.scale(new_game_page, (width, height))
load_game_page = pygame.transform.scale(load_game_page, (width, height))

planet_selection_lock = pygame.transform.scale(planet_selection_lock, (110, 40))
planet_selection_unlock = pygame.transform.scale(planet_selection_unlock, (110, 40))
shop_panel = pygame.transform.scale(shop_panel, (scale_x*450, scale_y*1047))
open_shop = pygame.transform.scale(open_shop, (scale_x*220, scale_y*220))
# global varianles
lock_offset_x = 0
lock_offset_y = 0

camera_offset_x = 0
camera_offset_y = 0
start_pan_x = 0
start_pan_y = 0

planet_locked = True  # if there is a planet that is locked
shop = False # shows if on shop
# classes
class CelestialBody:
    objs = []  # registrar

    def __init__(self, x, y, vel_x, vel_y, mass, radius, sprite, locked):
        CelestialBody.objs.append(self)

        self.x = x
        self.y = y
        self.true_x = x
        self.true_y = y
        self.camera_offset_x = 0
        self.camera_offset_y = 0

        self.vel_x = vel_x
        self.vel_y = vel_y

        self.force_x = 0
        self.force_y = 0

        self.zoom = zoom
        self.rel_mouse_x = width / 2
        self.rel_mouse_y = height / 2

        self.mass = mass
        self.radius = radius
        self.old_sprite = sprite
        self.sprite = pygame.transform.scale(sprite, (
            self.radius * self.zoom * 2.85,
            self.radius * self.zoom * 2.85))  # converts the size of the sprite to fit that of the planet's true radius

        self.locked = locked
        self.show_options = False

    def update(self):
        accel_x = self.force_x / self.mass
        accel_y = self.force_y / self.mass

        self.vel_x += accel_x * dt
        self.vel_y += accel_y * dt

        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        self.force_x = 0
        self.force_y = 0

        pixels.append([self.x, self.y])

    def display(self):
        global lock_offset_x, lock_offset_y, camera_offset_x, camera_offset_y, planet_locked
        # Calculate the blit position based on the zoom
        blit_x = (self.x - (self.rel_mouse_x * 1)) * self.zoom + width / 2
        blit_y = (self.y - (self.rel_mouse_y * 1)) * self.zoom + height / 2

        if self.locked:  # if locked on a planet, centre it to the screen
            lock_offset_x = blit_x - width / 2
            lock_offset_y = blit_y - height / 2

        # Blit the sprite to the screen
        self.true_x = blit_x - lock_offset_x
        self.true_y = blit_y - lock_offset_y
        if not planet_locked:  # in panning state
            self.true_x -= camera_offset_x
            self.true_y -= camera_offset_y

        screen.blit(self.sprite,
                    (self.true_x - self.sprite.get_width() / 2, self.true_y - self.sprite.get_height() / 2))
        if self.show_options:
            if self.locked:  # if the user is locked onto the planet then display the unlock icon
                screen.blit(planet_selection_unlock, (
                    self.true_x - planet_selection_unlock.get_width() / 2,
                    self.true_y - planet_selection_unlock.get_height() / 2))
            else:
                screen.blit(planet_selection_lock, (
                    self.true_x - planet_selection_lock.get_width() / 2,
                    self.true_y - planet_selection_lock.get_height() / 2))

    def apply_gravity(self, other_bodies):
        net_force_x = 0
        net_force_y = 0
        for body in other_bodies:
            distance = math.sqrt((self.x - body.x) ** 2 + (self.y - body.y) ** 2) * TRUE_PIXEL_DISTANCE

            m1 = self.mass
            m2 = body.mass
            force = (m1 * m2) / (distance ** 2) * G_CONSTANT

            normalized_dir = [(body.x - self.x) / distance, (body.y - self.y) / distance]

            net_force_x += normalized_dir[0] * force
            net_force_y += normalized_dir[1] * force

        self.force_x += net_force_x
        self.force_y += net_force_y
        return [net_force_x, net_force_y]

    def is_clicked(self, pos_x, pos_y):
        distance = math.sqrt(abs(self.true_x - pos_x) ** 2 + abs(self.true_y - pos_y) ** 2)
        if distance < self.radius * self.zoom:  # if the distance is less than the radius then the planet must be clicked
            return True
        else:
            return False

    @classmethod
    def change_zoom(cls, new_zoom, mouse_x, mouse_y):
        for obj in cls.objs:  # loop through all instances
            obj.rel_mouse_x = mouse_x
            obj.rel_mouse_y = mouse_y

            obj.zoom = obj.zoom + obj.zoom * new_zoom  # update zoom in a non-linear fashion
            obj.sprite = obj.old_sprite

            obj.sprite = pygame.transform.scale(obj.sprite, (
                obj.radius * obj.zoom * 2.85,
                obj.radius * obj.zoom * 2.85))  # converts the size of the sprite to fit that of the planet's true radius

    @classmethod
    def change_lock(cls, body):
        for obj in cls.objs:
            obj.locked = False
        if body is not None:
            body.locked = True


celestial_bodies = []  # create a list to contain all planets
celestial_bodies.append(CelestialBody(650, 450, 0, 0.00001280198, SOLAR_MASS * 0.000003, 30, earth, True))
celestial_bodies.append(CelestialBody(850, 450, 0, 0, SOLAR_MASS, 80, gas_giant, False))

pixels = []


def change_scene(newScene, gameState, buttons):
    for key in gameState.keys():
        if key == newScene:
            gameState[key] = True
        else:
            gameState[key] = False
    for button in buttons:
        if button.tag == newScene:
            button.active = True
        else:
            button.active = False
    get_button("close_shop", buttons).active = False  # make the shop closed button disabled


def get_button(name, buttons):
    for button in buttons:
        if button.name == name:
            return button
    return False

#pre-loop setup
buttons = gamebuttons.gather_buttons(scale_x, scale_y, scale_size, screen)  # setups the buttons in the gamebuttons file
change_scene("on_title_screen", game_state, buttons)  # start the game on the title screen

# Game loop.
while running:
    frame_fps = clock.get_fps()
    dt = clock.tick(fps) / 1000 * time_multiplier  # find the amount of time between each frame in seconds

    mouse_x, mouse_y = pygame.mouse.get_pos()  # gets user mouse inputs
    if game_state.get("on_title_screen"):  # if user is on the title screen
        screen.blit(title_screen, (0, 0))  # display the title screen
    elif game_state.get("on_settings"):
        screen.blit(settings_screen, (0, 0))
    elif game_state.get("on_game"):
        screen.fill(BACKGROUND)

        for i, body in enumerate(celestial_bodies):
            other_bodies = [x for j, x in enumerate(celestial_bodies) if j != i]  # append planets excluding self
            body.apply_gravity(other_bodies)
            body.update()
            body.display()
            if body.show_options:  # selected onto a planet
                button = get_button("lock_to_planet", buttons)
                button.x = body.true_x - 55
                button.y = body.true_y - 20

                button = get_button("upgrade_planet", buttons)
                button.x = body.true_x - 19
                button.y = body.true_y - 20

                button = get_button("delete_planet", buttons)
                button.x = body.true_x + 18
                button.y = body.true_y - 20
        if shop:  # if the shop is open then display the shop
            screen.blit(shop_panel, (15*scale_x, 15*scale_y))
        else:
            screen.blit(open_shop, (138*scale_x, 810*scale_y))

    elif game_state.get("on_load_game"):
        screen.blit(load_game_page, (0, 0))
    elif game_state.get("on_new_game"):
        screen.blit(new_game_page, (0, 0))
    elif game_state.get("on_pause"):
        print("Paused")

    for button in buttons:  # loop through all the game buttons
        if button.details == "LOCKED":
            if mouse_x > button.start_x + button.min_val and mouse_x < button.start_x + button.max_val:
                button.x = mouse_x
        if button.active and button.visible:
            if button.shape == "Circle":
                pygame.draw.circle(screen, (0, 0, 255), (button.x, button.y), button.radius)
            if button.shape == "Rectangle":
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(button.x, button.y, button.x_length, button.y_length))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:  # user clicks
            if game_state.get("on_game"):  # if on the main game tab
                if event.button == 1:  # left click
                    if panning is False:
                        start_pan_x = mouse_x + camera_offset_x
                        start_pan_y = mouse_y + camera_offset_y

                    panning = True
                    pass
                if event.button == 3:  # right click
                    # check to see if any planets have been clicked
                    for body in celestial_bodies:
                        if body.is_clicked(mouse_x, mouse_y):
                            if body.show_options:  # alternate whether the planet's options are showing
                                body.show_options = False
                                for button in buttons:
                                    if button.name == "lock_to_planet":
                                        button.active = False
                                    if button.name == "upgrade_planet":
                                        button.active = False
                                    if button.name == "delete_planet":
                                        button.active = False
                            else:
                                for o_body in celestial_bodies:  # turn off all planet options
                                    o_body.show_options = False

                                body.show_options = True  # turn selected planet option on

                                for button in buttons:
                                    if button.name == "lock_to_planet":
                                        button.active = True
                                    if button.name == "upgrade_planet":
                                        button.active = True
                                    if button.name == "delete_planet":
                                        button.active = True
                            # body.showOptions = not body.showOptions

                elif event.button == 4:  # Scroll wheel up
                    CelestialBody.change_zoom(0.2, mouse_x, mouse_y)  # zoom increases
                elif event.button == 5:  # Scroll wheel down
                    CelestialBody.change_zoom(-0.2, mouse_x, mouse_y)  # zoom decreases

            # print(mouse_x * scale_size, mouse_y * scale_size)
            if event.button == 1:
                for button in buttons:  # loop through buttons
                    if button.active:
                        if button.is_clicked(mouse_x, mouse_y):

                            if button.name == "settings":
                                change_scene("on_settings", game_state, buttons)
                                break

                            if button.name == "exit_settings":
                                change_scene("on_title_screen", game_state, buttons)
                                break

                            if button.name == "graphics_slider":
                                button.details = "LOCKED"
                                break
                            if button.name == "volume_slider":
                                button.details = "LOCKED"
                                break

                            if button.name == "new_game":
                                change_scene("on_new_game", game_state, buttons)
                                break

                            if button.name == "load_game":
                                change_scene("on_load_game", game_state, buttons)
                                break

                            if button.name == "back_to_title_screen":
                                change_scene("on_title_screen", game_state, buttons)
                                break

                            if button.name == "start_load_game1":
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_load_game2":
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_load_game3":
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_new_game1":
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_new_game2":
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_new_game3":
                                change_scene("on_game", game_state, buttons)

                            #shop buttons

                            if button.name == "open_shop" and not shop:
                                get_button("close_shop", buttons).active = True
                                shop = True
                                button.active = False
                            if button.name == "close_shop" and shop:
                                get_button("open_shop", buttons).active = True
                                shop = False
                                button.active = False

                            #planet buttons


                            if button.name == "lock_to_planet":
                                for body in celestial_bodies:
                                    if body.show_options:
                                        if body.locked:
                                            body.change_lock(None)
                                            planet_locked = False  # show that the user isn't locked onto any planet
                                            # centre for seemless transition between panning mode and locked mode
                                            start_pan_x = width/2 - 38
                                            start_pan_y = height/2 - 4
                                        else:
                                            body.change_lock(body)
                                            planet_locked = True
                            if button.name == "delete_planet":
                                for body in celestial_bodies:
                                    if body.show_options:  # if this is the planet that the user is selected on
                                        if body.locked:
                                            planet_locked = False  # if the planet is also locked then go into panning mode

                                        celestial_bodies.remove(body)  # remove planet

        elif event.type == MOUSEBUTTONUP:  # user unclicks
            panning = False
            for button in buttons:
                if button.active and button.details == "LOCKED":
                    button.details = "UNLOCKED"
    #print(panning)
    if panning:
        camera_offset_x = start_pan_x - mouse_x
        camera_offset_y = start_pan_y - mouse_y
    hovering = False
    for button in buttons:
        if button.is_clicked(
                mouse_x, mouse_y
        ) and button.active:  # checks if the mouse cursor is hovering over a button
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            hovering = True
            break
    if hovering is False:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    fps_list.append(frame_fps)
    if len(fps_list) > 2500:
        average_fps = sum(fps_list) / len(fps_list)
        print(average_fps)
        fps_list = []
    pygame.display.update()