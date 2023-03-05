import pygame as pg
from classes import *
from items import Food, Jelly
from projectiles import PlayerFireball, SlimeBall


class Entity(GameObject):
    def __init__(self, coords, filename, v, max_health, **kwargs):
        super().__init__(coords, filename)
        self.vx, self.vy = v
        self.max_health = max_health
        self.health = max_health
        self.damage = 0
        self.direction = "right"
        self.states = {"running": False, "jumping": False, "descent": True, "rising": True, "move_left": True,
                       "move_right": True, "fly": False, "jump_phase": 0, "falling": True, "attacking": False,
                       "attack_frame": 0, "spawned": True, "static": False}
        # self.attack_timer = pg.Clock()
        if kwargs:
            for s in kwargs:
                self.states[s] = kwargs[s]
        self.load_images()

    @property
    def dmg(self):
        return self.damage

    @dmg.setter
    def dmg(self, d):
        self.damage = d

    def render(self, surf):
        surf.blit(self.image, self.rect)

    def __bool__(self):
        return self.health > 0

    def load_images(self):
        self.images = {}
        self.arms_attacking = []
        pass

    def __getitem__(self, item):
        return self.states[item]

    def __setitem__(self, key, value):
        self.states[key] = value

    def update(self, **kwargs):
        if kwargs:
            #  and not(self["jumping"])
            if "gravity" in kwargs and self["falling"]:
                self.y += kwargs["gravity"]
        if self["jumping"] or self["falling"]:
            self.image = self.images[f"body_flying"]
        if self["jump_phase"]:
            self["jump_phase"] += 1
            self.y -= 12
            self.y -= kwargs["gravity"]
            self["jump_phase"] %= 12
        else:
            self["jumping"] = False
        if self["attacking"]:
            self.attack()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.coordinate()

    def take_damage(self, entity):
        d = entity.dmg
        self.health -= d

    def states_debug(self):
        for el in self.states:
            print(el, self[el])
        print()

    def attack(self, attack_animation):
        if self["attack_frame"] == 0 and self["attacking"] == False:
            self["image_changed"] = True
            self["attacking"] = True
            # self["attack_frame"] += 1
        elif self["attack_frame"] < len(attack_animation) - 1:
            self["attack_frame"] += 1
            self["image_changed"] = True
            pg.time.wait(50)
        else:
            self["attack_frame"] = 0
            self["attacking"] = False
            self["image_changed"] = True

    def touch(self, other):
        return GameObject.touch(self, other, speed=self.speed)

    def get_left_toucher(self):
        return GameObject.get_left_toucher(speed=self.speed)

    def get_right_toucher(self):
        return GameObject.get_right_toucher(speed=self.speed)

    def copy(self, coords):
        new = self
        new.x, new.y = coords
        return new

    @property
    def speed(self):
        return self.vx

    @speed.setter
    def speed(self, s):
        self.vx = s

    @property
    def max_hp(self):
        return self.max_health

    @max_hp.setter
    def max_hp(self, h):
        self.max_health = h
        self.health += h



class Player(Entity):
    def __init__(self, coords, filename="textures/player/player.png", vx=2, vy=1, max_health=32):
        super().__init__(coords, filename, (vx, vy), max_health)
        # self.direction = "right"
        self.load_images()
        self.damage = 5
        self.states["image_changed"] = False
        self.body = self.images["body"]
        self.arm = self.images["arm"]
        self.image = self.images["base"]
        self.money = 0
        self.cooldown = 0
        self.melee_attack = None
        self.melee_attack_rect = None
        self.range_attack = None
        self.weapon = "claws"
        # fireball claws
        self.hpbar = HealthBar()
        self.mbar = MoneyBar()
        self.weapon_frame = Inventory()
        self.golden_health = 0
        self.food = Jelly(coords)
        # print(self.dmg)

    def move(self, event, **kwargs):
        key = event.key
        success = False
        if self.vx > 1:
            self["running"] = True
        else:
            self["running"] = False
        if key == pg.K_a:
            if self.direction == "right":
                self.states["image_changed"] = True
            self.direction = "left"
            if self["move_left"]:
                self.x -= self.speed
            success = True
        if key == pg.K_d:
            if self.direction == "left":
                self.states["image_changed"] = True
            self.direction = "right"
            if self["move_right"]:
                self.x += self.speed
            success = True
        if key == pg.K_s:
            # key == pg.K_SPACE and event.mod & pg.KMOD_SHIFT
            if self["descent"] and not self["falling"]:
                self.y += 48
                self.states["image_changed"] = True
            success = True
        elif key == pg.K_SPACE or key == pg.K_w:
            # self.states_debug()
            if self["rising"] and not self["jumping"] and not(self["falling"]):
                self.states["image_changed"] = True
                self.y -= 24
                self["jumping"] = True
                # self["falling"] = True
                self["jump_phase"] = 1
                success = True
        self.coordinate()
        self.food.x, self.food.y = self.x, self.y
        self.food.coordinate()
        return success

    def load_images(self):
        self.images = {}
        self.images["body"] = pg.image.load("textures/player/body.png")
        self.images["body_flying"] = pg.image.load("textures/player/body_flying.png")
        self.images["arm"] = pg.image.load("textures/player/arm.png")
        self.images["base"] = pg.image.load("textures/player/player.png")
        self.images["corpse"] = pg.image.load("textures/player/corpse.png")
        self.arm_attacking = Animation("textures/player/arm_attacking.png")

    def attack(self, event=None):
        # self.melee_attack = Animation("textures/player/melee_attack.png")

        def claw_attack():
            if self["attack_frame"] == 0 and self["attacking"] == False:
                self["image_changed"] = True
                self["attacking"] = "melee"
                self.melee_attack = Animation("textures/player/melee_attack.png")
                if self.direction == "right":
                    self.melee_attack_rect = pg.Rect(self.right, self.top, self.melee_attack.width, self.melee_attack.height)
                elif self.direction == "left":
                    self.melee_attack_rect = pg.Rect(self.left - self.melee_attack.width, self.top, self.melee_attack.width, self.melee_attack.height)
                # self["attack_frame"] += 1
            elif self["attack_frame"] < len(self.arm_attacking) * 5 - 1:
                self["attack_frame"] += 1
                self["image_changed"] = True
                if self.direction == "right":
                    self.melee_attack_rect = pg.Rect(self.right, self.top, self.melee_attack.width, self.melee_attack.height)
                elif self.direction == "left":
                    self.melee_attack_rect = pg.Rect(self.left - self.melee_attack.width, self.top, self.melee_attack.width, self.melee_attack.height)
                # pg.time.wait(50)
            else:
                self["attack_frame"] = 0
                self["attacking"] = False
                self["image_changed"] = True
                self.melee_attack = None
                self.melee_attack_rect = None

        def attack_animation():
            if self["attack_frame"] == 0 and self["attacking"] == False:
                self["image_changed"] = True
                self["attacking"] = "other"
            elif self["attack_frame"] < len(self.arm_attacking) * 5 - 1:
                self["attack_frame"] += 1
                self["image_changed"] = True
                # pg.time.wait(50)
            else:
                self["attack_frame"] = 0
                self["attacking"] = False
                self["image_changed"] = True

        if self["attacking"] and event == None:
            if self["attacking"] == "melee":
                claw_attack()
            else:
                attack_animation()
        elif event.button == 1:
            if self.weapon == "claws":
                claw_attack()
            else:
                attack_animation()
        self["image_changed"] = True

    def render(self, surface):
        surface.blit(self.image, self.rect)
        if self["attacking"] == "melee":
            temp = self.melee_attack[self["attack_frame"] // 5].copy()
            if self.direction == "left":
                temp = pg.transform.flip(temp, True, False)
            surface.blit(temp, self.melee_attack_rect)
        elif self["attacking"] == "range":
            self.range_attack.render(surface)
        self.hpbar.render(self, surface)
        self.mbar.render(self, surface)
        self.weapon_frame.render(self, surface)

    def update(self, **kwargs):
        if kwargs:
            #  and not(self["jumping"])
            if "gravity" in kwargs and self["falling"]:
                self.y += kwargs["gravity"]

        if self.golden_health < 0:
            self.golden_health = 0

        if self["jump_phase"]:
            self["jump_phase"] += 1
            self.y -= 12
            self.y -= kwargs["gravity"]
            self["jump_phase"] %= 8
        else:
            self["jumping"] = False
            self["image_changed"] = True
        if self["spawned"]:
            self.image.blit(self.images["arm"], pg.Rect(0, 0, self.rect.width, self.rect.height))
            self["spawned"] = False
        if self["image_changed"]:
            self.image = pg.image.load("textures/player/player.png")
            if self["jumping"] or self["falling"]:
                self.body = self.images[f"body_flying"]
            else:
                self.body = self.images["body"]
            self.image.blit(self.body, pg.Rect(0, 0, self.width, self.height))
            if self["attacking"]:
                self.arm = self.arm_attacking[self["attack_frame"] // 5].copy()
                self.image.blit(self.arm, pg.Rect(0, 0, self.width, self.height))
                self.attack()
            else:
                self.image.blit(self.images["arm"], pg.Rect(0, 0, self.width, self.height))
            if self.direction == "left":
                self.image = pg.transform.flip(self.image, True, False)
            self["image_changed"] = False
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.coordinate()
        self.food.x, self.food.y = self.x, self.y
        self.food.coordinate()

    @property
    def dmg(self):
        return self.damage + self.food.dmg

    @property
    def max_hp(self):
        return self.max_health

    @property
    def speed(self):
        return self.vx + self.food.spd

    def take_damage(self, entity):
        if self.golden_health > 0:
            self.golden_health -= entity.dmg
        else:
            self.health -= entity.dmg

    def change_weapon(self):
        if self.weapon == "claws":
            self.weapon = "fireball"
        elif self.weapon == "fireball":
            self.weapon = "claws"

    def eat(self):
        self.food.activate(self)


class Slime(Entity):
    def __init__(self, coords, vx=1, vy=1, max_health=8):
        super().__init__(coords, "textures/slime/slime.png", (vx, vy), max_health)
        # self.image = pg.image.load("textures/slime/slime.png")
        self.body = self.images["body"]
        self.direction = "right"
        self.load_images()
        self.damage = 2
        self.states["image_changed"] = True

    def load_images(self):
        self.images = {}
        self.images["body"] = pg.image.load("textures/slime/body.png")
        self.images["body_jumping"] = pg.image.load("textures/slime/body_jumping.png")
        self.images["base"] = pg.image.load("textures/slime/slime.png")
        self.images["corpse"] = pg.image.load("textures/slime/corpse.png")

    def move(self, mode="auto"):
        success = False
        if not(self["static"]):
            if mode == "right":
                if self.direction == "left":
                    self["image_changed"] = True
                self.direction = "right"
                if self["move_right"]:
                    self.x += self.vx
                success = True
            elif mode == "left":
                if self.direction == "right":
                    self["image_changed"] = True
                self.direction = "left"
                if self["move_left"]:
                    self.x -= self.vx
                success = True
            elif mode == "up":
                if self["rising"] and not self["jumping"] and not (self["falling"]):
                    self.states["image_changed"] = True
                    # self.y -= 24
                    self["jumping"] = True
                    # self["falling"] = True
                    self["jump_phase"] = 1
                    success = True
            elif mode == "turn":
                if self.direction == "right":
                    self.direction = "left"
                elif self.direction == "left":
                    self.direction = "right"
                self["image_changed"] = True
            elif mode == "auto":
                if self.direction == "right":
                    if self["move_right"]:
                        self.x += self.vx
                    else:
                        self.direction = "left"
                if self.direction == "left":
                    if self["move_left"]:
                        self.x -= self.vx
                    else:
                        self.direction = "right"
            self.coordinate()
        return success

    def update(self, **kwargs):
        if kwargs:
            #  and not(self["jumping"])
            if "gravity" in kwargs and self["falling"]:
                self.y += kwargs["gravity"]
        if self["jump_phase"]:
            self["jump_phase"] += 1
            self.y -= 12
            self.y -= kwargs["gravity"]
            self["jump_phase"] %= 12
        else:
            self["jumping"] = False
            self["image_changed"] = True
        if self["image_changed"]:
            self.image = pg.image.load("textures/slime/slime.png")
            if self["jumping"] or self["falling"]:
                if self["jump_phase"] == 1:
                    self.body = self.images["corpse"]
                else:
                    self.body = self.images[f"body_jumping"]
            else:
                self.body = self.images["body"]
            self.image.blit(self.body, pg.Rect(0, 0, self.width, self.height))
            if self.direction == "left":
                self.image = pg.transform.flip(self.image, True, False)
            self["image_changed"] = False
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.coordinate()

    def render(self, surface):
        surface.blit(self.image, self.rect)
        # print(self.x, self.y)

class Shooter(Entity):
    def __init__(self, coords, vx=1, vy=1, max_health=8):
        super().__init__(coords, "textures/shooter/shooter.png", (vx, vy), max_health)
        # self.image = pg.image.load("textures/slime/slime.png")
        self.load_images()
        self.body = self.images["body"]
        self.direction = "right"
        self.load_images()
        self.damage = 3
        self.states["image_changed"] = True
        self.states["shooting"] = 0
        self.rate = 75

    def load_images(self):
        self.images = {}
        self.images["body"] = pg.image.load("textures/shooter/body.png")
        self.images["preparing"] = pg.image.load("textures/shooter/preparing.png")
        self.images["shooting"] = pg.image.load("textures/shooter/shooting.png")
        self.images["base"] = pg.image.load("textures/shooter/shooter.png")
        self.images["corpse"] = pg.image.load("textures/shooter/corpse.png")

    def move(self, mode="auto"):
        success = False
        if not(self["static"]):
            if mode == "right":
                if self.direction == "left":
                    self["image_changed"] = True
                self.direction = "right"
                if self["move_right"]:
                    self.x += self.vx
                success = True
            elif mode == "left":
                if self.direction == "right":
                    self["image_changed"] = True
                self.direction = "left"
                if self["move_left"]:
                    self.x -= self.vx
                success = True
            elif mode == "turn":
                if self.direction == "right":
                    self.direction = "left"
                elif self.direction == "left":
                    self.direction = "right"
                self["image_changed"] = True
            elif mode == "auto":
                if self.direction == "right":
                    if self["move_right"]:
                        self.x += self.vx
                    else:
                        self.direction = "left"
                if self.direction == "left":
                    if self["move_left"]:
                        self.x -= self.vx
                    else:
                        self.direction = "right"
            self.coordinate()
        return success

    def update(self, **kwargs):
        if kwargs:
            #  and not(self["jumping"])
            if "gravity" in kwargs and self["falling"]:
                self.y += kwargs["gravity"]
        if 0 < self["shooting"] < self.rate:
            self["shooting"] += 1
        elif self.rate <= self["shooting"] <= self.rate + 25:
            self["shooting"] += 1
        elif self["shooting"] > self.rate + 25:
            self["shooting"] = 0
            self["image_changed"] = True
        if self["shooting"] == 2 or self["shooting"] == self.rate:
            self["image_changed"] = True
        # print(self["shooting"])
        if self["image_changed"]:
            self.image = pg.image.load("textures/shooter/shooter.png")
            if self["shooting"] == 0:
                self.body = self.images["body"]
            elif self["shooting"] < self.rate:
                self.body = self.images["preparing"]
            elif 75 <= self["shooting"] <= self.rate:
                self.body = self.images["shooting"]
            self.image.blit(self.body, pg.Rect(0, 0, self.width, self.height))
            if self.direction == "left":
                self.image = pg.transform.flip(self.image, True, False)
            self["image_changed"] = False
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.coordinate()

    def render(self, surface):
        surface.blit(self.image, self.rect)
        # print(self.x, self.y)

    @property
    def trajectory(self):
        if self.direction == "right":
            return pg.Rect(self.center[0], self.center[1], 480, 1)
        else:
            return pg.Rect(self.center[0] - 480, self.center[1], 480, 1)

    def slimeball(self):
        s = SlimeBall(self.center, self.direction)
        s.damage = self.damage
        return s

    def prepare(self):
        if self["shooting"] == 0:
            self["shooting"] = 1


class Boss(Entity):
    def __init__(self, coords):
        Entity.__init__(self, coords, "textures/boss/body_1.png", (4, 4), 80)
        self.damage = 4
        self.attack_timer = 0
        self.states["image_changed"] = True
        self.states["dash_down"] = False
        self["dash_up"] = True
        self.attack = 1

    def load_images(self):
        self.images = {}
        self.images["phase_1"] = pg.image.load("textures/boss/body_1.png")
        self.images["phase_2"] = pg.image.load("textures/boss/body_2.png")
        self.images["base"] = pg.image.load("textures/boss/boss.png")

    def move(self, mode="auto"):
        success = False
        if not (self["static"]):
            if mode == "right":
                if self.direction == "left":
                    self["image_changed"] = True
                self.direction = "right"
                if self["move_right"]:
                    self.x += self.vx
                success = True
            elif mode == "left":
                if self.direction == "right":
                    self["image_changed"] = True
                self.direction = "left"
                if self["move_left"]:
                    self.x -= self.vx
                success = True
            elif mode == "turn":
                if self.direction == "right":
                    self.direction = "left"
                elif self.direction == "left":
                    self.direction = "right"
                self["image_changed"] = True
            elif mode == "auto":
                '''if self.direction == "right":
                    if self["move_right"]:
                        self.x += self.vx
                    else:
                        self.direction = "left"
                if self.direction == "left":
                    if self["move_left"]:
                        self.x -= self.vx
                    else:
                        self.direction = "right"'''
                if self["dash_down"] and self["descent"]:
                    self.y += self.vy * 2
                if not(self["descent"]):
                    self["dash_up"] = True
                    self["dash_down"] = False
                if self["rising"] and self["dash_up"] and self.y > 100 and not self["dash_down"]:
                    self.y -= self.vy
                else:
                    self["dash_up"] = False
            self.coordinate()
        return success

    def update(self, **kwargs):
        '''if kwargs:
            #  and not(self["jumping"])
            if "gravity" in kwargs and self["falling"]:
                self.y += kwargs["gravity"]'''
        self.attack_timer += 1
        if self.attack_timer == 300:
            self.attack_timer = 0
        if self.health < 40:
            self["image_changed"] = True
            self.vx *= 2
            self.vy *= 2
        # print(self["shooting"])
        if self["image_changed"]:
            self.image = pg.image.load("textures/boss/boss.png")
            if self.health < 40:
                self.body = self.images["phase_2"]
            else:
                self.body = self.images["phase_1"]
            self.image.blit(self.body, pg.Rect(0, 0, self.width, self.height))
            if self.direction == "left":
                self.image = pg.transform.flip(self.image, True, False)
            self["image_changed"] = False
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.coordinate()

    @property
    def trajectory(self):
        return pg.Rect(self.center[0], self.center[1], self.width, 800)
