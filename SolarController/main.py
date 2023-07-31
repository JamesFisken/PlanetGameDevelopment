# imports
import random
import sys
import math
import time
import gamebuttons
import copy
from loadimages import *  # starts up pygame and loads necessary images
import numpy as np

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


running = True
clock = pygame.time.Clock()

# time keeping variables
is_paused = False
average_fps = 1
fps = 1500
fps_list = []
dt = 1  # delta time, so that the speed of the game isn't dependent on fps
time_multiplier = 50000000  # this sets the speed of the game

# screen
width, height = 960, 540
screen = pygame.display.set_mode((width, height))

zoom = 0.5  # the higher the value the more zoomed in you are
min_zoom = 0.035
max_zoom = 4.5


# where the mouse is relative to the screen and thus where the zooms focus will be
rel_mouse_x = width / 2
rel_mouse_y = height / 2

panning = True

# constants
G_CONSTANT = 6.6743 * (10 ** -11)
SOLAR_MASS = 1.989 * 10 ** 30  # mass of the sun
TRUE_PIXEL_DISTANCE = 1515000000  # this number was calculated by taking the distance from the true sun to the earth and dividing by 100, this means that 100 pixels will equate to the distance from earth to the sun

# global varianles

# this will be a value that changes the positions of all planets so that the locked planet is centered
lock_offset_x = 0
lock_offset_y = 0

camera_offset_x = 0
camera_offset_y = 0

start_pan_x = 0
start_pan_y = 0

planet_locked = False  # if there is a planet that is locked
shop = False  # shows if on shop
shop_page = 1  # shows current shop page
balance = 2000000  # player balance
planet_place_click = 0
placing_planet = False




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

# classes
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

    def __init__(self, x, y, vel_x, vel_y, mass, radius, sprite, locked, name):
        CelestialBody.objs.append(self)
        self.name = name  # identifyer
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

        self.mass = mass
        self.radius = radius
        self.old_sprite = sprite
        self.sprite = pygame.transform.scale(sprite, (
            self.radius * zoom * 2.65,
            self.radius * zoom * 2.65))  # converts the size of the sprite to fit that of the planet's true radius

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
        blit_x = (self.x - (rel_mouse_x * 1)) * zoom + width / 2
        blit_y = (self.y - (rel_mouse_y * 1)) * zoom + height / 2

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
        # pygame.draw.circle(screen, (255, 0, 0), (self.true_x, self.true_y), self.radius*zoom)  # show hitbox
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
        if not other_bodies:
            return [0, 0]

            # Extract positions and masses of other bodies
        positions = np.array([(body.x, body.y) for body in other_bodies])
        masses = np.array([body.mass for body in other_bodies])

        # Calculate distances between self and other bodies
        differences = positions - np.array([self.x, self.y])
        distances = np.linalg.norm(differences, axis=1) * TRUE_PIXEL_DISTANCE

        # Avoid division by zero for self-gravity
        distances[distances < 10 * TRUE_PIXEL_DISTANCE] = 10 * TRUE_PIXEL_DISTANCE
        # Calculate forces
        forces = G_CONSTANT * self.mass * masses / distances ** 2

        # Calculate normalized directions
        normalized_dirs = differences / distances[:, np.newaxis]

        # Calculate net forces
        net_force = np.sum(normalized_dirs * forces[:, np.newaxis], axis=0)

        # Update self's force
        self.force_x += net_force[0]
        self.force_y += net_force[1]

        return net_force.tolist()

    def check_collisions(self, other_bodies):

        for body in other_bodies:
            if self.name != "debris" or body.name != "debris":  # stops collisions with collided objects
                distance = math.sqrt((self.x - body.x) ** 2 + (self.y - body.y) ** 2)
                if (body.radius + self.radius) > distance:
                    # print((body.radius + self.radius), distance)
                    create_collided_planet(self, body)
                    return [True, self, body]
        return [False]

    def is_clicked(self, pos_x, pos_y):
        distance = math.sqrt(abs(self.true_x - pos_x) ** 2 + abs(self.true_y - pos_y) ** 2)
        if distance < self.radius * zoom:  # if the distance is less than the radius then the planet must be clicked
            return True
        else:
            return False

    @classmethod
    def update_zoom(cls, mouse_x, mouse_y, update_mouse):
        global rel_mouse_x, rel_mouse_y
        for obj in cls.objs:  # loop through all instances
            if update_mouse:
                rel_mouse_x = mouse_x
                rel_mouse_y = mouse_y

            obj.sprite = obj.old_sprite

            obj.sprite = pygame.transform.scale(obj.sprite, (
                obj.radius * zoom * 2.85,
                obj.radius * zoom * 2.85))  # converts the size of the sprite to fit that of the planet's true radius

    @classmethod
    def change_lock(cls, body):
        for obj in cls.objs:
            obj.locked = False
        if body is not None:
            body.locked = True


celestial_bodies = []  # create a list to contain all planets on scene
avaiable_celestial_bodies = []  # this list will contain all celestial bodies able to get in this game
shop_cards = []  # create a list to contain all shop cards)
celestial_bodies.append(CelestialBody(850, 450, 0, 0, SOLAR_MASS, 450, sun, False, ""))

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

# create made_celestial_bodies
avaiable_celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0000010, 5, vulkan, False, "Debris"))
avaiable_celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0000010, 18, moon, False, "Moon"))
avaiable_celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0005000, 40, earth, False, "Earth"))
avaiable_celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0000001, 8, satellite, False, "Satellite"))
avaiable_celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0100000, 55, jupiter, False, "Jupiter"))

avaiable_celestial_bodies.append(
    CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0150000, 70, luxaurantius, False, "Lux Aurantius"))
avaiable_celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0175000, 90, ondori, False, "Ondori"))
avaiable_celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0200000, 130, malakorus, False, "Malakorus"))
avaiable_celestial_bodies.append(CelestialBody(0, 0, 0, 0, SOLAR_MASS * 0.0500000, 160, enduros, False, "Enduros"))


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


def change_shop(status):
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
    change_shop(False)


def convert_to_blit_coords(x, y, sprite_width, sprite_height):
    if not planet_locked:
        x = ((
                         x - width / 2 + lock_offset_x + camera_offset_x + sprite_width / 2) / zoom) + rel_mouse_x - sprite_width / 2 / zoom
        y = ((
                         y - height / 2 + lock_offset_y + camera_offset_y + sprite_height / 2) / zoom) + rel_mouse_y - sprite_height / 2 / zoom
    else:
        x = ((
                         x - width / 2 + lock_offset_x + sprite_width / 2) / zoom) + rel_mouse_x - sprite_width / 2 / zoom
        y = ((
                         y - height / 2 + lock_offset_y + sprite_width / 2) / zoom) + rel_mouse_y - sprite_height / 2 / zoom
    return x, y


def scale_number(num):
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
        sprite = body1.old_sprite
    elif body1.mass <= body2.mass:
        sprite = body2.old_sprite

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

    # spawn in the main bulk of the planet
    new_planet = CelestialBody(pos_x, pos_y, vel_x, vel_y, total_mass * inverse_impact_violence, new_radius, sprite,
                               False, "")
    total_mass -= (total_mass * inverse_impact_violence)
    total_area -= (total_area * inverse_impact_violence)

    celestial_bodies.append(new_planet)
    CelestialBody.objs.append(new_planet)

    # amount of debris follows this formula y=\operatorname{round}\left(\left(5\right)x+2\right)
    amount_of_debris = round(23 * impact_violence)
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
                                       debris_radius, vulkan, False, "debris")
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
        # print(math.sqrt((x-start_point[0])**2 + (y-start_point[1])**2))
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
    top_right = convert_to_blit_coords(width, 0, 0, 0)
    bottom_left = convert_to_blit_coords(0, height, 0, 0)
    bottom_right = convert_to_blit_coords(width+sprite_width, height+sprite_height, 0, 0)

    x1, y1 = (round_upwards(top_left[0] * zoom, sprite_width), round_upwards(top_left[1] * zoom, sprite_height))
    x2, y2 = (round_upwards(bottom_right[0] * zoom, sprite_width), round_upwards(bottom_right[1] * zoom, sprite_height))
    counter = 0

    for x in range(round((x2-x1)/sprite_width)):
        for y in range(round((y2 - y1)/sprite_height)):
            screen.blit(transformed_space_screen, ((x1+start_x)+ sprite_width*x, ((y1+start_y)+ sprite_height*y)))

    #screen.blit(transformed_space_screen, ((x1+start_x), (y1+start_y)))
    #screen.blit(transformed_space_screen, ((x2 + start_x), (y2 + start_y)))


# pre-loop setup
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
        start = time.time()
        screen.fill(BACKGROUND)

        transformed_space_screen = pygame.transform.scale(space_screen, (space_screen.get_width()*zoom, space_screen.get_height()*zoom))
        display_background(transformed_space_screen)

        #screen.blit(transfered_space_screen, (x2, y2))

        for i, body in enumerate(celestial_bodies):
            other_bodies = [x for j, x in enumerate(celestial_bodies) if j != i]  # append planets excluding self
            collision = body.check_collisions(other_bodies)
            if collision[0]:
                celestial_bodies.remove(collision[1])
                celestial_bodies.remove(collision[2])

            '''
            by putting a break here this will allow only one collision per frame which increases quality while making it less realistic
            '''

        for i, body in enumerate(celestial_bodies):
            other_bodies = [x for j, x in enumerate(celestial_bodies) if j != i and x.mass > SOLAR_MASS * 0.000010]  # append planets excluding self
            if len(other_bodies) > 0:
                body.apply_gravity(other_bodies)
            body.update()
            body.display()

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
                                     10 * zoom, (distance + 20) * 0.07)
                if planet.name == planet_name and planet_place_click == 2:
                    # add planet
                    new_planet = copy.copy(planet)

                    x, y = convert_to_blit_coords(placement_x, placement_y, new_planet.sprite.get_width(), new_planet.sprite.get_height())
                    x2, y2 = convert_to_blit_coords(mouse_x, mouse_y, new_planet.sprite.get_width(), new_planet.sprite.get_height())

                    new_planet.x = x
                    new_planet.y = y
                    if planet_locked:
                        for mass in celestial_bodies:
                            if mass.locked:
                                add_vel_x = mass.vel_x
                                add_vel_y = mass.vel_y
                                break
                        new_planet.vel_x = ((x2 - x) / 150000000) + add_vel_x
                        new_planet.vel_y = ((y2 - y) / 150000000) + add_vel_y
                    else:
                        new_planet.vel_x = (x2 - x) / 150000000
                        new_planet.vel_y = (y2 - y) / 150000000

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

        end = time.time()
        #print(end - start)

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

        elif event.type == pygame.KEYDOWN:
            if game_state.get("on_game"):  # if on the main game tab
                if event.key == 27:  # 27 is the keycode for escape
                    if is_paused:
                        time_multiplier = 50000000
                    else:
                        time_multiplier = 0
                    is_paused = not is_paused


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
                    if new_zoom <= max_zoom: # provides a boundary check on the zoom
                        zoom = new_zoom
                        CelestialBody.update_zoom(mouse_x, mouse_y, True)  # zoom increases
                elif event.button == 5:  # Scroll wheel down
                    new_zoom = zoom + zoom * -0.2
                    if new_zoom > min_zoom:
                        zoom = new_zoom
                        CelestialBody.update_zoom(mouse_x, mouse_y, True)  # zoom decreases

                #elif event

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

                            # shop buttons

                            if button.name == "open_shop" and not shop:
                                change_shop(True)

                            if button.name == "close_shop" and shop:
                                change_shop(False)

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
                                for card in shop_cards:
                                    if card.page == shop_page and card.position == 0:
                                        if balance >= card.cost:
                                            balance -= card.cost
                                            change_shop(False)  # close shop
                                            placing_planet = True
                                            planet_name = card.name
                            if button.name == "buy_2" and shop:
                                for card in shop_cards:
                                    if card.page == shop_page and card.position == 1:
                                        if balance >= card.cost:
                                            balance -= card.cost
                                            change_shop(False)  # close shop
                                            placing_planet = True
                                            planet_name = card.name
                            if button.name == "buy_3" and shop:
                                for card in shop_cards:
                                    if card.page == shop_page and card.position == 2:
                                        if balance >= card.cost:
                                            balance -= card.cost
                                            change_shop(False)  # close shop
                                            placing_planet = True
                                            planet_name = card.name
                            if button.name == "buy_4" and shop:
                                for card in shop_cards:
                                    if card.page == shop_page and card.position == 3:
                                        if balance >= card.cost:
                                            balance -= card.cost
                                            change_shop(False)  # close shop
                                            placing_planet = True
                                            planet_name = card.name

                            # planet buttons
                            if button.name == "lock_to_planet":
                                for body in celestial_bodies:
                                    if body.show_options:
                                        if body.locked:
                                            body.change_lock(None)
                                            planet_locked = False  # show that the user isn't locked onto any planet
                                            # centre for seemless transition between panning mode and locked mode
                                            start_pan_x = width / 2
                                            start_pan_y = height / 2
                                        else:
                                            body.change_lock(body)
                                            planet_locked = True
                            if button.name == "delete_planet":
                                for body in celestial_bodies:
                                    if body.show_options:  # if this is the planet that the user is selected on
                                        if body.locked:
                                            planet_locked = False  # if the planet is also locked then go into panning mode

                                        celestial_bodies.remove(body)  # remove planet
                                select_button(buttons, False)

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
    '''
    print("-----------------------------------")
    print("                                   ")
    print("rel_mouse", rel_mouse_x, rel_mouse_y)
    print("lock offset", lock_offset_x, lock_offset_y)
    print("camera_offset", camera_offset_x, camera_offset_y)
    print("start_pan", start_pan_x, start_pan_y)
    '''
    fps_list.append(frame_fps)
    if len(fps_list) > 100:
        average_fps = sum(fps_list) / len(fps_list)
        print(average_fps, min(fps_list))
        fps_list = []
    pygame.display.flip()
