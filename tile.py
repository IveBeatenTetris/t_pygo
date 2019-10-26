from .utils import (
    PATH,
    LIBPATH,
    validateDict,
    getFrames,
    draw
    )
import pygame as pg

class Tile(pg.sprite.Sprite):
    """cut out a sprite from an image."""
    default = {
        "image": LIBPATH["noimage"],
        "position": (0, 0),
        "size": (16, 16)
    }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.default)# dict
        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface(self.config["size"])# pygame surface
        img = pg.image.load(self.config["image"])# pygame surface

        draw(
            img, self.image, (
                -self.config["position"][0],
                -self.config["position"][1]
                )
            )
