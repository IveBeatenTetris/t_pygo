from .utils import (
    PATH,
    LIBPATH,
    validateDict,
    getFrames,
    draw
)
import pygame as pg

class Tile(pg.sprite.Sprite):
    """
    cut out a sprite from an image. actually its just replacement.
    'config' should be a directly loaded json-file.
    """
    default = {
        "image": LIBPATH["notile"],
        "size": (16, 16)
    }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.default)# dict
        pg.sprite.Sprite.__init__(self)
        # standard attributes
        # surface related stuff
        self.image = pg.Surface(self.config["size"])# pygame surface
        if self.config["image"] == LIBPATH["notile"]:
            img = pg.image.load(self.config["image"])
        else:
            img = pg.image.load(
                config["filepath"] + "\\" + self.config["image"]
            )
        draw(img, self.image)
