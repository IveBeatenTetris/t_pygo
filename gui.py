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

    'defaults'  is a dict of standard properties. on init, the given parameter
                'config' is beeing compared to the default dict. if some given
                properties are missing, they are simply replaced by default
                values. the result is a validated dict to draw initialisation-
                instructions. it also declares what arguments can be passed to
                the app-object.
    """
    class Cursor(pg.sprite.Sprite):
        """replacement for the native pygame-mouse-cursor."""
        def __init__(self, image_path=None):
            """
            renders the native cursor invisible, loads either an image from a
            given path or a library-default value.
            """
            if not image_path:
                image_path = u.PATH["sysimg"] + "\\cursors.png"

            pg.mouse.set_visible(False)
            pg.sprite.Sprite.__init__(self)
            self.image = pg.image.load(image_path)
        # dynamic properties
        @property
        def rect(self):
            """returns a valid pygame-rect."""
            rect = pg.Rect(0, 0, 16, 16)
            rect.center = pg.mouse.get_pos()

            return rect
    defaults = {
        "size": (320, 240),
        "title": "Unnamed Project",
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

        'config'            validated 'dict' of comparing a user-set dict of
                            properties with this object's default values.

        'display'           holds the actual 'pygame.display.surface' object.

        'accessories'       an extended sprite-group for sprites that have to
                            always be blitten on top of the visuals.

        'mouse_cursor'      sprite to use instead of the original one. when
                            cursor-object gets initialized, it renders the
                            native pygame-cursor invisible.

        'background'        used to draw to fill the surface with. might be
                            'str' or 'tuple'. if 'str', use it as image-path
                            and load a pygame.image-surface.

        'clock'             pygame.clock for tracking 'fps'.

        'preffered_fps'     user-defined maximal frames per second.

        'fps'               the actual FPS. it's gonna be updated by the
                            window's 'update()'-method.

        '_events'           a 'list' of momentary pygame.events. it's gonna be
                            filled by calling 'self.events' anywhere. use this
                            list for checking ongoing events.

        'keys'              an empty list. gets automatically filled with
                            pygame-events by going through the
                            'events'-property over and over.

        'resized'           bool to check if the window has been resized.
        """
        self.config = u.validateDict(kwargs, self.defaults)
        # pygame init
        pg.init()
        # creating display surface and drawing background
        self.display = u.getDisplay(
            self.config["size"],
            resizable = self.config["resizable"]
        )
        self.draw(self.background)
        # changing window- and mouse-cursor apprarance
        self.changeTitle(self.config["title"])
        self.changeIcon(self.config["icon"])
        self.accessories = pg.sprite.RenderUpdates()
        #self.mouse_cursor = self.Cursor(); self.accessories.add(self.mouse_cursor)
        # fps settings
        self.clock = pg.time.Clock()
        self.preffered_fps = self.config["fps"]
        self.fps = 0
        # event related
        self._events = []
        self.keys = []
        self.resized = False
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
                if evt.key is pg.K_ESCAPE:
                    self.keys.append("esc")
            # calling 'self.resize()' when window has been resized. also
            # marking the app as 'resized' (self.resized = True)
            if evt.type is pg.VIDEORESIZE:
                self.resized = True
                self.resize(evt.size)
            elif evt.type is pg.ACTIVEEVENT and self.resized:
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
                # drawing sprites
                if object.__class__.__bases__[0] is pg.sprite.Sprite:
                    self.display.blit(object.image, rect)
                # drawing surfaces
                elif (
                        object.__class__.__bases__[0] is pg.Surface or
                        type(object) is pg.Surface or
                        issubclass(type(object), pg.Surface)
                    ):
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
        self._events = self.events

        """
        # drawing all accessories to apps surface
        #bg = pg.Surface(self.rect.size, pg.SRCALPHA)
        bg = self.display.copy()
        #bg.fill(self.background)
        self.accessories.clear(self.display, bg)
        changes = self.accessories.draw(self.display)
        pg.display.update(changes)
        """

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
        "parent": None,
        "size": (300, 200),
        "position": (0, 0),
        "background": (35, 35, 45),
        "background_hover": None,
        "border": False,
        "border_color": (0, 0, 0),
        "border_size": 1,
        "dragable": False,
        "drag_area": None,
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
        self.config = u.validateDict(kwargs, self.defaults)
        # declaring parent
        if self.config["parent"]:
            self.parent = self.config["parent"]
        else:
            self.parent = pg.display.get_surface()
        # visuals and rect-dimensions
        self.background = self.config["background"]
        self.background_hover = self.config["background_hover"]
        self.rect = pg.Rect(
            self.config["position"],
            self.config["size"]
        )
        # event related stuff
        self.dragable = self.config["dragable"]
        if self.config["drag_area"]:
            self.drag_area = pg.Rect(self.config["drag_area"])
        else:
            self.drag_area = self.config["drag_area"]
        self.__dragged_at = None
        self.__clicked = False
        self.__hovering = False
        # first time creating surface and recreating inner element's visuals
        self.resize(self.config["size"])
        self.redraw()
    # dynamic properties
    @property# pg.surface
    def border(self):
        """returns a surface with a blitten border to it if preset by user."""
        border = None
        # drawing border to temprary surface if given
        if self.config["border"]:
            border_surface = pg.Surface(self.rect.size, pg.SRCALPHA)
            u.drawBorder(
                border_surface,
                color = self.config["border_color"],
                size = self.config["border_size"]
            )
            border = border_surface

        return border
    # event related properties
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
                    # clicked yet, set its '__clicked'-state 'true' and
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
            # specific place and update its topleft-position. this removes the
            # previously drawn element's trails from the surface again
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
    # basic methodes
    def draw(self, object, rect=None, area=None):
        """
        blits a surface-object / gui-element to the elements's surface.
        if 'object' is a list or tuple, fill the surface with this statement
        instead. 'area' takes a pygame.rect-statement for declaring a specific
        area to redraw for keep fps up.
        """
        if not rect: rect = (0, 0)

        if type(object) is list or type(object) is tuple:
            self.fill(object)
        else:
            if not area:
                self.blit(object, rect)
            else:
                self.display.blit(object, rect, area)
    def redraw(self):
        """
        rebuilds the surface with all inner elements updated. one can pass a
        'GuiMaster'-element and blit this to the surface as well.
        """
        # drawing background
        bg = self.background
        if self.hover:
            if self.background_hover:
                bg = self.background_hover
        else:
            if self.background:
                bg = self.background
        # drawing if background is not 'none'
        if bg:
            if type(bg) is tuple or type(bg) is list:
                self.fill(bg)
            else:
                self.blit(bg, (0, 0))
        # drawing drag-area if set by user
        if self.config["drag_area"]:
            rect = pg.Rect(self.config["drag_area"])
            self.fill(self.config["drag_area_background"], rect)
        # drawing background if set by user
        if self.border:
            self.draw(self.border, (0, 0))
    def resize(self, size):
        """
        resizes the surface and updates its dimensions. as well as redrawing
        the background if there is one.
        """
        self.rect.size = size
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        # redrawing backgrounds and stuff
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
class Table(GuiMaster):
    """
    acts like a grid with columns to use their rects for drawing.
    usage:
        surface.blit(element, table.columns[5])

    'default'   default-properties for this object.
    'Grid'      (class) is used to visualize the table.
    """
    default = {
        "rows": 1,
        "cols": 1,
        "background": None,
        "border": False,
        "border_size": 1,
        "border_color": (0, 0, 0)
    }
    # subordered table-classes
    class Grid(GuiMaster):
        """
        a grid object with a border drawn to its surface and a list of stores
        columns for accessing their rect-positions.
        """
        def __init__(self, **kwargs):
            """
            uses 'GuiMaster' as its parent with additional methodes and
            attributes.

            'columns'   a list of accessable cell-rects. the main reason for
                        this class.
            """
            GuiMaster.__init__(self, **kwargs)
            self.columns = []
            # using these for calculating next line's position
            x, y = 0, 0
            # drawing rows
            for row in range(kwargs["rows"]):
                pg.draw.lines(
                    self,
                    kwargs["border_color"],
                    False,
                    [
                        (self.rect.left, y),
                        (self.rect.right, y)
                    ],
                    kwargs["border_size"]
                )
                y += int(self.rect.height / kwargs["rows"])
            # drawing cols
            for col in range(kwargs["cols"]):
                pg.draw.lines(
                    self,
                    kwargs["border_color"],
                    False,
                    [
                        (x, self.rect.top),
                        (x, self.rect.bottom)
                    ],
                    kwargs["border_size"]
                )
                x += int(self.rect.width / kwargs["cols"])
            # storing every cell-rect in columns-list
            for r in range(kwargs["rows"]):
                for c in range(kwargs["cols"]):
                    rect = pg.Rect(
                        c * int(self.rect.width / kwargs["cols"]),
                        r * int(self.rect.height / kwargs["rows"]),
                        int(self.rect.width / kwargs["cols"]),
                        int(self.rect.height / kwargs["rows"]),
                    )
                    self.columns.append(rect)

    # table-initialisation
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methodes and attributes.

        'cfg'       'dict' of building instructions for the table.
        'columns'   'list' of rect-arguments, each resembling a place in the
                    table. it's gonna be filled automatically by calling
                    'self.grid' anywhere.
        """
        self.cfg = u.validateDict(kwargs, self.default)
        GuiMaster.__init__(self, **kwargs)
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        self.columns = []
        # first time drawing grid
        self.blit(self.grid, (0, 0))

    # dynamic properties
    @property# grid-object
    def grid(self):
        """returns a new calculated grid-surface-object ready to be drawn."""
        grid = self.Grid(
            size = self.rect.size,
            background = self.background,
            rows = self.cfg["rows"],
            cols = self.cfg["cols"],
            border = self.cfg["border"],
            border_size = self.cfg["border_size"],
            border_color = self.cfg["border_color"]
        )
        # updating self.columns
        self.columns = grid.columns

        return grid
    # basic methodes
    def resize(self, size):
        """overwrites parent's 'resize()'-method."""
        self.rect.size = size
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        # redrawing grid
        self.blit(self.grid, (0, 0))
    def update(self):
        """overwrites parent's 'update()'-method."""
        pass
class Text(GuiMaster):
    """
    resembles a text-object.

    'default'   default-properties for this object.
    """
    default = {
        "font": u.FONTS["base"]["name"],
    	"font_size": u.FONTS["base"]["size"],
    	"color": u.FONTS["base"]["color"],
        "background": None,
    	"text": "Text",
    	"antialias": True,
    	"bold": False,
    	"italic": False,
        "shadow": None,
        "wrap": None,
        "position": (0, 0),
        "padding": 0
    }
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methodes and attributes.

        'cfg'       'dict' of building instructions for the table.
        'font'      'pygame.font'-object to render a text with.
        'wrap'      'none' or 'int'. if int, use this value as width-statement
                    to wrap text-content.
        """
        self.cfg = u.validateDict(kwargs, self.default)
        # initialising and styling font-object
        pg.font.init()
        self.font = pg.font.SysFont(# pygame.font
        	self.cfg["font"],
        	self.cfg["font_size"]
        )
        self.font.set_bold(self.cfg["bold"])
        self.font.set_italic(self.cfg["italic"])
        # additional properties
        self.wrap = self.cfg["wrap"]
        # initialising text-object and downsizing it to text.rect-size
        kwargs["background"] = self.cfg["background"]
        kwargs["size"] = self.text.get_rect().size
        GuiMaster.__init__(self, **kwargs)
        #GuiMaster.__init__(self, **self.cfg)
        # drawing text to text-surface
        self.blit(self.text, (0, 0))
    # dynamic properties
    @property# pg.surface
    def text(self):
        """
        considering own 'wrap'-attribute, this returns a pygame.surface with
        blitten text to it.
        """
        # creating text-surface
        if self.wrap:
            text = u.wrapText(
                font = self.font,
                text = self.cfg["text"],
                color = self.cfg["color"],
                antialias = self.cfg["antialias"],
                size = self.wrap
            )
        else:
            text = self.font.render(
                self.cfg["text"],
                self.cfg["antialias"],
                self.cfg["color"]
            )
        # creating the former rect for the final surface to return
        rect = text.get_rect()
        # looking for padding to apply as size and position
        if self.cfg["padding"]:
            rect.width += 2 * self.cfg["padding"]
            rect.height += 2 * self.cfg["padding"]
            rect.left = self.cfg["padding"]
            rect.top = self.cfg["padding"]
        # this is the final surface we will return at the end
        final_surface = pg.Surface(rect.size, pg.SRCALPHA)
        # render a self-made shadow if user disires so
        if self.cfg["shadow"]:
            shadow = self.cfg["shadow"]
            color = (0, 0, 0, 255)
            pos = (0, 0)
            # converting passed shadow-arguments
            if type(shadow) is list:
                for attr in shadow:
                    if type(attr) is list or type(attr) is tuple:
                        if len(attr) >= 3:
                            color = attr
                        elif len(attr) == 2:
                            pos = attr
            # drawing shadow
            shadow_surface = text.copy()
            shadow_surface.fill(color, None, pg.BLEND_RGBA_MULT)
            final_surface.blit(shadow_surface, pos)
        # drawing everything to the returning-surface
        final_surface.blit(text, rect.topleft)

        return final_surface
    # basic methodes
    def resize(self, size):
        """overwrites parent's 'resize()'-method."""
        self.rect.size = size
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        # drawing text to text-surface
        self.redraw()
        self.blit(self.text, (0, 0))
    def update(self):
        """overwrites parent's 'update()'-method."""
        if self.hover or self.leave:
            self.redraw()
            self.blit(self.text, (0, 0))
class Button(Text):
    """
    represents a button but works like a text with GuiMaster's extended
    surface-features.
    """
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methodes and attributes.
        """
        Text.__init__(self, **kwargs)
class TextInput(GuiMaster):
    """
    resembles a text-inpus-element for typing in some text.

    'default'   default-properties for this object.
    """
    default = {
        "size": (175, 30),
        "position": (0, 0),
        "background": (35, 35, 45),
        "border": True,
        "border_color": (15, 15, 25)
    }
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methodes and attributes.

        'cfg'       'dict' of building instructions for the table.
        """
        self.cfg = u.validateDict(kwargs, self.default)
        GuiMaster.__init__(self, **self.cfg)
    def update(self):
        """overwrites parent's 'update()'-method."""
        if self.hover:
            cursor = (8,8), (4,4), (0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0)
            #pg.mouse.set_cursor(*cursor)
