from .utils import (
    draw,
    validateDict
)
import pygame as pg

class Overlay(pg.Surface):
    """for dimmed backgrounds on menus."""
    default = {
        "background": (0, 0, 0),
        "size": (320, 240),
        "opacity": 255
    }
    def __init__(self, config={}):
        """constructor"""
        # comparing dicts and creating a new one
        self.config = validateDict(config, self.default)# dict
        # initiating surface
        pg.Surface.__init__(self, self.config["size"])
        # setting opacity if there is one
        self.set_alpha(self.config["opacity"])
class Button(pg.sprite.Sprite):
    """interactive gui element."""
    default = {
        "size": (120, 40),
        "background": (0, 0, 0),
        "text": "Button",
        "position": (0, 0)
    }
    def __init__(self, config={}):
        # comparing dicts and creating a new one
        self.config = validateDict(config, self.default)# dict
        # initiating sprite
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(self.config["size"])# pygame.surface
        draw(self.config["background"], self.image)
        # additional attributes
        self.rect = self.image.get_rect()# pygame.rect
        self.rect.topleft = self.config["position"]# tuple
