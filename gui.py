from .utils import (
    draw,
    validateDict,
    getAnchors
)
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
        self.text = Text({# text object
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
class Text(pg.sprite.Sprite):
	"""text surface. ready to be drawn."""
	default = {
		"font": "Verdana",
		"fontsize": 16,
		"color": (0, 0, 0),
		"text": "No Text",
		"antialias": True,
		"bold": False,
		"italic": False
	}
	def __init__(self, config={}):
		"""
		creates a text that can be drawn to any surface.
		first validates the config dict by camparing it with its default values.
		validateDict() is going to do that for you.
		'fontsize' its in the name.
		'color' should be tuple by 3 like (50, 110, 95).
		'text' only one-liners right now.
		'antialias' if 'false' the font will appear pixelated.
		'font' creates a new pygame.font from an installed system font.
		"""
		# comparing both dicts and creating a new one from it
		self.config = validateDict(config, self.default)# dict
		# initiating
		pg.sprite.Sprite.__init__(self)
		pg.font.init()
		# additional attributes
		self.fontsize = self.config["fontsize"]# int
		self.color = self.config["color"]# tuple
		self.text = self.config["text"]# str
		self.antialias = self.config["antialias"]# bool
		self.font = pg.font.SysFont(# pygame.font
			self.config["font"],
			self.fontsize
		)
		self.font.set_bold(self.config["bold"])
		self.font.set_italic(self.config["italic"])
		# image and rect are going to be created there
		self.__create()
	def __create(self):
		"""
		recreate the image-surface of the text. this is necessary since the
		pygame.font only creates images instead of an interactive text-objects.
		usually the text-object doesnt have to be recreated anyways.
		"""
		self.image = self.font.render(self.text, self.antialias, self.color)
		self.rect = self.image.get_rect()
	def update(self, cfg):
		"""updates attributes with the given parameters. 'cfg' must be dict."""
		try:
			self.text = cfg["text"]
		except KeyError:
			pass

		self.__create()
class TextBox(pg.Surface):
    """surface for displaying text."""
    default = {
        "type": "textbox",
        "size": (300, 100),
        "position": (0, 0),
        "background": (0, 0, 0)
    }
    def __init__(self, config={}):
        """
        'type' declares if the object is gonna be build as 'textbox' or
            'speechbubble'
        'call' bool to check if the textbox is called or not.
        """
        # creating a new dict based on comparison of two
        self.config = validateDict(config, self.default)# dict
        self.type = self.config["type"]# str
        self.call = False# bool
        pg.Surface.__init__(self, self.config["size"], pg.SRCALPHA)
        self.rect = self.get_rect()# pygame.rect
        self.rect.topleft = self.config["position"]
        self.text = Text({# text object
            "text": "Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit... 'There is no one who loves pain itself, who seeks after it and wants to have it, simply because it is pain...'",
            "fontsize": 16,
            "bold": True,
            "italic": False,
            "color": (200, 200, 200)
        })
        draw(self.config["background"], self)
        draw(self.text, self)
    def setPosition(self, pos):
        """updating rect position."""
        self.rect.topleft = pos
