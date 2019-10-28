from .utils import (
    loadJSON,
    draw
    )
import pygame as pg

class Map(pg.Surface):
    """."""
    def __init__(self, path):
        """."""
        self.config = loadJSON(path)# dict        
