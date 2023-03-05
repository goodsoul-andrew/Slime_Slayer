import pygame as pg
from entities import *
from blocks import *
from classes import *
from items import *
from projectiles import *
from random import randint
import pytmx as tmx
import json


class Level:
    def __init__(self, stage=0, levelname=None, player=None, mode="normal", time=0):
        self.damage_freq = 30
        self.mode = mode
        self.update_time = time
        self.all_sprites = pg.sprite.Group()
        self.blocks = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.slimes = pg.sprite.Group()
        self.fireballs = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.decorations = pg.sprite.Group()
        self.touchable = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.width, self.height = 960, 672
        self.dx, self.dy = 0, 0
        self.start_render = True
        self.stage = stage
        # print(stage, levelname)
        if not(levelname):
            if mode == "normal":
                if stage == 0:
                    levelname = f"levels/abadoned_temple_room_0.tmx"
                    bg_name = "levels/abadoned_temple_bg.png"
                elif stage <= 4:
                    s = randint(1, 7)
                    levelname = f"levels/abadoned_temple_room_{s}.tmx"
                    bg_name = "levels/abadoned_temple_bg.png"
                elif stage == 5:
                    levelname = "levels/forbidden_shrine_room.tmx"
                    bg_name = "levels/forbidden_shrine_bg.png"
            else:
                if stage == 0:
                    levelname = f"levels/abadoned_temple_room_0.tmx"
                    bg_name = "levels/abadoned_temple_bg.png"
                else:
                    s = randint(1, 7)
                    levelname = f"levels/abadoned_temple_room_{s}.tmx"
                    bg_name = "levels/abadoned_temple_bg.png"
        else:
            if mode == "normal":
                if stage <= 4:
                    bg_name = "levels/abadoned_temple_bg.png"
            else:
                bg_name = "levels/abadoned_temple_bg.png"
        self.levelname = levelname
        if ".tmx" in levelname:
            self.background = Background(bg_name)
            level = tmx.load_pygame(levelname)
            temp = level.get_layer_by_name("blocks")
            for x, y, gid in temp:
                try:
                    b = Block((x * 48, y * 48), image=level.get_tile_image_by_gid(gid))
                    self.blocks.add(b)
                except FileNotFoundError:
                    pass
            temp = level.get_layer_by_name("platforms")
            for x, y, gid in temp:
                try:
                    b = Platform((x * 48, y * 48), image=level.get_tile_image_by_gid(gid))
                    self.platforms.add(b)
                except FileNotFoundError:
                    pass
            temp = level.get_layer_by_name("decorations")
            for x, y, gid in temp:
                try:
                    b = Tile((x * 48, y * 48), image=level.get_tile_image_by_gid(gid))
                    self.decorations.add(b)
                except FileNotFoundError:
                    pass
            temp = level.get_layer_by_name("touchable")
            for obj in temp:
                try:
                    c = (obj.x, obj.y)
                    # print("slime")
                    if obj.name == "candle":
                        b = Candle(c)
                    elif obj.name == "gate":
                        b = Gate(c)
                    elif obj.name == "gate_closed":
                        b = Gate(c)
                        b.lock = True
                    elif obj.name == "trap":
                        b = Trap(c)
                    elif obj.name == "stand":
                        b = Stand(c)
                        if obj.properties["item"] == "random":
                            b.place_random()
                        elif obj.properties["item"] == "golden_heart":
                            b.place(GoldenHeart(c))
                        elif obj.properties["item"] == "healing_potion":
                            b.place(HealingPotion(c))
                        elif obj.properties["item"] == "heart":
                            b.place(Heart(c))
                        elif obj.properties["item"] == "book_up":
                            b.place(BookUp(c))
                    self.touchable.add(b)
                except FileNotFoundError:
                    pass
            '''temp = level.get_layer_by_name("background")
            for x, y, gid in temp:
                try:
                    b = Tile((x * 48, y * 48), image=level.get_tile_image_by_gid(gid))
                    self.platforms.add(b)
                except FileNotFoundError:
                    pass'''
            temp = level.get_layer_by_name("slimes")
            for obj in temp:
                try:
                    #print("slime")
                    if obj.name == "slime":
                        b = Slime((obj.x, obj.y))
                        b.vx += 1 * stage // 2
                        b.damage += 1 * stage
                    elif obj.name == "shooter":
                        b = Shooter((obj.x, obj.y))
                        b.rate += 5 * stage // 2
                        b.damage += 2 * stage
                    elif obj.name == "boss":
                        b = Boss((obj.x, obj.y))
                    b.health += 8
                    self.slimes.add(b)
                except FileNotFoundError:
                    pass
            pl = level.get_object_by_name("player")
            if player == None:
                self.player = Player((pl.x, pl.y))
            else:
                self.player = player.copy((pl.x, pl.y))
            self.player.food.health += 8 * stage // 3
            del level
            self.start_health = self.player.health
        else:
            with open(levelname, "r") as file:
                level = [list(el.strip()) for el in file.readlines()]
                # self.player = Player((96, 96), filename="textures/hitbox_test.png")
                # self.map = [[None for i in range(len(level[j]))] for j in range(len(level))]
                for i in range(len(level)):
                    for j in range(len(level[i])):
                        temp = None
                        if level[i][j] == "#":
                            temp = Block((j * 48, i * 48), "textures/sand.png")
                            self.blocks.add(temp)
                        elif level[i][j] == "p":
                            self.player = Player((j * 48, i * 48), filename="textures/player_right.png")
                        elif level[i][j] == "_":
                            temp = Platform((j * 48, i * 48), "textures/platform.png")
                            self.platforms.add(temp)
                        elif level[i][j] == "s":
                            temp = Slime((j * 48, i * 48))
                            # temp["static"] = True
                            self.slimes.add(temp)
                        elif level[i][j] == "T":
                            temp = Stand((j * 48, i * 48), "textures/blocks/stand.png")
                            self.decorations.add(temp)
                        elif level[i][j] == "0":
                            temp = Coin((j * 48, i * 48), 10)
                            self.items.add(temp)
                        if temp:
                            self.all_sprites.add(temp)

    def move_player(self, event, **kwargs):
        success = self.player.move(event)
        self.player.update(**kwargs)
        return success

    def update(self, **kwargs):

        def player_update(**kwargs):
            falling, descent, rising, move_left, move_right = [True] * 5
            for block in self.blocks:
                if not(descent or falling or rising or move_right or move_left):
                    break
                if self.player.touch(block):
                    if descent and self.player.is_above(block):
                        descent = False
                        self.player["jumping"] = False
                        # print("above", block)
                    if falling and self.player.is_above(block):
                        # print("above", block)
                        falling = False
                        self.player["jumping"] = False
                    if rising and self.player.is_under(block):
                        # print("under", block)
                        rising = False
                    if move_right and self.player.is_lefter(block):
                        # print("lefter", block)
                        move_right = False
                    if move_left and self.player.is_righter(block):
                        # print("righter", block)
                        move_left = False

            for platform in self.platforms:
                if self.player.touch(platform):
                    if falling and self.player.get_bottom_toucher().colliderect(platform.rect):
                        self.player["jumping"] = False
                        falling = False
                        diff = platform.rect.top - self.player.get_bottom_toucher().bottom
                        self.player.y += diff + 1
                        self.player.coordinate()
                    '''if falling and self.player.is_above(platform):
                        # print("above", platform)
                        self.player["jumping"] = False
                        falling = False
                        break'''
                    '''elif falling and self.player.collide(platform):
                        self.player.rect.bottom = platform.top
                        self.player["jumping"] = False
                        falling = False'''
            self.player["falling"] = falling
            self.player["descent"] = descent
            self.player["rising"] = rising
            self.player["move_left"] = move_left
            self.player["move_right"] = move_right
            for item in self.items:
                if self.player.collide(item):
                    item.activate(self.player)
                    item.kill()
            self.player.update(**kwargs)
            if self.update_time % self.damage_freq == 0:
                for slime in self.slimes:
                    if type(slime) == Slime and self.player.collide(slime):
                        self.player.take_damage(slime)
                for t in self.touchable:
                    if type(t) == Trap and t.state == "spikes":
                        self.player.take_damage(t)

        def slimes_update(**kwargs):
            # print(len(self.slimes))
            for slime in self.slimes:
                if slime:
                    falling, descent, rising, move_left, move_right = [True] * 5
                    for block in self.blocks:
                        if not (descent or falling or rising or move_right or move_left):
                            break
                        if slime.touch(block):
                            # print("touch", block)
                            if descent and slime.is_above(block):
                                descent = False
                                slime["jumping"] = False
                                # print("above", block)
                            if falling and slime.is_above(block):
                                # print("above", block)
                                falling = False
                                slime["jumping"] = False
                            if rising and slime.is_under(block):
                                # print("under", block)
                                rising = False
                            if move_right and slime.is_lefter(block):
                                # print("lefter", block)
                                move_right = False
                            if move_left and slime.is_righter(block):
                                # print("righter", block)
                                move_left = False
                    for platform in self.platforms:
                        if slime.touch(platform):
                            if falling and slime.is_above(platform):
                                # print("above", platform)
                                slime["jumping"] = False
                                falling = False
                                break
                    slime["falling"] = falling
                    slime["descent"] = descent
                    slime["rising"] = rising
                    slime["move_left"] = move_left
                    slime["move_right"] = move_right
                    if type(slime) == Slime:
                        '''if abs(self.player.rect.center[0] - slime.rect.center[0]) < 96 and self.player.direction != slime.direction:
                            slime.move("up")
                            slime.move("turn")'''
                        slime.move()
                    elif type(slime) == Shooter:
                        if self.player.rect.center[0] < slime.rect.center[0] and slime.direction != "left":
                            slime.move("turn")
                        elif self.player.rect.center[0] >= slime.rect.center[0] and slime.direction != "right":
                            slime.move("turn")
                        if self.player.rect.colliderect(slime.trajectory):
                            slime.prepare()
                        if slime["shooting"] == 75:
                            self.projectiles.add(slime.slimeball())
                    slime.update(**kwargs)
                else:
                    try:
                        x, y = slime.x, slime.y
                        slime.kill()
                        drop = randint(1, 100)
                        if self.player.food == "jelly":
                            self.player.food.time += 1
                            print(self.player.food.time)
                        #print(drop)
                        if drop > 80:
                            item = HealingPotion((x, y), 10)
                        else:
                            item = Coin((x, y), 10)
                        self.items.add(item)
                    except KeyError:
                        print("KeyError")

        def items_update(**kwargs):
            for item in self.items:
                falling = True
                for block in self.blocks:
                    if item.collide(block):
                        falling = False
                        break
                for platform in self.platforms:
                    if item.collide(platform):
                        falling = False
                        break
                item.falling = falling
                item.update(**kwargs)

        def touchable_update(**kwargs):
            for t in self.touchable:
                if type(t) == Gate:
                    if len(self.slimes) == 0:
                        t.open()
                elif type(t) == Trap:
                    if self.player.is_above(t) and self.player.touch(t):
                        t.activate()
                    elif not(self.player.collide(t)) and t.timer > 40:
                        t.deactivate()
                t.update(**kwargs)

        def fireballs_update(**kwargs):
            for f in self.fireballs:
                for s in self.slimes:
                    if s.collide(f):
                        s.take_damage(f)
                        f.health = 0
                for p in self.projectiles:
                    if p.collide(f):
                        p.kill()
                        f.health = 0
                if not(f):
                    f.kill()
                else:
                    f.update()

        def projectiles_update(**kwargs):
            for p in self.projectiles:
                if p.collide(self.player):
                    self.player.take_damage(p)
                    p.kill()
                if not(p):
                    p.kill()
                else:
                    p.update(**kwargs)

        slimes_update(**kwargs)
        items_update(**kwargs)
        touchable_update(**kwargs)
        fireballs_update(**kwargs)
        projectiles_update(**kwargs)
        if "player_moved" not in kwargs:
            player_update(**kwargs)
        else:
            player_update()
        self.blocks.update()
        self.platforms.update()
        self.update_time += 1

    def render(self, screen, background=True, mode="full"):
        # d = self.camera_coordinate()
        # print(self.player.center[1] + d[1] == self.height // 2)
        self.background.render(screen, mode=mode)
        if self.start_render:
            self.blocks.draw(screen)
            self.platforms.draw(screen)
            # self.start_render = False
        for d in self.decorations:
            d.render(screen)
        for t in self.touchable:
            t.render(screen)
        self.player.render(screen)
        for slime in self.slimes:
            slime.render(screen)
        for item in self.items:
            screen.blit(item.image, item.rect)
        for f in self.fireballs:
            f.render(screen)
        for p in self.projectiles:
            p.render(screen)

    def coords_debug(self):
        self.player.coords_debug()
        for b in self.blocks:
            b.coords_debug()

    def states_debug(self, mode="player"):
        if mode == "player":
            self.player.states_debug()
        elif mode == "slimes":
            for slime in self.slimes:
                slime.states_debug()

    def player_attack(self, event, **kwargs):
        self.player.attack(event)
        if self.player["attacking"] == "melee":
            for slime in self.slimes:
                if self.player.melee_attack_rect.colliderect(slime.rect):
                    slime.take_damage(self.player)
                    '''if not(slime):
                        try:
                            slime.kill()
                        except KeyError:
                            print("KeyError")'''
            for p in self.projectiles:
                if self.player.melee_attack_rect.colliderect(p.rect):
                    p.kill()
        else:
            if self.player.weapon == "fireball":
                if len(self.fireballs) == 0:
                    if self.player.direction == "right":
                        fireball = PlayerFireball((self.player.rect.right, self.player.rect.center[1]),
                                                  self.player.direction)
                    else:
                        fireball = PlayerFireball((self.player.rect.left, self.player.rect.center[1]),
                                                  self.player.direction)
                    fireball.damage = self.player.damage
                    self.fireballs.add(fireball)
                for fireball in self.fireballs:
                    for slime in self.slimes:
                        if slime.collide(fireball):
                            slime.take_damage(fireball)
                            fireball.kill()
                            # pass
                    # print(len(self.slimes), hash(slime), slime.health)

    def player_touch(self, event):
        for t in self.touchable:
            if t.clicked(event):
                if type(t) == Gate and t.opened:
                    self.__init__(stage=self.stage + 1, player=self.player, mode=self.mode)
                    self.save()
                elif type(t) == Candle:
                    # print(t.lit)
                    t.extinguish()
                elif type(t) == Stand and len(self.slimes) == 0:
                    i = t.take()
                    if i != None:
                        self.items.add(i)

    @property
    def score(self):
        s = 0
        if self.stage == 5:
            s = self.start_health * 2
        else:
            s = self.player.health * 2
        return self.player.money + s + self.player.speed + self.player.damage + self.player.max_health + s + self.stage

    def save(self):
        with open("save.json", "w") as save:
            lvl = {}
            lvl["name"] = self.levelname
            lvl["stage"] = self.stage
            lvl["mode"] = self.mode
            lvl["time"] = self.update_time
            lvl["player"] = {}
            lvl["player"]["health"] = self.player.health
            lvl["player"]["max_health"] = self.player.max_health
            lvl["player"]["golden_health"] = self.player.golden_health
            lvl["player"]["speed"] = self.player.vx
            lvl["player"]["damage"] = self.player.damage
            lvl["player"]["money"] = self.player.money
            lvl["player"]["weapon"] = self.player.weapon
            lvl["player"]["food"] = {}
            lvl["player"]["food"]["name"] = self.player.food.name
            lvl["player"]["food"]["time"] = self.player.food.time
            json.dump(lvl, save, indent=4)


