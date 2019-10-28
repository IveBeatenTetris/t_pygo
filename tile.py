from .utils import (
    draw
)
import pygame as pg

class Tile(pg.sprite.Sprite):
    """
    cut out a sprite from an image. actually its just replacement.
    """
    def __init__(self, config={}):
        """."""
        pg.sprite.Sprite.__init__(self)
        self.image = config["image"]# pygame surface
        self.rect = self.image.get_rect()# pygame rect
        self.id = config["id"]# int
        # additional attributes
        try:# str
            self.name = config["name"]
        except KeyError:
            self.name = "NoName"
        try:# bool
            self.block = config["block"]
        except KeyError:
            self.block = False
        try:# bool
            self.visible = config["visible"]
        except KeyError:
            self.visible = True
