"""
this file contains all elements used to fuse a visual graphical user interface.
it starts of with 'GuiMaster' which serves as a master-class for most of the
gui-elements.
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
# special overall classes
class Stylesheet:
    """serves as gui-element-building-instructions."""
    def __init__(self, type="none", style={}):
        """
        'config'    'dict' that holds the contructed attributes for the chosen
                    element.

        every attribute form here on will be created on the fly. means:
        depending on element-type, the stylesheet will have different
        attributes. us 'self.__dict__' to get a dict of all available
        stylesheet-attributes.
        """
        # validating config
        self.config = u.validateDict(style, u.STYLE[type])
        # dynamically creating stylesheet-attributes
        for name, attr in self.config.items():
            setattr(self, name, attr)
class App:
    """
    pygames-window-module with extended features. can be accessed by calling
    'globals()["app"]'.
    """
    def __init__(self, **kwargs):
        """
        inits pygame to act as an app-window.

        'stylesheet'        validated 'dict' of comparing a user-set dict of
                            properties with this object's default values.
        'display'           holds the actual 'pygame.display.surface' object.
        'background'        used to draw to fill the surface with. might be
                            'str', 'tuple' or 'pg.surface'. if 'str', use it as
                            an image-path and load a pygame.image-surface.
        'cursor'            sprite to use instead of the original one. when
                            cursor-object gets initialized, it renders the
                            native pygame-cursor invisible.
        'draw_list'         an extended sprite-group for sprites that have to
                            always be blitten on top of the visuals.
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
        self.style = Stylesheet(
            type = "app",
            style = kwargs
        )
        # pygame init
        pg.init()
        # creating display surface and drawing background
        self.display = u.getDisplay(
            self.style.size,
            resizable = self.style.resizable
        )
        self.background = self.createBackground()
        self.draw(self.background)
        # changing window- and mouse-cursor apprarance
        self.changeTitle(self.style.title)
        self.changeIcon(self.style.icon)
        self.cursor = Cursor()
        # everything in this list will be drawn to the app-screen on their
        # event-updates.
        self.draw_list = pg.sprite.RenderUpdates()
        self.draw_list.add(self.cursor)
        # fps settings
        self.clock = pg.time.Clock()
        self.preffered_fps = self.style.fps
        self.fps = 0
        # event related
        self._events = []
        self.keys = []
        self.resized = False
        # adding this instance to 'globals'
        globals()["app"] = self
    # dynamic attributes
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
            #elif evt.type is pg.ACTIVEEVENT and self.resized:
                #self.resized = False
            else:
                self.resized = False

        return events
    @property# pg.surface
    def fps_image(self):
        """returns a pg.surface with the fps as a text drawn to it."""
        image = Text(
            text = str(self.fps),
            text_size = 13
        )

        return image
    @property# pg.rect
    def rect(self):
        """returns a valid pygame-rect with app's dimensions."""
        return self.display.get_rect()
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
    def createBackground(self):# pg.surface
        """returns a pygame.surface based on background-properties."""
        # prioritizing backgorund-statement
        if self.style.background_color:
            bg = self.style.background_color
        else:
            bg = self.style.background_image
        # looking for default-background-statement
        if type(bg) is str:
            # overwriting app's local 'background_repeat'-property if 'bg'
            # is the library's standard background-image.
            if bg == str(u.LIBPATH["windowbg"]):
                self.style.background_repeat = "xy"
            bg = pg.image.load(bg)
        # filling a newly created surface
        elif type(bg) is tuple:
            color = bg
            bg = pg.Surface(self.rect.size)
            bg.fill(color)
        # checking for background-repeat
        if type(bg) is pg.Surface:
            if self.style.background_repeat:
                # creating surfact with repeated background
                # 'self.config["background_repeat"]' is the indicator:
                # ('x', 'y', 'xy')
                bg = u.repeatBG(
                    bg,
                    self.display.get_rect().size,
                    self.style.background_repeat
                )

        return bg
    # basic methods
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
    def redraw(self):
        """redraws everything from 'draw_list'."""
        self.draw_list.clear(self.display, self.background)
        changes = self.draw_list.draw(self.display)
        # rendering another mouse-cursor depending on some specific element-
        # types
        for each in self.draw_list:
            self.cursor.state = "normal"
            # changing cursor to 'text-selection' if it's over a text-related
            # element
            if (
                type(each) is Text or
                type(each) is Text2 or
                type(each) is TextField or
                each.__class__.__bases__[0] is TextField
            ):
                if each.hover:
                    self.cursor.state = "text"
                    # exiting the loop cause we're only looking for these
                    # elements
                    break
            # special exceptions for slot since it has elements that don't need
            # a change of the mouse-cursor from default to text-selection
            elif type(each) is Slot:
                if each.text_field.hover:
                    self.cursor.state = "text"
                    break
        # drawing the new mouse-cursor
        self.display.blit(self.cursor.image, self.cursor.rect.topleft)
        # updating all drawn sprites
        for each in self.draw_list: each.update()
        pg.display.update(changes)
    def resize(self, size):# none / tuple
        """resizes the app's surface. 'size' needs to be a tuple."""
        # make new display surface
        self.display = u.getDisplay(
            size,
            resizable = self.style.resizable
        )
        # drawing new created background
        self.background = self.createBackground()
        self.draw(self.background)
    def queue(self, object):
        """adding objects to the drawing-queue 'draw_list'."""
        if type(object) is dict:
            self.draw_list.add(*[e for _, e in object.items()])
        elif type(object) is GuiMaster:
            self.draw_list.add(object)
        elif object.__class__.__bases__[0] is GuiMaster:
            self.draw_list.add(object)
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
        # overdrawing old moved sprite-trails on backgrounds
        self.redraw()
        # refreshing display visuals
        pg.display.update()
        # updating fps
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
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
        pg.sprite.Sprite.__init__(self)
        if not image_path: image_path = u.PATH["sysimg"] + "\\cursors.png"
        self.full_image = pg.image.load(image_path)
        self.state = "normal"
        pg.mouse.set_visible(False)
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
class TextCursor(pg.sprite.Sprite):
    """blinking text-cursor for text-field."""
    def __init__(self, **kwargs):
        """
        'style'             the validated 'dict' to draw building-
                            instructions from. evaluation between passed
                            keyword-args and a dict of predefined
                            attributes.
        'rect'              (pg.rect) cursor dimensions.
        'image'             image-surface of this sprite.
        'cooldown'          int to decrease on update for drawing a
                            blinking cursor to the text-field-element.
        """
        pg.sprite.Sprite.__init__(self)
        self.style = Stylesheet(
            type = "text_marker",
            style = kwargs
        )
        self.rect = pg.Rect(self.style.position, self.style.size)
        self.image = pg.Surface(self.rect.size)
        self.image.fill(self.style.color)
        self.cooldown = 100
class GuiMaster(pg.sprite.Sprite):
    """resembles a 'pygame.surface' but with advanced operations."""
    def __init__(self, **kwargs):
        """
        first creates a internal setup-config to decleare some properties.

        'style'             the validated 'dict' to draw building instructions
                            from. evaluation between pass keyword-args and a
                            dict of predefined attributes.
        'parent'            object which draws this element. must have
                            'GuiMaster' as master-class.
        'rect'              initialising rect dimensions.
        'absolute_rect'     pg.rect with absolute position for event-checking.
        'state'             (str) can be changed to mark the event-related
                            state of this event. values are "waiting" and
                            "active".
        '_clicked'          internal bool to check, if the element has been
                            clicked.
        '_hovering'         used to determine if the mouse floats over the
                            element.
        '_start_hovering'   'bool' used to check if the mosue starts to hover
                            an elemenet.
        'image'             image-surface of this sprite class.
        """
        # initialising sprite
        pg.sprite.Sprite.__init__(self)
        # appending a stylesheet for this specific element
        if "type" in kwargs:
            type = kwargs["type"]
        else:
            type = "none"
        self.style = Stylesheet(
            type = type,
            style = kwargs
        )
        # declaring parent
        if "parent" in kwargs:
            self.parent = kwargs["parent"]
        else:
            #self.parent = pg.display.get_surface()
            self.parent = globals()["app"]
        # visuals and rect-dimensions
        self.rect = self.create_rect()
        self.absloute_rect = pg.Rect(
            self.rect.topleft,
            self.style.size
        )
        # event related stuff
        self.state = "waiting"
        self._clicked = False
        self._hovering = False
        self._start_hovering = False
        # first time creating surface and recreating inner element's visuals
        self.image = pg.Surface(self.rect.size, pg.SRCALPHA)
        self.redraw()
    # dynamic attributes
    @property# pg.surface
    def background(self):
        """returns a ready to draw background-surface."""
        background = pg.Surface(self.rect.size, pg.SRCALPHA)

        # redraw background-color if it's not 'none'
        if self.style.background_color:
            background.fill(self.style.background_color)
        # draw hover-color if element is hovered
        if self.hover and self.style.background_hover:
            background.fill(self.style.background_hover)

        return background
    @property# pg.surface
    def border(self):
        """returns a surface with a blitten border to it if preset by user."""
        border = None
        # drawing border to temprary surface if given
        if self.style.border:
            border_surface = pg.Surface(self.rect.size, pg.SRCALPHA)
            u.drawBorder(
                border_surface,
                color = self.style.border_color,
                size = self.style.border_size
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
        mbut = self.mouse_events[0]
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
    @property# none / str
    def precise_click(self):
        """
        returns 'none' if nothing has clicked and a str related to used mouse-
        button.
        """
        precise_click = None
        # adding more precise mouse-events
        for evt in globals()["app"]._events:
            if evt.type is pg.MOUSEBUTTONDOWN and self.hover:
                if evt.button == 1:
                    precise_click = "left"

        return precise_click
    @property# bool
    def hover(self):
        """
        returns 'true' if the mouse-cursor floats over the element's rect. also
        sets 'self._hovering' to 'true', so we can check for several mouse-
        events.
        """
        # mouse-events
        mbut, mpos = self.mouse_events[:2]
        # returning-bool
        hover = False
        # this rect is used to check mouse-events. parent's position is going
        # to be added to its internal position.
        self.absloute_rect = pg.Rect(
            self.rect.left,
            self.rect.top,
            self.rect.width,
            self.rect.height,
        )
        if hasattr(self.parent, "rect"):
            self.absloute_rect.topleft = (
                self.absloute_rect.left + self.parent.rect.left,
                self.absloute_rect.top + self.parent.rect.top,
            )
        # mark as hovered
        if self.absloute_rect.collidepoint(mpos):
            hover = True
            self._hovering = True
        # if not hovered and clicked somwhere else, reset 'self.state'
        if not hover and (mbut[0] or mbut[1] or mbut[2]):
            self.state = "waiting"

        return hover
    @property# bool
    def start_hover(self):
        """returns 'true' if the cursor starts hovering an element."""
        start_hover = False

        if self._hovering and not self._start_hovering:
            self._start_hovering = True
            start_hover = True

        return start_hover
    @property# bool
    def leave(self):
        """
        returns 'true' if the mouse leaves the element. used to declare
        redrawing of surface on mouse-out.
        """
        leaving = False

        if self._hovering and not self.hover:
            leaving = True
            self._hovering = False
            self._start_hovering = False

        return leaving
    @property# tuple
    def mouse_events(self):
        """
        returns a tuple of 3 tuples containing clicked mouse-button, mouse-
        position and mouse-movement.
        """
        # somehow pg.mouse.get_rel() doesn't work here, so we have to get rels
        # from the app
        mrel = (0, 0)

        for evt in globals()["app"]._events:
            if evt.type == pg.MOUSEMOTION:
                mrel = evt.rel

        return (
            pg.mouse.get_pressed(),
            pg.mouse.get_pos(),
            mrel
        )
    # basic methods
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
    def create_rect(self):# pg.rect
        """
        returns a recreation of the element's rect. if 'style.position' is a
        tuple of three, the third argument can be a 'str' with a rect-anchor
        like 'topleft' or 'center'. this argument can be any pg.rect-positional
        key. example:
            position = (100, 50, "bottomleft")
        """
        rect = pg.Rect(
            self.style.position[:2],
            self.style.size
        )
        # setting rect-anchor if third tuple-arg is passed
        if len(self.style.position) > 2:
            setattr(rect, self.style.position[2], self.style.position[:2])

        return rect
    def redraw(self):
        """
        rebuilds the surface with all inner elements updated. one can pass a
        'GuiMaster'-element and blit this to the surface as well.
        """
        # drawing background
        self.redraw_background()
        # drawing background if set by user
        self.redraw_border()
    def redraw_background(self):
        """recreates only the background."""
        self.image.blit(self.background, (0, 0))
    def redraw_border(self):
        """only recreates border for the sprite.image."""
        if self.border:
            self.image.blit(self.border, (0, 0))
    def resize(self, size):
        """
        resizes the surface and updates its dimensions. as well as redrawing
        the background if there is one.
        """
        self.style.size = size
        self.rect.size = size
        self.image = pg.Surface(size, pg.SRCALPHA)
        # redrawing backgrounds and stuff
        self.redraw()
    def shift(self, pos, rect_pos="topleft"):
        """
        moves the element to the given position.

        'pos'           must be tuple of two ints.
        'rect_pos'      internal argument used for setting the new position to
                        an inner rect-position like 'center' or 'bottomright'
                        etc. all pg.rect-arguments are allowed.
        """
        setattr(self.rect, rect_pos, pos)
        self.style.position = self.rect.topleft
    def update(self):
        """runs with every game-loop."""
        # mouse-events
        mrel = self.mouse_events[2]
        # visual redrawing of this element depends on the following conditions:
        if self.start_hover or self.leave:
            self.redraw()
# most of these following elements draw their inherition from 'GuiMaster'
class Char(GuiMaster):
    """resembles an interactive character of a text"""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.
        """
        GuiMaster.__init__(self, type="char", **kwargs)
        self.font = pg.font.SysFont(
            self.style.font,
            self.style.font_size
        )
        self.image = self.font.render(
            self.style.digit,
            self.style.antialias,
            self.style.color
        )
        self.resize(self.image.get_rect().size)
    def __repr__(self):# str
        """string representation."""
        return "<Char({0})>".format(self.style.digit)
class Graph(GuiMaster):
    """a statistic graph drawing a line for inspecting the given value."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'chart'             'pg.surface' with the visualized graph already
                            drawn to it.
        'last_stat'         'int' positional height-argument for next graph-
                            line to start drawing from.
        'inspect'           subject to watch and draw a graph for. change this
                            with each game loop to keep it running. example:
                            graph.inspect = app.fps
        'text'              text-object - naming the element and displaying it
                            on the desired position.
        """
        GuiMaster.__init__(self, type="graph", **kwargs)
        self.chart = pg.Surface((self.rect.width,self.rect.height),pg.SRCALPHA)
        self.last_stat = 0
        self.inspect = None
        self.text = Text(
            text = self.style.text,
            font_size = 20,
            color = (120, 120, 130),
            position = (5, self.rect.height, "bottomleft")
        )
    # basic methods
    def resize(self, size):
        """overwrites parent's 'resize()'-method."""
        self.style.size = size
        self.rect.size = size
        self.image = pg.Surface(size, pg.SRCALPHA)
        self.chart = pg.Surface(size, pg.SRCALPHA)
        # redrawing backgrounds and stuff
        self.redraw()
    def update(self):
        """overwrites parent's 'update()'-method."""
        if self.inspect is not None:
            self.update_chart()
            self.redraw_border()
        if len(self.text.text_string) > 0:
            self.image.blit(self.text.image, self.text.rect)
    def update_chart(self):
        """creates a chart dan draws it to the graph-surface."""
        app = globals()["app"]
        chart_rect = self.chart.get_rect()
        line = (
            (
                chart_rect.width - 2,
                chart_rect.height - self.last_stat
            ),
            (
                chart_rect.width - 1,
                chart_rect.height - self.inspect
            )
        )
        # drawing the line to a minimalistic space on the right
        pg.draw.line(
            self.chart,
            self.style.line_color,
            *line,
            self.style.line_size
        )
        # cropping the image and shift it to left
        chop = pg.transform.chop(self.chart, [0, 0, 1, 0])
        # redrawing cropped area to chart
        self.chart = pg.Surface(chart_rect.size, pg.SRCALPHA)
        self.chart.fill(self.style.background_color)
        self.chart.blit(chop, (0, 0))
        # drawing chart to graph.image
        self.image.blit(self.chart, (0, 0))
        # updating next position for line to start drawing from
        self.last_stat = self.inspect
class Grid(GuiMaster):
    """grid-surface that has a border-drawn grid on it. used for tables etc."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'grid'              the grid-object with no contents, only a surface
                            with a drawn border if set by user.
        'cells'             'list' of rects created in 'self.create_grid'. each
                            rect is a positional drawing-arg for the values of
                            a cell.
        """
        GuiMaster.__init__(self, type="grid", **kwargs)
        self.grid = self.create_grid()
        self.cells = self.grid["rects"]
        # first time drawing grid to image-surface
        self.image.blit(self.grid["image"], (0, 0))
    # basic methods
    def create_grid(self):# dict
        """
        returns a dict, acting as a grid-element. uses 'self.grid["image"]' to
        draw the grid to the sprite-image-surface.
        """
        surface = pg.Surface(self.rect.size, pg.SRCALPHA)
        rects = []

        # storing every cell-rect in columns-list
        for r in range(len(self.style.rows)):
            for c in range(len(self.style.rows[0])):
                # creating a pg.rect for the momentary column
                rect = pg.Rect(
                    c * int(self.rect.width / len(self.style.rows[0])),
                    r * int(self.rect.height / len(self.style.rows)),
                    int(self.rect.width / len(self.style.rows[0])),
                    int(self.rect.height / len(self.style.rows)),
                )
                # drawing a border only if one is given by user
                if self.border: pg.draw.lines(
                    surface,
                    self.style.border_color,
                    False,
                    [
                        rect.bottomleft,
                        rect.topleft,
                        rect.topright
                    ],
                    self.style.border_size
                )
                # appending rect to returning-dict
                rects.append(rect)

        grid = {
            "image": surface,
            "rects": rects
        }

        return grid
    def resize(self, size):
        """overwrites parent's 'resize()'-method."""
        self.style.size = size
        self.rect.size = size
        # updating grid and cells
        self.grid = self.create_grid()
        self.cells = self.grid["rects"]
        # redrawing visuals
        self.redraw()
        self.image.blit(self.grid["image"], (0, 0))
    def update(self):
        """overwrites parent's 'update()'-method."""
        pass
class Table(GuiMaster):
    """table-object to pass gui-elements to its 'rows'-attribute."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'rows'      'tuple' of tuples that hold gui-elements or native python-
                    types.
        'grid'      'grid'-object that holds positional argument for drawing
                    the elements.
        """
        GuiMaster.__init__(self, type="table", **kwargs)
        self.rows = self.style.rows
        self.grid = Grid(**kwargs)
        # first time drawing visuals
        self.draw_visuals()
    # basic methods
    def draw_elements(self):
        """draws all elemenets in 'self.rows' to the grid-surface."""
        # 'i' is used to index the momentary rects-positon: grid.cells[i]
        i = 0
        # cycling trough elements to draw
        for r in range(len(self.rows)):
            for c in range(len(self.rows[r])):
                elem = self.rows[r][c]
                # resolving new position in two separate coordinates
                x, y = getattr(
                    self.grid.cells[i],
                    self.style.text_position
                )
                # drawing depends on element-type
                if type(elem) is str:
                    # creating new text-element and shift its position by
                    # user defined args before drawing it to the returning-
                    # surface
                    text = Text(
                        text = elem,
                        font_size = self.style.text_size
                    )
                    x += self.style.text_margin[3]
                    text.shift((x, y), self.style.text_position)
                    self.image.blit(text.image, text.rect)
                else:
                    self.image.blit(elem.image, (x, y))
                # changing next rects-index
                i += 1
    def draw_visuals(self):
        """redrawing all visuals."""
        self.image.blit(self.grid.image, (0, 0))
        self.draw_elements()
    def replace_rows(self, rows):
        """
        this method replaces the internal 'rows'-value with the given one.
        snytax looks like this:
            my_rows = (
                ("column1", "object1"),
                ("column2", "object2")
            )
            self.replace_rows(my_rows)
        each single str-value can also be replaced with drawable objects. but
        if it comes as a string, the table automatically creates a text-object
        to draw it on itself.
        """
        self.style.rows = rows
        self.rows = rows
        # redrawing visuals
        self.draw_visuals()
    def resize(self, size):
        """overwrites parent's 'resize()'-method."""
        self.style.size = size
        self.rect.size = size
        self.grid.resize(size)
        # redrawing visuals
        self.draw_visuals()
    def update(self):
        """overwrites parent's 'update()'-method."""
        pass
class Text(GuiMaster):
    """resembles a text-object."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'text_string'   actual text-string (str).
        'font'          'pygame.font'-object to render a text with.
        'rect'          'pg.rect' recreating this here enables the given
                        positon to apply.
        """
        # initialising text-object
        if not "type" in kwargs: kwargs["type"] = "text"
        GuiMaster.__init__(self, **kwargs)
        # initialising and styling font-object
        pg.font.init()
        self.text_string = self.style.text
        self.font = pg.font.SysFont(
        	self.style.font,
        	self.style.font_size
        )
        self.font.set_bold(self.style.bold)
        self.font.set_italic(self.style.italic)
        # downsizing element to text.rect-size
        self.style.size = self.text.get_rect().size
        self.resize(self.style.size)
        # recreating rect to apply positional args from inheriting classes
        self.rect = self.create_rect()
        # drawing text to text-surface
        self.image.blit(self.text, self.style.line_balance)
    # dynamic properties
    @property# pg.surface
    def text(self):
        """
        considering own 'wrap'-attribute, this returns a pg.surface with
        blitten text to it.
        """
        # creating text-surface
        if type(self.style.text) is pg.Surface:
            text = self.style.text
        else:
            text = u.makeText(
                font = self.style.font,
                text = self.style.text,
                size = self.style.font_size,
                color = self.style.color,
                antialias = self.style.antialias,
                bold = self.style.bold,
                italic = self.style.italic,
                wrap = self.style.wrap
            )
        # creating the former rect for the final surface to return
        rect = text.get_rect()
        # looking for padding to apply as size and position
        if self.style.padding:
            rect.width += 2 + self.style.padding[3] + self.style.padding[1]
            rect.height += 2 + self.style.padding[0] + self.style.padding[2]
            rect.left = self.style.padding[3]
            rect.top = self.style.padding[0]
        # this is the final surface we will return at the end
        final_surface = pg.Surface(rect.size, pg.SRCALPHA)
        # render a self-made shadow if user disires so
        if self.style.shadow:
            shadow = self.style.shadow
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
    # basic methods
    def resize(self, size):
        """overwrites parent's 'resize()'-method."""
        self.rect.size = size
        self.style.size = size
        self.image = pg.Surface(size, pg.SRCALPHA)
        # drawing text to text-surface
        self.redraw()
        self.image.blit(self.text, self.style.line_balance)
    def update(self):
        """overwrites parent's 'update()'-method."""
        pass
    def update_text(self, text):
        """updates 'text_string' and redraws text-visuals."""
        self.style.text = text
        self.text_string = text
        self.resize(self.text.get_rect().size)
class Button(Text):
    """
    represents a button but works like a text with GuiMaster's extended sprite-
    features.
    """
    def __init__(self, **kwargs):
        """
        uses 'Text' as its parent with additional methods and attributes.
        """
        Text.__init__(self, type="button", **kwargs)
    def update(self):
        """overwrites parent's 'update()'-method."""
        # mouse-events
        mrel = self.mouse_events[2]

        if (self.hover or self.leave) and (mrel[0] or mrel[1]):
            self.redraw()
            self.image.blit(self.text, self.style.line_balance)
class ArrowButton(GuiMaster):
    """represents an arrow-button with an arrow drawn on it."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'arrow'     pg.surface with the arrow alreay blitten on.
        'image'     pg.surface to draw on.
        """
        GuiMaster.__init__(self, type="arrow_button", **kwargs)
        # drawing an arrow to the image
        self.arrow = self.create_arrow()
        self.image.blit(self.arrow, (0, 0))
    def create_arrow(self):# pg.surface
        """returns a pg.surface with an arrow drawn on."""
        surface = pg.Surface(self.style.size, pg.SRCALPHA)

        surface = u.drawArrow(
            surface,
            direction = self.style.direction,
            color = self.style.arrow_color,
            margin = self.style.margin
        )

        return surface
    # basic mathodes
    def update(self):
        """overwrites parent's 'update()'-method."""
        # mouse-events
        mrel = self.mouse_events[2]
        # recreating visuals on hover
        if (self.hover or self.leave) and (mrel[0] or mrel[1]):
            self.redraw()
            self.image.blit(self.arrow, (0, 0))
class PanelButton(GuiMaster):
    """represents an arrow-button with an arrow drawn on it."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'symbol'        pg-surface with a butt-symbol ready to be drawn.
        """
        GuiMaster.__init__(self, type="panel_button", **kwargs)
        self.symbol = self.create_symbol()
        # first time drawing symbol to button
        self.image.blit(self.symbol, (0, 0))
    # basic mathodes
    def create_symbol(self):
        """returns a pg.surface with a symbol drawn to it."""
        symbol =  pg.Surface(self.rect.size, pg.SRCALPHA)
        color = self.style.symbol_color

        # drawing an 'x'-symbol
        if self.style.symbol == "close":
            symbol = u.drawSymbol(
                symbol,
                type = "x",
                color = color,
                margin = 5,
                size = 4
            )
        # drawing a rect-symbol
        if self.style.symbol == "maximize":
            symbol = u.drawSymbol(
                symbol,
                type = "rect",
                color = color,
                margin = 5,
                size = 3
            )
        # drawing an underline-symbol
        if self.style.symbol == "minimize":
            symbol = u.drawSymbol(
                symbol,
                type = "_",
                color = color,
                margin = 5,
                size = 3
            )

        return symbol
    def update(self):
        """overwrites parent's 'update()'-method."""
        # mouse-events
        mrel = self.mouse_events[2]
        # recreating visuals on hover
        if (self.hover or self.leave) and (mrel[0] or mrel[1]):
            self.redraw()
            self.image.blit(self.symbol, (0, 0))
class Panel(GuiMaster):
    """a panel-surface to draw information or elements on."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'drag_area'         user-declared area of dragging an element. if left
                            out, use the whole element-rect for dragging.
        '__dragged_at'      standard 'none' later becomes a tuple of 2 ints.
                            this can be used to calculate the position of an
                            element when the mouse tries to drag it.
        'buttons'           'list' of panel-button-elements to draw.
        """
        # initialising panel-object
        if not "type" in kwargs: kwargs["type"] = "panel"
        GuiMaster.__init__(self, **kwargs)
        if self.style.drag_area:
            self.drag_area = pg.Rect(self.style.drag_area)
        else:
            self.drag_area = self.style.drag_area
        self.__dragged_at = None
        self.buttons = self.create_buttons()
        # first time drawing buttons to image-surface
        for button in self.buttons:
            self.image.blit(button.image, button.rect)
    # dynamic attributes
    @property# bool
    def drag(self):
        """
        returns 'true' if element is dragable and been dragged by the mouse.
        calling this also drags the surface around when the element is
        dragable.
        """
        if self.style.dragable:
            # mouse events
            mbut, mpos, _ = self.mouse_events
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
                    # clicked yet, set its '_clicked'-state 'true' and
                    # calculate the clicked position on the element's rect
                    if not self._clicked:
                        # adding left and top of 'drag_area' so the element
                        # doesn't jump on click
                        if self.drag_area:
                            self.__dragged_at = (
                                mpos[0] - rect.x + self.drag_area.left,
                                mpos[1] - rect.y + self.drag_area.top
                            )
                        else:
                            self.__dragged_at = (
                                mpos[0] - rect.x,
                                mpos[1] - rect.y
                            )
                        self._clicked = True
            # if left mouse-button is released or just not pressed, mark
            # element as clicked ('true')
            if not mbut[0]:
                self.__dragged_at = None
                self._clicked = False
            # if element is marked as clicked, redraw parent's background on a
            # specific place and update its topleft-position. this removes the
            # previously drawn element's trails from the surface again
            if self._clicked:
                self.rect.topleft = (
                    mpos[0] - self.__dragged_at[0],
                    mpos[1] - self.__dragged_at[1]
                )
        else:
            self._clicked = False

        return self._clicked
    # basic methods
    def create_buttons(self):# list
        """returns a list of panel-buttons to blit on the panel."""
        buttons = []
        # declaring drawing-position for next button
        x = self.style.button_margin[1]

        for but in self.style.buttons:
            button = PanelButton(
                parent = self,
                symbol = but
            )
            # declaring position of buttons to draw
            if self.style.drag_area:
                pos = (
                    self.drag_area.right - x,
                    self.drag_area.top + self.style.button_margin[0]
                )

            else:
                pos = (
                    self.rect.width - x,
                    self.style.button_margin[0]
                )
            x += button.rect.width + self.style.button_margin[1]
            # moving button to 'pos'
            button.shift(pos, "topright")
            # appending button to returning-list
            buttons.append(button)

        return buttons
    def handle_buttons(self):
        """button-event-handler."""
        # mouse-events
        mrel = self.mouse_events[2]

        for button in self.buttons:
            # disabling drag-functionality on button-click
            if button.click:
                self._clicked = False
            # redrawing buttons on hover or out
            button.update()
            self.image.blit(button.image, button.rect)
    def redraw(self):
        """
        rebuilds the surface with all inner elements updated. one can pass a
        'GuiMaster'-element and blit this to the surface as well.
        """
        # drawing background
        self.redraw_background()
        # drawing drag-area if set by user
        self.redraw_dragarea()
        # drawing background if set by user
        self.redraw_border()
    def redraw_dragarea(self):
        """only recreates a drag-area if set by user."""
        if self.style.drag_area:
            rect = pg.Rect(self.style.drag_area)
            self.image.fill(self.style.drag_area_background, rect)
    def update(self):
        """overwrites parent's 'update()'-method."""
        # mouse-events
        mrel = self.mouse_events[2]
        # invoking drag-operation
        self.drag
        # visual redrawing of this element depends on the following conditions:
        if (self.hover and (mrel[0] or mrel[1])) or self.leave:
            # redrawing visuals
            if self.style.background_hover:
                self.redraw()
            # handling button-events
            self.handle_buttons()
class InfoBar(Panel):
    """
    this bar is used for displaying usefull information about the app and its
    contents.
    """
    def __init__(self, **kwargs):
        """
        uses 'Panel' as its parent with additional methods and attributes.
        """
        Panel.__init__(self, type="info_bar", **kwargs)
class MenuBar(Panel):
    """a menu-bar-object with menus to call on clicked options."""
    def __init__(self, **kwargs):
        """
        uses 'Panel' as its parent with additional methods and attributes.
        """
        Panel.__init__(self, type="menu_bar", **kwargs)
class Window(Panel):
    """a callable window-popup-surface."""
    def __init__(self, **kwargs):
        Panel.__init__(self, type="window", **kwargs)
class Slider(GuiMaster):
    """
    slider-element with a handle to drag around. the position of the handle
    becomes the value of this element.
    """
    class Rail(pg.sprite.Sprite):
        """resembling the moving-tracks of a slider-element."""
        def __init__(self, **kwargs):
            """
            'stylesheet'        the validated 'dict' to draw building-
                                instructions from. evaluation between passed
                                keyword-args and a dict of predefined
                                attributes.
            'rect'              element's dimensions.
            'image'             'pg.surface' of this element to draw on.
            """
            pg.sprite.Sprite.__init__(self)
            self.style = Stylesheet(
                type = "slider_rail",
                style = kwargs
            )
            self.rect = pg.Rect(self.style.position, self.style.size)
            self.image = pg.Surface(self.style.size)
            self.image.fill(self.style.background_color)
    class Handle(pg.sprite.Sprite):
        """resembling a dragable handle for a slider-element."""
        def __init__(self, **kwargs):
            """
            'stylesheet'        the validated 'dict' to draw building-
                                instructions from. evaluation between passed
                                keyword-args and a dict of predefined
                                attributes.
            'rect'      element's dimensions.
            'image'     'pg.surface' of this element to draw on.
            'dragged'   'bool' - 'true' if handle is dragged around.
            """
            pg.sprite.Sprite.__init__(self)
            self.style = Stylesheet(
                type = "slider_handle",
                style = kwargs
            )
            self.rect = pg.Rect(self.style.position, self.style.size)
            self.image = pg.Surface(self.style.size)
            self.image.fill(self.style.background_color)
            self.dragged = False
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'rail'      (sprite) this subelement is the track of the slider to move
                    the handle along.
        'handle'    (sprite) dragable handle-subelement of this class.
        """
        GuiMaster.__init__(self, type="slider", **kwargs)
        # changing self.rect.size and size of subelements relative to
        # 'style.alignment'
        if self.style.alignment == "vertical":
            self.resize((self.style.size[1], self.style.size[0]))
            rail_size = (int(self.rect.width / 2), self.rect.height)
            handle_size = (self.rect.width, self.rect.width)
        else:
            rail_size = (self.rect.width, int(self.rect.height / 2))
            handle_size = (self.rect.height, self.rect.height)
        # creating sub-elements ('rail' and 'handle')
        self.rail = self.Rail(
            size = rail_size
        )
        self.handle = self.Handle(
            size = handle_size
        )
        # drawing track and handle
        self.draw_elements()
    # dynamic attributes
    @property# bool
    def dragged(self):
        """returns 'true' if the handle is dragged around."""
        # assignments
        mbut, mpos, mrel = self.mouse_events
        # absolute position of the handle
        handle = pg.Rect(
            (
                self.handle.rect.left + self.style.position[0],
                self.handle.rect.top + self.style.position[1],
            ),
            self.handle.rect.size
        )
        # checking for drag
        if handle.collidepoint(mpos) and mbut[0]:
            self.handle.dragged = True
        elif self.handle.dragged and not mbut[0]:
            self.handle.dragged = False
        # updating handle-position on drag
        if self.handle.dragged:
            # restricting drag to left and right
            if self.style.alignment == "horizontal":
                if self.handle.rect.left + mrel[0] < 0:
                    self.handle.rect.left = 0
                elif self.handle.rect.right + mrel[0] > self.rail.rect.width:
                    self.handle.rect.right = self.rail.rect.width
                # updating handle-position if not to small or to big
                else:
                    self.handle.rect.left += mrel[0]
            # restricting drag to up and down
            elif self.style.alignment == "vertical":
                if self.handle.rect.top + mrel[1] < 0:
                    self.handle.rect.top = 0
                elif self.handle.rect.bottom + mrel[1] > self.rail.rect.height:
                    self.handle.rect.bottom = self.rail.rect.height
                # updating handle-position if not to small or to big
                else:
                    self.handle.rect.top += mrel[1]

        return self.handle.dragged
    # basic methods
    def draw_elements(self):
        """draws all internal elements to the image-surface."""
        # drawing rail depending on 'style.alignment'
        if self.style.alignment == "horizontal":
            self.image.blit(
                self.rail.image,
                (0, int(self.rail.rect.height / 2))
            )
        else:
            self.image.blit(
                self.rail.image,
                (int(self.rail.rect.width / 2), 0)
            )
        # drawing the handle
        self.image.blit(self.handle.image, self.handle.rect)
    def update(self):
        """overwrites parent's 'update()'-method."""
        if self.dragged:
            # recreating transparent background if there is no color for it
            if not self.style.background_color:
                self.image = pg.Surface(self.rect.size, pg.SRCALPHA)
            # drawing the slider-track (rail) and handle
            self.draw_elements()
            # recreating border if there is one
            if self.style.border:
                self.redraw_border()
class TextField2(GuiMaster):
    """resembles a text-field-element for typing in some text."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'text_string'   with entered keys combined as a str.
        'cursor'        'pg.surface' that comes along with some additional
                        operations for correctly drawing itself to its parent.
        """
        # initialising text-object
        if not "type" in kwargs: kwargs["type"] = "text_field"
        GuiMaster.__init__(self, **kwargs)
        self.text_string = ""
        self.cursor = TextCursor(
            size = (2, self.rect.height - 10),
            position = (5, 5)
        )
    # dynamic properties
    @property# text-object
    def text(self):
        """returns a text-object."""
        text = Text(
            text = self.text_string,
            font_size = 16,
            position = (8, 0)
        )
        text.rect.top = int(self.rect.height / 2) - int(text.rect.height / 2)

        return text
    # basic methods
    def handleCursor(self):
        """
        checks 'cooldown' and draws either 'cursor' or 'background'. draws the
        cursor on 'active' and clears it again on 'waiting'.
        """
        # mouse-events
        mbut = self.mouse_events[0]

        if self.state == "active":
            # updating blinking-cursors drawing-position
            self.cursor.rect.left = self.text.rect.right
            # drawing cursor if cooldown over 50
            if self.cursor.cooldown >= 50:
                self.image.blit(self.cursor.image, self.cursor.rect)
            # redrawing background over cursor if cooldown falls below 50
            elif self.cursor.cooldown < 50:
                self.image.blit(self.background, self.cursor.rect)
                self.redraw_border()
            # resetting cooldown or further reducing it
            if self.cursor.cooldown == 0:
                self.cursor.cooldown = 100
            else:
                self.cursor.cooldown -= 1
        # resetting cursor by clicking somewhere else
        elif not self.hover and (mbut[0] or mbut[1] or mbut[2]):
            self.redraw_background()
            self.redraw_border()
            # redrawing text if there is one typed in
            if len(self.text_string) >= 1:
                self.image.blit(self.text.image, self.text.rect)
    def handleInput(self):
        """
        translates pressed keys and adds their char to 'text_string'. draws the
        text to textfields-surface afterwards.
        """
        # mouse-events
        mrel = self.mouse_events[2]

        if self.state == "active":
            for evt in globals()["app"]._events:
                if evt.type is pg.KEYDOWN:
                    # translating key to unicode
                    char = pg.key.name(evt.key)
                    # special operations if key is longer than a single char or
                    # letter. adding an empty space to string
                    if evt.key is pg.K_SPACE:
                        char = " "
                    # removing last entered char from string
                    elif evt.key is pg.K_BACKSPACE:
                        self.text_string = self.text_string[:-1]
                        char = ""
                    # appending char to string
                    self.text_string += char
                # recreating background and drawing text to textfield (only
                # when mouse is not moving)
                if not(mrel[0] or mrel[1]):
                    self.redraw()
                    self.image.blit(self.text.image, self.text.rect)
    def update(self):
        """overwrites parent's 'update()'-method."""
        # mouse-events
        mrel = self.mouse_events[2]
        # visual redrawing of this element depends on the following conditions:
        if (
            (self.hover and (mrel[0] or mrel[1])) or self.click or self.leave
        ):
            self.redraw()
            self.image.blit(self.text.image, self.text.rect)
        # drawing cursor on activation
        self.handleCursor()
        # handling input-chars & letters for displaying them in the textfield
        self.handleInput()
class Slot(GuiMaster):
    """
    this is an advanced text-input with 'up'- and 'down' buttons to lower and
    raise its content.
    """
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'text_field'    pg.srpite that acts as a text_field to lower or raise.
        'arrow_up'      up-button-sprite.
        'arrow_down'    down-button-sprite.
        """
        GuiMaster.__init__(self, type="slot", **kwargs)
        self.text_field = TextField(
            size = (self.rect.width, self.rect.height),
            position = self.style.position,
            background_color = self.style.background_color,
            border = self.style.border,
            border_size = self.style.border_size,
            border_color = self.style.border_color
        )
        self.arrow_up = ArrowButton(
            parent = self,
            size = (int(self.rect.height / 2), int(self.rect.height / 2)),
            position = (self.rect.width, 0),
            background_color = self.style.border_color,
            background_hover = self.style.background_hover,
            border = self.style.border,
            border_size = self.style.border_size,
            border_color = self.style.border_color,
            direction = "up",
            margin = 4,
            arrow_color = self.style.background_color
        )
        self.arrow_down = ArrowButton(
            parent = self,
            size = (int(self.rect.height / 2), int(self.rect.height / 2)),
            position = (self.rect.width, self.arrow_up.rect.height),
            background_color = self.style.border_color,
            background_hover = self.style.background_hover,
            border = self.style.border,
            border_size = self.style.border_size,
            border_color = self.style.border_color,
            direction = "down",
            margin = 4,
            arrow_color = self.style.background_color
        )
        # resizing surface to make some space for the arrow-buttons to draw
        self.resize((
            self.rect.width + self.arrow_up.rect.width,
            self.rect.height
        ))
        # drawing everything to the image-surface
        self.image.blit(self.text_field.image, (0, 0))
        self.image.blit(self.arrow_up.image, self.arrow_up.rect)
        self.image.blit(self.arrow_down.image, self.arrow_down.rect)
    # basic methods
    def raise_value(self):
        """raises the value of the slot.frame if it represents an integer."""
        try:
            self.text_field.text_string = str(
                int(self.text_field.text_string) + 1
            )
        except ValueError:
            pass
    def lower_value(self):
        """lowers the value of the slot.frame if it represents an integer."""
        try:
            self.text_field.text_string = str(
                int(self.text_field.text_string) - 1
            )
        except ValueError:
            pass
    def update(self):
        """overwrites parent's 'update()'-method."""
        # redrawing arrow-buttons on hover or out
        if self.arrow_up.hover or self.arrow_up.leave:
            self.arrow_up.update()
            self.image.blit(self.arrow_up.image, self.arrow_up.rect)
        if self.arrow_down.hover or self.arrow_down.leave:
            self.arrow_down.update()
            self.image.blit(self.arrow_down.image, self.arrow_down.rect)
        # changing value of the text-field if it's an integer
        if self.arrow_up.precise_click:
            self.raise_value()
        elif self.arrow_down.precise_click:
            self.lower_value()
        # redrawing text-field
        self.text_field.update()
        self.image.blit(self.text_field.image, (0, 0))
class Menu(GuiMaster):
    """
    represents a listable menu. its dimensions depend on its options.
    example:
        menu = Menu(
            ("Option 1", print, "Option1 has been clicked."),
            ("Option 2", pprint, "Option2 has been clicked.")
        )
    while the first argument sets the name for this option, the second one
    holds the function to call on click. any more arguments behind these two
    will automatically become pass-args for the function to call.
    """
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'options'       list of renderable options.
        """
        GuiMaster.__init__(self, type="menu", **kwargs)
        # creating a rect with absolute position for mouse-events
        self.options = self.create_options()
        self.draw_options()
    # basic methods
    def create_options(self):# list
        """
        creates a list of renderable options with their callable functions and
        returns it.
        """
        # returning list
        options = []
        # will be influenced by the biggest element to draw. this is used to
        # recreate the menu-surface with this width-argument
        biggest_width = 0
        # determines the next option's vertical drawing-position
        y = self.style.margin[0]

        for opt in self.style.options:
            name = opt[0]
            func = opt[1]
            params = opt[2:]
            # creating the text-element
            option = Text(
                text = name,
                font_size = self.style.font_size
            )
            # adding function-name and parameter to option
            option.call = (func, *params)
            # updating next option's vertical drawing-position
            option.rect.top += y
            y += option.rect.height
            # putting some margin in front of this option
            option.rect.left += self.style.margin[3]
            # updating maximal-width for menu
            if option.rect.width > biggest_width:
                biggest_width = option.rect.width
            # creating a rect with absolute position for mouse-events
            option.absolute_rect = pg.Rect(
                option.rect.left + self.rect.left - self.style.margin[3],
                option.rect.top + self.rect.top,
                *option.rect.size,
            )
            # appending option to returning-list
            options.append(option)
        # exception fot biggest_width being 0
        if biggest_width == 0:
            biggest_width = u.STYLE["menu"]["size"][0]
        # resizing menu
        self.resize((
            biggest_width + self.style.margin[1],
            y + self.style.margin[2]
        ))
        # stretching width of absolute_rect
        for opt in options:
            opt.absolute_rect.width = self.rect.width

        return options
    def draw_options(self):# list
        """draws all options to the menu-element."""
        # mouse-events
        mpos = self.mouse_events[1]

        for opt in self.options:
            # drawing background_hover if set by user
            if opt.absolute_rect.collidepoint(mpos):
                if self.style.background_hover:
                    self.image.fill(
                        self.style.background_hover,
                        [
                            opt.rect.left - self.style.margin[3],
                            opt.rect.top,
                            self.rect.width,
                            opt.rect.height
                        ]
                    )
            #drawing default background if set by user
            elif self.style.background_color:
                self.image.fill(
                    self.style.background_color,
                    [
                        opt.rect.left - self.style.margin[3],
                        opt.rect.top,
                        self.rect.width,
                        opt.rect.height
                    ]
                )
            # drawing text over background
            self.image.blit(opt.image, opt.rect)
    def update(self):
        """overwrites parent's 'update()'-method."""
        # mouse-events
        mpos = self.mouse_events[1]
        # drawing all options
        self.draw_options()

        for opt in self.options:
            # on option.hover
            if opt.absolute_rect.collidepoint(mpos):
                # on option.precise_click
                if opt.precise_click:
                    # if option's function is callable
                    if callable(opt.call[0]):
                        opt.call[0].__call__(*opt.call[1:])
                    else:
                        print("Function '{0}' not callable.".format(
                            opt.call[0]
                        ))
class DropDown(GuiMaster):
    """represents a drop-down-menu while using a menu-class as a subelement."""
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'menu'          a whole rendered menu-element to draw when the dropdown
                        element has been clicked (selection was made).
        'selection'     the selected menu.option as a 'text'-element.
        'arrow'         'pg.sprite' of a hoverable and clickable arrow-button.
        """
        GuiMaster.__init__(self, type="drop_down", **kwargs)
        self.menu = Menu(
            options = self.style.options,
            position = self.absloute_rect.topleft,
            #margin = [0, 0, 0, 0]
        )
        self.selection = self.menu.options[0]
        self.arrow = ArrowButton(
            parent = self,
            size = (self.rect.height, self.rect.height),
            background_color = self.style.border_color,
            background_hover = self.style.background_hover,
            border = self.style.border,
            border_size = self.style.border_size,
            border_color = self.style.border_color,
            direction = "down",
            margin = 7,
            arrow_color = self.style.background_color
        )
        # resizing dropdown-surface based on menu-width
        self.resize((
            self.menu.rect.width + self.arrow.rect.width,
            self.rect.height
        ))
        # drawing selected option (at first time it's gonna be menu.options[0])
        self.draw_selection()
        # repositioning arrow-button and drawing it to menu.image
        self.arrow.rect.right = self.rect.width
        self.image.blit(self.arrow.image, self.arrow.rect)
    # basic methods
    def call_menu(self):
        """
        calls and draws the menu right under the dropdown-element. uses app's
        'draw_list' to render the menu as long as it's not de-clicked.
        """
        # mouse-events
        mbut = self.mouse_events[0]
        app = globals()["app"]

        # adding menu to draw_list on click
        if self.arrow.click:
            app.draw_list.add(self.menu)
        # removing menu from 'draw_list' if clicked or aborted
        elif (
            self.menu in app.draw_list and
            (not self.hover and mbut[0]) or
            self.menu.precise_click
        ):
            app.draw_list.remove(self.menu)
    def draw_arrow(self):
        """draws the arrow button to the dropdown-surface."""
        self.arrow.update()
        self.image.blit(self.arrow.image, self.arrow.rect)
    def draw_selection(self):
        """draws the selected option as a text on the text-output."""
        pos = (
            self.menu.style.margin[3],
            int(self.rect.height / 2) - int(self.selection.rect.height / 2)
        )

        self.image.blit(self.selection.image, pos)
    def make_selection(self):
        """changes the momentary selection and redraws it on the surface."""
        # changing 'self.selection' on menu.option.click and redrawing visuals.
        # the way this segment works is a little buggy but in a funny way:
        # while click- and hold the textarea, u can change the inner-value as
        # well.
        # mouse-events
        mbut, mpos = self.mouse_events[:2]

        for opt in self.menu.options:
            if opt.absolute_rect.collidepoint(mpos) and mbut[0]:
                self.selection = opt
                self.redraw()
                self.draw_arrow()
                self.draw_selection()
    def update(self):
        """overwrites parent's 'update()'-method."""
        # mouse-events
        #mrel = self.mouse_events[2]

        if self.click or self.hover or self.leave:
            # drawing updated arrow-image
            self.draw_arrow()
            # drawing menu if dropdown or its arrow has been clicked
            self.call_menu()
            # change selection related to menu.option.click
            self.make_selection()

class TextField(GuiMaster):
    """
    resembles a text-field-element for typing in some text.

    class 'Marker'      a blinking text-marker (pg.sprite).
    """
    class Marker(pg.sprite.Sprite):
        """blinking text-cursor for text-field."""
        def __init__(self, **kwargs):
            """
            'style'             the validated 'dict' to draw building-
                                instructions from. evaluation between passed
                                keyword-args and a dict of predefined
                                attributes.
            'rect'              (pg.rect) cursor dimensions.
            'cooldown'          'int' to decrease on update for drawing a
                                blinking marker to the text-field-element.
            '__cd'              internal int to save the initial cooldown.
            'visible'           used to determine the drawing-state of this
                                element. set this 'bool' true or false within
                                its parent element.
            """
            pg.sprite.Sprite.__init__(self)
            self.style = Stylesheet(
                type = "text_marker",
                style = kwargs
            )
            self.rect = pg.Rect(self.style.position, self.style.size)
            self.cooldown = 150
            self.__cd = 150
            self.visible = False
        # dynamic attributes
        @property
        def image(self):# pg.surface
            """"
            returns the image-surface of the marker either filled or not
            depending on cooldown.
            """
            image = pg.Surface(self.rect.size, pg.SRCALPHA)

            if self.cooldown >= int(self.__cd / 2):
                image.fill(self.style.color)

            self.cooldown -= 1
            if self.cooldown == 0:
                self.cooldown = self.__cd

            return image
        # basic methods
        def shift(self, pos, rect_pos="topleft"):
            """
            moves the element to the given position.

            'pos'           must be tuple of two ints.
            'rect_pos'      internal argument used for setting the new position
                            to an inner rect-position like 'center' or
                            'bottomright' etc. all pg.rect-arguments are
                            allowed.
            """
            setattr(self.rect, rect_pos, pos)
            self.style.position = self.rect.topleft
    def __init__(self, **kwargs):
        """
        uses 'GuiMaster' as its parent with additional methods and attributes.

        'text_string'       the fully entered text-input as a str. by drawing
                            'self.text' to a surface, this variable is used to
                            create a new text-object.
        'marker'            a blinking pg.sprite shows where the cursor is set
                            within the textfield.
        """
        # initialising text-object
        if not "type" in kwargs: kwargs["type"] = "text_field"
        GuiMaster.__init__(self, **kwargs)
        self.text_string = ""
        self.marker = self.Marker(
            size = (2, self.rect.height - 10),
            position = (5, 5)
        )
    # dynamic properties
    @property# text-object
    def text(self):
        """returns a text-object."""
        text = Text(
            text = self.text_string,
            font_size = self.style.font_size
        )
        if self.style.multiline:
            pass
        else:
            text.shift((
                text.rect.left,
                int(self.rect.height / 2) - int(text.rect.height / 2)
            ))

        return text
    # basic methods
    def handle_input(self):
        """
        translates pressed keys and adds their char to 'text_string'. draws the
        text to textfields-surface afterwards.
        """
        # mouse-events
        mrel = self.mouse_events[2]

        if self.state == "active":
            for evt in globals()["app"]._events:
                if evt.type is pg.KEYDOWN:
                    # translating key to unicode
                    char = pg.key.name(evt.key)
                    # special operations if key is longer than a single char or
                    # letter. adding an empty space to string
                    if evt.key is pg.K_SPACE:
                        char = " "
                    # removing last entered char from string
                    elif evt.key is pg.K_BACKSPACE:
                        self.text_string = self.text_string[:-1]
                        char = ""
                    # appending char to string
                    self.text_string += char
                # recreating background and drawing text to textfield (only
                # when mouse is not moving)
                if not(mrel[0] or mrel[1]):
                    self.redraw()
                    self.image.blit(self.text.image, self.text.rect)
    def handle_marker(self):
        """
        checks 'cooldown' and draws either 'marker' or 'background'. draws the
        marker on 'active' and clears it again on 'waiting'.
        """
        if self.click:
            self.marker.visible = True

        if self.marker.visible:
            """self.marker.shift(
                (
                    self.rect.right,
                    self.marker.rect.top
                )
            )"""

            self.image.blit(
                self.background,
                self.marker.rect.topleft,
                self.marker.rect
            )
            self.image.blit(self.marker.image, self.marker.rect)
    def update(self):
        """overwrites parent's 'update()'-method."""
        if self.start_hover or self.leave:
            self.redraw()
            self.image.blit(self.text.image, self.text.rect)

        self.handle_input()
        self.handle_marker()

class Text2(GuiMaster):
    """."""
    def __init__(self, **kwargs):
        """."""
        GuiMaster.__init__(self, type="text", **kwargs)
        self.text = self.create_text()
        #self.resize(self.text["rect"].size)
        #self.image.blit(self.text["surface"], (0, 0))
        pass
    def create_text(self):
        """."""
        app = globals()["app"]
        rect = pg.Rect(0, 0, 0, 0)
        lines, actual_line, y = [[]], 0, 0
        line_height = Char(
            digit = "Tg",
            font = self.style.font,
            font_size = self.style.font_size,
            color = self.style.color,
            antialias = self.style.antialias
        ).rect.height

        if self.style.wrap:
            # determining the width to wrap with
            if type(self.style.wrap) is bool and self.style.wrap is True:
                wrap_width = app.rect.width
            elif type(self.style.wrap) is int:
                wrap_width = sself.style.wrap
            # enumerating the text-string to resolve its chatacters into
            # several lines if necessary.
            for i, c in enumerate(self.style.text):
                char = Char(
                    digit = c,
                    font = self.style.font,
                    font_size = self.style.font_size,
                    color = self.style.color,
                    antialias = self.style.antialias
                )

                if rect.width + char.rect.width > wrap_width:
                    lines.append([])
                    actual_line += 1
                    rect = pg.Rect(0, 0, 0, 0)

                lines[actual_line].append(char)
                rect.width += char.rect.width

            for line in lines:
                print(line)

        return
    def create_text2(self):
        """
        returns a dict with the text-surface along with a list of each chars
        rect.
        """
        if not self.style.wrap: width = self.parent.rect.width
        else: width = self.style.wrap
        font = pg.font.SysFont(
            self.style.font,
            self.style.font_size
        )
        char_rects, previous_y, line_height = [], 0, font.size("Tg")[1]
        surface = pg.Surface((width, line_height), pg.SRCALPHA)

        for i, s in enumerate(self.style.text):
            char = font.render(
                self.style.text[i],
                self.style.antialias,
                self.style.color
            )
            char_rect = char.get_rect()
            char_rect.left += previous_y
            surface.blit(char, char_rect.topleft)
            previous_y += char_rect.width
            char_rects.append(char_rect)
            """print(
                "#{}".format(i),
                s,
                char_rect,
            )"""

        return {
            "surface": surface,
            "rect": surface.get_rect(),
            "char_rects": char_rects
        }
    def update(self):
        """."""
        app = globals()["app"]
        mpos = self.mouse_events[1]

        if app.resized:
            #if not self.style.wrap: size = app.rect.size
            #else: size = (self.style.wrap, app.rect.height)
            #self.resize(size)
            #self.image.blit(self.text, (0, 0))
            pass

        for i, char in enumerate(self.text["char_rects"]):
            if char.collidepoint(mpos):
                print(self.style.text[i], self.text["char_rects"][i])
