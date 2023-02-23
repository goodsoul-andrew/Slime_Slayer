import pygame as pg
from classes import GameObject, Animation


class Projectile(GameObject):
    def __init__(self, coords, filename, v, health, **kwargs):
        GameObject.__init__(self, coords, filename)
        self.states = {"player_damage": True, "move": True}
        self.damage = 0
        self.direction = "right"
        self.vx, self.vy = v
        self.health = health
        if kwargs:
            for s in kwargs:
                self.states[s] = kwargs[s]
        self.load_images()

    def load_images(self):
        pass

    def update(self):
        self.health -= 1
        if self["move"]:
            if self.direction == "right":
                self.x += self.vx
            elif self.direction == "left":
                self.x -= self.vx
            elif self.direction == "up":
                self.y -= self.vy
            elif self.direction == "down":
                self.y += self.vy

    def __bool__(self):
        return self.health > 0



class PlayerFireball(Projectile):
    def __init__(self, coords, direction):
        Projectile.__init__(self, coords, "textures/player/fireball.png", (3, 0), 70)
        self.damage = 2
        self.states["player_damage"] = False
        self.states["image_changed"] = False
        self.direction = direction
        self.load_images()

    def load_images(self):
        self.images = {}
        self.images["base"] = pg.image.load("textures/player/fireball.png")
        self.fireball = Animation("textures/player/fireball_flying.png")

    def update(self):
        Projectile.update(self)
        # print(self.health // 5, self["direction"], self["image_changed"])
        if self.health % 5 == 0:
            self.image = self.fireball[self.health // 5].copy()
            # self["image_changed"] = True
            if self.direction == "left":
                self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.coordinate()

    def __bool__(self):
        return self.health > 0

    def render(self, surface):
        surface.blit(self.image, self.rect)


