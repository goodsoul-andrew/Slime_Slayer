import json

import pygame as pg
import sys
from game import *
from entities import *
import datetime as dtm


pg.init()
fullscreen = False
screen = pg.display.set_mode((1248, 672), pg.RESIZABLE)
screen.fill((0, 0, 0))
font = pg.font.Font(None, 50)
fps = 60
clock = pg.time.Clock()
running = True
cont = False
menu = pg.image.load("textures/menu.png")
mode = "normal"
#_____________________________________________________________________________
while running:
    pg.mixer.music.load('space_music_1.ogg')
    # pg.mixer.music.play()
    # screen.fill((0, 0, 0))
    main_menu = True
    newgame_button = font.render("Новая игра", True, (255, 255, 255))
    continue_button = font.render("Продолжить", True, (255, 255, 255))
    exit_button = font.render("Выйти", True, (255, 255, 255))
    infinity_button = font.render("Бесконечный режим", True, (255, 255, 255))
    # sounds_button = font.render("Звуки", True, (255, 255, 255))
    screen.blit(newgame_button, (50, 200))
    screen.blit(continue_button, (50, 100))
    screen.blit(infinity_button, (50, 300))
    screen.blit(exit_button, (50, 500))
    running_game = True
    screen.blit(menu, (0, 0))
    while main_menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                main_menu = False
                running = False
                running_game = False
                end = False
                # pg.quit()
            if event.type == pg.MOUSEMOTION:
                if newgame_button.get_rect(topleft=(50, 200)).collidepoint(event.pos):
                    newgame_button = font.render("Новая игра", True, (0, 100, 255))
                else:
                    newgame_button = font.render("Новая игра", True, (255, 255, 255))
                if continue_button.get_rect(topleft=(50, 100)).collidepoint(event.pos):
                    continue_button = font.render("Продолжить", True, (0, 100, 255))
                else:
                    continue_button = font.render("Продолжить", True, (255, 255, 255))
                if exit_button.get_rect(topleft=(50, 500)).collidepoint(event.pos):
                    exit_button = font.render("Выйти", True, (0, 100, 255))
                else:
                    exit_button = font.render("Выйти", True, (255, 255, 255))
                if infinity_button.get_rect(topleft=(50, 300)).collidepoint(event.pos):
                    infinity_button = font.render("Бесконечный режим", True, (0, 100, 255))
                else:
                    infinity_button = font.render("Бесконечный режим", True, (255, 255, 255))
            if event.type == pg.MOUSEBUTTONDOWN:
                if newgame_button.get_rect(topleft=(50, 200)).collidepoint(event.pos):
                    newgame_button = font.render("Новая игра", True, (0, 100, 200))
                    cont = False
                    main_menu = False
                    mode = "normal"
                else:
                    newgame_button = font.render("Новая игра", True, (255, 255, 255))
                if continue_button.get_rect(topleft=(50, 100)).collidepoint(event.pos):
                    continue_button = font.render("Продолжить", True, (0, 100, 200))
                    cont = True
                    main_menu = False
                else:
                    continue_button = font.render("Продолжить", True, (255, 255, 255))
                if infinity_button.get_rect(topleft=(50, 300)).collidepoint(event.pos):
                    infinity_button = font.render("Бесконечный режим", True, (0, 100, 255))
                    cont = False
                    main_menu = False
                    mode = "infinity"
                else:
                    infinity_button = font.render("Бесконечный режим", True, (255, 255, 255))
                if exit_button.get_rect(topleft=(50, 500)).collidepoint(event.pos):
                    exit_button = font.render("Выйти", True, (0, 100, 200))
                    main_menu = False
                    running = False
                    pg.quit()
                else:
                    exit_button = font.render("Выйти", True, (255, 255, 255))
        screen.blit(newgame_button, (50, 200))
        screen.blit(continue_button, (50, 100))
        screen.blit(infinity_button, (50, 300))
        screen.blit(exit_button, (50, 500))
        pg.display.flip()
        clock.tick(fps)
    #_____________________________________________________________________________
    screen.fill((0, 0, 0))
    if cont:
        with open("save.json") as file:
            save = json.load(file)
            level = Level(save["stage"], levelname=save["name"], mode=save["mode"])
            level.player.max_health = save["player"]["max_health"]
            level.player.health = save["player"]["health"]
            level.player.vx = save["player"]["speed"]
            level.player.damage = save["player"]["damage"]
            level.player.golden_health = save["player"]["golden_health"]
            level.player.weapon = save["player"]["weapon"]
            level.player.vx = save["player"]["speed"]
            level.player.money = save["player"]["money"]
            if save["player"]["food"]["name"] == "jelly":
                level.player.food = Jelly(level.player.rect.topleft)
                level.player.food.time = save["player"]["food"]["time"]
    else:
        # print("new_game")
        with open("start.json") as file:
            save = json.load(file)
            level = Level(save["stage"], levelname=save["name"], mode=save["mode"], time=save["time"])
            level.mode = mode
            level.player.max_health = save["player"]["max_health"]
            level.player.health = save["player"]["health"]
            level.player.vx = save["player"]["speed"]
            level.player.damage = save["player"]["damage"]
            level.player.golden_health = save["player"]["golden_health"]
            level.player.weapon = save["player"]["weapon"]
            level.player.vx = save["player"]["speed"]
            level.player.money = save["player"]["money"]
            if save["player"]["food"]["name"] == "jelly":
                level.player.food = Jelly(level.player.rect.topleft)
                level.player.food.time = save["player"]["food"]["time"]
    mode = level.mode
    mover = None
    end = False
    while running_game:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running_game = False
                running = False
                # pg.quit()
            elif event.type == pg.KEYDOWN:
                if event.key in [pg.K_a, pg.K_d]:
                    mover = event
                else:
                    mover = None
                if event.key == pg.K_SPACE or event.key == pg.K_w or event.key == pg.K_s:
                    level.move_player(event, gravity=1)
                if event.key == pg.K_TAB:
                    level.player.change_weapon()
                if event.key == pg.K_q:
                    level.player.eat()
                if event.key == pg.K_p and event.mod & pg.KMOD_SHIFT:
                    level.states_debug(mode="slimes")
                elif event.key == pg.K_p:
                    level.coords_debug()
            elif event.type == pg.KEYUP:
                mover = None
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    level.player_attack(event)
                elif event.button == 3:
                    level.player_touch(event)
                # print(level.player["attacking"], level.player.range_attack, level.player["attack_frame"])
        if mover != None:
            if level.move_player(mover, gravity=1):
                level.update(player_moved=True, gravity=1)
            else:
                level.update(gravity=1)
        else:
            level.update(gravity=1)
        #print(480, 344, level.player.center)
        level.render(screen, background=True, mode="fill")
        pg.display.flip()
        clock.tick(fps)
        if not(level.player):
            print("killed")
            end = True
            running_game = False
            with open("records.txt", "r") as records:
                data = [int(el.strip()) for el in records.readlines()]
                if mode == "normal":
                    r = data[0]
                else:
                    r = data[2]
                t = data[1]
                # print(r)
                if level.player.money > r:
                    r = level.score
                if mode == "normal" and level.stage == 5 and level.update_time > t:
                    t = level.update_time
            with open("records.txt", "w") as rec:
                rec.write(str(r) + "\n" + str(t))
            with open("start.json") as start:
                with open("save.json", "w") as save:
                    print("new save")
                    st = json.load(start)
                    json.dump(st, save, indent=4)
    #________________________________________________________________________
            if mode == "normal":
                game_over = font.render(f"Игра окончена.", True, (255, 0, 0))
                record = font.render(f"Счёт: {level.score}. Рекорд: {r}.    Время: {level.update_time}. Лучшее время: {t}", True, (255, 0, 0))
            else:
                game_over = font.render(f"Игра окончена.", True, (255, 0, 0))
                record = font.render(f"Игра окончена. Счёт: {level.score}. Рекорд: {r}", True, (255, 0, 0))
    screen.fill((0, 0, 0))
    level.stop_sounds()
    while end:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end = False
                running = False
                pg.quit()
        if not(level.player):
            screen.blit(game_over, (100, 200))
            screen.blit(record, (100, 300))
        pg.display.flip()
        pg.time.wait(1000)
        main_menu = True
        end = False
        clock.tick(fps)
pg.quit()
sys.exit()
