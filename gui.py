from .utils import (
    draw,
    validateDict,
    getAnchors
)
from .text import Text
import pygame as pg

class Button(pg.sprite.Sprite):
    """interactive gui element."""
    default = {
        "size": (120, 40),
        "background": (0, 0, 0),
        "hoverbackground": (20, 20, 20),
        "text": "Button",
        "textcolor": (255, 255, 255),
        "fontsize": 16,
        "bold": False,
        "italic": False,
        "position": (0, 0)
    }
    def __init__(self, config={}):
        """
        'anchors' holds shortcuts for positional arguments like "midcenter" or
            "topright" etc for documentation look into 'utils.py'.
        'text' the actual displayed text.
        """
        # comparing dicts and creating a new one
        self.config = validateDict(config, self.default)# dict
        # initiating sprite
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(self.config["size"])# pygame.surface
        # additional attributes
        self.rect = self.image.get_rect()# pygame.rect
        self.rect.topleft = self.config["position"]# tuple
        self.anchors = getAnchors(self.rect.size)# dict
        self.text = Text({# button
            "text": self.config["text"],
            "fontsize": self.config["fontsize"],
            "bold": self.config["bold"],
            "italic": self.config["italic"],
            "color": self.config["textcolor"]
        })
        # building the sprite object
        self.__build()
    def __build(self):
        """redrawing everything"""
        # determining background
        if self.rect.collidepoint(pg.mouse.get_pos()):
            bg = self.config["hoverbackground"]
        else:
            bg = self.config["background"]
        # drawing on button
        draw(bg, self.image)
        # drawing text in the very center of the button
        draw(
            self.text,
            self.image,
            (
                self.anchors["midcenter"][0] - int(self.text.rect.width / 2),
                self.anchors["midcenter"][1] - int(self.text.rect.height / 2)
            )
        )
    def hover(self, events):
        """return 'true' if the mouse hovers the button."""
        mouse = pg.mouse.get_pos()
        hover = False

        for event in events:
            if self.rect.collidepoint(mouse):
                hover = True

        # rebuilding the surface so the hover effect can pop in
        self.__build()

        return hover
    def leftClick(self, events):
        """returns 'true' if button is left-clicked."""
        mouse = pg.mouse.get_pos()
        click = False

        for event in events:
            if self.hover(events):
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    click = True

        return click
class Overlay(pg.Surface):
    """
    for dimmed backgrounds on menus. 'opacity' somehow works backwards. means
    that 0 is for none blending while 255 is for full rendering.
    """
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
