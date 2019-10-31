from .utils import validateDict
import pygame as pg

class Camera(pg.Rect):
    """."""
    # default values
    default = {
        "size": (640, 480),
        "position": (0, 0),
        "border": None,
        "track": None,
        "zoomfactor": 1
    }
    def __init__(self, config={}):
        self.config = validateDict(config, self.default)# dict
        pg.Rect.__init__(self, self.config["position"], self.config["size"])
        self.tracking = self.config["track"]# none / entity
        self.zoomfactor = self.config["zoomfactor"]# int
