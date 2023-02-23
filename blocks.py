import pygame as pg
from classes import GameObject, Animation


class Block(GameObject):
    def __init__(self, coords, filename="", image=None):
        GameObject.__init__(self, coords, filename=filename, image=image)

    def update(self):
        pass

class Tile(GameObject):
    def __init__(self, coords, filename="", image=None):
        GameObject.__init__(self, coords, filename=filename, image=image)

    def update(self):
        pass

class Platform(GameObject):
    def __init__(self, coords, filename="", image=None, orientation="top"):
        GameObject.__init__(self, coords, filename=filename, image=image)
        self.orientation = orientation
        '''if self.orientation == "top":
            self.rect.height = self.rect.height // 2
        else:
            self.rect.top -= self.rect.height // 2'''
        # print(self.rect)

    def update(self):
        pass


class Upper(GameObject):
    def __init__(self, coords, filename="", image=None, power=2):
        GameObject.__init__(self, coords, filename=filename, image=image)
        self.power = power

    def render(self):
        pass


class Touchable(GameObject):
    def __init__(self, coords, filename="", image=None):
        GameObject.__init__(self, coords, filename=filename, image=image)

    def update(self, **kwargs):
        pass

    def clicked(self, event):
        return self.rect.collidepoint(event.pos)

    def activate(self):
        pass


class Stand(Touchable):
    def __init__(self, coords):
        Touchable.__init__(self, coords, filename="textures/blocks/stand.png", image=None)
        self.item = None

    def place(self, item):
        self.item = item
        # print(item.rect.y)
        self.item.rect.center = (self.rect.center[0], self.rect.top + item.rect.width // 2 + 4)
        # print(self.item.rect.y)
        #self.item.coordinate()

    def take(self):
        # print(self.item.rect.y)
        item = self.item
        # print(item.rect.y)
        item.rect.center = (self.rect.center[0], self.rect.top + item.rect.width // 2 + 4)
        self.item = None
        return item

    def render(self, surface):
        surface.blit(self.image, self.rect)
        if self.item:
            surface.blit(self.item.image, self.item.rect)


class Candle(Touchable):
    def __init__(self, coords, filename="textures/blocks/candle.png", image=None):
        Touchable.__init__(self, coords, filename=filename, image=image)
        self.lit = True
        # print(self.x, self.y)
        self.load_images()
        self.image = pg.image.load(filename)

    def load_images(self):
        self.image_unlit = pg.image.load("textures/blocks/candle.png")
        self.image_lit = Animation("textures/blocks/candle_lit.png")

    def update(self, **kwargs):
        if self.lit:
            self.image_lit.update()
            self.image = self.image_lit.image

    def extinguish(self):
        self.lit = False
        self.image = self.image_unlit

    def render(self, surface):
        surface.blit(self.image, self.rect)


class Gate(Touchable):
    def __init__(self, coords, filename="textures/blocks/gates.png", image=None):
        Touchable.__init__(self, coords, filename=filename, image=image)
        self.opened = False
        self.lock = False
        self.image_closed = pg.image.load("textures/blocks/gates.png")
        self.image_opened = pg.image.load("textures/blocks/gates_open.png")

    def open(self):
        if not(self.lock):
            self.opened = True
            self.image = self.image_opened

    def close(self):
        self.opened = False
        self.image = self.image_closed

    def render(self, surface):
        surface.blit(self.image, self.rect)


class Trap(Touchable):
    def __init__(self, coords):
        Touchable.__init__(self, coords, filename="textures/blocks/trap.png", image=None)
        self.state = "calm"
        self.timer = 0
        self.damage = 4
        self.load_images()

    def load_images(self):
        self.base_image = pg.image.load("textures/blocks/trap.png")
        self.base_rect = self.rect
        self.activated_image = pg.image.load("textures/blocks/trap_activated.png")
        self.spikes_image = pg.image.load("textures/blocks/trap_spikes.png")
        self.spikes_rect = self.spikes_image.get_rect(topleft=(self.x, self.y - 48))

    def update(self, **kwargs):
        if self.state == "activated":
            self.timer += 1
        if self.timer == 0:
            self.state = "calm"
            self.image = self.base_image.copy()
            self.rect = self.base_rect
        elif self.timer == 30:
            self.state = "spikes"
            self.image = self.spikes_image.copy()
            self.rect = self.spikes_rect
            self.timer += 1
        elif self.timer > 30:
            self.timer += 1

    def activate(self):
        self.image = self.activated_image.copy()
        self.rect = self.base_rect
        self.state = "activated"

    def deactivate(self):
        self.image = self.base_image.copy()
        self.rect = self.base_rect
        self.state = "calm"
        self.timer = 0

    def render(self, surface):
        surface.blit(self.image, self.rect)

