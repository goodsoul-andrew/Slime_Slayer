import pygame as pg
import os


class HealthBar:
    def __init__(self):
        self.images = {}
        self.images[8] = pg.image.load("textures/player/hearts/heart.png")
        self.images[6] = pg.image.load("textures/player/hearts/heart_34.png")
        self.images[4] = pg.image.load("textures/player/hearts/heart_half.png")
        self.images[2] = pg.image.load("textures/player/hearts/heart_quarter.png")
        self.images[0] = pg.image.load("textures/player/hearts/heart_empty.png")
        self.images["g"] = pg.image.load("textures/player/hearts/heart_golden.png")
        self.width = self.images[8].get_width()
        self.height = self.images[8].get_height()

    def __getitem__(self, item):
        return self.images[item]

    def render(self, player, surface):
        hp, max_hp = player.health, player.max_hp
        cnt = 0
        rect = pg.Rect(10, 10, self.width, self.height)
        # print("_____", hp)
        while cnt < max_hp // 8:
            if hp >= 8:
                surface.blit(self[8], rect)
                # print(16, end=" ")
                hp -= 8
            elif hp >= 6:
                surface.blit(self[6], rect)
                hp -= 6
                # print(12, end=" ")
            elif hp >= 4:
                surface.blit(self[4], rect)
                hp -= 4
            elif hp >= 2:
                surface.blit(self[2], rect)
                hp -= 2
            else:
                surface.blit(self[0], rect)
            cnt += 1
            rect.left += self.width + 1
        golden_hp = player.golden_health // 8 + int(player.golden_health % 8 > 0)
        for i in range(golden_hp):
            surface.blit(self["g"], rect)
            rect.left += self.width + 1


class MoneyBar:
    def __init__(self):
        self.image = pg.image.load("textures/items/coin_big.png")
        self.rect = self.image.get_rect(topleft=(10, 50))

    def render(self, player, surface):
        surface.blit(self.image, self.rect)
        font = pg.font.Font(None, 30)
        num = font.render(str(player.money), True, (255, 255, 255))
        surface.blit(num, (45, 50))


class Inventory:
    def __init__(self):
        self.image = pg.image.load("textures/player/frame.png")
        self.rect1 = self.image.get_rect(topleft=(10, 630))
        self.rect2 = self.image.get_rect(topleft=(10 + self.image.get_width() + 2, 630))
        self.claws_image = pg.image.load("textures/player/claws_icon.png")
        self.fireball_image = pg.image.load("textures/player/fireball_icon.png")

    def render(self, player, surface):
        surface.blit(self.image, self.rect1)
        surface.blit(self.image, self.rect2)
        if player.weapon == "claws":
            surface.blit(self.claws_image, self.rect1)
        elif player.weapon == "fireball":
            surface.blit(self.fireball_image, self.rect1)
        if player.food.time >= player.food.effect_time:
            surface.blit(player.food.image_full, self.rect2)
        else:
            surface.blit(player.food.image_eaten, self.rect2)


class Animation:
    def __init__(self, filename):
        name = filename[:filename.find(".")] + "_anim.txt"
        try:
            self.current_frame = 0
            self.frames = []
            with open(name) as file:
                data = [el.strip() for el in file.readlines()]
                number_frames = int(data[0][data[0].find("=") + 1:])
                change_time = int(data[1][data[1].find("=") + 1:])
                self.change_time = change_time
            temp = pg.image.load(filename)
            self.width = temp.get_width()
            self.height = temp.get_height() // number_frames
            for i in range(number_frames):
                self.frames.append(temp.subsurface(pg.Rect(0, self.height * i, self.width, self.height)))
            self.image = self.frames[self.current_frame]
        except FileNotFoundError:
            self.current_frame = 0
            self.frames = [pg.image.load(filename)]
            self.width = self.frames[0].get_width()
            self.height = self.frames[0].get_height()
            self.image = self.frames[self.current_frame]
            self.change_time = 0
        self.time = 0

    def blit(self, other, rect):
        self.image.blit(other, rect)

    def render(self, other, rect):
        other.blit(self.image, rect)

    def update(self):
        if self.time > 0 and self.time % self.change_time == 0:
            self.current_frame += 1
            self.time = 0
        self.current_frame %= len(self.frames)
        self.image = self.frames[self.current_frame]
        self.time += 1

    def __getitem__(self, item):
        return self.frames[item % len(self.frames)]

    def __len__(self):
        return len(self.frames)


class GameObject(pg.sprite.Sprite):
    def __init__(self, coords, filename="", image=None):
        super().__init__()
        # nonlocal obj_count
        if image != None:
            self.image = image
        else:
            self.image = pg.image.load(filename)
        self.rect = self.image.get_rect(topleft=coords)
        self.x, self.y = coords
        self.texture = filename
        self.top = self.rect.top
        self.bottom = self.rect.bottom
        self.left = self.rect.left
        self.right = self.rect.right
        self.width = self.rect.width
        self.height = self.rect.height
        self.center = self.rect.center
        self.states = {}
        # obj_count += 1

    def __getitem__(self, item):
        return self.states[item]

    def __setitem__(self, key, value):
        self.states[key] = value

    def collide_group(self, *groups):
        for group in groups:
            if pg.sprite.spritecollideany(self, group):
                return True
        return False

    def collide(self, other):
        return self.rect.colliderect(other.rect)

    def touch(self, other, speed=1):
        s = speed
        right_toucher = pg.Rect(self.right, self.top + 1, s, self.height - 2)
        if right_toucher.colliderect(other.rect):
            #print("right toucher", right_toucher, other.rect, type(other))
            return True
        left_toucher = pg.Rect(self.left - s, self.top + 1, s, self.height - 2)
        if left_toucher.colliderect(other.rect):
            # print("left toucher", left_toucher, other.rect, type(other))
            return True
        top_toucher = pg.Rect(self.left + 1, self.top - 1, self.width - 2, 1)
        if top_toucher.colliderect(other.rect):
            return True
        bottom_toucher = pg.Rect(self.left + 1, self.bottom, self.width - 2, 1)
        if bottom_toucher.colliderect(other.rect):
            return True
        '''if self.top == other.rect.bottom:
            top_toucher = pg.Rect(self.left + 1, self.top - 10, self.width - 2, self.height)
            if top_toucher.colliderect(other.rect):
                return True
        if self.bottom == other.rect.top:
            bottom_toucher = pg.Rect(self.left + 1, self.top + 10, self.width - 2, self.height)
            if bottom_toucher.colliderect(other.rect):
                return True
        if self.left == other.rect.right:
            left_toucher = pg.Rect(self.left - 10, self.top + 1, self.width, self.height - 2)
            if left_toucher.colliderect(other.rect):
                return True
        if self.right == other.rect.left:
            right_toucher = pg.Rect(self.left + 10, self.top + 1, self.width, self.height - 2)
            if right_toucher.colliderect(other.rect):
                return True'''
        return False

    def get_bottom_toucher(self):
        return pg.Rect(self.left + 1, self.bottom, self.width - 2, 1)

    def get_top_toucher(self):
        return pg.Rect(self.left + 1, self.top - 1, self.width - 2, 1)

    def get_left_toucher(self, speed=1):
        s = speed
        return pg.Rect(self.left - s, self.top + 1, s, self.height - 2)

    def get_right_toucher(self, speed=1):
        s = speed
        return pg.Rect(self.right, self.top + 1, s, self.height - 2)

    def touch_group(self, *groups):
        for group in groups:
            for other in group:
                if self.touch(other):
                    return True
        return False

    def is_above(self, other):
        return self.rect.bottom <= other.rect.top and self.rect.bottom < other.rect.bottom

    def is_under(self, other):
        return other.is_above(self)

    def is_lefter(self, other):
        return self.rect.right <= other.rect.left and self.right < other.rect.right

    def is_righter(self, other):
        return other.is_lefter(self)

    def coords_debug(self):
        print(f"{self}:")
        print(f"    top: {self.top}")
        print(f"    bottom: {self.bottom}")
        print(f"    left: {self.left}")
        print(f"    right: {self.right}")
        print()

    def __repr__(self):
        return f"{type(self)}: {(self.top, self.left)}, {self.image}"

    def __str__(self):
        return f"{type(self)}: {(self.top, self.left)}, {self.image}"

    def __hash__(self):
        # nonlocal  obj_count
        return hash(self.texture) + hash(str(type(self)))# + obj_count

    def coordinate(self):
        self.top = self.rect.top
        self.bottom = self.rect.bottom
        self.left = self.rect.left
        self.right = self.rect.right
        self.width = self.rect.width
        self.height = self.rect.height
        self.center = self.rect.center
        self.rect.topleft = self.x, self.y

    def above_group(self, *groups):
        for group in groups:
            for other in group:
                if self.is_above(other):
                    return True
        return False

    def under_group(self, *groups):
        for group in groups:
            for other in group:
                if self.is_under(other):
                    return True
        return False

    def lefter_group(self, *groups):
        for group in groups:
            for other in group:
                if self.is_lefter(other):
                    return True
        return False

    def righter_group(self, *groups):
        for group in groups:
            for other in group:
                if self.is_righter(other):
                    return True
        return False

    def touch_check(self, other, key):
        '''if key == "above":
            if self.bottom == other.rect.top:
                bottom_toucher = pg.Rect(self.left + 1, self.top + 10, self.width - 2, self.height)
                if bottom_toucher.colliderect(other.rect):
                    return True and self.is_above(other)
        elif key == "under":
            if self.top == other.rect.bottom:
                top_toucher = pg.Rect(self.left + 1, self.top - 10, self.width - 2, self.height)
                if top_toucher.colliderect(other.rect):
                    return True and self.is_under(other)
        elif key == "righter":
            if self.left == other.rect.right:
                left_toucher = pg.Rect(self.left - 10, self.top + 1, self.width, self.height - 2)
                if left_toucher.colliderect(other.rect):
                    return True and self.is_righter(other)
        elif key == "lefter":
            if self.right == other.rect.left:
                right_toucher = pg.Rect(self.left + 10, self.top + 1, self.width, self.height - 2)
                if right_toucher.colliderect(other.rect):
                    return True and self.is_lefter(other)'''
        if self.touch(other):
            if key == "above":
                return self.is_above(other)
            elif key == "under":
                return self.is_under(other)
            elif key == "lefter":
                return self.is_lefter(other)
            elif key == "righter":
                return self.is_righter(other)
        return False

    def touch_check_group(self, key, *groups):
        for group in groups:
            for other in group:
                if self.touch_check(other, key):
                    return True
        return False

    def render(self, surface):
        surface.blit(self.image, self.rect)

    def center_coordinate(self):
        self.x, self.y = self.rect.topleft


class TextButton(pg.Surface):
    def __init__(self, font, text:str, coords, smooth=True, color=(255, 255, 255), bg_color=(0, 0, 0), alt_color=(255, 255, 255), alt_bg_color=(0, 0, 0)):
        self.surface = font.render(text, smooth, color, bg_color)
        self.x, self.y = coords
        self.color, self.alt_color = color, alt_color
        self.bg_color, self.alt_bg_color = bg_color, alt_bg_color
        self.text = text
        self.font = font
        self.smooth = smooth

    def blit(self, other, rect):
        self.surface.blit(other, rect)

    def draw(self, surf):
        surf.blit(self.surface, (self.x, self.y))

    def color(self):
        self.surface = self.font.render(self.text, self.smooth, self.alt_color, self.alt_bg_color)

    def uncolor(self):
        self.surface = self.font.render(self.text, self.smooth, self.color, self.bg_color)


class Background(pg.sprite.Sprite):
    def __init__(self, filename):
        super().__init__()
        self.image = pg.image.load(filename)
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.y = 0
        self.x = 0
        self.color = self.get_average_color()
        self.tile = self.image.subsurface(pg.Rect(0, 0, 48, 48))
        self.width = self.rect.width
        self.height = self.rect.height

    def render(self, surface, mode="full"):
        if mode == "full":
            surface.blit(self.image, (self.x, self.y))
        elif mode == "fill":
            surface.fill(self.color)
        elif mode == "tile":
            for i in range(0, self.width, 48):
                for j in range(0, self.height, 48):
                    surface.blit(self.tile, pg.Rect(i, j, i + 48, j + 48))



    def fill(self, color):
        self.image.fill(color)

    def get_average_color(self):
        s = 0
        arr = pg.PixelArray(self.image)
        '''for i in range(48):
            for j in range(48):
                print(hex(arr[i][j]))
                s += arr[i][j]'''
        return arr[10][10]


class Ground(pg.sprite.Sprite):
    def __init__(self, filename, coords=(0, 640-32)):
        super().__init__()
        self.image = pg.image.load(filename)
        self.rect = self.image.get_rect(topleft=coords)

    def render(self, surf):
        surf.blit(self.image, (self.rect.x, self.rect.y))