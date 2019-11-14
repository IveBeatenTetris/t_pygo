import pygame as pg

class Controller(object):
    """handling game pad input. for now only from xbox one controllers."""
    def __init__(self):
        """
        initiating controller if there is one.
        'events' is been updated from out the window in its 'events()'-method.
        """
        try:
            self.joystick = pg.joystick.Joystick(0)
            self.joystick.init()
            self.events = []# list > pygame.events
        except pg.error:
            self.joystick = None
    def update(self, events):
        """
        updating events with each game loop. 'window'-class is calling this so
        not necessary to call it somewhere else again.
        """
        self.events = events
    def buttons(self):
        """
        looks for controller events. i want to scrap the given 'events'
        property.
        """
        buttons = {
            "select": False,
            "start": False,
            "lb": False,
            "lt": False,
            "rb": False,
            "rt": False,
            "a": False,
            "x": False,
            "b": False,
            "y": False,
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }

        for event in self.events:
            if event.type == pg.JOYBUTTONDOWN:
                if event.button == 6:
                    buttons["select"] = True
                if event.button == 7:
                    buttons["start"] = True
                if event.button == 4:
                    buttons["lb"] = True
                if event.button == 5:
                    buttons["rb"] = True
                if event.button == 0:
                    buttons["a"] = True
                if event.button == 2:
                    buttons["x"] = True
                if event.button == 1:
                    buttons["b"] = True
                if event.button == 3:
                    buttons["y"] = True
            if event.type == pg.JOYAXISMOTION:
                if event.axis == 2:
                    if round(event.value, 2) > 0.3:
                        buttons["lt"] = True
                    if round(event.value, 2) < -0.3:
                        buttons["rt"] = True
            if event.type == pg.JOYHATMOTION:
                if event.value[1] == 1:
                    buttons["up"] = True
                elif event.value[1] == -1:
                    buttons["down"] = True
                if event.value[0] == 1:
                    buttons["right"] = True
                if event.value[0] == -1:
                    buttons["left"] = True

        return buttons
    def sticks(self):
        """response for using the joysticks."""
        left = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "click": False
        }
        right = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "click": False
        }

        for event in self.events:
            if event.type == pg.JOYAXISMOTION:
                # left stick
                if event.axis == 0:
                    if round(event.value, 2) < -0.3:
                        left["left"] = True
                    elif round(event.value, 2) > 0.3:
                        left["right"] = True
                elif event.axis == 1:
                    if round(event.value, 2) < -0.3:
                        left["up"] = True
                    elif round(event.value, 2) > 0.3:
                        left["down"] = True
                # right stick
                if event.axis == 4:
                    if round(event.value, 2) < -0.3:
                        right["left"] = True
                    elif round(event.value, 2) > 0.3:
                        right["right"] = True
                elif event.axis == 3:
                    if round(event.value, 2) < -0.3:
                        right["up"] = True
                    elif round(event.value, 2) > 0.3:
                        right["down"] = True
            elif event.type == pg.JOYBUTTONDOWN:
                if event.button == 8:
                    left["click"] = True
                if event.button == 9:
                    right["click"] = True

        return [left, right]
