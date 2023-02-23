import pygame as pg
from classes import GameObject, Animation


class Item(GameObject):
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


class Coin(Item):
    def __init__(self, coords, cost):
        if cost <= 10:
            filename = "textures/items/coin.png"
        Item.__init__(self, coords, filename)
        self.cost = cost

    def activate(self, player):
        player.money += self.cost


class HealingPotion(Item):
    def __init__(self, coords, heal):
        if heal <= 10:
            filename = "textures/items/healing_potion.png"
        Item.__init__(self, coords, filename)
        self.heal_value = heal

    def activate(self, player):
        player.health += self.heal_value
        if player.health > player.max_health:
            player.health = player.max_health


class GoldenHeart(Item):
    def __init__(self, coords):
        Item.__init__(self, coords, "textures/player/hearts/heart_golden.png")

    def activate(self, player):
        player.golden_health += 8


class Heart(Item):
    def __init__(self, coords):
        Item.__init__(self, coords, "textures/player/hearts/heart.png")

    def activate(self, player):
        player.max_health += 8
        player.health += 8