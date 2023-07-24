import pygame
from pygame.locals import *
pygame.init()

width, height = 960, 540

screen = pygame.display.set_mode((width, height))
#screen
width, height = 960, 540
scale_x, scale_y = width / 1920, height / 1080 # used for changing the scale of sprites with the aspect ratio
scale_size = min(scale_x, scale_y)


# Load sprites
# backgrounds
title_screen = pygame.image.load('Sprites/BaseScreens/TitleScreen.png').convert_alpha()
settings_screen = pygame.image.load('Sprites/BaseScreens/Settings.png').convert_alpha()
new_game_page = pygame.image.load('Sprites/BaseScreens/NewGamePage.png').convert_alpha()
load_game_page = pygame.image.load('Sprites/BaseScreens/LoadGamePage.png').convert_alpha()

# sprites
sun = pygame.image.load('Sprites/Sun.png').convert_alpha()
moon = pygame.image.load('Sprites/Moon.png').convert_alpha()
earth = pygame.image.load('Sprites/Earth.png').convert_alpha()
satellite = pygame.image.load('Sprites/Satellite.png').convert_alpha()
jupiter = pygame.image.load('Sprites/Jupiter.png').convert_alpha()
luxaurantius = pygame.image.load('Sprites/LuxAurantius.png').convert_alpha()
malakorus = pygame.image.load('Sprites/Malakorus.png').convert_alpha()
ondori = pygame.image.load('Sprites/Ondori.png').convert_alpha()
enduros = pygame.image.load('Sprites/Enduros.png').convert_alpha()
vulkan = pygame.image.load('Sprites/Vulkan.png').convert_alpha()
asteroid = pygame.image.load('Sprites/Asteroids1.png').convert_alpha()

# GUI
shop_panel = pygame.image.load('Sprites/Shop/ShopPanel.png').convert_alpha()
open_shop = pygame.image.load('Sprites/Shop/OpenShop.png').convert_alpha()
planet_selection_lock = pygame.image.load('Sprites/PlanetSelectionlock.png').convert_alpha()
planet_selection_unlock = pygame.image.load('Sprites/PlanetSelectionUnlock.png').convert_alpha()
page_button_1 = pygame.image.load('Sprites/Shop/PageButton1.png').convert_alpha()
page_button_2 = pygame.image.load('Sprites/Shop/PageButton2.png').convert_alpha()
page_button_3 = pygame.image.load('Sprites/Shop/PageButton3.png').convert_alpha()
page_button_4 = pygame.image.load('Sprites/Shop/PageButton4.png').convert_alpha()

# shop cards
earth_card_afford = pygame.image.load('Sprites/Shop/Cards/EarthAfford.png').convert_alpha()
earth_card_unafford = pygame.image.load('Sprites/Shop/Cards/EarthUnafford.png').convert_alpha()
enduros_card_afford = pygame.image.load('Sprites/Shop/Cards/EndurosAfford.png').convert_alpha()
enduros_card_unafford = pygame.image.load('Sprites/Shop/Cards/EndurosUnafford.png').convert_alpha()
jupiter_card_afford = pygame.image.load('Sprites/Shop/Cards/JupiterAfford.png').convert_alpha()
jupiter_card_unafford = pygame.image.load('Sprites/Shop/Cards/JupiterUnafford.png').convert_alpha()
luxaurantius_card_afford = pygame.image.load('Sprites/Shop/Cards/LuxAurantiusAfford.png').convert_alpha()
luxaurantius_card_unafford = pygame.image.load('Sprites/Shop/Cards/LuxAurantiusUnafford.png').convert_alpha()
malakorus_card_afford = pygame.image.load('Sprites/Shop/Cards/MalakorusAfford.png').convert_alpha()
malakorus_card_unafford = pygame.image.load('Sprites/Shop/Cards/MalakorusUnafford.png').convert_alpha()
moon_card_afford = pygame.image.load('Sprites/Shop/Cards/MoonAfford.png').convert_alpha()
moon_card_unafford = pygame.image.load('Sprites/Shop/Cards/MoonUnafford.png').convert_alpha()
ondori_card_afford = pygame.image.load('Sprites/Shop/Cards/OndoriAfford.png').convert_alpha()
ondori_card_unafford = pygame.image.load('Sprites/Shop/Cards/OndoriUnafford.png').convert_alpha()
satellite_card_afford = pygame.image.load('Sprites/Shop/Cards/SatelliteAfford.png').convert_alpha()
satellite_card_unafford = pygame.image.load('Sprites/Shop/Cards/SatelliteUnafford.png').convert_alpha()



# Transform sprites to the correct size
title_screen = pygame.transform.scale(title_screen, (width, height))
settings_screen = pygame.transform.scale(settings_screen, (width, height))
new_game_page = pygame.transform.scale(new_game_page, (width, height))
load_game_page = pygame.transform.scale(load_game_page, (width, height))

planet_selection_lock = pygame.transform.scale(planet_selection_lock, (110*scale_x, 40*scale_y))
planet_selection_unlock = pygame.transform.scale(planet_selection_unlock, (110*scale_x, 40*scale_y))
shop_panel = pygame.transform.scale(shop_panel, (scale_x*413, scale_y*1054))
open_shop = pygame.transform.scale(open_shop, (scale_x*220, scale_y*220))
page_button_1 = pygame.transform.scale(page_button_1, (scale_x*398, scale_y*39))
page_button_2 = pygame.transform.scale(page_button_2, (scale_x*398, scale_y*39))
page_button_3 = pygame.transform.scale(page_button_3, (scale_x*398, scale_y*39))
page_button_4 = pygame.transform.scale(page_button_4, (scale_x*398, scale_y*39))

earth_card_unafford = pygame.transform.scale(earth_card_unafford, (scale_x*397, scale_y*190))
earth_card_afford = pygame.transform.scale(earth_card_afford, (scale_x*397, scale_y*190))
moon_card_unafford = pygame.transform.scale(moon_card_unafford, (scale_x*397, scale_y*190))
moon_card_afford = pygame.transform.scale(moon_card_afford, (scale_x*397, scale_y*190))
enduros_card_afford = pygame.transform.scale(enduros_card_afford, (scale_x*397, scale_y*190))
enduros_card_unafford = pygame.transform.scale(enduros_card_unafford, (scale_x*397, scale_y*190))
jupiter_card_afford = pygame.transform.scale(jupiter_card_afford, (scale_x*397, scale_y*190))
jupiter_card_unafford = pygame.transform.scale(jupiter_card_unafford, (scale_x*397, scale_y*190))
luxaurantius_card_afford = pygame.transform.scale(luxaurantius_card_afford, (scale_x*397, scale_y*190))
luxaurantius_card_unafford = pygame.transform.scale(luxaurantius_card_unafford, (scale_x*397, scale_y*190))
malakorus_card_afford = pygame.transform.scale(malakorus_card_afford, (scale_x*397, scale_y*190))
malakorus_card_unafford = pygame.transform.scale(malakorus_card_unafford, (scale_x*397, scale_y*190))
ondori_card_afford = pygame.transform.scale(ondori_card_afford, (scale_x*397, scale_y*190))
ondori_card_unafford = pygame.transform.scale(ondori_card_unafford, (scale_x*397, scale_y*190))
satellite_card_afford = pygame.transform.scale(satellite_card_afford, (scale_x*397, scale_y*190))
satellite_card_unafford = pygame.transform.scale(satellite_card_unafford, (scale_x*397, scale_y*190))
