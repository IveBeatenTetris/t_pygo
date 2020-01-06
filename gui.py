"""
this file contains all elements used to fuse a visual graphical user interface.
it starts of with 'GuiMaster' which serves as a master class for all / most of
the gui-elements.
"""
# dependencies
import pygame as pg
import os, sys
from . import utils as u
# overall functions to pick from
def loadXMLInterface(name):
    """
    returns an interface structure written in a markup language. the output is
    already converted to a readable dict.
    """
    for cfg in u.loadAssets(u.PATH["interface"] + "\\" + name):
        if cfg["type"] == "interface":
            return cfg
# first step to creating a pygame window
class App:
    """
    pygames-window-module with extended features. can be accessed by calling
    'globals()["app"]'.

    'defaults' is a dict of standard properties. on init, the given parameter
        'config' is beeing compared to the default dict. if some given
        properties are missing, they are simply replaced by default values.
        the result is a validated dict to draw initialisation instructions.
        it also declares what arguments can be passed to the app-object.
    """
    defaults = {
        "size": (320, 240),
        "title": "No Title",
        "resizable": False,
        "fullscreen": False,
        "background": u.LIBPATH["windowbg"],
        "background_repeat": None,
        "icon": u.LIBPATH["windowicon"],
        "fps": 30
    }
    def __init__(self, **kwargs):
        """
        inits pygame to act as an app-window.

        'config' validated 'dict' of comparing a user-set dict of properties
            with this object's default values.
        'display' holds the actual 'pygame.display.surface' object.
        'background' used to draw to fill the surface with. might be 'str' or
            'tuple'. if 'str', use it as image-path and load a
            pygame.image-surface.
        'clock' pygame.clock for tracking 'fps'.
        'preffered_fps' user-defined maximal frames per second.
        'fps' the actual FPS. it's gonna be updated by the window's
            'update()'-method.
        'keys' an empty list. gets automatically filled with pygame-events by
            going through the 'events'-property over and over.
        """
        self.config = u.validateDict(kwargs, self.defaults)
        # pygame init and window centering
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        # creating display surface and drawing background
        self.display = u.getDisplay(
            self.config["size"],
            resizable = self.config["resizable"]
        )
        #self.background = self.config["background"]
        self.draw(self.background)
        # fps settings
        self.clock = pg.time.Clock()
        self.preffered_fps = self.config["fps"]
        self.fps = 0
        # event related
        self.keys = []
    # dynamic properties
    @property# pg.surface
    def background(self):
        """returns a pygame.surface based on background-properties."""
        bg = self.config["background"]

        if type(bg) is str:
            # overwriting app's local 'background_repeat'-property if 'bg'
            # is the library's standard background-image.
            if bg == str(u.LIBPATH["windowbg"]):
                self.config["background_repeat"] = "xy"
            bg = pg.image.load(bg)
        elif type(bg) is tuple:
            pass
        # checking background repeat
        if type(bg) is pg.Surface:
            if self.config["background_repeat"]:
                # creating surfact with repeated background
                # 'self.config["background_repeat"]' is the indicator:
                # ('x', 'y', 'xy')
                bg = u.repeatBG(
                    bg,
                    self.display.get_rect().size,
                    self.config["background_repeat"]
                )

        return bg
    @property# list
    def events(self):
        """
        checks for the most basic events and returns the pg-event-list.
        updates internal property 'keys' with a fresh list of pressed keys.
        """
        events = pg.event.get()
        # resetting previous event-list
        self.keys = []

        for evt in events:
            # exiting the app
            if evt.type is pg.QUIT:
                self.quit()
            # calling 'self.resize()' when window has been resized
            if evt.type is pg.VIDEORESIZE:
                self.resize(evt.size)
            # appending a string to list 'self.keys' resembling the pressed key
            if evt.type is pg.KEYDOWN:
                if evt.key == pg.K_ESCAPE:
                    self.keys.append("esc")

        return events
    @property# pg.rect
    def rect(self):
        """returns a valid pygame-rect with app's dimensions."""
        return self.display.get_rect()
    # basic methodes
    def draw(self, object, rect=None, area=None):
        """
        blits a surface-object / gui-element to the app's surface.
        if 'object' is a list or tuple, fill the surface with this statement
        instead. 'area' takes a pygame.rect-statement for declaring a specific
        area to redraw for keep fps up.
        """
        if not rect: rect = (0, 0)

        if type(object) is list or type(object) is tuple:
            self.display.fill(object)
        else:
            if not area:
                self.display.blit(object, rect)
            else:
                self.display.blit(object, rect, area)
    def resize(self, size=None):# tuple
        """
        resizes the app's surface.

        'size' needs to be a tuple. if no 'size parameter' is given this method
            serves as a 'resized-event' checker and returns 'true' or 'false'.
        """
        # on given parameter
        if size:
            # make new display surface
            self.display = u.getDisplay(
                size,
                resizable = self.config["resizable"]
            )
            # drawing background
            self.draw(self.background)
        # with no given parameter
        else:
            # return a tuple when resized or not
            resized = None

            for evt in self.events:
                if evt.type is pg.VIDEORESIZE:
                    resized = evt.size

            return resized
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def update(self):
        """
        updates dimensions, visuals and physics of the pygame.display with each
        game-loop.
        """
        # refreshing display visuals
        pg.display.update()
        # updating fps
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
class GuiMaster(pg.Surface):
    """
    resembles a 'pygame.surface' but with advanced operations.

    'defaults' serves as a setup-dict to evaluate building instructions for the
        master-element.
    """
    defaults = {
        "size": (300, 200),
        "position": (0, 0),
        "background": (45, 45, 55),
        "background_hover": None,
        "dragable": False
    }
    def __init__(self, **kwargs):
        """
        first creates a internal setup-config to decleare some properties.

        'config' the validated 'dict' to draw building instructions from.
            evaluation between pass keyword-args and a dict of predefined
            attributes.
        'background' either 'str' or 'tuple' / 'list'. if 'none', leave the
            surface transparent.
        'background_hover' might be 'tuple' or 'list'. if it's 'none', don't
            apply a hover effect later.
        'rect' initialising rect dimensions.
        'dragable' user-defined bool for checking if a dragging-operation can
            come in.
        '__dragged_at' standard 'none' later becomes a tuple of 2 ints. this can
            be used to calculate the position of an element when the mouse
            tries to drag it.
        '__clicked' internal bool to check, if the element has been clicked.
        '__hovering' used to determine if the mouse floats over the element.
        """
        self.config = u.validateDict(kwargs, self.defaults)
        self.background = self.config["background"]
        self.background_hover = self.config["background_hover"]
        self.rect = pg.Rect(self.config["position"], self.config["size"])
        # event related stuff
        self.dragable = self.config["dragable"]
        self.__dragged_at = None
        self.__clicked = False
        self.__hovering = False
        # first time creating surface
        self.resize(self.config["size"])
    # dynamic properties
    @property# list
    def click(self):
        """
        returns the mouse-button the element has just been clicked with.
        otherwise returns 'none'.
        """
        mbut = pg.mouse.get_pressed()
        buttons = []

        if self.hover:
            if mbut[0]: buttons.append("left")
            if mbut[1]: buttons.append("wheel")
            if mbut[2]: buttons.append("right")

        return buttons
    @property
    def drag(self):
        """
        returns 'true' if element is dragable and been dragged by the mouse.
        calling this also drags the surface around when the element is
        dragable.
        """
        if self.dragable:
            # mouse events
            mpos = pg.mouse.get_pos()
            mbut = pg.mouse.get_pressed()
            # on hover and left-click
            if self.hover and "left" in self.click:
                # if element is not clicked yet, set it's '__clicked'-state
                # 'true' and calculate the clicked position on the element's
                # rect
                if not self.__clicked:
                    self.__dragged_at = (
                        mpos[0] - self.rect.x,
                        mpos[1] - self.rect.y
                    )
                    self.__clicked = True
            # if left mouse-button is released or just not pressed
            elif not mbut[0]:
                self.__dragged_at = None
                self.__clicked = False
            # if element is clicked, update the rect's position
            if self.__clicked:
                self.rect.topleft = (
                    mpos[0] - self.__dragged_at[0],
                    mpos[1] - self.__dragged_at[1]
                )

        return self.__clicked
    @property# bool
    def hover(self):
        """
        returns 'true' if the mouse-cursor floats over the element's rect. also
        sets 'self.__hovering' to 'true' so we can check for several mouse events.
        """
        mpos = pg.mouse.get_pos()
        hover = False

        if self.rect.collidepoint(mpos):
            hover = True
            self.__hovering = True

        return hover
    @property# bool
    def leave(self):
        """
        returns 'true' if the mouse leaves the element. used to declare
        redrawing of surface on mouse-out.
        """
        leaving = False

        if self.__hovering and not self.hover:
            leaving = True

            return leaving

    def drawBackground(self, bg=None):
        """draws background to surface if 'background' is preset by user."""
        if bg:
            if type(bg) is list or type(bg) is tuple:
                self.fill(bg)
    def resize(self, size):
        """
        resizes the surface and updates its dimensions. as well as redrawing
        the background if there is one.
        """
        self.rect.size = size
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        self.drawBackground(self.background)
    def update(self):
        """runs with every game-loop."""
        redraw = False
        # invoking drag-operation
        self.drag
        # visual redrawing of this element depends on the following conditions:
        if self.click or self.hover or self.leave:
            redraw = True
            # drawing background depending on mouse-cursor and 'background_hover'
            if redraw:
                if self.hover:
                    if self.background_hover:
                        self.drawBackground(self.background_hover)
                else:
                    self.drawBackground(self.background)
