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
        "size":                 (320, 240),
        "title":                "Test Project 0.1",
        "resizable":            False,
        "fullscreen":           False,
        "background":           u.LIBPATH["windowbg"],
        "background_repeat":    None,
        "icon":                 u.LIBPATH["windowicon"],
        "fps":                  30
    }
    def __init__(self, **kwargs):
        """
        inits pygame to act as an app-window.

        'config'            validated 'dict' of comparing a user-set dict of
                            properties with this object's default values.

        'display'           holds the actual 'pygame.display.surface' object.

        'background'        used to draw to fill the surface with. might be
                            'str' or 'tuple'. if 'str', use it as image-path
                            and load a pygame.image-surface.

        'clock'             pygame.clock for tracking 'fps'.

        'preffered_fps'     user-defined maximal frames per second.

        'fps'               the actual FPS. it's gonna be updated by the
                            window's 'update()'-method.

        'keys'              an empty list. gets automatically filled with
                            pygame-events by going through the
                            'events'-property over and over.

        'resized'           bool to check if the window has been resized.
        """
        self.config         =   u.validateDict(kwargs, self.defaults)
        # pygame init
        pg.init()
        # creating display surface and drawing background
        self.display        =   u.getDisplay(
                                    self.config["size"],
                                    resizable = self.config["resizable"]
                                )
        self.draw(self.background)
        # changing windows apprarance
        self.changeTitle(self.config["title"])
        self.changeIcon(self.config["icon"])
        # fps settings
        self.clock          =   pg.time.Clock()
        self.preffered_fps  =   self.config["fps"]
        self.fps            =   0
        # event related
        self.keys           =   []
        self.resized        =   False
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
        # resetting previous event-list and app's internal events
        self.keys = []

        for evt in events:
            # exiting the app
            if evt.type is pg.QUIT:
                self.quit()
            # appending a string to list 'self.keys' resembling the pressed key
            if evt.type is pg.KEYDOWN:
                if evt.key == pg.K_ESCAPE:
                    self.keys.append("esc")
            # calling 'self.resize()' when window has been resized. also
            # marking the app as 'resized' (self.resized = True)
            if evt.type is pg.VIDEORESIZE:
                self.resized = True
                self.resize(evt.size)
            elif self.resized:
                self.resized = False
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
    def resize(self, size):# none / tuple
        """resizes the app's surface. 'size' needs to be a tuple."""
        # make new display surface
        self.display = u.getDisplay(
            size,
            resizable = self.config["resizable"]
        )
        # drawing background
        self.draw(self.background)
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def update(self):
        """
        updates dimensions, visuals and physics of the pygame.display with each
        game-loop-tick.
        """
        events = self.events
        # refreshing display visuals
        pg.display.update()
        # updating fps
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
    # window appearance
    def changeIcon(self, path):
        """creates an icon for the window from an image."""
        if type(path) is pg.Surface:
            icon = path
        elif type(path) is str:
            icon = pg.image.load(path)

        icon = pg.transform.scale(icon, (32, 32))
        pg.display.set_icon(icon)
    def changeTitle(self, title):
        """changes the window title. 'title' should be a string."""
        if type(title) is not str:
            title = str(title)
        pg.display.set_caption(title)
class GuiMaster(pg.Surface):
    """
    resembles a 'pygame.surface' but with advanced operations.

    'defaults' serves as a setup-dict to evaluate building instructions for the
        master-element.
    """
    defaults = {
        "parent":               None,
        "size":                 (300, 200),
        "position":             (0, 0),
        "background":           (35, 35, 45),
        "background_hover":     None,
        "dragable":             False,
        "drag_area":            None,
        "drag_area_background": (45, 45, 55)
    }
    def __init__(self, **kwargs):
        """
        first creates a internal setup-config to decleare some properties.

        'config'            the validated 'dict' to draw building instructions
                            from. evaluation between pass keyword-args and a
                            dict of predefined attributes.

        'parent'            object which draws this element. must have
                            'GuiMaster' as master-class.

        'background'        either 'str' or 'tuple' / 'list'. if 'none', leave
                            the surface transparent.

        'background_hover'  might be 'tuple' or 'list'. if it's 'none', don't
                            apply a hover effect later.

        'rect'              initialising rect dimensions.

        'dragable'          user-defined bool for checking if a dragging-
                            operation can come in.

        'drag_area'         user-declared area of dragging an element. if left
                            out, use the whole element-rect for dragging.

        '__dragged_at'      standard 'none' later becomes a tuple of 2 ints.
                            this can be used to calculate the position of an
                            element when the mouse tries to drag it.

        '__clicked'         internal bool to check, if the element has been
                            clicked.

        '__hovering'        used to determine if the mouse floats over the
                            element.
        """
        self.config             =   u.validateDict(kwargs, self.defaults)
        # declaring parent
        if self.config["parent"]:
            self.parent         =   self.config["parent"]
        else:
            self.parent         =   pg.display.get_surface()
        # visuals and rect-dimensions
        self.background         =   self.config["background"]
        self.background_hover   =   self.config["background_hover"]
        self.rect               =   pg.Rect(
                                        self.config["position"],
                                        self.config["size"]
                                    )
        # event related stuff
        self.dragable           =   self.config["dragable"]
        if self.config["drag_area"]:
            self.drag_area      =   pg.Rect(self.config["drag_area"])
        else:
            self.drag_area      =   self.config["drag_area"]
        self.__dragged_at       =   None
        self.__clicked          =   False
        self.__hovering         =   False
        # first time creating surface and recreating inner element's visuals
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
    @property# bool
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
            # using 'drag_area' as rect for collisions if available
            if self.drag_area:
                rect = pg.Rect(
                    self.drag_area.left + self.rect.left,
                    self.drag_area.top + self.rect.top,
                    self.drag_area.width,
                    self.drag_area.height
                )
            # else using the element's rect instead
            else: rect = self.rect
            # on hover and left-click
            if rect.collidepoint(mpos) and mbut[0]:
                    # marking the element as clicked ('true). if element is not
                    # clicked yet, set it's '__clicked'-state 'true' and
                    # calculate the clicked position on the element's rect
                    if not self.__clicked:
                        # adding left and top of 'drag_area' so the element
                        # doesn't jump on click
                        self.__dragged_at = (
                            mpos[0] - rect.x + self.drag_area.left,
                            mpos[1] - rect.y + self.drag_area.top
                        )
                        self.__clicked = True
            # if left mouse-button is released or just not pressed, mark
            # element as clicked ('true')
            if not mbut[0]:
                self.__dragged_at = None
                self.__clicked = False
            # if element is marked as clicked, redraw parent's background on a
            # specific place and update it's topleft-position. this removes the
            # previously drawn element's trails from the surface again
            if self.__clicked:
                # only redrawing abb-background for now
                if hasattr(self.parent, "display"):
                    self.parent.display.blit(
                        self.parent.background,
                        self.rect.topleft,
                        self.rect
                    )
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

    def redraw(self, element=None):
        """
        rebuilds the surface with all inner elements updated. one can pass a
        'GuiMaster'-element and blit this to the surface as well.
        """
        # drawing background
        bg = self.background
        if self.hover:
            if self.background_hover:
                bg = self.background_hover
        if type(bg) is tuple or type(bg) is list:
            self.fill(bg)
        else:
            self.blit(bg, (0, 0))
        # drawing drag-area if set by user
        if self.config["drag_area"]:
            rect = pg.Rect(self.config["drag_area"])
            self.fill(self.config["drag_area_background"], rect)
        # drawing picked elements
        if element:
            if type(element) is list:
                for elem in element:
                    self.blit(elem, elem.rect)
            else:
                self.blit(element, element.rect)
    def resize(self, size):
        """
        resizes the surface and updates its dimensions. as well as redrawing
        the background if there is one.
        """
        self.rect.size = size
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        self.redraw()
    def update(self):
        """runs with every game-loop."""
        redraw = False
        # invoking drag-operation
        self.drag
        # visual redrawing of this element depends on the following conditions:
        if self.click or self.hover or self.leave:
            self.redraw()
# all these following elements draw their inherition from 'GuiMaster'
class Layout(GuiMaster):
    """
    a layout for better positioning of elements. works similar to a html-table.

    'default' default properties for this object.

    class 'Row' is used to visualize a row in the layout. it's parent-class is
        'GuiMaster, so we can treat and handle it like a normal pygame.surface'.
    class 'Col' is used to visualize a col in the layout. it's parent-class is
        'GuiMaster, so we can treat and handle it like a normal pygame.surface'.
    """
    default = {
        "rows"          :   [],
        "background"    :   (200, 200, 215)
    }
    # subordered layout-classes
    class Row(GuiMaster):
        """resembles a row of the layout."""
        default = {
            "background"    :   (180, 180, 195),
            "border"        :   None,
            "size"          :   ("100%", 25)
        }
        def __init__(self, **kwargs):
            GuiMaster.__init__(self, **kwargs)
            self.cfg            =   u.validateDict(kwargs, self.default)
            self.rect           =   u.convertRect(
                                        [
                                            0,
                                            0,
                                            self.cfg["size"][0],
                                            self.cfg["size"][1]
                                        ],
                                        self.parent.rect
                                    )
            self.background     =   self.cfg["background"]
            # resizing row since it's rect got changed
            self.resize(self.rect.size)
            # drawing a border around the row if the user desires so
            if self.cfg["border"]:
                self.background =   u.drawBorder(
                                        self,
                                        color   =   self.cfg["border"][1],
                                        size    =   self.cfg["border"][0]
                                    )
    class Col(GuiMaster):
        """resembles a col of the layout."""
        default = {}
        def __init__(self, **kwargs):
            GuiMaster.__init__(self, **kwargs)
            self.cfg          =   u.validateDict(kwargs, self.default)
    # layout initialisation
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methodes and attributes.

        'cfg'          'dict' of building instructions for the layout.
        'background'    overwriting 'GuiMaster's backgruond-property.
        """
        self.cfg            =   u.validateDict(kwargs, self.default)
        GuiMaster.__init__(self, **kwargs)
        self.background     =   self.structure[2]

    # dynamic properties
    @property# list
    def cols(self):
        """returns a list of layout-cells."""
        return self.structure[1]
    @property# list
    def rows(self):
        """returns a list of layout-rows."""
        return self.structure[0]
    @property
    def structure(self):# tuple
        """
        returns a tuple of valuable rows, cols and the surface, all elements
        have been blitten to.
        """
        # creating a surface
        surf = pg.Surface(self.rect.size, pg.SRCALPHA)
        # empty lists for returning filled at the end
        rows, cols = [], []
        # this variable is needed to calculate the next vertical drawing-
        # position of the row
        y = 0

        for i, setup in enumerate(self.cfg["rows"]):
            # appending a parent to the setup
            if not "parent" in setup:
                setup["parent"] = self
            # additional attributes
            if i % 2: setup["background"] = (
                self.cfg["background"][0] + 10,
                self.cfg["background"][1] + 10,
                self.cfg["background"][2] + 10
            )
            # init row and updating it's vertical postion
            row = self.Row(**setup)
            row.rect.top = y
            # drawing to temporary surface
            surf.blit(row, row.rect)
            # appending row to returning list
            rows.append(row)
            # updating 'y'
            y += row.rect.height

        return (rows, cols, surf)

    def resize(self, size):
        """overwrites parent's 'resize()'-method."""
        self.rect.size = size
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        self.background = self.structure[2]
        self.redraw()
    def update(self):
        """overwrites parent's 'update()'-method."""
        pass
