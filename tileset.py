# dependencies
from .utils import (
    validateDict,
    loadJSON
)
from .tile import Tile
import pygame as pg

class Tileset:
    """."""
    default = {

    }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.default)# dict
