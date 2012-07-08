#!/usr/bin/env python

import os
import random
import math
import cProfile
import libtcodpy as tcod

import game_map
import ui
import entity
import constant

MAIN_MENU_X = 5
MAIN_MENU_Y = 5
MAIN_MENU_WIDTH = 30 
MAIN_MENU_HEIGHT = 10 

VISION_RANGE = 40

tcod.console_set_custom_font(os.path.join('fonts', 'terminal10x10.png'),
                             tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

tcod.console_init_root(constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT, 'S.T.A.L.K.E.R RL', False)
ui_con   = tcod.console_new(constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT)
game_con = tcod.console_new(constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT)

tcod.sys_set_fps(constant.LIMIT_FPS)
tcod.console_set_keyboard_repeat(10, 50)

tcod.console_credits()

img = tcod.image_load(os.path.join('images', 'menu_background.png'))
tcod.image_blit_2x(img, game_con, 0, 0)
tcod.console_blit(game_con, 0, 0, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT, 0, 0, 0)
tcod.console_flush()

def update_camera(follow_x, follow_y, map_width, map_height):
    camera_x = follow_x - constant.SCREEN_WIDTH / 2
    if camera_x < 0:
        camera_x = 0
    elif camera_x > map_width - constant.SCREEN_WIDTH:
        camera_x = map_width - constant.SCREEN_WIDTH

    camera_y = follow_y - constant.SCREEN_HEIGHT / 2
    if camera_y < 0:
        camera_y = 0
    elif camera_y > map_height - constant.SCREEN_HEIGHT:
        camera_y = map_height - constant.SCREEN_HEIGHT

    return (camera_x, camera_y)

def update_fov(a_map, fov_map):
    for y in xrange(a_map.height):
        for x in xrange(a_map.width):
            tcod.map_set_properties(fov_map, x, y, a_map.data[y][x].is_transparent,
                                                   a_map.data[y][x].is_walkable)
    return fov_map

def update_entity_fov(entity_list, a_map, fov_map):
    for _entity in entity_list:
        tcod.map_set_properties(fov_map, _entity.x, _entity.y,
                                _entity.is_transparent and a_map.data[_entity.y][_entity.x].is_transparent,
                                _entity.is_walkable and a_map.data[_entity.y][_entity.x].is_walkable)
    return fov_map

def check_collision(x, y, a_map, entity_list):
    if not a_map.data[y][x].is_walkable:
        return True

    for _entity in entity_list:
        if _entity.x == x and _entity.y == y:
            return True

    return False

def play_arena():
    the_map = game_map.make_map(constant.SCREEN_WIDTH + 10, constant.SCREEN_HEIGHT + 10)
    fov_map = tcod.map_new(constant.SCREEN_WIDTH + 10, constant.SCREEN_HEIGHT + 10)
    player = entity.Entity(0, 0, "@", tcod.black)

    entity_list = [player]
    for y in xrange(the_map.height):
        for x in xrange(the_map.width):
            if random.randint(1,10) == 2:
                entity_list.append(entity.Entity(x, y, "^", tcod.green, False, False))
    camera_x, camera_y = (0, 0)

    fov_map = update_fov(the_map, fov_map)
    fov_recompute = True
    
    while True:
        (camera_x, camera_y) = update_camera(player.x, player.y,
                                             the_map.width, the_map.height)

        if fov_recompute:
            tcod.map_compute_fov(fov_map, player.x, player.y, VISION_RANGE, True, tcod.FOV_SHADOW)

        update_entity_fov(entity_list, the_map, fov_map)

        mouse_status = tcod.mouse_get_status()

        the_map.render(game_con, fov_map, camera_x, camera_y, player.x, player.y, mouse_status.cx, mouse_status.cy)

        for _entity in entity_list:
            _entity.render(game_con, camera_x, camera_y)

        tcod.console_blit(game_con, 0, 0, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT, 0, 0, 0)
        tcod.console_flush()

        fov_recompute = True

        key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)
        if key.vk == tcod.KEY_LEFT:
            if not check_collision(player.x - 1, player.y, the_map, entity_list):
                player.x -= 0 if player.x == 0 else 1
        elif key.vk == tcod.KEY_RIGHT:
            if not check_collision(player.x + 1, player.y, the_map, entity_list):
                player.x += 0 if player.x == the_map.width else 1
        elif key.vk == tcod.KEY_UP:
            if not check_collision(player.x, player.y - 1, the_map, entity_list):
                player.y -= 0 if player.y == 0 else 1
        elif key.vk == tcod.KEY_DOWN:
            if not check_collision(player.x, player.y + 1, the_map, entity_list):
                player.y += 0 if player.y == the_map.height else 1
        elif key.vk == tcod.KEY_ESCAPE:
            break
        else:
            fov_recompute = False

while not tcod.console_is_window_closed():
    option = ui.menu(['New Game', 'Load Game', 'Highscores', 'Credits', 'Exit'], "S.T.A.L.K.E.R. RL",
                     MAIN_MENU_X, MAIN_MENU_Y, MAIN_MENU_WIDTH, MAIN_MENU_HEIGHT, ui_con, game_con, 0.7)
    if option == 0:
        while True:
            new_game_option = ui.menu(['Arena'], "Game mode?", MAIN_MENU_X, MAIN_MENU_Y,
                                      MAIN_MENU_WIDTH, MAIN_MENU_HEIGHT, ui_con, game_con, 0.7)
            if new_game_option == -1:
                break
            elif new_game_option == 0:
                play_arena()
                tcod.image_blit_2x(img, game_con, 0, 0)
    elif option == 1:
        pass
    elif option == 2:
        pass
    elif option == 3:
        pass
    elif option == 4:
        break
