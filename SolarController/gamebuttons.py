# imports
import math


class Button:  # class applied to all instances of buttons
    def __init__(self, name, tag, details, min_val, max_val, visible, x, y, *size, offset_x=0, offset_y=0, value=0.0):

        # x and y position
        self.start_x = x  # used to base the range off of this constant, since the actual x/y may vary with offset
        self.start_y = y

        # add button offset(this is used for sliders if the slider were to start at a particular value)
        self.x = x + offset_x
        self.y = y + offset_y

        # if active then the button is clickable
        self.active = False
        self.visible = visible
        self.min_val = min_val  # if the button is a slider, then this value will be the minimum amount the slider can move to the left from its starting X
        self.max_val = max_val  # max value
        self.name = name  # used to identify a particular button( if button.name == "name":)
        self.tag = tag  # additional identifier that describes what screen the button should be displayed on
        self.details = details  # custom property of the button(if self.details == "LOCKED")
        self.value = value  # custom value for buttons, used for sliders

        # unpack size,if their are 2 values, then the button is a rectangle(xlen, ylen). if one value then it is circle
        if len(size) == 1:
            self.shape = "Circle"
            self.radius = size[0]
        elif len(size) == 2:
            self.shape = "Rectangle"
            self.x_length = size[0]
            self.y_length = size[1]

    def is_clicked(self, pos_x, pos_y):  # takes mouse coordinate parameters and checks whether that clicks a button
        if self.shape == "Circle":  # if the button is circular
            distance = math.sqrt((self.x - pos_x) ** 2 + (self.y - pos_y) ** 2)  # pythagoras calculation for distance
            if distance < self.radius:  # if the distance is less than the radius then the button must be clicked
                return True
            else:
                return False
        if self.shape == "Rectangle":
            if self.x < pos_x < self.x + self.x_length and self.y < pos_y < self.y + self.y_length:  # logic to collide
                return True
            else:
                return False


def gather_buttons(scale_x, scale_y, scale_size):
    buttons = []  # create list that will be filled with button instances

    # create instances of a class for each button with varying properties and append them to a list
    buttons.append(
        Button("new_game", "on_title_screen", "", 0, 0, False, scale_x * 705, scale_y * 555,
               170 * scale_size))
    buttons.append(
        Button("load_game", "on_title_screen", "", 0, 0, False, scale_x * 1487, scale_y * 568,
               115 * scale_size))
    buttons.append(
        Button("settings", "on_title_screen", "", 0, 0, False, scale_x * 1127, scale_y * 938,
               130 * scale_size))

    buttons.append(
        Button("exit_settings", "on_settings", "", 0, 0, False, scale_x * 771, scale_y * 883,
               673 * scale_x, 155 * scale_y))
    buttons.append(
        Button("graphics_slider", "on_settings", "", 0, 337 * scale_x, True, scale_x * 1062, scale_y * 538,
               28 * scale_size))
    buttons.append(
        Button("volume_slider", "on_settings", "", 0, 337 * scale_x, True, scale_x * 1062, scale_y * 673,
               28 * scale_size))

    buttons.append(
        Button("back_to_title_screen", "on_new_game", "", 0, 0, False, scale_x * 684, scale_y * 918,
               917 * scale_x, 163 * scale_y))
    buttons.append(
        Button("start_new_game1", "on_new_game", "", 0, 0, False, scale_x * 703, scale_y * 556,
               173 * scale_size))
    buttons.append(
        Button("start_new_game2", "on_new_game", "", 0, 0, False, scale_x * 1144, scale_y * 556,
               173 * scale_size))
    buttons.append(
        Button("start_new_game3", "on_new_game", "", 0, 0, False, scale_x * 1586, scale_y * 556,
               173 * scale_size))

    buttons.append(
        Button("back_to_title_screen", "on_load_game", "", 0, 0, False, scale_x * 684, scale_y * 918,
               917 * scale_x, 163 * scale_y))
    buttons.append(
        Button("start_load_game1", "on_load_game", "", 0, 0, False, scale_x * 703, scale_y * 556,
               173 * scale_size))
    buttons.append(
        Button("start_load_game2", "on_load_game", "", 0, 0, False, scale_x * 1144, scale_y * 556,
               173 * scale_size))
    buttons.append(
        Button("start_load_game3", "on_load_game", "", 0, 0, False, scale_x * 1586, scale_y * 556,
               173 * scale_size))

    buttons.append(
        Button("open_shop", "on_game", "", 0, 0, False, scale_x * 221, scale_y * 921,
               115 * scale_size))
    buttons.append(
        Button("close_shop", "on_game", "", 0, 0, False, scale_x * 221, scale_y * 86,
               67 * scale_size))
    buttons.append(
        Button("shop_page_1", "on_game", "", 0, 0, False, scale_x * 23, scale_y * 157,
               97 * scale_x, 39 * scale_y))
    buttons.append(
        Button("shop_page_2", "on_game", "", 0, 0, False, scale_x * 124, scale_y * 157,
               97 * scale_x, 39 * scale_y))
    buttons.append(
        Button("shop_page_3", "on_game", "", 0, 0, False, scale_x * 224, scale_y * 157,
               97 * scale_x, 39 * scale_y))
    buttons.append(
        Button("shop_page_4", "on_game", "", 0, 0, False, scale_x * 324, scale_y * 157,
               97 * scale_x, 39 * scale_y))

    buttons.append(
        Button("buy_1", "on_game", "", 0, 0, False, scale_x * 213, scale_y * 331,
               187 * scale_x, 59 * scale_y))
    buttons.append(
        Button("buy_2", "on_game", "", 0, 0, False, scale_x * 213, scale_y * 531,
               187 * scale_x, 59 * scale_y))
    buttons.append(
        Button("buy_3", "on_game", "", 0, 0, False, scale_x * 213, scale_y * 731,
               187 * scale_x, 59 * scale_y))
    buttons.append(
        Button("buy_4", "on_game", "", 0, 0, False, scale_x * 213, scale_y * 931,
               187 * scale_x, 59 * scale_y))

    buttons.append(
        Button("lock_to_planet", "on_game", "", 0, 0, False, scale_x * 0, scale_y * 0,
               39 * scale_x, 39 * scale_y))
    buttons.append(
        Button("unlock_planet", "on_game", "", 0, 0, False, scale_x * 0, scale_y * 0,
               39 * scale_x, 39 * scale_y))
    buttons.append(
        Button("upgrade_planet", "on_game", "", 0, 0, False, scale_x * 0, scale_y * 0,
               39 * scale_x, 39 * scale_y))
    buttons.append(
        Button("delete_planet", "on_game", "", 0, 0, False, scale_x * 0, scale_y * 0,
               39 * scale_x, 39 * scale_y))

    buttons.append(
        Button("teleport_to_sun", "on_game", "", 0, 0, False, scale_x * 566, scale_y * 1006,
               242 * scale_x, 65 * scale_y))

    buttons.append(
        Button("clear_debris", "on_game", "", 0, 0, False, scale_x * 566, scale_y * 928,
               242 * scale_x, 65 * scale_y))

    buttons.append(
        Button("time_slider", "on_game", "", 0, 577 * scale_x, True, scale_x * 874, scale_y * 1038,
               33 * scale_size, offset_x=298 * scale_x, value=0.5))

    return buttons
