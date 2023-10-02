# imports
import random
import sys
import math
import time
import gamebuttons
import copy
from loadimages import *  # starts up pygame and loads necessary images
import numpy as np
import threading
import pickle
from pygame.locals import *

# Pygame Variables and setup
running = True
clock = pygame.time.Clock()
# screen
width, height = 1920, 1080
screen = pygame.display.set_mode((width, height))

# time keeping variables
is_paused = False
average_fps = 1
fps = 144
fps_list = []
dt = 1  # delta time, so that the speed of the game isn't dependent on fps
time_multiplier = 37630000  # this sets the speed of the game(varies)
starting_time = 150000000  # held constant
speed_multiplier = 0.5  # speed starts halfway

# zoom
zoom = 0.3  # the higher the value the more zoomed in you are
min_zoom = 0.05
max_zoom = 1.25

# where the mouse is relative to the screen and thus where the zooms focus will be
rel_mouse_x = width / 2
rel_mouse_y = height / 2

# constants
G_CONSTANT = 6.6743 * (10 ** -11)
SOLAR_MASS = 1.989 * 10 ** 30  # mass of the sun
TRUE_PIXEL_DISTANCE = 1515000000  # this number was calculated by taking the distance from the true sun to the earth and dividing by 100, this means that 100 pixels will equate to the distance from earth to the sun

# position calculation variables
# this will be a value that changes the positions of all planets so that the locked planet is centered
lock_offset_x = 0
lock_offset_y = 0

# this is where the camera is relative to the starting scene(moves with panning)
camera_offset_x = 0
camera_offset_y = 0

start_pan_x = 0
start_pan_y = 0
panning = True

planet_locked = True  # if there is a planet that is locked then it is true
shop = False  # shows if on shop
shop_page = 1  # shows current shop page

balance = 5000  # players starting balance

planet_place_click = 0  # used to record the state of a planet after buying it (0 = placement phase)
placing_planet = False  # describes if a planet is being placed

# saves
save_slot = None  # records what save slot a user is saving to

# fonts
balance_text = balance_font.render(str(balance), True, (255, 255, 255))
fade_text = []  # holds instances of animated(fading) text

# screen dictionary
game_state = {
    "on_title_screen": False,
    "on_game": False,
    "on_settings": False,
    "on_new_game": False,
    "on_load_game": False,
    "on_pause": False
}


def save_game(game_data, slot):
    filename = f"save_slot_{slot}.dat"
    pickled_list = copy.copy(game_data)  # create a copy of the game

    # encode unpicklable objects to a pickalable string
    for instance in pickled_list:
        instance.sprite_size = instance.sprite.get_size()
        instance.old_sprite_size = instance.old_sprite.get_size()
        instance.sprite = pygame.image.tostring(instance.sprite, "RGBA")
        instance.old_sprite = pygame.image.tostring(instance.old_sprite, "RGBA")

    total_save_data = [pickled_list, [], balance, zoom]  # saves planets along with additional game data
    with open(filename, 'wb') as save_file:
        pickle.dump(total_save_data, save_file)  # dumps information to the file


def load_game(slot):
    global balance
    global zoom
    filename = f"save_slot_{slot}.dat"
    try:
        with open(filename, 'rb') as save_file:  # open save file location
            game_data = pickle.load(save_file)  # retrieve data

            # decode back to objects
            for instance in game_data[0]:
                instance.sprite = pygame.image.fromstring(instance.sprite, instance.sprite_size, "RGBA")
                instance.old_sprite = pygame.image.fromstring(instance.old_sprite, instance.old_sprite_size, "RGBA")

            CelestialBody.objs = CelestialBody.objs + game_data[0]
            change_balance(game_data[2] - balance)  # change balance to the loaded balance
            zoom = game_data[3]  # change zoom to the loaded zoom
            return game_data[0]
    except FileNotFoundError:
        return celestial_bodies  # if there is no save, then use default celestial bodies



def update_lock_offset(locked_planet):
    global lock_offset_x, lock_offset_y
    # if a planet is locked, centre it to the screen and globalize that value as the basis to move all other objects and backgrounds relative to it
    # Calculate the blit position based on the zoom
    blit_x = (locked_planet.x - (rel_mouse_x * 1)) * zoom + width / 2
    blit_y = (locked_planet.y - (rel_mouse_y * 1)) * zoom + height / 2

    lock_offset_x = blit_x - width / 2
    lock_offset_y = blit_y - height / 2


def display(x, y):
    global lock_offset_x, lock_offset_y, camera_offset_x, camera_offset_y, planet_locked
    # Calculate the blit position based on the zoom
    blit_x = (x - (rel_mouse_x * 1)) * zoom + width / 2
    blit_y = (y - (rel_mouse_y * 1)) * zoom + height / 2

    # Blit the sprite to the screen
    true_x = blit_x - lock_offset_x
    true_y = blit_y - lock_offset_y
    if not planet_locked:  # in panning state
        true_x -= camera_offset_x
        true_y -= camera_offset_y

    return true_x, true_y


def is_approximately_equal(value1, value2, tolerance):
    return abs(value1 - value2) <= tolerance


def calculate_opposite_angle(angle):  # calculates the opposite angle(in radians)
    opposite_angle = angle + math.pi
    if opposite_angle > math.pi:
        opposite_angle -= 2 * math.pi
    return opposite_angle


class FadingText:  # class that creates instances of fading text
    def __init__(self, screen, text, font, fade_in_duration, hold_duration, fade_out_duration, x, y, position):
        self.screen = screen
        self.text = font.render(text, True, (255, 255, 255))
        self.fade_in_duration = fade_in_duration
        self.hold_duration = hold_duration
        self.fade_out_duration = fade_out_duration
        self.total_duration = fade_in_duration + hold_duration + fade_out_duration

        self.text_alpha = 0
        self.animation_thread = threading.Thread(target=self._animate_text, daemon=True)  # start thread
        self.animation_thread.start()

        self.x = x
        self.y = y

    def _animate_text(self):
        start_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time

            if elapsed_time < self.fade_in_duration:
                self.text_alpha = int((elapsed_time / self.fade_in_duration) * 255)
            elif elapsed_time < self.fade_in_duration + self.hold_duration:
                self.text_alpha = 255
            elif elapsed_time < self.total_duration:
                remaining_time = elapsed_time - (self.fade_in_duration + self.hold_duration)
                self.text_alpha = int((1 - remaining_time / self.fade_out_duration) * 255)
            else:
                break  # Exit the animation loop when one cycle is complete
            if dt != 0:
                time.sleep(1 / dt)  # Sleep for 1 frame

        # Delete the instance after completing one cycle
        fade_text.remove(self)
        del self

    def show(self):
        self.screen.blit(self.text, (self.x - self.text.get_width() // 2, self.y - self.text.get_height() // 2))
        self.text.set_alpha(self.text_alpha)


class OverwriteDict:
    def __init__(self):
        self.data = {}

    def add_or_overwrite(self, key, value):
        self.data[value] = key

    def get_key(self, value):
        return self.data.get(value)

    def __str__(self):
        return str(self.data)


class ShopCard:
    def __init__(self, name, cost, page, position, image_afford, image_unafford):
        self.name = name
        self.cost = cost
        self.page = page
        self.position = position
        self.image_afford = image_afford
        self.image_unafford = image_unafford

        self.x = 23 * scale_x
        self.y = (200 * scale_x) * position + 208 * scale_y

    def display(self, page, balance):
        if self.page == page:
            if self.cost <= balance:
                screen.blit(self.image_afford, (self.x, self.y))
            else:
                screen.blit(self.image_unafford, (self.x, self.y))


class CelestialBody:
    objs = []  # registrar

    def __init__(self, x, y, vel_x, vel_y, mass, radius, sprite, locked, name, orbit_value):
        CelestialBody.objs.append(self)
        self.name = name  # identifyer

        # enviromental position (doesn't change with camera)
        self.x = x
        self.y = y

        # True onscreen blitted position (changes with zoom and camera)
        self.true_x = x
        self.true_y = y
        self.camera_offset_x = 0
        self.camera_offset_y = 0

        self.vel_x = vel_x
        self.vel_y = vel_y

        self.force_x = 0
        self.force_y = 0

        self.mass = mass
        self.radius = radius
        self.old_sprite = sprite

        if self.name == "Sun":
            self.sprite = pygame.transform.scale(sprite, (
                self.radius * zoom * 4.5,
                self.radius * zoom * 4.5))  # converts the size of the sprite to fit that of the sun's true radius
        else:
            self.sprite = pygame.transform.scale(sprite, (
                self.radius * zoom * 2.65,
                self.radius * zoom * 2.65))  # converts the size of the sprite to fit that of the planet's true radius

        self.locked = locked
        self.show_options = False

        # orbit related class variables
        self.forces = OverwriteDict()  # used to find orbital parent

        self.angle = None  # the angle at which a full orbit takes place
        self.opp_angle = None  # the angle at which half a full orbit takes place, used as a checkpoint before full orb

        self.orbital_parent = None  # planet that self is orbiting around if one exists
        self.cleared_checkpoint = False  # set to true once a planet has passed self.opp_angle

        self.orbit_value = orbit_value  # amount of money a player earns for an orbit of this planet

        self.sprite_size = None
        self.old_sprite_size = None

    def update(self):
        # rearranged f=ma to a = f/m
        accel_x = self.force_x / self.mass
        accel_y = self.force_y / self.mass

        # integrate acceleration to get velocity
        self.vel_x += accel_x * dt
        self.vel_y += accel_y * dt

        # add velocity
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        #reset force after it has been exerted
        self.force_x = 0
        self.force_y = 0

    def display(self):

        # Calculate the blit position based on the zoom
        blit_x = (self.x - (rel_mouse_x * 1)) * zoom + width / 2
        blit_y = (self.y - (rel_mouse_y * 1)) * zoom + height / 2

        # Blit the sprite to the screen
        self.true_x = blit_x - lock_offset_x
        self.true_y = blit_y - lock_offset_y
        if not planet_locked:  # in panning state
            self.true_x -= camera_offset_x
            self.true_y -= camera_offset_y

        if self.locked:  # if planet is locked then blit it to the center of the screen
            screen.blit(self.sprite,
                        (width / 2 - self.sprite.get_width() / 2, height / 2 - self.sprite.get_height() / 2))
        else:
            screen.blit(self.sprite,
                        (self.true_x - self.sprite.get_width() / 2, self.true_y - self.sprite.get_height() / 2))

        # pygame.draw.circle(screen, (255, 0, 0), (self.true_x, self.true_y), self.radius*zoom)  # show hitbox(debug)
        if self.show_options:
            if self.locked:  # if the user is locked onto the planet then display the unlock icon
                screen.blit(planet_selection_unlock, (
                    width / 2 - planet_selection_unlock.get_width() / 2,
                    height / 2 - planet_selection_unlock.get_height() / 2))
            else:  # else display the lock icon to the center
                screen.blit(planet_selection_lock, (
                    self.true_x - planet_selection_lock.get_width() / 2,
                    self.true_y - planet_selection_lock.get_height() / 2))

    def apply_gravity(self, other_bodies):
        if not other_bodies:
            return [0, 0], None  # Return None when no other bodies

        positions = np.array([(body.x, body.y) for body in other_bodies])
        masses = np.array([body.mass for body in other_bodies])

        differences = positions - np.array([self.x, self.y])
        distances = np.linalg.norm(differences, axis=1) * TRUE_PIXEL_DISTANCE

        distances[distances < 10 * TRUE_PIXEL_DISTANCE] = 10 * TRUE_PIXEL_DISTANCE
        forces = G_CONSTANT * self.mass * masses / distances ** 2  # calculate the forces applied on a particular planet

        normalized_dirs = differences / distances[:, np.newaxis]  # find net direction
        net_force = np.sum(normalized_dirs * forces[:, np.newaxis], axis=0)  # find net force

        max_force_index = np.argmax(forces)  # Index of the planet with the greatest force(for orbit detection)

        prev_value = self.orbital_parent
        if other_bodies[max_force_index].mass >= self.mass:
            self.orbital_parent = other_bodies[max_force_index]

        if prev_value != self.orbital_parent:
            self.angles = []

        self.force_x += net_force[0]  # update forces
        self.force_y += net_force[1]

        return net_force.tolist()

    def check_collisions(self, other_bodies):
        for body in other_bodies:
            if self.name != "debris" or body.name != "debris":  # stops collisions with collided objects(optional)
                distance = math.sqrt((self.x - body.x) ** 2 + (self.y - body.y) ** 2)  # calculate distance between bods
                if (body.radius + self.radius) > distance:  # if distance less than sum of radii then collision occurs
                    create_collided_planet(self, body)
                    return [True, self, body]
        return [False]

    def is_clicked(self, pos_x, pos_y):
        distance = math.sqrt(abs(self.true_x - pos_x) ** 2 + abs(self.true_y - pos_y) ** 2)
        if distance < self.radius * zoom:  # if the distance is less than the radius then the planet must be clicked
            return True
        else:
            return False

    def check_for_orbit(self):
        if self.orbital_parent in celestial_bodies:  # checks to see if the orbital_parent still exists
            if self.name != "debris":  # makes sure that debris aren't counted as they have no orbital value

                # calculate delta position
                dx = self.x - self.orbital_parent.x
                dy = self.y - self.orbital_parent.y

                # using trigonometry to calculate angle in radians
                angle_radians = math.atan2(dy, dx)

                if self.angle is None:  # set the starting angle
                    self.angle = angle_radians
                    self.opp_angle = calculate_opposite_angle(
                        angle_radians)  # find the opposite angle as a sort of checkpoint
                    return

                if not self.cleared_checkpoint:  # hasn't passed orbit mid_point
                    if is_approximately_equal(angle_radians, self.opp_angle, 0.05):  # if passed checkpoint
                        self.cleared_checkpoint = True

                else:
                    if is_approximately_equal(angle_radians, self.angle, 0.05):  # if completed full orbit
                        self.cleared_checkpoint = False

                        change_balance(self.orbit_value)  # reward user for the orbit
            else:
                self.angles = []

    @classmethod
    def update_zoom(cls, mouse_x, mouse_y, update_mouse):
        global rel_mouse_x, rel_mouse_y
        for obj in cls.objs:  # loop through all instances
            if update_mouse:
                # updates mouse position
                rel_mouse_x = mouse_x
                rel_mouse_y = mouse_y

            # uses a copy of the original sprite to avoid image deterioration
            obj.sprite = obj.old_sprite

            if obj.name == "Sun":
                obj.sprite = pygame.transform.scale(obj.sprite, (
                    obj.radius * zoom * 4.5,
                    obj.radius * zoom * 4.5))  # converts the size of the sprite to fit that of the sun's true radius
            else:
                obj.sprite = pygame.transform.scale(obj.sprite, (
                    obj.radius * zoom * 2.65,
                    obj.radius * zoom * 2.65))  # converts the size of the sprite to fit that of the planet's true radi

    @classmethod
    def change_lock(cls, body):
        for obj in cls.objs:
            obj.locked = False
        if body is not None:
            body.locked = True


celestial_bodies = []  # create a list to contain all planets on scene
avaiable_celestial_bodies = []  # this list will contain all celestial bodies able to get in this game
shop_cards = []  # create a list to contain all shop cards
celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS, 450, sun, True, "Sun", 0))

pixels = []
# create shop cards
shop_cards.append(ShopCard("Moon", 350, 1, 0, moon_card_afford, moon_card_unafford))
shop_cards.append(ShopCard("Earth", 900, 1, 1, earth_card_afford, earth_card_unafford))
shop_cards.append(ShopCard("Satellite", 2600, 1, 2, satellite_card_afford, satellite_card_unafford))
shop_cards.append(ShopCard("Jupiter", 9500, 1, 3, jupiter_card_afford, jupiter_card_unafford))

shop_cards.append(ShopCard("Lux Aurantius", 30000, 2, 0, luxaurantius_card_afford, luxaurantius_card_unafford))
shop_cards.append(ShopCard("Ondori", 50000, 2, 1, ondori_card_afford, ondori_card_unafford))
shop_cards.append(ShopCard("Malakorus", 80000, 2, 2, malakorus_card_afford, malakorus_card_unafford))
shop_cards.append(ShopCard("Enduros", 150000, 2, 3, enduros_card_afford, enduros_card_unafford))

# create pre-made celestial_bodies
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0000010, 5, vulkan, False, "Debris", 0))
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0000010, 18, moon, False, "Moon", 40))
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0005000, 40, earth, False, "Earth", 110))
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0000001, 8, satellite, False, "Satellite", 315))
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0100000, 55, jupiter, False, "Jupiter", 1100))
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0150000, 70, luxaurantius, False, "Lux Aurantius", 3600))
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0175000, 90, ondori, False, "Ondori", 7500))
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0200000, 130, malakorus, False, "Malakorus", 12000))
avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0300000, 160, enduros, False, "Enduros", 30000))

def get_button(name, buttons):
    for button in buttons:
        if button.name == name:
            return button
    return False

def select_button(buttons, function):
    for button in buttons:
        if button.name == "lock_to_planet":
            button.active = function
        if button.name == "upgrade_planet":
            button.active = function
        if button.name == "delete_planet":
            button.active = function


def change_shop(status):  # opens/closes shop and activates/deactivates various buttons
    global shop
    get_button("close_shop", buttons).active = status
    get_button("open_shop", buttons).active = not status
    shop = status
    # enable other shop sprites
    get_button("shop_page_1", buttons).active = status
    get_button("shop_page_2", buttons).active = status
    get_button("shop_page_3", buttons).active = status
    get_button("shop_page_4", buttons).active = status
    get_button("buy_1", buttons).active = status
    get_button("buy_2", buttons).active = status
    get_button("buy_3", buttons).active = status
    get_button("buy_4", buttons).active = status


def change_scene(newScene, gameState, buttons):  # function that changes the scene using the game_state dictionary
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
    change_shop(False)


def convert_to_blit_coords(x_pos, y_pos, sprite_width, sprite_height):
    # takes the true coordinates on the pygame screen and converts them to the game's coordinate setting
    if not planet_locked:
        x = ((
                     x_pos - width / 2 + lock_offset_x + camera_offset_x + sprite_width / 2) / zoom) + rel_mouse_x - sprite_width / 2 / zoom
        y = ((
                     y_pos - height / 2 + lock_offset_y + camera_offset_y + sprite_height / 2) / zoom) + rel_mouse_y - sprite_height / 2 / zoom
    else:
        x = ((
                     x_pos - width / 2 + lock_offset_x + sprite_width / 2) / zoom) + rel_mouse_x - sprite_width / 2 / zoom
        y = ((
                     y_pos - height / 2 + lock_offset_y + sprite_width / 2) / zoom) + rel_mouse_y - sprite_height / 2 / zoom
    return x, y


def scale_number(num):
    # function that squishes very small numbers between 0 and 0.9, similar to the RELU function
    if num < 1e-12:
        return 0
    elif num > 1e-6:
        return 0.9
    else:
        scaled_num = (num - 1e-12) / (1e-6 - 1e-12) * 0.9
        return round(scaled_num, 4)


def add_debris_nearby(x1, y1, r1, r2, num_circles):
    circles = []
    safety = 4
    orbit = 0  # counter variable for the number ob debris in an orbit
    distance_offset = 0  # Offset to expand the placement area
    min_distance = r1 + r2 + safety + distance_offset  # Minimum distance between the circles

    # Generate a random angle
    start_angle = random.uniform(0, 2 * math.pi)
    # calculate the angle that a piece of debris occupies using the cosine rule
    angle_size = math.acos((min_distance ** 2 + min_distance ** 2 - (2 * r2) ** 2) / (2 * min_distance ** 2))
    num_orbits = math.floor(2 * math.pi / angle_size)
    angle_size = 2 * math.pi / num_orbits  # spreads them out more so that they fit uniformly

    for i in range(num_circles):
        if orbit == num_orbits:
            distance_offset += r2 + safety
            min_distance = r1 + r2 + safety + distance_offset  # Minimum distance between the circles
            orbit = 0
            # calculate the angle that a piece of debris occupies using the cosine rule
            angle_size = math.acos((min_distance ** 2 + min_distance ** 2 - (2 * r2) ** 2) / (2 * min_distance ** 2))
            num_orbits = math.floor(2 * math.pi / angle_size)
            angle_size = 2 * math.pi / num_orbits  # spreads them out more so that they fit uniformly

        valid_position = False
        while not valid_position:
            # Calculate the new circle's position
            x2 = x1 + (min_distance + distance_offset) * math.cos(start_angle + angle_size * i)
            y2 = y1 + (min_distance + distance_offset) * math.sin(start_angle + angle_size * i)

            valid_position = True
            orbit += 1

        circles.append((x2, y2))
    return circles


def create_collided_planet(body1, body2):
    total_mass = body1.mass + body2.mass
    total_area = (math.pi * (body1.radius ** 2) + math.pi * (body2.radius ** 2))

    if body1.mass >= body2.mass:
        main_body = body1
    elif body1.mass <= body2.mass:
        main_body = body2
    valuation = main_body.orbit_value
    name = main_body.name

    # impact is essientially the difference in momentum which will result in the number of fragments
    impact_violence = (abs(body1.vel_x - body2.vel_x) + abs(body1.vel_y - body2.vel_y)) * (
            min(body1.mass, body2.mass) / max(body1.mass, body2.mass)) ** 2

    # stretch impact violence between 0 and 1 so that it can be used as a percentage
    impact_violence = scale_number(impact_violence)
    inverse_impact_violence = 1 - impact_violence

    '''
    if the mass of the collision is so minute then don't allow them to split
    also don't allow them to split if there are too many planets

    '''
    if total_area < 10000 or total_mass < 5e+26 or len(celestial_bodies) > 500:
        impact_violence = 0
        inverse_impact_violence = 1

    # v' = (m1v1 + m2v2)/m1 + m2 calculate velocity based on the conservation of momentum
    vel_x = (body1.mass * body1.vel_x + body2.mass * body2.vel_x) / (body1.mass + body2.mass)
    vel_y = (body1.mass * body1.vel_y + body2.mass * body2.vel_y) / (body1.mass + body2.mass)

    # calculate a weighted average based on mass
    pos_x = (body1.x * body1.mass + body2.x * body2.mass) / (body1.mass + body2.mass)
    pos_y = (body1.y * body1.mass + body2.y * body2.mass) / (body1.mass + body2.mass)

    # calculate increase in radius
    new_radius = math.sqrt((total_area * inverse_impact_violence) / math.pi)

    # calculate detariation in value
    valuation *= new_radius / max(body1.radius, body2.radius)

    # spawn in the main bulk of the planet
    new_planet = CelestialBody(pos_x, pos_y, vel_x, vel_y, total_mass * inverse_impact_violence, new_radius,
                               main_body.old_sprite,
                               False, name, round(valuation))

    new_planet.show_options = main_body.show_options  # keep the options value to the major planet
    new_planet.locked = main_body.locked  # keep the locked value to the major planet
    # various orbit information
    new_planet.angle = main_body.angle  # the angle at which a full orbit takes place
    new_planet.opp_angle = main_body.opp_angle  # the angle at which half a full orbit takes place, used as a checkpoint before full orb
    new_planet.orbital_parent = main_body.orbital_parent  # planet that self is orbiting around if one exists
    new_planet.cleared_checkpoint = main_body.cleared_checkpoint  # set to true once a planet has passed self.opp_angle

    # substract area and mass off to account for the main bulk of the
    total_mass -= (total_mass * inverse_impact_violence)
    total_area -= (total_area * inverse_impact_violence)

    celestial_bodies.append(new_planet)
    CelestialBody.objs.append(new_planet)

    #calculate amount of debris  n = 10x
    amount_of_debris = round(10 * impact_violence)
    if amount_of_debris > 0:
        debris_radius = math.sqrt((total_area / amount_of_debris) / math.pi)
        debris_positions = add_debris_nearby(pos_x, pos_y, new_radius, debris_radius, amount_of_debris)
        for x in range(amount_of_debris):
            debris_x, debris_y = debris_positions[x]  # allocate the precalculated positions of debris
            '''
            velocity of the debris is determined on 3 factors
            -given the velocity of the main bulk of the planet calculated previously
            - added the velocity of the difference between the position of the debris and the main bulk which 
            contributes to the explosive outward looking affect
            - small randomness to incite intresting behaviour among fragments(new orbits and collisions)
            '''
            debris_vel_x = vel_x + ((debris_x - pos_x) * 0.000000027) + random.uniform(-1, 1) * 0.0000006
            debris_vel_y = vel_y + ((debris_y - pos_y) * 0.000000027) + random.uniform(-1, 1) * 0.0000006

            new_debris = CelestialBody(debris_x, debris_y, debris_vel_x, debris_vel_y, total_mass / amount_of_debris,
                                       debris_radius, vulkan, False, "debris", 0)
            celestial_bodies.append(new_debris)
            CelestialBody.objs.append(new_debris)
    # update zoom on new planets
    CelestialBody.update_zoom(mouse_x, mouse_y, False)


def draw_dotted_line(surface, start_point, end_point, start_distance, dot_radius, dot_distance,
                     line_color=(255, 255, 255)):
    # Calculate the direction vector of the line
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]

    # Calculate the length of the line
    length = max(abs(dx), abs(dy))

    # Calculate the step values for each axis
    try:
        x_step = dx / length
        y_step = dy / length
    except:
        x_step = dx / 0.000001
        y_step = dy / 0.000001

    # Draw the dotted line
    x = start_point[0]
    y = start_point[1]
    for _ in range(int(length / dot_distance)):
        if math.sqrt((x - start_point[0]) ** 2 + (y - start_point[1]) ** 2) > start_distance:
            pygame.draw.circle(surface, line_color, (int(x), int(y)), dot_radius)
        x += x_step * dot_distance
        y += y_step * dot_distance


def round_upwards(value, rounding_value):
    return (value // rounding_value) * (rounding_value)


def display_background(transformed_space_screen):
    sprite_width = transformed_space_screen.get_width()
    sprite_height = transformed_space_screen.get_height()

    start_x, start_y = display(0, 0)  # relative starting coords to base the rest of the backgrounds off of.
    top_left = convert_to_blit_coords(0, 0, 0, 0)  # finds what the top left of the screens planetary coordinates are.
    bottom_right = convert_to_blit_coords(width + sprite_width, height + sprite_height, 0, 0)

    x1, y1 = (round_upwards(top_left[0] * zoom, sprite_width), round_upwards(top_left[1] * zoom, sprite_height))
    x2, y2 = (round_upwards(bottom_right[0] * zoom, sprite_width), round_upwards(bottom_right[1] * zoom, sprite_height))

    # loop through all the x and y positions of where the background is meant to be displayed
    for x in range(round((x2 - x1) / sprite_width)):
        for y in range(round((y2 - y1) / sprite_height)):
            screen.blit(transformed_space_screen,
                        ((x1 + start_x) + sprite_width * x, ((y1 + start_y) + sprite_height * y)))

def buy_planet(position):
    global placing_planet, planet_name
    for card in shop_cards:
        if card.page == shop_page and card.position == position:
            if balance >= card.cost:
                change_balance(-card.cost)
                change_shop(False)  # close shop
                placing_planet = True
                planet_name = card.name

def change_balance(change_amount):
    # changes the users balance and starts the animation text
    global balance, balance_text

    if change_amount >= 0:
        text_string = "+" + str(change_amount)  # add positive sign
    else:
        text_string = str(change_amount)

    balance += change_amount  #increase/decrease balance
    balance_text = balance_font.render(str(balance), True, (255, 255, 255))
    fade_text.append(FadingText(screen, text_string, income_font, 1000, 100, 500, 1730 * scale_x,
                                980 * scale_y + len(fade_text) * -45 * scale_y, "empty"))


# pre-loop setup
buttons = gamebuttons.gather_buttons(scale_x, scale_y, scale_size)  # setups the buttons in the gamebuttons file
change_scene("on_title_screen", game_state, buttons)  # start the game on the title screen

counter = 0
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
        start = time.time()

        # update the lockoffset which will be used for positioning planets and the background relative to a lockedplanet
        for body in celestial_bodies:
            if body.locked == True:
                update_lock_offset(body)

        transformed_space_screen = pygame.transform.scale(space_screen, (
            space_screen.get_width() * zoom, space_screen.get_height() * zoom))  # scale the background
        display_background(transformed_space_screen)  # displays the infinitely tiled space background

        for i, body in enumerate(celestial_bodies):
            other_bodies = [x for j, x in enumerate(celestial_bodies) if j != i]  # append planets excluding self
            collision = body.check_collisions(other_bodies)
            if collision[0]:
                celestial_bodies.remove(collision[1])  # remove original planets
                celestial_bodies.remove(collision[2])

        for i, body in enumerate(celestial_bodies):  # loop through each planet
            other_bodies = [x for j, x in enumerate(celestial_bodies) if
                            j != i and x.mass > SOLAR_MASS * 0.000010]  # append planets excluding self
            if len(other_bodies) > 0:
                body.apply_gravity(other_bodies)  # apply gravity to the planet
                body.check_for_orbit()  # check planet for orbit
            body.update()  # update velocity of the planet
            body.display()  # display planet

            if body.show_options:  # selected onto a planet
                # positioning of the planet menu buttons
                button = get_button("lock_to_planet", buttons)
                button.x = body.true_x - 55 * scale_x
                button.y = body.true_y - 20 * scale_y

                button = get_button("upgrade_planet", buttons)
                button.x = body.true_x - 19 * scale_x
                button.y = body.true_y - 20 * scale_y

                button = get_button("delete_planet", buttons)
                button.x = body.true_x + 18 * scale_x
                button.y = body.true_y - 20 * scale_y

        if placing_planet:
            for planet in avaiable_celestial_bodies:
                if planet.name == planet_name and planet_place_click == 0:
                    half_opacity_sprite = planet.sprite.copy()  # might need to be optimized
                    half_opacity_sprite.set_alpha(128)  # 50% opacity (128 out of 255)
                    screen.blit(half_opacity_sprite,
                                (mouse_x - planet.sprite.get_width() / 2, mouse_y - planet.sprite.get_height() / 2))
                if planet.name == planet_name and planet_place_click == 1:
                    half_opacity_sprite = planet.sprite.copy()  # might need to be optimized
                    half_opacity_sprite.set_alpha(128)  # 50% opacity (128 out of 255)
                    screen.blit(half_opacity_sprite, (
                        placement_x - planet.sprite.get_width() / 2, placement_y - planet.sprite.get_height() / 2))
                    # pygame.draw.line(screen, (255, 255, 255), (placement_x, placement_y), (mouse_x, mouse_y), 3)
                    distance = math.sqrt((placement_x - mouse_x) ** 2 + (placement_y - mouse_y) ** 2)
                    draw_dotted_line(screen, (placement_x, placement_y), (mouse_x, mouse_y), (planet.radius + 5) * zoom,
                                     20 * zoom, (distance + 1) * 0.3 * zoom)
                if planet.name == planet_name and planet_place_click == 2:
                    # add a new planet
                    new_planet = copy.copy(planet)

                    x, y = convert_to_blit_coords(placement_x, placement_y, new_planet.sprite.get_width(),
                                                  new_planet.sprite.get_height())
                    x2, y2 = convert_to_blit_coords(mouse_x, mouse_y, new_planet.sprite.get_width(),
                                                    new_planet.sprite.get_height())

                    new_planet.x = x
                    new_planet.y = y
                    if planet_locked:
                        for mass in celestial_bodies:
                            if mass.locked:
                                add_vel_x = mass.vel_x
                                add_vel_y = mass.vel_y
                                break
                        # if locked on a planet add that planets velocity along with the difference in (x,y)/constant
                        new_planet.vel_x = ((x2 - x) / 150000000) + add_vel_x
                        new_planet.vel_y = ((y2 - y) / 150000000) + add_vel_y
                    else:
                        new_planet.vel_x = (x2 - x) / 150000000
                        new_planet.vel_y = (y2 - y) / 150000000

                    #  clear planet orbit and forces
                    new_planet.orbit_positions = []
                    new_planet.forces = []

                    celestial_bodies.append(new_planet)
                    # add to register
                    CelestialBody.objs.append(new_planet)

                    # reset planet setting variable
                    planet_place_click = 0
                    placing_planet = False

        if shop:  # if the shop is open then display the shop
            screen.blit(shop_panel, (15 * scale_x, 15 * scale_y))
            # dislay shop page buttons depending on what page your on

            if shop_page == 1:
                screen.blit(page_button_1, (23 * scale_x, 157 * scale_y))
            elif shop_page == 2:
                screen.blit(page_button_2, (23 * scale_x, 157 * scale_y))
            elif shop_page == 3:
                screen.blit(page_button_3, (23 * scale_x, 157 * scale_y))
            elif shop_page == 4:
                screen.blit(page_button_4, (23 * scale_x, 157 * scale_y))
            for card in shop_cards:
                card.display(shop_page, balance)
        else:
            screen.blit(open_shop, (111 * scale_x, 810 * scale_y))

        screen.blit(game_bar,
                    (518 * scale_x, 906 * scale_y))  # position and display game_bar at the bottom of the screen

        for text in fade_text:
            text.show()
        screen.blit(balance_text, (1640 * scale_x, 995 * scale_y))  # balance text


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
                button.value = (button.x - button.start_x) / button.max_val

                # the buttons don't quite extend out to the extremes (+1, 0) therefore the if statement rounds up/down
                # past a certain value
                if button.value < 0.03:
                    button.value = 0
                elif button.value > 0.97:
                    button.value = 1

                # drag button logic below
                if button.name == "time_slider":
                    speed_multiplier = button.value ** 2
                    time_multiplier = starting_time * speed_multiplier  # change time depending on the time slider
        if button.active and button.visible:
            if button.shape == "Circle":
                pygame.draw.circle(screen, (0, 0, 255), (button.x, button.y), button.radius)
            if button.shape == "Rectangle":
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(button.x, button.y, button.x_length, button.y_length))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if game_state.get("on_game"):  # if on the main game tab
                if event.key == 27:  # 27 is the keycode for escape

                    # save game
                    save_game(celestial_bodies, save_slot)

                    # exit game
                    pygame.quit()
                    sys.exit()


        elif event.type == MOUSEBUTTONDOWN:  # user clicks
            # print(mouse_x / scale_x, mouse_y / scale_y)
            if game_state.get("on_game"):  # if on the main game tab
                if event.button == 1:  # left click

                    if button.name == "time_slider":  # get the time slider button
                        if button.is_clicked(mouse_x, mouse_y):  # check if it was clicked
                            button.details = "LOCKED"  # lock the button slider to the mouse
                            break  # break the loop so that it doesn't pan the screen while shifting the slider

                    if panning is False:
                        start_pan_x = mouse_x + camera_offset_x
                        start_pan_y = mouse_y + camera_offset_y
                    panning = True

                    if planet_place_click == 0 and placing_planet:  # placing planet and haven't clicked yet
                        planet_place_click += 1
                        placement_x = mouse_x
                        placement_y = mouse_y

                    elif planet_place_click == 1 and placing_planet:  # placing planet and has clicked
                        planet_place_click += 1

                if event.button == 3:  # right click
                    # check to see if any planets have been clicked
                    for body in celestial_bodies:
                        if body.is_clicked(mouse_x, mouse_y):
                            if body.show_options:  # alternate whether the planet's options are showing
                                body.show_options = False
                                select_button(buttons, False)  # turn off all buttons
                            else:
                                for o_body in celestial_bodies:  # turn off all planet options
                                    o_body.show_options = False

                                body.show_options = True  # turn selected planet option on
                                select_button(buttons, True)  # turn on all buttons
                            # body.showOptions = not body.showOptions


                elif event.button == 4:  # Scroll wheel up
                    # update zoom in a non-linear fashion
                    new_zoom = zoom + zoom * 0.2
                    if new_zoom < max_zoom:  # provides a boundary check on the zoom
                        zoom = new_zoom
                    else:
                        zoom = max_zoom
                    CelestialBody.update_zoom(mouse_x, mouse_y, True)  # zoom increases
                elif event.button == 5:  # Scroll wheel down
                    new_zoom = zoom + zoom * -0.2
                    if new_zoom > min_zoom:
                        zoom = new_zoom
                    else:
                        zoom = min_zoom
                    CelestialBody.update_zoom(mouse_x, mouse_y, True)  # zoom decreases

                # elif event

            # print(mouse_x * scale_size, mouse_y * scale_size)
            if event.button == 1:
                for button in buttons:  # loop through buttons
                    if button.active:
                        if button.is_clicked(mouse_x, mouse_y):

                            # button click functionality checker
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
                                celestial_bodies = load_game(1)
                                save_slot = 1
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_load_game2":
                                celestial_bodies = load_game(2)
                                save_slot = 2

                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_load_game3":
                                save_slot = 3
                                celestial_bodies = load_game(3)
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_new_game1":
                                save_slot = 1
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_new_game2":
                                save_slot = 2
                                change_scene("on_game", game_state, buttons)
                            if button.name == "start_new_game3":
                                save_slot = 3
                                change_scene("on_game", game_state, buttons)

                            #shop buttons
                            if button.name == "open_shop" and not shop:
                                change_shop(True)
                                break
                            if button.name == "close_shop" and shop:
                                change_shop(False)
                                break
                            # change shop pages
                            if button.name == "shop_page_1" and shop:
                                shop_page = 1
                            if button.name == "shop_page_2" and shop:
                                shop_page = 2
                            if button.name == "shop_page_3" and shop:
                                shop_page = 3
                            if button.name == "shop_page_4" and shop:
                                shop_page = 4

                            # check which button has been clicked and then link that button to the card
                            if button.name == "buy_1" and shop:
                                buy_planet(0)
                            if button.name == "buy_2" and shop:
                                buy_planet(1)
                            if button.name == "buy_3" and shop:
                                buy_planet(2)
                            if button.name == "buy_4" and shop:
                                buy_planet(3)

                            # planet buttons
                            if button.name == "lock_to_planet":
                                for body in celestial_bodies:
                                    if body.show_options:
                                        if body.locked:
                                            body.change_lock(None)
                                            planet_locked = False  # show that the user isn't locked onto any planet
                                            # centre for seamless transition between panning mode and locked mode
                                            start_pan_x = width / 2 + mouse_x - width / 2
                                            start_pan_y = height / 2 + mouse_y - height / 2

                                        else:
                                            body.change_lock(body)
                                            planet_locked = True

                            if button.name == "delete_planet":
                                for body in celestial_bodies:
                                    if body.show_options:  # if this is the planet that the user is selected on
                                        if body.name != "Sun":  # makes sure users cannot delete the sun
                                            if body.locked:
                                                # unlock the planet
                                                body.change_lock(None)
                                                planet_locked = False  # if the planet is also locked then go into panning mode
                                                # centre for seamless transition between panning mode and locked mode
                                                start_pan_x = width / 2 + mouse_x - width / 2
                                                start_pan_y = height / 2 + mouse_y - height / 2

                                            celestial_bodies.remove(body)  # remove planet
                                            select_button(buttons, False)

                            if button.name == "clear_debris":
                                deletions = []
                                for i, body in enumerate(celestial_bodies):
                                    if body.name == "debris":
                                        deletions.append(i)  # create a list of indexes that need to be removed
                                for i, x in enumerate(deletions):
                                    celestial_bodies.pop(x - i)  # remove bodies by their indexes

                            if button.name == "teleport_to_sun":
                                for body in celestial_bodies:
                                    if body.name == "Sun":  # get the sun object
                                        body.change_lock(body)
                                        planet_locked = True
                                        break


        elif event.type == MOUSEBUTTONUP:  # user unclicks
            panning = False
            for button in buttons:
                if button.active and button.details == "LOCKED":
                    button.details = "UNLOCKED"

    # print(panning)
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

    pygame.display.flip()
