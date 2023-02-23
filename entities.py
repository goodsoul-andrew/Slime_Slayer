import pygame as pg
from classes import *
from projectiles import PlayerFireball


class Entity(GameObject):
    def __init__(self, coords, filename, v, max_health, **kwargs):
        super().__init__(coords, filename)
        self.vx, self.vy = v
        self.speed = 1
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
        self.health -= entity.damage

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
        return GameObject.touch(self, other, speed=self.vx)

    def get_left_toucher(self):
        return GameObject.get_left_toucher(speed=self.vx)

    def get_right_toucher(self):
        return GameObject.get_right_toucher(speed=self.vx)



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
        self.weapon = "fireball"
        # fireball claws
        self.hpbar = HealthBar()
        self.mbar = MoneyBar()
        self.weapon_frame = WeaponFrame()
        self.golden_health = 0

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
                self.x -= self.vx
            success = True
        if key == pg.K_d:
            if self.direction == "left":
                self.states["image_changed"] = True
            self.direction = "right"
            if self["move_right"]:
                self.x += self.vx
            success = True
        if key == pg.K_SPACE and event.mod & pg.KMOD_SHIFT:
            if self["descent"] and not self["falling"]:
                self.y += 48
                self.states["image_changed"] = True
            success = True
        elif key == pg.K_SPACE:
            # self.states_debug()
            if self["rising"] and not self["jumping"] and not(self["falling"]):
                self.states["image_changed"] = True
                self.y -= 24
                self["jumping"] = True
                # self["falling"] = True
                self["jump_phase"] = 1
                success = True
        self.coordinate()
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

    def take_damage(self, entity):
        if self.golden_health > 0:
            self.golden_health -= entity.damage
        else:
            self.health -= entity.damage


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
                    self.direction == "left"
                elif self.direction == "left":
                    self.direction == "right"
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