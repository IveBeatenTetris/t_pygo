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
            self.buttons = {
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
                "dup": False,
                "ddown": False,
                "dleft": False,
                "dright": False,
                "l3": False,
                "r3": False
            }
            self.sticks = [
                {
                    "up": False,
                    "down": False,
                    "left": False,
                    "right": False
                },
                {
                    "up": False,
                    "down": False,
                    "left": False,
                    "right": False
                }
            ]
        except pg.error:
            self.joystick = None
    def update(self, events):
        """
        updating events with each game loop. 'window'-class is calling this so
        not necessary to call it somewhere else again.
        """
        sticks = self.sticks
        buttons = self.buttons

        for event in events:
            # sticks
            if event.type == pg.JOYAXISMOTION:
                # left stick
                # left - right axis
                if event.axis == 0:
                    if round(event.value, 2) < -0.3:
                        sticks[0]["left"] = True
                    else:
                        sticks[0]["left"] = False
                    if round(event.value, 2) > 0.3:
                        sticks[0]["right"] = True
                    else:
                        sticks[0]["right"] = False
                # up - down axis
                elif event.axis == 1:
                    if round(event.value, 2) < -0.3:
                        sticks[0]["up"] = True
                    else:
                        sticks[0]["up"] = False
                    if round(event.value, 2) > 0.3:
                        sticks[0]["down"] = True
                    else:
                        sticks[0]["down"] = False
                # right stick
                # left - right axis
                if event.axis == 4:
                    if round(event.value, 2) < -0.3:
                        sticks[1]["left"] = True
                    else:
                        sticks[1]["left"] = False
                    if round(event.value, 2) > 0.3:
                        sticks[1]["right"] = True
                    else:
                        sticks[1]["right"] = False
                # up - down axis
                elif event.axis == 3:
                    if round(event.value, 2) < -0.3:
                        sticks[1]["up"] = True
                    else:
                        sticks[1]["up"] = False
                    if round(event.value, 2) > 0.3:
                        sticks[1]["down"] = True
                    else:
                        sticks[1]["down"] = False
            # buttons
            # button pressed
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
                if event.button == 8:
                    buttons["l3"] = True
                if event.button == 9:
                    buttons["r3"] = True
            # button released
            if event.type == pg.JOYBUTTONUP:
                if event.button == 6:
                    buttons["select"] = False
                if event.button == 7:
                    buttons["start"] = False
                if event.button == 4:
                    buttons["lb"] = False
                if event.button == 5:
                    buttons["rb"] = False
                if event.button == 0:
                    buttons["a"] = False
                if event.button == 2:
                    buttons["x"] = False
                if event.button == 1:
                    buttons["b"] = False
                if event.button == 3:
                    buttons["y"] = False
                if event.button == 8:
                    buttons["l3"] = False
                if event.button == 9:
                    buttons["r3"] = False
            # trigger
            if event.type == pg.JOYAXISMOTION:
                if event.axis == 2:
                    if round(event.value, 2) > 0.3:
                        buttons["lt"] = True
                    else:
                        buttons["lt"] = False
                    if round(event.value, 2) < -0.3:
                        buttons["rt"] = True
                    else:
                        buttons["rt"] = False
            # dpad
            if event.type == pg.JOYHATMOTION:
                if event.value[1] == 1:
                    buttons["dup"] = True
                else:
                    buttons["dup"] = False
                if event.value[1] == -1:
                    buttons["ddown"] = True
                else:
                    buttons["ddown"] = False
                if event.value[0] == 1:
                    buttons["dright"] = True
                else:
                    buttons["dright"] = False
                if event.value[0] == -1:
                    buttons["dleft"] = True
                else:
                    buttons["dleft"] = False

        self.events = events
    def stop(self, name):
        """
        interrupts the named element so it doesnt trigger button-pressed
        anymore.
        """
        self.buttons[name] = False
