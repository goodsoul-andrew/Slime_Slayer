import json

import pygame as pg
import sys
from game import *
from entities import *


pg.init()
fullscreen = False
screen = pg.display.set_mode((1248, 672), pg.RESIZABLE)
screen.fill((0, 0, 0))
font = pg.font.Font(None, 50)
fps = 60
clock = pg.time.Clock()
running = True
cont = False
#_____________________________________________________________________________
while running:
    pg.mixer.music.load('space_music_1.ogg')
    pg.mixer.music.play()
    screen.fill((0, 0, 0))
    main_menu = True
    newgame_button = font.render("Новая игра", True, (255, 255, 255))
    continue_button = font.render("Продолжить", True, (255, 255, 255))
    exit_button = font.render("Выйти", True, (255, 255, 255))
    screen.blit(newgame_button, (50, 200))
    screen.blit(continue_button, (50, 100))
    screen.blit(exit_button, (50, 300))
    while main_menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                main_menu = False
                running = False
                pg.quit()
            if event.type == pg.MOUSEMOTION:
                if newgame_button.get_rect(topleft=(50, 200)).collidepoint(event.pos):
                    newgame_button = font.render("Новая игра", True, (0, 100, 255))
                else:
                    newgame_button = font.render("Новая игра", True, (255, 255, 255))
                if continue_button.get_rect(topleft=(50, 100)).collidepoint(event.pos):
                    continue_button = font.render("Продолжить", True, (0, 100, 255))
                else:
                    continue_button = font.render("Продолжить", True, (255, 255, 255))
                if exit_button.get_rect(topleft=(50, 300)).collidepoint(event.pos):
                    exit_button = font.render("Выйти", True, (0, 100, 255))
                else:
                    exit_button = font.render("Выйти", True, (255, 255, 255))

            if event.type == pg.MOUSEBUTTONDOWN:
                if newgame_button.get_rect(topleft=(50, 200)).collidepoint(event.pos):
                    newgame_button = font.render("Новая игра", True, (0, 100, 200))
                    cont = False
                    main_menu = False
                else:
                    newgame_button = font.render("Новая игра", True, (255, 255, 255))
                if continue_button.get_rect(topleft=(50, 100)).collidepoint(event.pos):
                    continue_button = font.render("Продолжить", True, (0, 100, 200))
                    cont = True
                    main_menu = False
                else:
                    continue_button = font.render("Продолжить", True, (255, 255, 255))
                if exit_button.get_rect(topleft=(50, 300)).collidepoint(event.pos):
                    exit_button = font.render("Выйти", True, (0, 100, 200))
                    main_menu = False
                    running = False
                    pg.quit()
                else:
                    exit_button = font.render("Выйти", True, (255, 255, 255))
        screen.blit(newgame_button, (50, 200))
        screen.blit(continue_button, (50, 100))
        screen.blit(exit_button, (50, 300))
        pg.display.flip()
        clock.tick(fps)
    #_____________________________________________________________________________
    screen.fill((0, 0, 0))
    if cont:
        with open("save.json") as file:
            save = json.load(file)
            level = Level(save["stage"], levelname=save["name"])
            level.player.max_health = save["player"]["max_health"]
            level.player.health = save["player"]["health"]
            level.player.golden_health = save["player"]["golden_health"]
            level.player.weapon = save["player"]["weapon"]
            level.player.vx = save["player"]["speed"]
            level.player.money = save["player"]["money"]
            if save["player"]["food"]["name"] == "jelly":
                level.player.food = Jelly(level.player.rect.topleft)
                level.player.food.time = save["player"]["food"]["time"]
    else:
        # print("new_game")
        level = Level(0)
    running_game = True
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
            end = True
            running_game = False
            with open("records.txt", "r") as records:
                r = int(records.read().strip())
                # print(r)
                if level.player.money > r:
                    r = level.player.money
            with open("records.txt", "w") as rec:
                rec.write(str(r))
            with open("start.json") as start:
                with open("save.json", "w") as save:
                    st = json.load(start)
                    json.dump(st, save, indent=4)
    #________________________________________________________________________
    game_over = font.render(f"Игра окончена. Счёт: {level.player.money}. Рекорд: {r}", True, (255, 0, 0))
    screen.fill((0, 0, 0))
    while end:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end = False
                running = False
                pg.quit()
        screen.blit(game_over, (300, 300))
        pg.display.flip()
        pg.time.wait(600)
        main_menu = True
        end = False
        clock.tick(fps)
pg.quit()
sys.exit()
