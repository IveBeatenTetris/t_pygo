from .utils import (
    PATH,
    loadAssets,
    draw,
    getFrames,
    drawBorder,
    getAnchors
)
import pygame as pg
from .libs.zrect import ZRect

class Entity(pg.sprite.Sprite):
    """
    every form of ingame-agency will be based on this class. 'name' should be
    asset-name. in dev-mode it shows bounding outlines etc.
    """
    def __init__(self, name):
        """
        opens an asset by adding the given name to the asset-path. when done
        initiating it uses the '__build()' method to recalculate some stuff and
        ane keep the '__init__' clean.
        'name' doesnt have to match the files name.
        'rawimage' reference because the actual image is about to be tweaked.
        'size' again im planing to remove this attribute once and for all.
        'frames' list of all cut-out sprites from an image. usefull for
            animations or quickly chaning sprite-image.
        'image' based of a frame out of 'self.frames'.
        'rect' is a pyzero.zrect for smoother mooving-transitions.
        'anchors' is used for quick-pointing a part of the rect. for example:
            draw(object, self, self.anchors["midcenter"]).
        'collisionbox' the actual box for calculating collisions with.
        'speed' is used to determine the moving speed of the entity. this is by
            the way the amount of pixels that the entity moves per frame.
        'dev_move' if 'true' this will render the entity bounding borders.
        """
        # looking for a json-file to use as the config
        for each in loadAssets(PATH["entities"] + "\\" + name):
            if each["type"] == "player":
                self.config = each# dict
        # initializing the sprite
        pg.sprite.Sprite.__init__(self)
        # additional attributes
        self.name = self.config["name"]# str
        self.rawimage = pg.image.load(# pygame.surface
            self.config["filepath"] + "\\" + self.config["image"]
        )
        self.size = self.config["framesize"]# tuple
        self.frames = getFrames(self.rawimage, self.size)# list
        self.image = self.frames[0]# pygame.surface
        self.rect = ZRect(self.image.get_rect())# pgzero.zrect
        self.anchors = getAnchors(self.rect.size)# dict
        self.collisionbox = pg.Rect(self.config["collisionbox"])# pygame.rect
        self.speed = self.config["speed"]# int
        self.dev_mode = self.config["dev_mode"]# bool
        # keeping __init__ organazied
        self.__build()
    def __build(self):
        """drawing depending on dev_mode."""
        if self.dev_mode is True:
            # whole sprite border in red
            drawBorder(
            	self.image,
            	self.rect,
            	(1, 'solid', (255, 0, 0))
            )
            # blue border for collision-box
            bound = drawBorder(
            	pg.Surface(self.collisionbox.size, pg.SRCALPHA),
            	self.collisionbox,
            	(1, 'solid', (0, 0, 255))
            )
            draw(bound, self.image, self.collisionbox)
        else:
            self.image = self.frames[0]
    def __moveSingleAxis(self, pos, blocks):
        """
        if a list of blocks is given the move-method then checks for collision
        first before actually moving the player.
        """
        self.rect.left = self.rect.left + pos[0]
        self.rect.top = self.rect.top + pos[1]
        # absolute position of collisionbox. necessary for computing collision
        self.collisionbox.topleft = (
            self.rect.left + self.config["collisionbox"][0],
            self.rect.top + self.config["collisionbox"][1]
            )
        # collision checking
        for block in blocks:
            if self.collisionbox.colliderect(block):
                rect = pg.Rect(self.config["collisionbox"])
                if pos[0] > 0:
                    self.rect.right = block.left + (self.rect.width - rect.right)
                if pos[0] < 0:
                    self.rect.left = block.right - rect.left
                if pos[1] > 0:
                    self.rect.bottom = block.top + (self.rect.height - rect.bottom)
                if pos[1] < 0:
                    self.rect.top = block.bottom - rect.top
    def move(self, blocks=[]):
        """move the entity to the given coordinates."""
        keys = pg.key.get_pressed()
        # moving
        if keys[pg.K_a]:
            self.__moveSingleAxis((-self.speed, 0), blocks)
        if keys[pg.K_d]:
            self.__moveSingleAxis((self.speed, 0), blocks)
        if keys[pg.K_w]:
            self.__moveSingleAxis((0, -self.speed), blocks)
        if keys[pg.K_s]:
            self.__moveSingleAxis((0, self.speed), blocks)
    def position(self, pos=(0, 0)):
        """reposition of the entity sprite. updates the rect."""
        if type(pos) is pg.Rect:
            self.rect.topleft = pos.topleft
        elif type(pos) is tuple:
            self.rect.topleft = pos
class Player(Entity):
    """representing a playable character."""
    def __init__(self, name):
        """inherit everything from its master class."""
        Entity.__init__(self, name)
