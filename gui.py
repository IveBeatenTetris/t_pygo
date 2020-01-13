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

    'Cursor'    (class) a cursor-image for replacing the real one.
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

            'full_image'    the once loaed full-image as a pg.surface.
            'state'         the actual state of the mouse in a str. by changing
                            this, the app will draw another mouse-curor based on
                            following names:
                                'normal',
                                'text'
            """
            if not image_path: image_path = u.PATH["sysimg"] + "\\cursors.png"
            self.full_image = pg.image.load(image_path)
            self.state = "normal"
            pg.mouse.set_visible(False)
            pg.sprite.Sprite.__init__(self)
        # dynamic properties
        @property
        def image(self):
            """returns a cropped pg.surface-image."""
            image = pg.Surface((16, 16), pg.SRCALPHA)
            # calculate image-position to draw (each 16x16-steps there is
            # another cursor on the image)
            if self.state == "normal": pos = (0, 0)
            elif self.state == "text": pos = (-16, 0)
            # drawing picked cursor to returning image-surface
            image.blit(self.full_image, pos)

            return image
        @property
        def rect(self):
            """returns a valid pygame-rect."""
            rect = pg.Rect(0, 0, 16, 16)
            rect.topleft = pg.mouse.get_pos()

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

        'draw_list'         an extended sprite-group for sprites that have to
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
        self.cursor = self.Cursor()
        # everything in this list will be drawn to the app-screen on their
        # event-updates.
        self.draw_list = pg.sprite.RenderUpdates()
        self.draw_list.add(self.cursor)
        # fps settings
        self.clock = pg.time.Clock()
        self.preffered_fps = self.config["fps"]
        self.fps = 0
        # event related
        self._events = []
        self.keys = []
        self.resized = False
        # adding this instance to 'globals'
        globals()["app"] = self
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
        it also cycles trough 'self.draw_list' to draw everything that is given
        to this list.
        """
        self._events = self.events
        # creating a background-surface if 'self.background' is a list or tuple
        if type(self.background) is not pg.Surface:
            bg = pg.Surface(self.rect.size)
            bg.fill(self.background)
        else:
            bg = self.background
        # overdrawing old moved sprite-trails on backgrounds
        self.draw_list.clear(self.display, bg)
        changes = self.draw_list.draw(self.display)
        # drawing the new mouse-cursor
        self.display.blit(self.cursor.image, self.cursor.rect.topleft)
        # updating all drawn sprites
        for each in self.draw_list: each.update()
        pg.display.update(changes)
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
class GuiMaster(pg.sprite.Sprite):
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
        'state'             (str) can be changed to mark the event-related
                            state of this event. values are "waiting" and
                            "active".
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
        # initialising sprite
        pg.sprite.Sprite.__init__(self)
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
        self.state = "waiting"
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

        # adding marking for used button on hover
        if self.hover:
            if mbut[0]: buttons.append("left")
            if mbut[1]: buttons.append("wheel")
            if mbut[2]: buttons.append("right")
        # marking element as activated
        if "left" in buttons:
            self.state = "active"

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
        mbut = pg.mouse.get_pressed()
        hover = False
        # mark as hovered
        if self.rect.collidepoint(mpos):
            hover = True
            self.__hovering = True
        # if not hovered and clicked somwhere else, reset 'self.state'
        if not hover and (mbut[0] or mbut[1] or mbut[2]):
            self.state = "waiting"

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
    # internal methodes
    def checkCursor(self, default="normal", hover="pointer"):
        """
        changes apps mouse-cursor depending on element-hover. putting this in
        an elements 'update'-method, this results in a change of the mouse-
        cursor on element-hover.
        """
        if self.hover:
            globals()["app"].cursor.state = hover
        elif not self.hover and globals()["app"].cursor.state != "normal":
            globals()["app"].cursor.state = default
    # basic methodes
    def draw(self, object, rect=None, area=None):
        """
        blits a surface-object / gui-element to the elements's surface.
        if 'object' is a list or tuple, fill the surface with this statement
        instead. 'area' takes a pygame.rect-statement for declaring a specific
        area to redraw for keep fps up.
        """
        if not rect:
            rect = (0, 0, *self.rect.size)
        # filling self.image with color
        if type(object) is list or type(object) is tuple:
            self.image.fill(object, rect)
        # drawing sprite.image to self.image
        elif (
            type(object) is pg.sprite.Sprite or
            object.__class__.__bases__[0] is GuiMaster
        ):
            # with drawing boundaries
            if area: self.image.blit(object.image, rect, area)
            else: self.image.blit(object.image, rect)
        # drawing surface-object to self.image
        elif (
            type(object) is pg.Surface or
            issubclass(type(object), pg.Surface) or
            object.__class__.__bases__[0] is pg.Surface
        ):
            # with drawing boundaries
            if area: self.image.blit(object, rect, area)
            else: self.image.blit(object, rect)
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
                self.image.fill(bg)
            else:
                self.image.blit(bg, (0, 0))
        # drawing drag-area if set by user
        if self.config["drag_area"]:
            rect = pg.Rect(self.config["drag_area"])
            self.image.fill(self.config["drag_area_background"], rect)
        # drawing background if set by user
        if self.border:
            self.image.blit(self.border, (0, 0))
    def resize(self, size):
        """
        resizes the surface and updates its dimensions. as well as redrawing
        the background if there is one.
        """
        self.rect.size = size
        self.image = pg.Surface(size, pg.SRCALPHA)
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
                    self.image,
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
                    self.image,
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
    default = {
        "rows": 1,
        "cols": 1,
        "background": None,
        "border": False,
        "border_size": 1,
        "border_color": (0, 0, 0)
    }
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methodes and attributes.

        'cfg'       'dict' of building instructions for the table.
        'image'     'pg.surface'-image the original surface-image.
        'columns'   'list' of rect-arguments, each resembling a place in the
                    table. it's gonna be filled automatically by calling
                    'self.grid' anywhere.
        """
        self.cfg = u.validateDict(kwargs, self.default)
        GuiMaster.__init__(self, **kwargs)
        self.image = pg.Surface(self.rect.size, pg.SRCALPHA)
        self.columns = []
        # first time drawing grid
        self.image.blit(self.grid.image, (0, 0))
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
        self.image = pg.Surface(size, pg.SRCALPHA)
        # redrawing grid
        self.image.blit(self.grid.image, (0, 0))
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
        self.image.blit(self.text, (0, 0))
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
        self.image = pg.Surface(size, pg.SRCALPHA)
        # drawing text to text-surface
        self.redraw()
        self.image.blit(self.text, (0, 0))
    def update(self):
        """overwrites parent's 'update()'-method."""
        if self.hover or self.leave:
            # only redrawing text if there is a background. else it would oddly
            # overdraw the old text
            self.redraw()
            if self.background:
                self.image.blit(self.text, (0, 0))
class Button(Text):
    """
    represents a button but works like a text with GuiMaster's extended sprite-
    features.
    """
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methodes and attributes.
        """
        Text.__init__(self, **kwargs)
class TextField(GuiMaster):
    """
    resembles a text-field-element for typing in some text.

    'default'   default-properties for this object.
    """
    class TextCursor(pg.Surface):
        """blinking text-cursor for text-field."""
        default = {
            "size": (1, 30),
            "position": (2, 0),
            "color": (100, 100, 100)
        }
        def __init__(self, **kwargs):
            """
            'cfg'           validated dict with building-instructions.
            'rect'          (pg.rect) cursor dimensions.
            'cooldown'      int to decrease on update for drawing a blinking
                            cursor to the text-field-element.
            """
            self.cfg = u.validateDict(kwargs, self.default)
            pg.Surface.__init__(self, self.cfg["size"])
            self.fill(self.cfg["color"])
            self.rect = pg.Rect(self.cfg["position"], self.get_rect().size)
            self.cooldown = 100
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
        'cursor'    (class) 'pg.surface' that comes along with some operations
                    for correctly drawing itself to its parent.
        """
        self.cfg = u.validateDict(kwargs, self.default)
        GuiMaster.__init__(self, **self.cfg)
        self.cursor = self.TextCursor(
            size=(2, self.rect.height - 6),
            position=(3, 3)
        )
    def update(self):
        """overwrites parent's 'update()'-method."""
        mbut = pg.mouse.get_pressed()
        self.checkCursor(default="normal", hover="text")
        # provoking a 'click'- event
        self.click
        # making text-cursor blink.
        if self.state == "active":
            # checking cooldown and drawing either cursor or background
            if self.cursor.cooldown >= 50:
                self.image.blit(self.cursor, self.cursor.rect)
            elif self.cursor.cooldown < 50:
                self.image.fill(self.background, self.cursor.rect)
            # resetting cooldown or further reducing it
            if self.cursor.cooldown == 0: self.cursor.cooldown = 100
            else: self.cursor.cooldown -= 1
        # resetting cursor by clicking somewhere else
        elif not self.hover and (mbut[0] or mbut[1] or mbut[2]):
            self.image.fill(self.background, self.cursor.rect)
class Panel(GuiMaster):
    """
    a panel-surface to draw information or elements on.

    'default'   default-properties for this object.
    """
    default = {

    }
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methodes and attributes.
        """
        GuiMaster.__init__(self, **kwargs)
