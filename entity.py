from .utils import (
    PATH,
    loadAssets,
    draw
)
from .libs.zrect import ZRect
import pygame as pg

class Entity(pg.sprite.Sprite):
    """every form of ingame-agency will be based of this class."""
    def __init__(self, name):
        """."""
        for each in loadAssets(PATH["entities"] + "\\" + name):
            if each["type"] == "player":
                self.config = each# dict
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(
            self.config["filepath"] + "\\" + self.config["image"]
        )
class Player(Entity):
    """representing a playable character."""
    def __init__(self, name):
        """."""
        Entity.__init__(self, name)
