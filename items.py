import pygame as pg
from classes import GameObject, Animation


class Consumable(GameObject):
    def __init__(self, coords, filename):
        GameObject.__init__(self, coords, filename)
        self.falling = True

    def update(self, **kwargs):
        if "gravity" in kwargs:
            if self.falling:
                self.y += kwargs["gravity"]
            # print(self.y, self.falling)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.coordinate()

    def activate(self):
        pass


class Coin(Consumable):
    def __init__(self, coords, cost):
        if cost <= 10:
            filename = "textures/items/coin.png"
        Consumable.__init__(self, coords, filename)
        self.cost = cost

    def activate(self, player):
        player.money += self.cost


class HealingPotion(Consumable):
    def __init__(self, coords, heal=8):
        if heal <= 8:
            filename = "textures/items/healing_potion_small.png"
        else:
            filename = "textures/items/healing_potion.png"
        Consumable.__init__(self, coords, filename)
        self.heal_value = heal

    def activate(self, player):
        player.health += self.heal_value
        if player.health > player.max_hp:
            player.health = player.max_hp


class GoldenHeart(Consumable):
    def __init__(self, coords):
        Consumable.__init__(self, coords, "textures/player/hearts/heart_golden.png")

    def activate(self, player):
        player.golden_health += 8


class Heart(Consumable):
    def __init__(self, coords):
        Consumable.__init__(self, coords, "textures/player/hearts/heart.png")

    def activate(self, player):
        player.max_health += 8
        player.health += 8

class Book(Consumable):
    def __init__(self, coords, filename="textures/items/book.png"):
        Consumable.__init__(self, coords, filename)
        self.damage = 0
        self.speed = 0
        self.health = 0

    def activate(self, player):
        player.damage += self.damage
        player.vx += self.speed
        player.max_health += self.health
        player.health += self.health

class DamageBook(Book):
    def __init__(self, coords):
        Book.__init__(self, coords, filename="textures/items/book_damage.png")
        self.damage = 2


class SpeedBook(Book):
    def __init__(self, coords):
        Book.__init__(self, coords, filename="textures/items/book_speed.png")
        self.speed = 2


class HealthBook(Book):
    def __init__(self, coords):
        Book.__init__(self, coords, filename="textures/items/book_health.png")
        self.health = 2


class BookUp(Book):
    def __init__(self, coords):
        Book.__init__(self, coords, filename="textures/items/book_up.png")
        self.damage = 1
        self.speed = 1
        self.health = 8


class Item:
    def __init__(self, coords, filename, name="item", health=0, damage=0, speed=0):
        self.image = pg.image.load(filename)
        self.rect = self.image.get_rect(topleft=coords)
        self.health = health
        self.damage = damage
        self.speed = speed
        self.name = name
        self.image_big = pg.image.load(filename[:filename.find(".")] + "_big.png")

    def clicked(self, event):
        return self.rect.collidepoint(event.pos)

    def __str__(self):
        return self.name


class Food(GameObject):
    def __init__(self, coords, filename):
        GameObject.__init__(self, coords, filename)
        self.health = 0
        self.damage = 0
        self.speed = 0
        self.effect_time = 0
        self.time = 0
        self.activated = False
        self.image_full = pg.image.load(filename)
        self.image_eaten = pg.image.load(filename[:filename.find(".")] + "_eaten.png")
        self.name = "name"

    def clicked(self, event):
        return self.rect.collidepoint(event.pos)

    def __str__(self):
        return self.name

    def activate(self):
        self.activated = True
        self.image = self.image_eaten

    def update(self):
        if self.activated and self.time > 0:
            self.time -= 1
        if self.time == 0:
            self.activated = False
            self.time = self.effect_time
            self.image = self.image_full

    def __eq__(self, other):
        if type(other) == str:
            return self.name == other

    @property
    def dmg(self):
        if self.activated:
            return self.damage
        else:
            return 0

    @property
    def spd(self):
        if self.activated:
            return self.speed
        else:
            return 0


class Jelly(Food):
    def __init__(self, coords):
        Food.__init__(self, coords, "textures/items/jelly.png")
        self.health = 8
        self.time = 6
        self.name = "jelly"

    def activate(self, player):
        if self.time == self.effect_time:
            player.health += 8
            if player.health > player.max_health:
                player.health = player.max_health
            self.time = 0
            self.image = self.image_eaten

    def update(self):
        if self.time == self.effect_time:
            self.image = self.image_full