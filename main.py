#!/usr/bin/env python

import os
import math
import libtcodpy as tcod
import game_map
import ui
import entity
import constant

MAIN_MENU_WIDTH = 30  # Size of main menu
MAIN_MENU_HEIGHT = 10 
MAIN_MENU_X = (constant.SCREEN_WIDTH / 2)  - (MAIN_MENU_WIDTH / 2) # Co-ordinates to draw main menu at
MAIN_MENU_Y = (constant.SCREEN_HEIGHT / 2) - (MAIN_MENU_HEIGHT / 2)

VISION_RANGE = 40 # How far the player can see

tcod.console_set_custom_font(os.path.join('fonts', 'terminal10x10.png'),
                             tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

tcod.console_init_root(constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT, 'S.T.A.L.K.E.R RL', False)

# Console for any temporary UI elements (inventory, equipment, etc)
ui_con   = tcod.console_new(constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT)
# Main console that the map and constant UI elements are rendered to
game_con = tcod.console_new(constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT)

tcod.sys_set_fps(constant.LIMIT_FPS)
tcod.console_set_keyboard_repeat(10, 50)

tcod.console_credits()

img = tcod.image_load(os.path.join('images', 'menu_background.png'))
#img2 = tcod.image_load(os.path.join('images', 'test.png'))
#tcod.image_set_key_color(img2, tcod.pink)
tcod.image_blit_2x(img, game_con, 0, 0)
#tcod.image_blit(img2, game_con, 10, 10, tcod.BKGND_SET, 1, 1, 0)
tcod.console_blit(game_con, 0, 0, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT, 0, 0, 0)
tcod.console_flush()

def update_camera(follow_x, follow_y, map_width, map_height):
    """Returns (camera_x, camera_y) centered on (follow_x, follow_y)"""
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

def get_point_ahead(player_x, player_y, mouse_x, mouse_y, distance):
    """Returns the co-ordinates of a point "distance" ahead of the player"""
    if player_x == mouse_x and player_y == mouse_y:
        return (player_x, player_y) # Avoid division by zero

    # What proportion of the player-mouse distance the target point is at
    proportion = distance / math.sqrt((player_x - mouse_x) ** 2 + (player_y - mouse_y) ** 2)

    point_x = int(round(player_x - (proportion * (player_x - mouse_x))))
    point_y = int(round(player_y - (proportion * (player_y - mouse_y))))

    return (point_x, point_y)

def update_fov(a_map, fov_map):
    """Updates the fov map with all map information in a_map"""
    for y in xrange(a_map.height):
        for x in xrange(a_map.width):
            tcod.map_set_properties(fov_map, x, y, a_map.data[y][x].is_transparent,
                                                   a_map.data[y][x].is_walkable)
    return fov_map

def update_entity_fov(entity_list, a_map, fov_map):
    """Update fov_map for all entities in entity_list"""
    for _entity in entity_list:
        tcod.map_set_properties(fov_map, _entity.x, _entity.y,
                                _entity.is_transparent and a_map.data[_entity.y][_entity.x].is_transparent,
                                _entity.is_walkable and a_map.data[_entity.y][_entity.x].is_walkable)
    return fov_map

def play_arena():
    map_size = (constant.SCREEN_WIDTH * 4, constant.SCREEN_HEIGHT * 4)
    the_map = game_map.make_map(*map_size)
    fov_map = tcod.map_new(*map_size)
    player = entity.Entity(map_size[0] / 2, map_size[1] / 2, "@", tcod.black)

    entity_list = [player]

    camera_x, camera_y = (player.x, player.y)

    fov_map = update_fov(the_map, fov_map)
    tcod.map_compute_fov(fov_map, player.x, player.y, VISION_RANGE, True, tcod.FOV_BASIC)
    fov_recompute = True

    in_menu = False
    menu_index = 0

    mouse_status = tcod.mouse_get_status()
    
    while True:
        if not in_menu:
            # Update camera. This must be done before rendering
            (center_x, center_y) = get_point_ahead(player.x, player.y, mouse_status.cx + camera_x,
                                                   mouse_status.cy + camera_y, constant.CAMERA_DISTANCE)
            (camera_x, camera_y) = update_camera(center_x, center_y, the_map.width, the_map.height)

        # Update FOV
        if fov_recompute:
            tcod.map_compute_fov(fov_map, player.x, player.y, VISION_RANGE, True, tcod.FOV_BASIC)
        update_entity_fov(entity_list, the_map, fov_map)

        # Render the map and entities
        the_map.render(game_con, fov_map, camera_x, camera_y, player.x, player.y, mouse_status.cx, mouse_status.cy)
        
        # Only entities in the player's line of sight should be drawn
        for _entity in entity_list:
            if game_map.in_player_fov(_entity.x, _entity.y, player.x, player.y, mouse_status.cx + camera_x,
                                      mouse_status.cy + camera_y, fov_map):
                _entity.render(game_con, camera_x, camera_y)

        # fps display
        tcod.console_print_right(game_con, constant.SCREEN_WIDTH - 1, 0, tcod.BKGND_NONE, str(tcod.sys_get_fps()))
        
        # Finally, blit the console and flush
        tcod.console_blit(game_con, 0, 0, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT, 0, 0, 0)
        tcod.console_flush()

        fov_recompute = False

        mouse_status = tcod.mouse_get_status()

        key = tcod.console_check_for_keypress(tcod.KEY_PRESSED)

        if not in_menu:

            if key.vk == tcod.KEY_LEFT: # Move left
                if not entity.check_collision(player.x - 1, player.y, the_map, entity_list):
                    player.x -= 0 if player.x == 0 else 1
                    fov_recompute = True
            elif key.vk == tcod.KEY_RIGHT: # Move right
                if not entity.check_collision(player.x + 1, player.y, the_map, entity_list):
                    player.x += 0 if player.x == the_map.width else 1
                    fov_recompute = True
            elif key.vk == tcod.KEY_UP: # Move up
                if not entity.check_collision(player.x, player.y - 1, the_map, entity_list):
                    player.y -= 0 if player.y == 0 else 1
                    fov_recompute = True
            elif key.vk == tcod.KEY_DOWN: # Move down
                if not entity.check_collision(player.x, player.y + 1, the_map, entity_list):
                    player.y += 0 if player.y == the_map.height else 1
                    fov_recompute = True
            elif key.c == "i":
                in_menu = "inventory"
            elif key.vk == tcod.KEY_ESCAPE: # Quit back to main menu
                break
        elif in_menu == "inventory":
            if key.vk == tcod.KEY_ESCAPE:
                in_menu = False
            elif key.vk == tcod.KEY_UP:
                menu_index += menu_index and -1
            elif key.vk == tcod.KEY_DOWN:
                menu_index += 0 if menu_index == len(truncated_items) - 1 else 1
            elif key.vk == tcod.KEY_ENTER:
                return menu_index


main_menu_index = 0
while not tcod.console_is_window_closed():
    tcod.image_blit_2x(img, game_con, 0, 0)
    #tcod.image_blit(img2, game_con, 10, 10, tcod.BKGND_SET, 1, 1, 0)
    tcod.console_blit(game_con, 0, 0, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT, 0, 0, 0)
    tcod.console_clear(ui_con)
    ui.draw_menu(ui_con, "S.T.A.L.K.E.R. RL", ['New Game', 'Load Game', 'Highscores', 'Exit'],
                     MAIN_MENU_X, MAIN_MENU_Y, MAIN_MENU_WIDTH, MAIN_MENU_HEIGHT, 0.7, main_menu_index)
    tcod.console_flush()

    option = ui.handle_menu_input(tcod.console_wait_for_keypress(True), main_menu_index, 4)

    if option == "ENTER":
        if main_menu_index == 0:
            gamemode_menu_index = 0
            while True:
                tcod.image_blit_2x(img, game_con, 0, 0)
                tcod.console_blit(game_con, 0, 0, constant.SCREEN_WIDTH, constant.SCREEN_HEIGHT, 0, 0, 0)
                tcod.console_clear(ui_con)
                ui.draw_menu(ui_con, "Game mode?", ['Arena'], MAIN_MENU_X, MAIN_MENU_Y,
                            MAIN_MENU_WIDTH, MAIN_MENU_HEIGHT, 0.7, gamemode_menu_index)
                tcod.console_flush()

                option = ui.handle_menu_input(tcod.console_wait_for_keypress(True), gamemode_menu_index, 1)

                if option == "ENTER":
                    if gamemode_menu_index == 0:
                        play_arena()
                        tcod.image_blit_2x(img, game_con, 0, 0)
                elif option == "ESCAPE":
                    break
                else:
                    gamemode_menu_index = option
        elif main_menu_index == 1:
            pass
        elif main_menu_index == 2:
            pass
        elif main_menu_index == 3:
            break
    elif option != "ESCAPE":
        main_menu_index = option
