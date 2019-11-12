import pygame as pg

class Controller(object):
    """handling game pad input. for now only from xbox one controllers."""
    def __init__(self):
        """initiating controller."""
        self = pg.joystick.Joystick(0)
        self.init()
    def buttons(self, events):
        """
        looks for controller events. i want to scrap the given 'events'
        property.
        """
        buttons = {
            "a": False,
            "x": False,
            "b": False,
            "y": False
        }

        for event in events:
            if event.type == pg.JOYBUTTONDOWN:
                #print(event.dict, event.joy, event.button, 'pressed')
                if event.button == 0:
                    buttons["a"] = True
                if event.button == 2:
                    buttons["x"] = True
                if event.button == 1:
                    buttons["b"] = True
                if event.button == 3:
                    buttons["y"] = True
            if event.type == pg.JOYAXISMOTION:
                pass

        return buttons
