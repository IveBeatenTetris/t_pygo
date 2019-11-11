from .utils import (
    PATH,
    validateDict,
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
        'frames' list of all cut-out sprites from an image. usefull for
            animations or quickly chaning sprite-image.
        'image' based of a frame out of 'self.frames'.
        'rect' is a pyzero.zrect for smoother mooving-transitions.
        'animationspeed' determines how fast an animation will run.
        'animations' dict of animation objects.
        'anchors' is used for quick-pointing a part of the rect. for example:
            draw(object, self, self.anchors["midcenter"]).
        'collisionbox' the actual box for calculating collisions with.
        'speed' is used as the moving speed of the entity. this is by
            the way the amount of pixels that the entity moves per frame.
        'facing' is used for determining the right picture for entity to
            display.
        'knownblocks' holds all block-tiles from the active map.
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
        self.frames = getFrames(self.rawimage, self.config["framesize"])# list
        self.image = self.frames[0]# pygame.surface
        self.rect = ZRect(self.image.get_rect())# pgzero.zrect
        self.animationspeed = self.config["animationspeed"]# int
        self.animations = {# dict
            "walkdown": Animation({
                "frames": self.frames,
                "sequence": [4, 5, 6, 7],
                "duration": self.animationspeed
                }),
            "walkleft": Animation({
                "frames": self.frames,
                "sequence": [8, 9, 10, 11],
                "duration": self.animationspeed
                }),
            "walkup": Animation({
                "frames": self.frames,
                "sequence": [12, 13, 14, 15],
                "duration": self.animationspeed
                }),
            "walkright": Animation({
                "frames": self.frames,
                "sequence": [16, 17, 18, 19],
                "duration": self.animationspeed
                })
            }
        self.anchors = getAnchors(self.rect.size)# dict
        self.collisionbox = pg.Rect(self.config["collisionbox"])# pygame.rect
        self.speed = self.config["speed"]# int
        self.facing = "down"# str
        self.knownblocks = ["knownblocks"]# list
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
    def move(self):
        """moving entity. also animate while still moving."""
        keys = pg.key.get_pressed()
        moving = False
        speed = self.speed
        # shift key is pressed
        if pg.key.get_mods() & pg.KMOD_SHIFT:
            speed = int(self.speed * 1.5)
        # moving and correct facing direction
        if keys[pg.K_a]:
            self.__moveSingleAxis((-speed, 0), self.knownblocks)
            self.facing = "left"
            moving = True
        if keys[pg.K_d]:
            self.__moveSingleAxis((speed, 0), self.knownblocks)
            self.facing = "right"
            moving = True
        if keys[pg.K_w]:
            self.__moveSingleAxis((0, -speed), self.knownblocks)
            self.facing = "up"
            moving = True
        if keys[pg.K_s]:
            self.__moveSingleAxis((0, speed), self.knownblocks)
            self.facing = "down"
            moving = True
        # walking cycle animation
        if moving:
            if self.facing == "down":
                name = "walkdown"
            elif self.facing == "left":
                name = "walkleft"
            elif self.facing == "up":
                name = "walkup"
            elif self.facing == "right":
                name = "walkright"

            self.image = self.animations[name].image
            self.animations[name].update()
        # idle facing direction
        else:
            if self.facing == "down":
                self.image = self.frames[0]
            elif self.facing == "left":
                self.image = self.frames[1]
            elif self.facing == "up":
                self.image = self.frames[2]
            elif self.facing == "right":
                self.image = self.frames[3]
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
class Animation(pg.sprite.Sprite):
    """
    an animated sprite class. calling it would look like this:
    anim = Animation({
        "frames": entity.frames,
        "sequence": [4, 5, 6, 7],
        "duration": entity.animationspeed
        })
    """
    default = {
        "frames": [],
        "sequence": [],
        "duration": 100
        }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.default)# dict
        self.sequence = self.config["sequence"]# tuple / list
        self.duration = self.config["duration"]# int
        self.frames = self.config["frames"][# list
            self.sequence[0]: self.sequence[-1] + 1
        ]
        pg.sprite.Sprite.__init__(self)# pygame.sprite
        self.pointer = 0# int
        self.image = self.frames[self.pointer]# pygame.surface
        self.framecount = len(self.frames)# int
        self.timer = self.duration + 1# int
        self.timemod = int(self.timer / self.framecount)# int
    def update(self):
        """
        updating the pointers position. the active frame is always drawn to
        the animation image surface.
        """
        for i in range(self.framecount):
            if self.timer == int((i) * self.timemod):
                self.nextFrame()

        if self.timer == 0:
            self.timer = self.duration + 1
        else:
            self.timer = self.timer - 1
    def nextFrame(self):
        """set the pointer to the next frame."""
        if self.pointer < self.framecount - 1:
            self.pointer += 1
        else:
            self.pointer = 0

        self.image = self.frames[self.pointer]
