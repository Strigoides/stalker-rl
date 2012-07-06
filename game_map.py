import copy
import math
import random
import libtcodpy as tcod
import tile_types
import constant

class Map:
    def __init__(self, data):
        self.data = data
        self.height = len(data)
        self.width = len(data[0])

    def render(self, screen, fov_map, camera_x, camera_y, player_x, player_y, mouse_x, mouse_y):
        tcod.console_clear(screen)

        for y in xrange(constant.SCREEN_HEIGHT):
            adj_y = y + camera_y

            for x in xrange(constant.SCREEN_WIDTH):
                adj_x = x + camera_x

                p = math.sqrt((adj_x    - mouse_x)  ** 2 + (adj_y    - mouse_y)  ** 2)
                s = math.sqrt((player_x - mouse_x)  ** 2 + (player_y - mouse_y)  ** 2)
                m = math.sqrt((adj_x    - player_x) ** 2 + (adj_y    - player_y) ** 2)

                if p != 0 and s != 0 and m != 0:
                    try:
                        angle = math.acos((p ** 2 - s ** 2 - m ** 2) / (-2 * s * m))
                    except:
                        pass
                else:
                    angle = 0

#               # S   <- (x, y)                cosine rule used to find P; angle between
#               |\ m                           s and m. If this angle is > FOV_ANGLE / 2,
#             p | # P <- (player_x, player_y)  the square s is out of vision
#               |/ s
#               # M   <- (mouse_x, mouse_y)

                if (tcod.map_is_in_fov(fov_map, adj_x, adj_y) and
                        angle < constant.FOV_ANGLE / 2):
                    self.data[adj_y][adj_x].explored = True

                    tcod.console_put_char_ex(screen, x, y,
                                             ord(self.data[adj_y][adj_x].char),
                                             self.data[adj_y][adj_x].fore_color,
                                             self.data[adj_y][adj_x].back_color)
                elif self.data[adj_y][adj_x].explored:
                    tcod.console_put_char_ex(screen, x, y,
                                             ord(self.data[adj_y][adj_x].char),
                                             self.data[adj_y][adj_x].fore_color * constant.MEMORY_TINT,
                                             self.data[adj_y][adj_x].back_color * constant.MEMORY_TINT)
                else:
                    tcod.console_set_back(screen, x, y, tcod.black)

def make_map(width, height):
    return Map([[Tile("grass", True, True) for n in xrange(width)] for n in xrange(height)])
            
class Tile:
    def __init__(self, material, is_walkable, is_transparent):
        self.material = material
        self.char =  random.choice(tile_types.char[material])

        self.back_color = copy.deepcopy(tile_types.color[material])
        self.fore_color = copy.deepcopy(tile_types.color[material])

        r_max = min(255, self.back_color.r + constant.COLOR_VARIATION)
        r_min = max(0, self.back_color.r - constant.COLOR_VARIATION)
        g_max = min(255, self.back_color.g + constant.COLOR_VARIATION)
        g_min = max(0, self.back_color.g - constant.COLOR_VARIATION)
        b_max = min(255, self.back_color.b + constant.COLOR_VARIATION)
        b_min = max(0, self.back_color.b - constant.COLOR_VARIATION)

        self.back_color.r = random.randrange(r_min, r_max + 1)
        self.back_color.g = random.randrange(g_min, g_max + 1)
        self.back_color.b = random.randrange(b_min, b_max + 1)

        self.fore_color.r = random.randrange(r_min, r_max + 1)
        self.fore_color.g = random.randrange(g_min, g_max + 1)
        self.fore_color.b = random.randrange(b_min, b_max + 1)

        self.is_walkable = is_walkable
        self.is_transparent = is_transparent

        self.explored = False
