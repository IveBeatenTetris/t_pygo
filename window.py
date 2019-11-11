from .utils import (
    LIBPATH,
    validateDict,
    getDisplay,
    draw
)
import sys
import pygame as pg

class Window:
    """pygame's window module with extended features."""
    default = {
        "size": (320, 240),
        "title": "No Title",
        "resizable": False,
        "icon": LIBPATH["windowicon"],
        "fps": 30
    }
    def __init__(self, config={}):
        """
        initiates pygame to act as a pygame-window.
        'title' is gonna be displayed as the windows title.
        'icon' is displayed next to the title in the window.
        'preffered_fps' - its in the name.
        'fps' is gonna be updated from the windows update-method.
        'pausemenu' is a switch for showing a gui and closing it.
        'mode' is for switching trough modes like 'moving' or 'paused'.
        'display' holds the actual pygame window.
        """
        pg.init()
        self.config = validateDict(config, self.default)# dict
        # additional attributes
        self.title = self.config["title"]# str
        self.icon = self.config["icon"]# str / pygame.surface
        self.clock = pg.time.Clock()# pygame.clock
        self.preffered_fps = self.config["fps"]# int
        self.fps = 0# int
        self.pausemenu = False# bool
        self.mode = "moving"# str
        # display related stuff
        self.display = getDisplay(# pygame.surface
            self.config["size"],
            resizable = self.config["resizable"]
        )
        self.changeTitle(self.config["title"])
        self.changeIcon(self.icon)
    def update(self):
        """updates stuff at apps loop-end."""
        pg.display.update()
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def draw(self, object, position=(0, 0)):
        """draw everything to the windows surface."""
        draw(object, self.display, position)
    def resize(self, size):
        """'size' needs to be a tuple."""
        self.display = getDisplay(# pygame.surface
            size,
            resizable = self.config["resizable"]
        )
    def events(self):# pygame.event
        """pygame events"""
        events = []
        for event in pg.event.get():
            # quit application
            if event.type is pg.QUIT:
                pg.quit()
                sys.exit()
            # resizing the window
            if event.type is pg.VIDEORESIZE:
                self.resize(event.size)
            # pause menu
            if event.type is pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.pausemenu is True:
                    self.pausemenu = False
                else:
                    self.pausemenu = True
            # going fullscreen
            if event.type is pg.KEYDOWN and event.key == pg.K_F12:
                pass
            events.append(event)
        return events
    def pressedKeys(self):
        """return pygame-event's pressed-keys."""
        return pg.key.get_pressed()
    def changeIcon(self, path):
        """create an icon for the window from an image."""
        if type(path) is pg.Surface:
            icon = path
        elif type(path) is str:
            icon = pg.image.load(path)

        icon = pg.transform.scale(icon, (32, 32))
        pg.display.set_icon(icon)
    def changeTitle(self, title):
        """change the window-title. 'title' should be a string."""
        if type(title) is not str:
            title = str(title)
        pg.display.set_caption(title)
