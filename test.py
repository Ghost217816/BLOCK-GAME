import pygame as pg
import math
import random
import json  # Додаємо для збереження світу
import os    # Додаємо для перевірки наявності файлу збереження
import sys

def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)

pg.init()

# =====================================
# Налаштування вікна
# =====================================

WIDTH = 500
HEIGHT = 500

# Зберігаємо початкове віконне розширення
WINDOW_WIDTH = WIDTH
WINDOW_HEIGHT = HEIGHT

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Block Game")

is_fullscreen = False  # Прапорець повного екрана
camera_scale = 1.0     # Масштаб камери (1.0 - звичайний, 1.5 - наближений)

clk = pg.time.Clock()
running = True

# =====================================
# Константи
# =====================================

BLOCK_SIZE = 50
PLACE_DISTANCE = BLOCK_SIZE * 5

HOTBAR_SIZE = 9

inventory_open = False

# Базові налаштування звичайного інвентарю
INVENTORY_ROWS = 3
INVENTORY_COLS = 9
MAX_STACK_SIZE = 64

# Креативний інвентар (збільшено до 120 слотів: 13 рядків по 9 слотів = 117 + 3 слоти в 14 ряду)
CREATIVE_ROWS = 14
CREATIVE_COLS = 9

# Сундук константи
CHEST_ROWS = 3
CHEST_COLS = 9

# Збільшено світ до 6000 blocks за проханням гравця
WORLD_WIDTH = 6000
WORLD_HEIGHT = 1350  # Верхній світ + Пекло, збільшене на 1000 блоків.

# Межі вимірів по висоті (в блоках від верху світу y = 0)
HEAVEN_BOTTOM = 100     # Рай займає блоки з 0 до 100 (висота над землею 200+ блоків)
OVERWORLD_START = 100   # Порожнеча та Верхній світ починаються зі 100
OVERWORLD_HEIGHT = 300  # Верхній світ закінчується на 300 блоці

# Глобальний прапорець креативного режиму
is_creative = False

# Зберігаємо координати структури порталу для телепортації
portal_structure_pos = (0, 0)
portal_frame_positions = set()       # Активовані обсидіанові рамки не мають колізії.
nether_portal_pairs = {}             # (x, y) блоку порталу -> безпечна точка призначення.
portal_charge = 0.0
portal_cooldown = 0.0
PORTAL_WARMUP_SECONDS = 3.0

# Список усіх предметів гри для креативного меню
ALL_ITEMS = [
    "grass.png", "dirt.png", "stone.png", "cobblestone.png", "sand.png", "basalt.png", "wood.png", "planks.png", "leaves.png",
    "bedrock.png", "tall_grass.png", "water.png", "bucket.png", "water_bucket.png", "lava_bucket.png", "crafting_table.png", "furnace.png", "chest.png", "seeds.png", "wheat.png",
    "bread.png", "potato.png", "baked_potato.png", "kelp.png", "dried_kelp.png", "stick.png", "coal_ore.png", "iron_ore.png", 
    "gold_ore.png", "diamond_ore.png", "netherite_ore.png", "coal.png", "iron_ingot.png", "gold_ingot.png", "diamond.png", "netherite_scrap.png", 
    "netherite_ingot.png", "torch.png", "netherrack.png", "lava.png", "nether_gold_ore.png", "gold_block.png",
    "iron_block.png", "diamond_block.png", "netherite_block.png", "cloud_ore.png", "heaven_shard.png", "heaven_ingot.png", "flight_emblem.png",
    "fishing_rod.png", "fish.png", "cooked_fish.png", "sushi.png", "rice.png", "door_closed.png", "cactus.png", "heaven_cloud.png", "string.png",
    "snow_grass.png", "bed.png", "wool.png", "end_stone.png", "obsidian.png", "end_crystal.png", "ender_pearl.png", "dragon_egg.png",
    "wood_pickaxe.png", "stone_pickaxe.png", "iron_pickaxe.png", "gold_pickaxe.png", "diamond_pickaxe.png", "netherite_pickaxe.png",
    "wood_shovel.png", "stone_shovel.png", "iron_shovel.png", "gold_shovel.png", "diamond_shovel.png", "netherite_shovel.png",
    "wood_axe.png", "stone_axe.png", "iron_axe.png", "gold_axe.png", "diamond_axe.png", "netherite_axe.png",
    "wood_hoe.png", "stone_hoe.png", "iron_hoe.png", "gold_hoe.png", "diamond_hoe.png", "netherite_hoe.png", "portal_frame.png", "portal.png", "potal_ad.png",
    "warped_grass.png", "warped_wood.png", "warped_leaves.png", "nether_brick.png", "birch_wood.png", "birch_leaves.png"
]

# Ініціалізація інвентарю та хотбару
inventory = [None for _ in range(INVENTORY_ROWS * INVENTORY_COLS)]
hotbar = [None for _ in range(HOTBAR_SIZE)]

# Координати біомів для телепортації 
biome_coords = {
    "plains": 100 * BLOCK_SIZE,
    "sea": 2000 * BLOCK_SIZE,
    "desert": 3000 * BLOCK_SIZE,
    "volcano": 3800 * BLOCK_SIZE,
    "snow": 4500 * BLOCK_SIZE,  
    "birch": 5200 * BLOCK_SIZE,
    "nether": 100 * BLOCK_SIZE, 
    "warped": 4700 * BLOCK_SIZE,
    "fortress": 3500 * BLOCK_SIZE,
    "end_dungeon": 100 * BLOCK_SIZE,
    "heaven": 100 * BLOCK_SIZE,
    "end": 100 * BLOCK_SIZE
}

BLOCK_DURATIONS = {
    "tall_grass.png": 1,
    "wheat_stage0.png": 1,
    "wheat_stage1.png": 1,
    "wheat_stage2.png": 1,
    "wheat_stage3.png": 1,
    "potato_stage0.png": 1,
    "potato_stage1.png": 1,
    "potato_stage2.png": 1,
    "potato_stage3.png": 1,
    "rice_stage0.png": 1,
    "rice_stage1.png": 1,
    "leaves.png": 15,
    "grass.png": 35,
    "snow_grass.png": 35,  
    "dirt.png": 35,
    "farmland.png": 35,
    "wood.png": 60,
    "crafting_table.png": 75,
    "furnace.png": 110,
    "chest.png": 70,
    "stone.png": 90,
    "cobblestone.png": 90,
    "basalt.png": 100,
    "coal_ore.png": 95,
    "iron_ore.png": 110,
    "gold_ore.png": 115,
    "diamond_ore.png": 140,
    "netherite_ore.png": 160,
    "cloud_ore.png": 200,
    "door_closed.png": 40,
    "door_open.png": 40,
    "sand.png": 30,               
    "kelp_stage0.png": 5,          
    "kelp_stage1.png": 5,
    "kelp_stage2.png": 5,
    "kelp_stage3.png": 5,
    "torch.png": 1,
    "netherrack.png": 45,
    "nether_gold_ore.png": 80,
    "gold_block.png": 100,
    "iron_block.png": 110,
    "diamond_block.png": 130,
    "netherite_block.png": 180,
    "cactus.png": 20,
    "heaven_cloud.png": 15,
    "bed.png": 40,
    "wool.png": 25,
    "end_stone.png": 50,
    "obsidian.png": 250,
    "end_crystal.png": 5,
    "dragon_egg.png": 20,
    "portal_frame.png": -1,
    "portal.png": -1,
    "potal_ad.png": -1,
    "warped_grass.png": 35, "warped_wood.png": 60, "warped_leaves.png": 15,
    "nether_brick.png": 100, "birch_wood.png": 60, "birch_leaves.png": 15
}
DEFAULT_DURATION = 50

# Визначені висотні діапазони (глибина від поверхні) для всіх руд.
ORE_DEPTH_RANGES = {
    "coal_ore.png": (6, 45), "iron_ore.png": (12, 75),
    "gold_ore.png": (38, 110), "diamond_ore.png": (70, 180),
    "nether_gold_ore.png": (8, 700), "netherite_ore.png": (80, 950),
    "cloud_ore.png": (0, 20),
}

mining_block = None
mining_timer = 0.0

# Змінні Дня та Ночі 
day_time = 0.0  
DAY_DURATION = 30 * 60  

# Температурні таймери 
desert_sun_timer = 0.0
snow_freeze_timer = 0.0
temperature_damage_cooldown = 0.0

# Механіка Погоди
is_raining = False
rain_timer = random.randint(3600, 7200)  
rain_particles = []
splash_particles = []  
MAX_RAIN_PARTICLES = 90
rain_cover_cache = {}

RAIN_TRANSPARENT_BLOCKS = {
    "tall_grass.png", "water.png", "lava.png", "torch.png", "potal_ad.png",
    "heaven_cloud.png", "leaves.png", "palm_leaves.png"
}

def is_rain_covered(grid_x, grid_y):
    """Перевірка стелі для дощу; результат кешується, тому не гальмує кадр."""
    if not (OVERWORLD_START * BLOCK_SIZE <= grid_y < OVERWORLD_HEIGHT * BLOCK_SIZE):
        return True
    key = (grid_x, grid_y)
    cached = rain_cover_cache.get(key)
    if cached is not None:
        return cached
    for check_y in range(grid_y - BLOCK_SIZE, OVERWORLD_START * BLOCK_SIZE - 1, -BLOCK_SIZE):
        above_b = blocks_map.get((grid_x, check_y))
        if above_b and above_b.texture not in RAIN_TRANSPARENT_BLOCKS:
            rain_cover_cache[key] = True
            return True
    rain_cover_cache[key] = False
    return False

def update_weather(dt):
    global is_raining, rain_timer, rain_particles, splash_particles
    
    if player.rect.y < -2000 * BLOCK_SIZE:
        is_raining = False
        rain_particles.clear()
        return

    if not is_raining:
        rain_timer -= 1
        if rain_timer <= 0:
            is_raining = True
            rain_timer = random.randint(2400, 4800)  
    else:
        rain_timer -= 1
        if rain_timer <= 0:
            is_raining = False
            rain_timer = random.randint(3600, 7200)
            rain_particles.clear()
            
        player_block_x = player.rect.x // BLOCK_SIZE
        
        # Погода є глобальною: вона не обривається на межах звичайних чанків.
        if len(rain_particles) < MAX_RAIN_PARTICLES:
            # Опади глобальні: біом снігу більше не перетворює дощ на
            # локальний інший ефект, тому дощ однаково видно в усьому світі.
            speed = random.randint(7, 10)
            rain_particles.append([random.randint(0, WIDTH), random.randint(-20, 0), speed, False])
                
        for particle in rain_particles[:]:
            particle[1] += particle[2] 
            if not particle[3]:
                particle[0] -= 1  
            else:
                particle[0] += random.choice([-0.5, 0.5]) 
                
            p_world_x = int((particle[0] / camera_scale) + camera_x)
            p_world_y = int((particle[1] / camera_scale) + camera_y)
            grid_x = (p_world_x // BLOCK_SIZE) * BLOCK_SIZE
            grid_y = (p_world_y // BLOCK_SIZE) * BLOCK_SIZE
            
            has_roof_above = is_rain_covered(grid_x, grid_y)

            hit_surface = False
            block = blocks_map.get((grid_x, grid_y))
            if (block and block.texture not in ["tall_grass.png", "lava.png", "potal_ad.png"]) or has_roof_above:
                hit_surface = True
            
            if particle[1] > HEIGHT or hit_surface:
                if hit_surface and not particle[3] and not has_roof_above:
                    for _ in range(3):
                        splash_particles.append([particle[0], particle[1], random.uniform(-1, 1), random.uniform(-2, -0.5), 20])
                
                if is_raining:
                    particle[1] = random.randint(-20, 0)
                    particle[0] = random.randint(0, WIDTH)
                    particle[3] = False
                    particle[2] = random.randint(7, 10)
                else:
                    rain_particles.remove(particle)

    for splash in splash_particles[:]:
        splash[0] += splash[2]
        splash[1] += splash[3]
        splash[3] += 0.1 
        splash[4] -= 1   
        if splash[4] <= 0:
            splash_particles.remove(splash)

def draw_weather():
    if is_raining:
        for particle in rain_particles:
            p_world_x = int((particle[0] / camera_scale) + camera_x)
            p_world_y = int((particle[1] / camera_scale) + camera_y)
            grid_x = (p_world_x // BLOCK_SIZE) * BLOCK_SIZE
            grid_y = (p_world_y // BLOCK_SIZE) * BLOCK_SIZE
            has_roof = is_rain_covered(grid_x, grid_y)
            if has_roof:
                continue
                
            if particle[3]: 
                pg.draw.circle(screen, (240, 245, 255), (int(particle[0]), int(particle[1])), int(2 * camera_scale))
            else: 
                pg.draw.line(screen, (100, 150, 255), (particle[0], particle[1]), (particle[0] - 2, particle[1] + 8), 1)
                
        for splash in splash_particles:
            pg.draw.circle(screen, (120, 160, 255), (int(splash[0]), int(splash[1])), 1)


def get_sky_color(world_y, overworld_color):
    """Повертає колір неба з висотним градієнтом для Раю."""
    if world_y < -2000 * BLOCK_SIZE:
        return (25, 10, 35)
    if world_y < HEAVEN_BOTTOM * BLOCK_SIZE:
        # Внизу Раю колір теплий, а на великій висоті переходить у блакитний.
        height_ratio = 1.0 - max(0.0, min(1.0, world_y / (HEAVEN_BOTTOM * BLOCK_SIZE)))
        low = (255, 245, 200)
        high = (145, 205, 255)
        return tuple(int(low[i] + (high[i] - low[i]) * height_ratio) for i in range(3))
    if world_y < OVERWORLD_HEIGHT * BLOCK_SIZE:
        return overworld_color
    # Світліший, але все ще червонуватий фон Аду.
    return (78, 24, 24)

# =====================================
# Інвентар та Слоти
# =====================================

creative_inventory = [None for _ in range(CREATIVE_ROWS * CREATIVE_COLS)]
for idx, img_path in enumerate(ALL_ITEMS):
    if idx < len(creative_inventory):
        creative_inventory[idx] = {"texture": img_path, "count": MAX_STACK_SIZE}

crafting_grid = [None, None, None, None]
workbench_grid = [None for _ in range(9)]
furnace_grid = [None, None, None]
furnace_cook_time = 0
FURNACE_COOK_DURATION = 120

chests_data = {}  
active_chest_pos = None  

selected_block = 0
selected_inventory_slot = None
left_hand_slot = None  

solid_placed_blocks = set()

# =====================================
# Стани гри
# =====================================

MENU = 0
GAME = 1
WORKBENCH = 2
FURNACE = 3
PAUSE = 4
CODES_MENU = 5
FISHING_GAME = 6
CHEST_MENU = 7  
RECIPES_MENU = 8 

state = MENU

code_input_text = ""
code_feedback_text = ""
code_feedback_timer = 0
code_potato_used = False

font = pg.font.SysFont("arial", 20)

ALL_RECIPES = [
    {"result": "planks.png", "count": 4, "grid": ["wood.png", None, None, None]},
    {"result": "stick.png", "count": 4, "grid": ["planks.png", None, "planks.png", None]},
    {"result": "bucket.png", "count": 1, "grid": ["iron_ingot.png", None, "iron_ingot.png", None, "iron_ingot.png", None, None, None, None], "is_3x3": True},
    {"result": "crafting_table.png", "count": 1, "grid": ["planks.png", "planks.png", "planks.png", "planks.png"]},
    {"result": "torch.png", "count": 4, "grid": ["coal.png", None, "stick.png", None]},
    {"result": "wool.png", "count": 1, "grid": ["string.png", "string.png", "string.png", "string.png"]},
    {"result": "chest.png", "count": 1, "grid": ["planks.png", "planks.png", "planks.png", "planks.png", None, "planks.png", "planks.png", "planks.png", "planks.png"], "is_3x3": True},
    {"result": "furnace.png", "count": 1, "grid": ["cobblestone.png", "cobblestone.png", "cobblestone.png", "cobblestone.png", None, "cobblestone.png", "cobblestone.png", "cobblestone.png", "cobblestone.png"], "is_3x3": True},
    {"result": "bed.png", "count": 1, "grid": [None, None, None, "wool.png", "wool.png", "wool.png", "planks.png", "planks.png", "planks.png"], "is_3x3": True},
    {"result": "sushi.png", "count": 1, "grid": ["rice.png", "fish.png", None, None]},
    {"result": "gold_block.png", "count": 1, "grid": ["gold_ingot.png"] * 9, "is_3x3": True},
    {"result": "gold_ingot.png", "count": 9, "grid": ["gold_block.png", None, None, None]},
    {"result": "iron_block.png", "count": 1, "grid": ["iron_ingot.png"] * 9, "is_3x3": True},
    {"result": "iron_ingot.png", "count": 9, "grid": ["iron_block.png", None, None, None]},
    {"result": "diamond_block.png", "count": 1, "grid": ["diamond.png"] * 9, "is_3x3": True},
    {"result": "diamond.png", "count": 9, "grid": ["diamond_block.png", None, None, None]},
    {"result": "netherite_block.png", "count": 1, "grid": ["netherite_ingot.png"] * 9, "is_3x3": True},
    {"result": "netherite_ingot.png", "count": 9, "grid": ["netherite_block.png", None, None, None]},
    {"result": "bread.png", "count": 1, "grid": [None, None, None, "wheat.png", "wheat.png", "wheat.png", None, None, None], "is_3x3": True},
    {"result": "door_closed.png", "count": 3, "grid": ["planks.png", "planks.png", None, "planks.png", "planks.png", None, "planks.png", "planks.png", None], "is_3x3": True},
    {"result": "fishing_rod.png", "count": 1, "grid": [None, None, "stick.png", None, "stick.png", "string.png", "stick.png", None, "string.png"], "is_3x3": True},
    {"result": "netherite_ingot.png", "count": 1, "grid": ["netherite_scrap.png", "netherite_scrap.png", "gold_ingot.png", "netherite_scrap.png", "netherite_scrap.png", "gold_ingot.png", "gold_ingot.png", "gold_ingot.png", None], "is_3x3": True},
    {"result": "heaven_ingot.png", "count": 1, "grid": ["heaven_shard.png", "heaven_shard.png", "heaven_shard.png", "heaven_shard.png", "netherite_ingot.png", "heaven_shard.png", "heaven_shard.png", "heaven_shard.png", "heaven_shard.png"], "is_3x3": True},
    {"result": "flight_emblem.png", "count": 1, "grid": ["heaven_ingot.png", None, None, None]},
    {"result": "wood_pickaxe.png", "count": 1, "grid": ["planks.png", "planks.png", "planks.png", None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "stone_pickaxe.png", "count": 1, "grid": ["cobblestone.png", "cobblestone.png", "cobblestone.png", None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "iron_pickaxe.png", "count": 1, "grid": ["iron_ingot.png", "iron_ingot.png", "iron_ingot.png", None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "gold_pickaxe.png", "count": 1, "grid": ["gold_ingot.png", "gold_ingot.png", "gold_ingot.png", None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "diamond_pickaxe.png", "count": 1, "grid": ["diamond.png", "diamond.png", "diamond.png", None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "netherite_pickaxe.png", "count": 1, "grid": ["netherite_ingot.png", "netherite_ingot.png", "netherite_ingot.png", None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "wood_shovel.png", "count": 1, "grid": [None, "planks.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "stone_shovel.png", "count": 1, "grid": [None, "cobblestone.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "iron_shovel.png", "count": 1, "grid": [None, "iron_ingot.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "gold_shovel.png", "count": 1, "grid": [None, "gold_ingot.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "diamond_shovel.png", "count": 1, "grid": [None, "diamond.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "netherite_shovel.png", "count": 1, "grid": [None, "netherite_ingot.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "wood_axe.png", "count": 1, "grid": ["planks.png", "planks.png", None, "planks.png", "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "stone_axe.png", "count": 1, "grid": ["cobblestone.png", "cobblestone.png", None, "cobblestone.png", "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "iron_axe.png", "count": 1, "grid": ["iron_ingot.png", "iron_ingot.png", None, "iron_ingot.png", "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "gold_axe.png", "count": 1, "grid": ["gold_ingot.png", "gold_ingot.png", None, "gold_ingot.png", "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "diamond_axe.png", "count": 1, "grid": ["diamond.png", "diamond.png", None, "diamond.png", "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "netherite_axe.png", "count": 1, "grid": ["netherite_ingot.png", "netherite_ingot.png", None, "netherite_ingot.png", "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "wood_hoe.png", "count": 1, "grid": ["planks.png", "planks.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "stone_hoe.png", "count": 1, "grid": ["cobblestone.png", "cobblestone.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "iron_hoe.png", "count": 1, "grid": ["iron_ingot.png", "iron_ingot.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "gold_hoe.png", "count": 1, "grid": ["gold_ingot.png", "gold_ingot.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "diamond_hoe.png", "count": 1, "grid": ["diamond.png", "diamond.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True},
    {"result": "netherite_hoe.png", "count": 1, "grid": ["netherite_ingot.png", "netherite_ingot.png", None, None, "stick.png", None, None, "stick.png", None], "is_3x3": True}
]

# =====================================
# Кеш текстур
# =====================================

texture_cache = {}

def load_texture(path, size):
    size = (int(size[0]), int(size[1]))
    key = (path, size)

    if key not in texture_cache:
        try:
            img = pg.image.load(resource_path(path)).convert_alpha()
        except pg.error:
            img = pg.Surface(size, pg.SRCALPHA)
            if path == "water.png":
                img.fill((80, 0, 200, 200)) 
            elif path == "portal.png":
                img.fill((128, 0, 128, 220))
            elif path == "potal_ad.png":
                img.fill((180, 0, 220, 210))
            elif path == "lava.png":
                img.fill((255, 69, 0, 220))  
            elif path == "netherrack.png":
                img.fill((112, 36, 36))      
            elif path == "basalt.png":
                img.fill((70, 70, 75))
            elif path == "bucket.png":
                img.fill((190, 190, 190))
                pg.draw.rect(img, (50, 50, 50), (4, 4, size[0]-8, size[1]-8), 2)
            elif path == "water_bucket.png":
                img.fill((190, 190, 190))
                pg.draw.rect(img, (0, 100, 255), (4, 4, size[0]-8, size[1]-8))
            elif path == "lava_bucket.png":
                img.fill((190, 190, 190))
                pg.draw.rect(img, (255, 80, 0), (4, 4, size[0]-8, size[1]-8))
            elif path == "coal_ore.png":
                img.fill((40, 40, 40))
            elif path == "iron_ore.png":
                img.fill((180, 130, 90))
            elif path == "gold_ore.png":
                img.fill((230, 190, 70))     
            elif path == "diamond_ore.png":
                img.fill((0, 255, 255))      
            elif path == "netherite_ore.png":
                img.fill((50, 30, 30))       
            elif path == "cloud_ore.png":
                img.fill((200, 220, 255))    
            elif path == "coal.png":
                img.fill((20, 20, 20))
            elif path == "iron_ingot.png":
                img.fill((220, 220, 220))
            elif path == "gold_ingot.png":
                img.fill((255, 215, 0))      
            elif path == "diamond.png":
                img.fill((100, 240, 255))
            elif path == "netherite_scrap.png":
                img.fill((120, 80, 70))
            elif path == "netherite_ingot.png":
                img.fill((60, 50, 55))
            elif path == "torch.png":
                img.fill((255, 200, 50))
            elif path == "dried_kelp.png":
                img.fill((34, 139, 34))
            elif path == "nether_gold_ore.png":
                img.fill((150, 70, 70))  
            elif path == "gold_block.png":
                img.fill((230, 175, 0))  
            elif path == "iron_block.png":
                img.fill((200, 200, 200))
            elif path == "diamond_block.png":
                img.fill((80, 220, 255))
            elif path == "netherite_block.png":
                img.fill((40, 35, 40))
            elif path == "heaven_shard.png":
                img.fill((230, 250, 255))
            elif path == "heaven_ingot.png":
                img.fill((180, 240, 255))
            elif path == "flight_emblem.png":
                img.fill((255, 215, 0))
            elif path == "fishing_rod.png":
                img.fill((139, 69, 19))
            elif path == "fish.png":
                img.fill((70, 130, 180))
            elif path == "cooked_fish.png":
                img.fill((210, 140, 90))
            elif path == "rice.png":
                img.fill((240, 240, 230))
            elif path == "sushi.png":
                img.fill((255, 100, 100))
            elif path == "door_closed.png":
                img.fill((150, 100, 50))
            elif path == "door_open.png":
                img.fill((150, 100, 50, 100))
            elif path == "string.png":
                img.fill((240, 240, 240))
            elif path == "cactus.png":
                img.fill((34, 139, 34))
            elif path == "chest.png":
                img.fill((139, 89, 39))  
            elif path == "heaven_cloud.png":
                img.fill((255, 255, 255, 160))  
            elif path == "snow_grass.png":
                img.fill((220, 240, 255))
            elif path == "end_stone.png":
                img.fill((238, 232, 170))
            elif path == "obsidian.png":
                img.fill((25, 15, 40))
            elif path == "end_crystal.png":
                img.fill((255, 105, 180))
            elif path == "ender_pearl.png":
                img.fill((0, 128, 128))
            elif path == "dragon_egg.png":
                img.fill((180, 20, 20))
            elif path == "bed.png":
                img.fill((220, 50, 50))
            elif path == "wool.png":
                img.fill((240, 240, 240))
            elif path == "portal_frame.png":
                img.fill((0, 0, 50))
                pg.draw.rect(img, (0, 255, 150), (4, 4, size[0]-8, size[1]-8), 2)
            elif path == "dragon_fly1.png":
                img.fill((15, 10, 20))
                pg.draw.rect(img, (148, 0, 211), (5, 5, size[0]-10, 15))
            elif path == "dragon_fly2.png":
                img.fill((15, 10, 20))
                pg.draw.rect(img, (148, 0, 211), (5, size[1]-20, size[0]-10, 15))
            else:
                img.fill((200, 100, 100))
        img = pg.transform.scale(img, size)
        texture_cache[key] = img

    return texture_cache[key]

def draw_cracks(surface, rect, progress):
    if progress <= 0:
        return

    stage = int(progress * 5)
    if stage == 0:
        return

    crack_surf = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
    cx, cy = rect.width // 2, rect.height // 2

    points = [
        (cx, cy),
        (cx - 12, cy - 10), (cx + 10, cy - 12),
        (cx - 8, cy + 14), (cx + 14, cy + 8),
        (cx - 18, cy - 4), (cx + 18, cy + 6),
        (cx - 5, cy - 20), (cx + 6, cy + 20)
    ]

    color = (0, 0, 0, 200)
    thickness = 2 if rect.width > 30 else 1

    lines_to_draw = stage * 2
    for i in range(1, min(lines_to_draw + 1, len(points))):
        pg.draw.line(crack_surf, color, points[0], points[i], thickness)
        if stage >= 3 and i > 2:
            p_branch = (points[i][0] + (5 if i % 2 == 0 else -5), points[i][1] + (5 if i % 3 == 0 else -5))
            pg.draw.line(crack_surf, color, points[i], p_branch, thickness - 1)

    surface.blit(crack_surf, rect.topleft)

# =====================================
# Клас блока
# =====================================

class Block:
    # У світі можуть бути мільйони блоків. __slots__ прибирає окремий
    # словник атрибутів з кожного звичайного блока й суттєво зменшує RAM.
    __slots__ = ("rect", "color", "texture", "mining_progress", "light_level")

    def __init__(self, x, y, w, h, color, img):
        if img == "bed.png":
            w, h = 100, 50
        self.rect = pg.Rect(x, y, w, h)
        self.color = color
        self.texture = img
        self.mining_progress = 0.0
        self.light_level = 0.0  

    def draw(self, screen, camera_x, camera_y):
        scaled_w = int(self.rect.w * camera_scale)
        scaled_h = int(self.rect.h * camera_scale)

        draw_x = int((self.rect.x - camera_x) * camera_scale)
        draw_y = int((self.rect.y - camera_y) * camera_scale)

        if (
            draw_x + scaled_w < 0 or
            draw_x > WIDTH or
            draw_y + scaled_h < 0 or
            draw_y > HEIGHT
        ):
            return

        image = load_texture(self.texture, (scaled_w, scaled_h))
        screen.blit(image, (draw_x, draw_y))

        ignoring_light_blocks = [
            "tall_grass.png", "water.png", "lava.png", "wheat_stage0.png", "wheat_stage1.png",
            "wheat_stage2.png", "wheat_stage3.png", "potato_stage0.png", "potato_stage1.png",
            "potato_stage2.png", "potato_stage3.png", "rice_stage0.png", "rice_stage1.png", "kelp_stage0.png", "kelp_stage1.png",
            "kelp_stage2.png", "kelp_stage3.png", "torch.png", "wood.png", "leaves.png", "cactus.png", "heaven_cloud.png", "door_open.png",
            "end_crystal.png", "portal.png", "potal_ad.png"
        ]

        # В Аду немає печерної темряви: блоки не накладають чорну тінь.
        if self.texture not in ignoring_light_blocks and self.rect.y < OVERWORLD_HEIGHT * BLOCK_SIZE:
            def is_solid(cx, cy):
                b = blocks_map.get((cx, cy))
                return b is not None and b.texture not in ignoring_light_blocks

            max_check_distance = 4

            up_steps = 0
            check_y = self.rect.y - BLOCK_SIZE
            while up_steps < max_check_distance and check_y >= 0:
                if is_solid(self.rect.x, check_y):
                    up_steps += 1
                else:
                    break
                check_y -= BLOCK_SIZE

            down_steps = 0
            check_y = self.rect.y + BLOCK_SIZE
            while down_steps < max_check_distance and check_y < WORLD_HEIGHT * BLOCK_SIZE:
                if is_solid(self.rect.x, check_y):
                    down_steps += 1
                else:
                    break
                check_y += BLOCK_SIZE

            left_steps = 0
            check_x = self.rect.x - BLOCK_SIZE
            while left_steps < max_check_distance and check_x >= 0:
                if is_solid(check_x, self.rect.y):
                    left_steps += 1
                else:
                    break
                check_x -= BLOCK_SIZE

            right_steps = 0
            check_x = self.rect.x + BLOCK_SIZE
            while right_steps < max_check_distance and check_x < WORLD_WIDTH * BLOCK_SIZE:
                if is_solid(check_x, self.rect.y):
                    right_steps += 1
                else:
                    break
                check_x += BLOCK_SIZE

            min_steps_to_light = min(up_steps, down_steps, left_steps, right_steps)

            if min_steps_to_light >= 1:
                shadow_surf = pg.Surface((scaled_w, scaled_h), pg.SRCALPHA)
                if min_steps_to_light == 1:
                    shadow_surf.fill((0, 0, 0, 80))
                elif min_steps_to_light == 2:
                    shadow_surf.fill((0, 0, 0, 160))
                else:
                    shadow_surf.fill((0, 0, 0, 245))
                screen.blit(shadow_surf, (draw_x, draw_y))

        if self.mining_progress > 0:
            draw_cracks(screen, pg.Rect(draw_x, draw_y, scaled_w, scaled_h), self.mining_progress)

class SandBlock(Block):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, (244, 164, 96), "sand.png")

class WheatBlock(Block):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "wheat_stage0.png")
        self.age = 0.0
        self.stage = 0

    def update_growth(self, dt):
        if self.stage < 3:
            self.age += dt
            new_stage = min(3, int(self.age / 100))
            if new_stage != self.stage:
                self.stage = new_stage
                self.texture = f"wheat_stage{self.stage}.png"

class PotatoBlock(Block):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "potato_stage0.png")
        self.age = 0.0
        self.stage = 0

    def update_growth(self, dt):
        if self.stage < 3:
            self.age += dt
            new_stage = min(3, int(self.age / 100))
            if new_stage != self.stage:
                self.stage = new_stage
                self.texture = f"potato_stage{self.stage}.png"

class RiceBlock(Block):
    def __init__(self, x, y):
        super().__init__(x, y - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE * 2, (255, 255, 255), "rice_stage0.png")
        self.age = 0.0
        self.stage = 0

    def update_growth(self, dt):
        if self.stage < 1:
            self.age += dt
            if self.age > 80:  
                self.stage = 1
                self.texture = "rice_stage1.png"
                below_x = self.rect.x
                below_y = self.rect.y + BLOCK_SIZE
                below_b = get_block_at(below_x, below_y)
                if below_b is None or below_b.texture != "water.png":
                    if below_b:
                        remove_block(below_b)
                    add_block(Block(below_x, below_y, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "water.png"))

class KelpBlock(Block):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "kelp_stage0.png")
        self.age = 0.0
        self.stage = 0

    def update_growth(self, dt):
        if self.stage < 3:
            self.age += dt
            new_stage = min(3, int(self.age / 50))
            if new_stage != self.stage:
                self.stage = new_stage
                self.texture = f"kelp_stage{self.stage}.png"

    def draw(self, screen, camera_x, camera_y):
        scaled_w = int(self.rect.w * camera_scale)
        scaled_h = int(self.rect.h * camera_scale)

        draw_x = int((self.rect.x - camera_x) * camera_scale)
        draw_y = int((self.rect.y - camera_y) * camera_scale)

        if (
            draw_x + scaled_w < 0 or
            draw_x > WIDTH or
            draw_y + scaled_h < 0 or
            draw_y > HEIGHT
        ):
            return

        water_image = load_texture("water.png", (scaled_w, scaled_h))
        screen.blit(water_image, (draw_x, draw_y))

        image = load_texture(self.texture, (scaled_w, scaled_h))
        screen.blit(image, (draw_x, draw_y))

        if self.mining_progress > 0:
            draw_cracks(screen, pg.Rect(draw_x, draw_y, scaled_w, scaled_h), self.mining_progress)

liquid_update_cooldown = 0
def update_liquids():
    global liquid_update_cooldown
    liquid_update_cooldown += 1
    if liquid_update_cooldown < 25:  
        return
    liquid_update_cooldown = 0

    current_start_gx = int(camera_x // BLOCK_SIZE) - 2
    current_end_gx = int((camera_x + WIDTH / camera_scale) // BLOCK_SIZE) + 2
    current_start_gy = int(camera_y // BLOCK_SIZE) - 2
    current_end_gy = int((camera_y + HEIGHT / camera_scale) // BLOCK_SIZE) + 2

    visible_liquids = []
    for gx in range(max(0, current_start_gx), min(WORLD_WIDTH, current_end_gx)):
        for gy in range(max(0, current_start_gy), min(WORLD_HEIGHT, current_end_gy)):
            b = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
            if b and b.texture in ["water.png", "lava.png"]:
                visible_liquids.append(b)

    random.shuffle(visible_liquids)
    # Рідини оновлюються лише біля камери й у фіксованому бюджеті за тик;
    # це зберігає воду/лаву/обсидіан, але не дає рідині клонуватися лавиною.
    visible_liquids = visible_liquids[:24]

    for liq in visible_liquids:
        lx, ly = liq.rect.x, liq.rect.y
        down_b = blocks_map.get((lx, ly + BLOCK_SIZE))
        
        if down_b and ((liq.texture == "water.png" and down_b.texture == "lava.png") or (liq.texture == "lava.png" and down_b.texture == "water.png")):
            remove_block(down_b)
            add_block(Block(lx, ly + BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255,255,255), "obsidian.png"))
            solid_placed_blocks.add((lx, ly + BLOCK_SIZE))
            continue
            
        if ly + BLOCK_SIZE < WORLD_HEIGHT * BLOCK_SIZE and down_b is None:
            add_block(Block(lx, ly + BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255,255,255), liq.texture))
            continue
        
        for dx in random.sample([-BLOCK_SIZE, BLOCK_SIZE], 2):
            side_x = lx + dx
            if 0 <= side_x < WORLD_WIDTH * BLOCK_SIZE:
                side_b = blocks_map.get((side_x, ly))
                if side_b and ((liq.texture == "water.png" and side_b.texture == "lava.png") or (liq.texture == "lava.png" and side_b.texture == "water.png")):
                    remove_block(side_b)
                    add_block(Block(side_x, ly, BLOCK_SIZE, BLOCK_SIZE, (255,255,255), "obsidian.png"))
                    solid_placed_blocks.add((side_x, ly))
                elif side_b is None:
                    add_block(Block(side_x, ly, BLOCK_SIZE, BLOCK_SIZE, (255,255,255), liq.texture))

def _place_nether_portal(min_x, min_y):
    """Створює активну рамку 4x5 і повертає її внутрішні блоки."""
    interior = []
    for x in range(min_x, min_x + 4):
        for y in range(min_y, min_y + 5):
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            old = get_block_at(*pos)
            if old:
                remove_block(old)
            border = x in (min_x, min_x + 3) or y in (min_y, min_y + 4)
            add_block(Block(*pos, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "obsidian.png" if border else "potal_ad.png"))
            if border:
                portal_frame_positions.add(pos)
            else:
                interior.append(pos)
    return interior

def _create_nether_partner():
    """Гарантує випадкову простору печеру навколо вихідного порталу."""
    min_x = random.randint(20, WORLD_WIDTH - 24)
    min_y = random.randint(OVERWORLD_HEIGHT + 25, WORLD_HEIGHT - 25)
    for x in range(min_x - 8, min_x + 12):
        for y in range(min_y - 7, min_y + 10):
            old = get_block_at(x * BLOCK_SIZE, y * BLOCK_SIZE)
            if old:
                remove_block(old)
    for x in range(min_x - 8, min_x + 12):
        add_block(Block(x * BLOCK_SIZE, (min_y + 9) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "netherrack.png"))
    return _place_nether_portal(min_x, min_y)

def try_activate_nether_portal(start_x, start_y):
    # ВИПРАВЛЕНО: Гнучка перевірка рамки з обсидіану 4x5
    for min_x in range(start_x - 3, start_x + 1):
        for min_y in range(start_y - 4, start_y + 1):
            frame_valid = True
            for x in range(min_x, min_x + 4):
                for y in range(min_y, min_y + 5):
                    is_border = (x == min_x or x == min_x + 3 or y == min_y or y == min_y + 4)
                    b = get_block_at(x * BLOCK_SIZE, y * BLOCK_SIZE)
                    if is_border:
                        if not b or b.texture != "obsidian.png":
                            frame_valid = False
                            break
                    else:
                        if b and b.texture not in ["tall_grass.png", "water.png", "lava.png", "torch.png"]:
                            frame_valid = False
                            break
                if not frame_valid: break
            
            if frame_valid:
                # Активація порталу всередині 2x3
                source = _place_nether_portal(min_x, min_y)
                target = _create_nether_partner()
                source_spawn = (source[0][0], source[0][1] - BLOCK_SIZE)
                target_spawn = (target[0][0], target[0][1] - BLOCK_SIZE)
                for pos in source:
                    nether_portal_pairs[pos] = target_spawn
                for pos in target:
                    nether_portal_pairs[pos] = source_spawn
                return True
    return False

def update_portal_teleport(dt):
    """Портал спрацьовує тільки після трьох секунд безперервного перебування."""
    global portal_charge, portal_cooldown
    portal_cooldown = max(0.0, portal_cooldown - dt)
    gx, gy = player.rect.centerx // BLOCK_SIZE, player.rect.centery // BLOCK_SIZE
    here = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
    end_x, end_y = portal_structure_pos[0] // BLOCK_SIZE, portal_structure_pos[1] // BLOCK_SIZE
    in_end_portal = portal_structure_pos != (0, 0) and end_x - 2 <= gx <= end_x + 2 and player.rect.bottom // BLOCK_SIZE == end_y + 2
    destination = nether_portal_pairs.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE)) if here and here.texture == "potal_ad.png" else None
    if portal_cooldown or (not in_end_portal and destination is None):
        portal_charge = 0.0
        return
    portal_charge += dt
    if portal_charge < PORTAL_WARMUP_SECONDS:
        return
    if in_end_portal:
        # Виправлено: портал Краю веде до Краю, а не на спавн Верхнього світу.
        player.rect.x, player.rect.y = 100 * BLOCK_SIZE, -2035 * BLOCK_SIZE
    else:
        player.rect.x, player.rect.y = destination
    player.vel_y = 0
    player.inAir = True
    portal_charge = 0.0
    portal_cooldown = 2.0

# =====================================
# Механіки Енду та Ендер Дракона
# =====================================
class DragonFireball:
    def __init__(self, x, y, tx, ty):
        self.rect = pg.Rect(x, y, 30, 30)
        dx = tx - x
        dy = ty - y
        dist = math.hypot(dx, dy)
        self.vx = (dx / dist) * 7 if dist > 0 else 0
        self.vy = (dy / dist) * 7 if dist > 0 else 7

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        
        if self.rect.colliderect(player.rect):
            if not is_creative:
                player.health -= 3
            return True
            
        gx = self.rect.centerx // BLOCK_SIZE
        gy = self.rect.centery // BLOCK_SIZE
        b = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
        if b and b.texture not in ["tall_grass.png", "water.png", "lava.png", "portal.png", "potal_ad.png"]:
            return True
        return False

    def draw(self, screen, camera_x, camera_y):
        dx = int((self.rect.x - camera_x) * camera_scale)
        dy = int((self.rect.y - camera_y) * camera_scale)
        if 0 <= dx <= WIDTH and 0 <= dy <= HEIGHT:
            pg.draw.circle(screen, (255, 0, 255), (dx + 15, dy + 15), int(15 * camera_scale))
            pg.draw.circle(screen, (255, 200, 255), (dx + 15, dy + 15), int(7 * camera_scale))

dragon_fireballs = []
endermen = []
enderman_spawn_timer = 0.0


class Enderman:
    """Легкий моб: активний тільки поряд із гравцем, тому не додає лагів."""
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 40, BLOCK_SIZE * 3)
        self.speed = random.choice([-1, 1])
        self.attack_cooldown = 0.0
        self.teleport_cooldown = random.uniform(1.5, 4.0)
        self.walk_frame = random.randint(0, 2)
        self.animation_timer = 0.0

    def update(self, dt):
        distance = math.hypot(self.rect.centerx - player.rect.centerx,
                              self.rect.centery - player.rect.centery)
        if distance > BLOCK_SIZE * 28:
            return True

        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.animation_timer += dt
        if self.animation_timer >= 0.16:
            self.walk_frame = (self.walk_frame + 1) % 3
            self.animation_timer = 0.0
        self.teleport_cooldown -= dt
        if distance > BLOCK_SIZE * 3:
            self.rect.x += int(self.speed * 1.2)
        elif self.attack_cooldown <= 0.0 and self.rect.colliderect(player.rect):
            if not is_creative:
                player.health -= 2
            self.attack_cooldown = 1.25

        # Рідкісний короткий телепорт не потребує пошуку блоків у всьому світі.
        if self.teleport_cooldown <= 0.0:
            self.rect.x += random.choice([-1, 1]) * random.randint(2, 5) * BLOCK_SIZE
            self.teleport_cooldown = random.uniform(2.0, 5.0)
        return False

    def draw(self, screen, camera_x, camera_y):
        x = int((self.rect.x - camera_x) * camera_scale)
        y = int((self.rect.y - camera_y) * camera_scale)
        w = max(1, int(self.rect.w * camera_scale))
        h = max(1, int(self.rect.h * camera_scale))
        if x + w < 0 or x > WIDTH or y + h < 0 or y > HEIGHT:
            return
        texture_name = f"enderman_walk{self.walk_frame + 1}.png"
        if os.path.exists(resource_path(texture_name)):
            screen.blit(load_texture(texture_name, (w, h)), (x, y))
        else:
            # Запасний вигляд, поки три PNG ще не покладені поруч із грою.
            pg.draw.rect(screen, (18, 14, 25), (x, y, w, h), border_radius=max(1, w // 6))
            eye_y = y + h // 3
            pg.draw.rect(screen, (225, 80, 255), (x + w // 5, eye_y, max(1, w // 5), max(1, h // 15)))
            pg.draw.rect(screen, (225, 80, 255), (x + w * 3 // 5, eye_y, max(1, w // 5), max(1, h // 15)))


def update_endermen(dt):
    """Спавнить максимум трьох ендерменів у Краю та викривленому лісі."""
    global enderman_spawn_timer
    in_end = player.rect.y < -2000 * BLOCK_SIZE
    in_warped_forest = (4600 <= player.rect.centerx // BLOCK_SIZE <= 4780 and
                        player.rect.y >= OVERWORLD_HEIGHT * BLOCK_SIZE)
    if not (in_end or in_warped_forest):
        endermen.clear()
        return

    enderman_spawn_timer += dt
    if enderman_spawn_timer >= 3.0 and len(endermen) < 3:
        enderman_spawn_timer = 0.0
        side = random.choice([-1, 1])
        spawn_x = player.rect.x + side * random.randint(5, 10) * BLOCK_SIZE
        spawn_y = player.rect.bottom - BLOCK_SIZE * 3
        endermen.append(Enderman(spawn_x, spawn_y))

    for mob in endermen[:]:
        if mob.update(dt):
            endermen.remove(mob)

class EnderDragon:
    def __init__(self):
        self.rect = pg.Rect(150 * BLOCK_SIZE, -2060 * BLOCK_SIZE, 900, 450)
        self.max_health = 200
        self.health = self.max_health
        self.speed = 8 
        self.angle = 0
        self.active = False
        self.target_x = 100 * BLOCK_SIZE
        self.target_y = -2050 * BLOCK_SIZE
        self.attack_timer = 0
        self.anim_frame = 0
        self.anim_timer = 0
        self.facing_right = False
        self.shoot_cooldown = 0
        self.hit_cooldown = 0

    def update(self):
        if player.rect.y < -2000 * BLOCK_SIZE and not self.active and self.health > 0:
            self.active = True

        if not self.active or player.rect.y > -2000 * BLOCK_SIZE:
            return

        self.anim_timer += 1
        if self.anim_timer >= 15: 
            self.anim_frame = 1 if self.anim_frame == 0 else 0
            self.anim_timer = 0

        crystals = [b for b in blocks_map.values() if b.texture == "end_crystal.png"]
        for c in crystals:
            dist = math.hypot(c.rect.x - self.rect.centerx, c.rect.y - self.rect.centery)
            if dist < 1200:
                self.health = min(self.max_health, self.health + 0.1)
                self.crystal_link = (c.rect.centerx, c.rect.centery)

        self.attack_timer += 1
        if self.attack_timer > 200:
            # Наліт прямо на гравця
            self.target_x = player.rect.centerx - 450
            self.target_y = player.rect.centery - 225
            if self.attack_timer > 320:
                self.attack_timer = 0
        else:
            self.angle += 0.02
            self.target_x = (100 * BLOCK_SIZE) + math.sin(self.angle) * 1000 - 450
            self.target_y = (-2060 * BLOCK_SIZE) + math.cos(self.angle) * 400 - 225

        dx = self.target_x - self.rect.x
        dy = self.target_y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist > 5:
            vx = (dx / dist) * self.speed
            self.rect.x += int(vx)
            self.rect.y += int((dy / dist) * self.speed)
            
            # Розвертаємо дракона
            if vx > 0:
                self.facing_right = False
            elif vx < 0:
                self.facing_right = True

        # Механіка атаки налітом (фізичне зіткнення з гравцем)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        if self.rect.colliderect(player.rect) and self.hit_cooldown <= 0:
            if not is_creative:
                player.health -= 4
                # Відштовхування гравця при таранній атаці
                player.vel_y = -8
                player.rect.x += 20 if self.facing_right else -20
            self.hit_cooldown = 60

        # Стрільба фаєрболами
        self.shoot_cooldown += 1
        if self.shoot_cooldown > 90:
            self.shoot_cooldown = 0
            dragon_fireballs.append(DragonFireball(self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))

    def draw(self, screen, camera_x, camera_y):
        if not self.active or player.rect.y > -2000 * BLOCK_SIZE:
            return
        draw_x = int((self.rect.x - camera_x) * camera_scale)
        draw_y = int((self.rect.y - camera_y) * camera_scale)
        
        if draw_x + self.rect.w < 0 or draw_x > WIDTH or draw_y + self.rect.h < 0 or draw_y > HEIGHT:
            pass
        else:
            texture_name = "dragon_fly1.png" if self.anim_frame == 0 else "dragon_fly2.png"
            image = load_texture(texture_name, (int(self.rect.w * camera_scale), int(self.rect.h * camera_scale)))
            
            if not self.facing_right:
                image = pg.transform.flip(image, True, False)
                
            screen.blit(image, (draw_x, draw_y))
        
        bar_w = 300
        bar_h = 15
        bx = WIDTH // 2 - bar_w // 2
        by = 50
        pg.draw.rect(screen, (50, 0, 50), (bx, by, bar_w, bar_h))
        curr_w = int(bar_w * (self.health / self.max_health))
        pg.draw.rect(screen, (148, 0, 211), (bx, by, curr_w, bar_h))
        pg.draw.rect(screen, (255, 255, 255), (bx, by, bar_w, bar_h), 2)
        txt = font.render("ENDER DRAGON", True, (255, 255, 255))
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, by - 22))

dragon = EnderDragon()

class DroppedItem:
    def __init__(self, x, y, texture, count=1, vel_x=0.0, vel_y=0.0):
        self.rect = pg.Rect(x, y, 26, 26)
        self.texture = texture
        self.count = count
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.pickup_delay = 25

    def update(self):
        self.vel_y += 0.35
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        self.vel_x *= 0.9

        start_gx = (self.rect.x // BLOCK_SIZE) - 1
        end_gx = ((self.rect.x + self.rect.w) // BLOCK_SIZE) + 1
        start_gy = (self.rect.y // BLOCK_SIZE) - 1
        end_gy = ((self.rect.h + self.rect.y) // BLOCK_SIZE) + 1

        for gx in range(start_gx, end_gx + 1):
            for gy in range(start_gy, end_gy + 1):
                block = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
                if block:
                    if block.texture in [
                        "tall_grass.png", "water.png", "lava.png", "wheat_stage0.png", "wheat_stage1.png",
                        "wheat_stage2.png", "wheat_stage3.png", "potato_stage0.png", "potato_stage1.png",
                        "potato_stage2.png", "potato_stage3.png", "rice_stage0.png", "rice_stage1.png", "kelp_stage0.png", "kelp_stage1.png",
                        "kelp_stage2.png", "kelp_stage3.png", "torch.png", "door_open.png", "portal.png", "potal_ad.png"
                    ]:
                        continue
                    if (block.texture in ["wood.png", "leaves.png", "cactus.png", "obsidian.png"]) and ((block.rect.x, block.rect.y) not in solid_placed_blocks):
                        continue
                    if self.rect.colliderect(block.rect) and self.vel_y > 0:
                        self.rect.bottom = block.rect.top
                        self.vel_y = 0

        if self.pickup_delay > 0:
            self.pickup_delay -= 1
            return False
        if math.hypot(self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery) < 55:
            if is_creative:
                return True
            return add_to_inventory(self.texture, self.count)
        return False

    def draw(self, screen, camera_x, camera_y):
        scaled_w = int(self.rect.w * camera_scale)
        scaled_h = int(self.rect.h * camera_scale)
        draw_x = int((self.rect.x - camera_x) * camera_scale)
        draw_y = int((self.rect.y - camera_y) * camera_scale)

        if draw_x + scaled_w < 0 or draw_x > WIDTH or draw_y + scaled_h < 0 or draw_y > HEIGHT:
            return

        image = load_texture(self.texture, (scaled_w, scaled_h))
        screen.blit(image, (draw_x, draw_y))

        if self.count > 1:
            count_txt = font.render(str(self.count), True, (255, 255, 255))
            screen.blit(count_txt, (draw_x + scaled_w - 5, draw_y + scaled_h - 10))

class Fish:
    def __init__(self, x, y):
        self.rect = pg.Rect(x, y, 32, 20)
        self.vel_x = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
        self.base_y = y
        self.anim_offset = random.uniform(0, 10)
        self.ai_timer = 0

    def update(self):
        dist_to_player = math.hypot(self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery)
        
        if dist_to_player < 120:  
            if player.rect.centerx > self.rect.centerx:
                self.vel_x = -3.5  
            else:
                self.vel_x = 3.5   
        else:
            self.ai_timer += 1
            if self.ai_timer > random.randint(100, 250):
                self.vel_x = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
                self.ai_timer = 0

        next_x = self.rect.x + self.vel_x
        block_here = get_block_at(int(next_x // BLOCK_SIZE) * BLOCK_SIZE, int(self.rect.centery // BLOCK_SIZE) * BLOCK_SIZE)
        
        if block_here and (block_here.texture == "water.png" or isinstance(block_here, (KelpBlock, RiceBlock))):
            self.rect.x = next_x
        else:
            self.vel_x *= -1  

        self.rect.y = self.base_y + int(math.sin(pg.time.get_ticks() * 0.005 + self.anim_offset) * 8)
        
        if self.rect.x < 1850 * BLOCK_SIZE:
            self.rect.x = 1850 * BLOCK_SIZE
            self.vel_x *= -1
        if self.rect.x > 2150 * BLOCK_SIZE:
            self.rect.x = 2150 * BLOCK_SIZE
            self.vel_x *= -1

    def draw(self, screen, camera_x, camera_y):
        scaled_w = int(self.rect.w * camera_scale)
        scaled_h = int(self.rect.h * camera_scale)
        draw_x = int((self.rect.x - camera_x) * camera_scale)
        draw_y = int((self.rect.y - camera_y) * camera_scale)
        
        if 0 <= draw_x <= WIDTH and 0 <= draw_y <= HEIGHT:
            image = load_texture("fish.png", (scaled_w, scaled_h))
            if self.vel_x > 0:
                image = pg.transform.flip(image, True, False)
            screen.blit(image, (draw_x, draw_y))

class Player:
    def __init__(self, x, y, w, h, color):
        self.rect = pg.Rect(x, y, w, h)
        self.speed = 5
        self.gravity = 0.7
        self.jump_power = -14

        self.vel_y = 0
        self.inAir = True
        self.in_water = False
        self.in_lava = False  

        self.max_health = 20
        self.health = self.max_health
        self.highest_y = y

        self.max_hunger = 20
        self.hunger = self.max_hunger
        self.hunger_tick_timer = 0.0
        self.starvation_timer = 0.0
        self.regeneration_timer = 0.0
        self.lava_damage_timer = 0.0  
        self.cactus_damage_timer = 0.0

        self.direction = 1
        self.frame = 0

        self.anim_frames = [f"{i}.png" for i in range(1, 6)]
        self.idle_frame = "6.png"
        self.jump_frame = "7.png"

        self.current_frame_name = self.idle_frame

    def has_flight_emblem(self):
        for stack in hotbar:
            if stack and stack["texture"] == "flight_emblem.png": return True
        for stack in inventory:
            if stack and stack["texture"] == "flight_emblem.png": return True
        return False

    def collide(self, other):
        if (other.rect.x, other.rect.y) in portal_frame_positions:
            return False
        if other.texture in [
            "tall_grass.png", "water.png", "lava.png",
            "wheat_stage0.png", "wheat_stage1.png", "wheat_stage2.png", "wheat_stage3.png",
            "potato_stage0.png", "potato_stage1.png", "potato_stage2.png", "potato_stage3.png",
            "rice_stage0.png", "rice_stage1.png", "kelp_stage0.png", "kelp_stage1.png", "kelp_stage2.png", "kelp_stage3.png", 
            "torch.png", "door_open.png", "crafting_table.png", "furnace.png", "chest.png", "bed.png", "end_crystal.png", "portal.png", "potal_ad.png"
        ]:
            return False
        # Усі природні дерева, включно з пальмами й викривленими, прохідні.
        if other.texture in [
            "wood.png", "leaves.png", "birch_wood.png", "birch_leaves.png",
            "warped_wood.png", "warped_leaves.png", "palm_wood.png",
            "palm_leaves.png", "cactus.png"
        ]:
            return False
        if other.texture == "obsidian.png" and (other.rect.x, other.rect.y) not in solid_placed_blocks:
            return False
        return self.rect.colliderect(other.rect)

    def check_liquids(self):
        self.in_water = False
        self.in_lava = False
        start_gx = (self.rect.x // BLOCK_SIZE)
        end_gx = ((self.rect.x + self.rect.w) // BLOCK_SIZE)
        start_gy = (self.rect.y // BLOCK_SIZE)
        end_gy = ((self.rect.y + self.rect.h) // BLOCK_SIZE)

        for gx in range(start_gx, end_gx + 1):
            for gy in range(start_gy, end_gy + 1):
                block = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
                if block:
                    if block.texture == "water.png" or isinstance(block, KelpBlock):
                        self.in_water = True
                    elif block.texture == "lava.png":
                        self.in_lava = True

    def update(self):
        global desert_sun_timer, snow_freeze_timer, temperature_damage_cooldown
        
        if self.health <= 0:
            self.health = 0
            self.die()
            return

        self.check_liquids()
        keys = pg.key.get_pressed()
        move_x = 0

        current_speed = self.speed
        if self.in_water:
            current_speed = self.speed * 0.6
        elif self.in_lava:
            current_speed = self.speed * 0.35

        can_fly = is_creative or self.has_flight_emblem()
        if can_fly:
            current_speed = self.speed * 1.5

        if keys[pg.K_a]:
            move_x -= current_speed
            self.direction = -1

        if keys[pg.K_d]:
            move_x += current_speed
            self.direction = 1

        self.rect.x += move_x

        start_gx = (self.rect.x // BLOCK_SIZE) - 1
        end_gx = ((self.rect.x + self.rect.w) // BLOCK_SIZE) + 1
        start_gy = (self.rect.y // BLOCK_SIZE) - 1
        end_gy = ((self.rect.y + self.rect.h) // BLOCK_SIZE) + 1

        self.cactus_damage_timer += 1.0 / 60.0
        for gx in range(start_gx, end_gx + 1):
            for gy in range(start_gy, end_gy + 1):
                block = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
                if block:
                    if block.texture == "cactus.png" and self.rect.colliderect(block.rect):
                        if self.cactus_damage_timer >= 0.5 and not is_creative:
                            self.health -= 1
                            self.cactus_damage_timer = 0.0
                            if self.health <= 0:
                                self.health = 0
                                self.die()
                                return
                    if self.collide(block):
                        if move_x > 0:
                            self.rect.right = block.rect.left
                        elif move_x < 0:
                            self.rect.left = block.rect.right

        if can_fly:
            if keys[pg.K_w]:
                self.rect.y -= current_speed
            if keys[pg.K_s]:
                self.rect.y += current_speed

        if self.inAir and not can_fly:
            self.current_frame_name = self.jump_frame
        elif move_x != 0 or (can_fly and (keys[pg.K_w] or keys[pg.K_s])):
            self.frame += 0.12
            if self.frame >= len(self.anim_frames):
                self.frame = 0
            self.current_frame_name = self.anim_frames[int(self.frame)]
        else:
            self.frame = 0
            self.current_frame_name = self.idle_frame

        if self.rect.y > WORLD_HEIGHT * BLOCK_SIZE:
            if can_fly:
                self.rect.y = OVERWORLD_START * BLOCK_SIZE + 50
            else:
                self.health = 0
                self.die()

        dt = 1.0 / 60.0

        if is_creative:
            self.health = self.max_health
            self.hunger = self.max_hunger
            return

        player_block_x = self.rect.centerx // BLOCK_SIZE
        player_block_y = self.rect.top // BLOCK_SIZE
        
        has_roof = False
        # Перевіряємо тільки найближчу ділянку над гравцем. Повний обхід від
        # вершини світу щокадру був зайвим і особливо гальмував у виживанні.
        for check_y in range(max(0, player_block_y - 48), player_block_y):
            b_above = blocks_map.get((player_block_x * BLOCK_SIZE, check_y * BLOCK_SIZE))
            if b_above and b_above.texture not in ["tall_grass.png", "water.png", "lava.png", "torch.png", "potal_ad.png"]:
                has_roof = True
                break
                
        has_heat_source = False
        active_item = hotbar[selected_block]
        if (active_item and active_item["texture"] == "torch.png") or (left_hand_slot and left_hand_slot["texture"] == "torch.png"):
            has_heat_source = True
        else:
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    b_check = blocks_map.get(((player_block_x + dx) * BLOCK_SIZE, (player_block_y + dy) * BLOCK_SIZE))
                    if b_check and b_check.texture == "torch.png":
                        has_heat_source = True
                        break
                if has_heat_source: break

        if 2600 <= player_block_x <= 3600 and not has_roof:
            desert_sun_timer += dt
            if desert_sun_timer > 300.0:  
                temperature_damage_cooldown += dt
                if temperature_damage_cooldown >= 1.0:
                    self.health -= 1
                    temperature_damage_cooldown = 0.0
                    if self.health <= 0:
                        self.health = 0
                        self.die()
                        return
        else:
            desert_sun_timer = max(0.0, desert_sun_timer - dt * 2) 

        if 4000 <= player_block_x <= 5000:
            if not has_heat_source:
                snow_freeze_timer += dt
                if snow_freeze_timer > 10.0:  
                    temperature_damage_cooldown += dt
                    if temperature_damage_cooldown >= 1.0:
                        self.health -= 1
                        temperature_damage_cooldown = 0.0
                        if self.health <= 0:
                            self.health = 0
                            self.die()
                            return
            else:
                snow_freeze_timer = max(0.0, snow_freeze_timer - dt * 4) 
        else:
            snow_freeze_timer = max(0.0, snow_freeze_timer - dt)

        if self.in_lava:
            self.lava_damage_timer += dt
            if self.lava_damage_timer >= 0.5:
                self.lava_damage_timer = 0.0
                self.health -= 3
                if self.health <= 0:
                    self.health = 0
                    self.die()
                    return
        else:
            self.lava_damage_timer = 0.0

        if move_x != 0:
            self.hunger_tick_timer += dt * 0.5
        else:
            self.hunger_tick_timer += dt * 0.1

        if self.hunger_tick_timer >= 120.0:
            self.hunger_tick_timer = 0.0
            if self.hunger > 0:
                self.hunger -= 1

        if self.hunger == 0:
            self.starvation_timer += dt
            if self.starvation_timer >= 2.0:
                self.starvation_timer = 0.0
                self.health -= 1
                if self.health <= 0:
                    self.health = 0
                    self.die()
                    return
        else:
            self.starvation_timer = 0.0

        if self.hunger >= 18 and self.health < self.max_health:
            self.regeneration_timer += dt
            if self.regeneration_timer >= 4.0:
                self.regeneration_timer = 0.0
                self.hunger -= 1
                self.health = min(self.max_health, self.health + 1)
        else:
            self.regeneration_timer = 0.0

    def jump(self):
        if is_creative or self.has_flight_emblem():
            return
        keys = pg.key.get_pressed()
        if self.in_water or self.in_lava:
            if keys[pg.K_SPACE]:
                self.vel_y = -4 if self.in_water else -2.5
                self.highest_y = self.rect.y
        else:
            if keys[pg.K_SPACE] and not self.inAir:
                self.vel_y = self.jump_power
                self.inAir = True
                self.highest_y = self.rect.y
                self.hunger_tick_timer += 0.25

    def apply_gravity(self):
        if is_creative or self.has_flight_emblem():
            self.vel_y = 0
            self.inAir = False
            return

        if not self.inAir:
            self.highest_y = self.rect.y
        else:
            if self.rect.y < self.highest_y:
                self.highest_y = self.rect.y

        if self.in_water:
            current_gravity = self.gravity * 0.2
        elif self.in_lava:
            current_gravity = self.gravity * 0.1
        else:
            current_gravity = self.gravity

        self.vel_y += current_gravity

        if self.in_water and self.vel_y > 2:
            self.vel_y = 2
        elif self.in_lava and self.vel_y > 1:
            self.vel_y = 1

        self.rect.y += self.vel_y
        self.inAir = True

        start_gx = (self.rect.x // BLOCK_SIZE) - 1
        end_gx = ((self.rect.x + self.rect.w) // BLOCK_SIZE) + 1
        start_gy = (self.rect.y // BLOCK_SIZE) - 1
        end_gy = ((self.rect.y + self.rect.h) // BLOCK_SIZE) + 1

        # Не перебираємо весь світ заради ліжка. У зоні колізії є лише
        # декілька клітин, тож перевірка має сталу складність.
        on_bed = False
        for gx in range(start_gx - 1, end_gx + 2):
            for gy in range(start_gy - 1, end_gy + 2):
                b = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
                if b and b.texture == "bed.png" and self.rect.colliderect(b.rect):
                    on_bed = True
                    break
            if on_bed:
                break

        for gx in range(start_gx, end_gx + 1):
            for gy in range(start_gy, end_gy + 1):
                block = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
                if block and self.collide(block):
                    if self.vel_y > 0:
                        self.rect.bottom = block.rect.top

                        fall_distance = (self.rect.y - self.highest_y) / BLOCK_SIZE
                        if fall_distance > 7 and not self.in_water and not self.in_lava and not on_bed:
                            damage = int((fall_distance - 7) * 2)
                            self.health -= damage
                            if self.health <= 0:
                                self.health = 0
                                self.die()
                                return

                        self.vel_y = 0
                        self.inAir = False
                    elif self.vel_y < 0:
                        self.rect.top = block.rect.bottom
                        self.vel_y = 0

        if on_bed:
            self.vel_y = 0
            self.inAir = False
            self.highest_y = self.rect.y

    def die(self):
        global inventory, hotbar, crafting_grid, workbench_grid, state, inventory_open, desert_sun_timer, snow_freeze_timer, left_hand_slot

        for i in range(len(inventory)):
            if inventory[i] is not None:
                drop_item_at_pos(inventory[i]["texture"], self.rect.centerx, self.rect.centery, count=inventory[i]["count"])
                inventory[i] = None

        for i in range(len(hotbar)):
            if hotbar[i] is not None:
                drop_item_at_pos(hotbar[i]["texture"], self.rect.centerx, self.rect.centery, count=hotbar[i]["count"])
                hotbar[i] = None

        if left_hand_slot is not None:
            drop_item_at_pos(left_hand_slot["texture"], self.rect.centerx, self.rect.centery, count=left_hand_slot["count"])
            left_hand_slot = None

        for i in range(len(crafting_grid)):
            if crafting_grid[i] is not None:
                drop_item_at_pos(crafting_grid[i]["texture"], self.rect.centerx, self.rect.centery, count=crafting_grid[i]["count"])
                crafting_grid[i] = None

        for i in range(len(workbench_grid)):
            if workbench_grid[i] is not None:
                drop_item_at_pos(workbench_grid[i]["texture"], self.rect.centerx, self.rect.centery, count=workbench_grid[i]["count"])
                workbench_grid[i] = None

        spawn_block_x = 100
        self.rect.x = spawn_block_x * BLOCK_SIZE
        
        spawn_y = OVERWORLD_START * BLOCK_SIZE + 50
        for y_coord in range(OVERWORLD_START, WORLD_HEIGHT):
            b = blocks_map.get((self.rect.x, y_coord * BLOCK_SIZE))
            if b and b.texture not in ["tall_grass.png", "water.png", "lava.png", "potal_ad.png"]:
                spawn_y = b.rect.y - self.rect.h - 10
                break
        
        self.rect.y = spawn_y
        self.vel_y = 0
        self.health = self.max_health
        self.hunger = self.max_hunger
        self.inAir = True
        self.highest_y = self.rect.y
        desert_sun_timer = 0.0
        snow_freeze_timer = 0.0

        state = GAME
        inventory_open = False

    def draw(self, screen, camera_x, camera_y):
        scaled_w = int(self.rect.w * camera_scale)
        scaled_h = int(self.rect.h * camera_scale)

        draw_x = int((self.rect.x - camera_x) * camera_scale)
        draw_y = int((self.rect.y - camera_y) * camera_scale)

        img = load_texture(self.current_frame_name, (scaled_w, scaled_h))

        if self.direction == -1:
            img = pg.transform.flip(img, True, False)

        screen.blit(img, (draw_x, draw_y))

def draw_hud():
    if is_creative:
        return

    icon_size = 24
    start_x = 15
    start_hearts_y = 15
    start_hunger_y = 44
    spacing = 4

    for i in range(10):
        heart_hp = (i + 1) * 2
        if player.health >= heart_hp:
            img = load_texture("heart_full.png", (icon_size, icon_size))
        elif player.health == heart_hp - 1:
            img = load_texture("heart_half.png", (icon_size, icon_size))
        else:
            img = load_texture("heart_empty.png", (icon_size, icon_size))
        screen.blit(img, (start_x + i * (icon_size + spacing), start_hearts_y))

    for i in range(10):
        hunger_slot_val = (i + 1) * 2
        if player.hunger >= hunger_slot_val:
            img = load_texture("hunger_full.png", (icon_size, icon_size))
        elif player.hunger == hunger_slot_val - 1:
            img = load_texture("hunger_half.png", (icon_size, icon_size))
        else:
            img = load_texture("hunger_empty.png", (icon_size, icon_size))

        screen.blit(img, (start_x + i * (icon_size + spacing), start_hunger_y))

def draw_clock():
    total_minutes = int((day_time / DAY_DURATION) * 24 * 60)
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    
    current_dimension = "OVERWORLD"
    if player.rect.y < -2000 * BLOCK_SIZE:
        current_dimension = "THE END"
    elif player.rect.y < HEAVEN_BOTTOM * BLOCK_SIZE:
        current_dimension = "HEAVEN"
    elif player.rect.y >= OVERWORLD_HEIGHT * BLOCK_SIZE:
        current_dimension = "NETHER"
        
    time_str = f"{hours:02d}:{minutes:02d} | {current_dimension}"
    clock_txt = font.render(time_str, True, (255, 255, 255))
    
    bg_rect = pg.Rect(WIDTH - 210, 15, 195, 30)
    pg.draw.rect(screen, (30, 30, 30), bg_rect, border_radius=5)
    pg.draw.rect(screen, (200, 200, 200), bg_rect, 2, border_radius=5)
    
    screen.blit(clock_txt, (bg_rect.centerx - clock_txt.get_width() // 2, bg_rect.centery - clock_txt.get_height() // 2))

# =====================================
# Управління блоками
# =====================================

class CompactBlockMap(dict):
    """Мапа блоків з компактними цілими ключами замість мільйонів tuple."""
    __slots__ = ()

    @staticmethod
    def _pack(key):
        x, y = key
        return ((x // BLOCK_SIZE) << 32) | ((y // BLOCK_SIZE) & 0xFFFFFFFF)

    def __getitem__(self, key):
        return super().__getitem__(self._pack(key))

    def __setitem__(self, key, value):
        super().__setitem__(self._pack(key), value)

    def get(self, key, default=None):
        return super().get(self._pack(key), default)

    def pop(self, key, default=None):
        return super().pop(self._pack(key), default)

    def __contains__(self, key):
        return super().__contains__(self._pack(key))


# Єдине джерело правди для блоків. Раніше ті самі об'єкти одночасно
# зберігались у list та dict. Це витрачало пам'ять і робило видалення
# блока O(n), через що гра зависала наприкінці генерації структур.
blocks_map = CompactBlockMap()
growing_plants = []
sand_blocks = []
fishes = []  

def add_block(block):
    # Будь-яка зміна блока може відкрити або закрити небо над печерою.
    rain_cover_cache.clear()
    old_block = blocks_map.get((block.rect.x, block.rect.y))
    if old_block is not None:
        if old_block in growing_plants:
            growing_plants.remove(old_block)
        if old_block in sand_blocks:
            sand_blocks.remove(old_block)
    blocks_map[(block.rect.x, block.rect.y)] = block
    if isinstance(block, (WheatBlock, PotatoBlock, RiceBlock, KelpBlock)):
        growing_plants.append(block)
    if isinstance(block, SandBlock):
        sand_blocks.append(block)

def remove_block(block):
    rain_cover_cache.clear()
    blocks_map.pop((block.rect.x, block.rect.y), None)
    if block in growing_plants:
        growing_plants.remove(block)
    if block in sand_blocks:
        sand_blocks.remove(block)

def clear_world_blocks():
    blocks_map.clear()
    rain_cover_cache.clear()
    growing_plants.clear()
    sand_blocks.clear()
    fishes.clear()
    endermen.clear()

def get_block_at(x, y):
    return blocks_map.get((x, y))

def add_to_inventory(texture, amount=1):
    capacity = sum(
        MAX_STACK_SIZE if stack is None else MAX_STACK_SIZE - stack["count"]
        for stack in inventory
        if stack is None or stack["texture"] == texture
    )
    if capacity < amount:
        return False
    for stack in inventory:
        if stack is not None and stack["texture"] == texture and stack["count"] < MAX_STACK_SIZE:
            added = min(amount, MAX_STACK_SIZE - stack["count"])
            stack["count"] += added
            amount -= added
            if amount == 0:
                return True
    for i in range(len(inventory)):
        if inventory[i] is None:
            added = min(amount, MAX_STACK_SIZE)
            inventory[i] = {"texture": texture, "count": added}
            amount -= added
            if amount == 0:
                return True
    return False

def drop_item_towards_cursor(texture, count=1):
    m_x, m_y = pg.mouse.get_pos()
    world_mouse_x = (m_x / camera_scale) + camera_x
    world_mouse_y = (m_y / camera_scale) + camera_y

    start_x = player.rect.centerx - 13
    start_y = player.rect.centery - 13

    dx = world_mouse_x - player.rect.centerx
    dy = world_mouse_y - player.rect.centery
    dist = math.hypot(dx, dy)
    
    if dist == 0:
        vel_x = 0
        vel_y = -3
    else:
        throw_power = 6.0
        vel_x = (dx / dist) * throw_power
        vel_y = (dy / dist) * throw_power - 2.0  

    dropped_items.append(DroppedItem(start_x, start_y, texture, count, vel_x, vel_y))

def drop_item_at_pos(texture, x, y, count=1):
    vx = random.uniform(-1.5, 1.5)
    vy = random.uniform(-4, -2)
    dropped_items.append(DroppedItem(x, y, texture, count, vx, vy))

# =====================================
# Збереження та Завантаження
# =====================================

SAVE_FILE = "savegame.json"

def save_world():
    world_data = {
        "player": {
            "x": player.rect.x,
            "y": player.rect.y,
            "health": player.health,
            "hunger": player.hunger
        },
        "blocks": [
            {
                "x": b.rect.x,
                "y": b.rect.y,
                "texture": b.texture,
                "is_wheat": isinstance(b, WheatBlock),
                "is_potato": isinstance(b, PotatoBlock),
                "is_rice": isinstance(b, RiceBlock),
                "is_kelp": isinstance(b, KelpBlock),
                "is_sand": isinstance(b, SandBlock),
                "wheat_age": getattr(b, "age", 0.0),
                "wheat_stage": getattr(b, "stage", 0)
            } for b in blocks_map.values()
        ],
        "inventory": inventory,
        "hotbar": hotbar,
        "left_hand_slot": left_hand_slot,
        "is_creative": is_creative,
        "solid_placed_blocks": list(solid_placed_blocks),
        "chests_data": {f"{k[0]},{k[1]}": v for k, v in chests_data.items()},
        "portal_structure_pos": portal_structure_pos
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(world_data, f)
        print("Світ успішно збережено!")
    except Exception as ex:
        print("Помилка збереження:", ex)

def load_world():
    global inventory, hotbar, dropped_items, is_creative, solid_placed_blocks, chests_data, left_hand_slot, portal_structure_pos
    if not os.path.exists(SAVE_FILE):
        return False
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        player.rect.x = data["player"]["x"]
        player.rect.y = data["player"]["y"]
        player.health = data["player"].get("health", player.max_health)
        player.hunger = data["player"].get("hunger", player.max_hunger)
        player.vel_y = 0
        player.inAir = True
        player.highest_y = player.rect.y
        is_creative = data.get("is_creative", False)
        solid_placed_blocks = set(tuple(p) for p in data.get("solid_placed_blocks", []))
        left_hand_slot = data.get("left_hand_slot", None)
        portal_structure_pos = tuple(data.get("portal_structure_pos", (0, 0)))
        
        raw_chests = data.get("chests_data", {})
        chests_data = {}
        for k, v in raw_chests.items():
            pos = tuple(map(int, k.split(",")))
            chests_data[pos] = v

        clear_world_blocks()
        for b_data in data["blocks"]:
            if b_data.get("is_wheat", False):
                wheat = WheatBlock(b_data["x"], b_data["y"])
                wheat.age = b_data.get("wheat_age", 0.0)
                wheat.stage = b_data.get("wheat_stage", 0)
                wheat.texture = f"wheat_stage{wheat.stage}.png"
                add_block(wheat)
            elif b_data.get("is_potato", False):
                potato = PotatoBlock(b_data["x"], b_data["y"])
                potato.age = b_data.get("wheat_age", 0.0)
                potato.stage = b_data.get("wheat_stage", 0)
                potato.texture = f"potato_stage{potato.stage}.png"
                add_block(potato)
            elif b_data.get("is_rice", False):
                rice = RiceBlock(b_data["x"], b_data["y"])
                rice.age = b_data.get("wheat_age", 0.0)
                rice.stage = b_data.get("wheat_stage", 0)
                rice.texture = f"rice_stage{rice.stage}.png"
                add_block(rice)
            elif b_data.get("is_kelp", False):
                kelp = KelpBlock(b_data["x"], b_data["y"])
                kelp.age = b_data.get("wheat_age", 0.0)
                kelp.stage = b_data.get("wheat_stage", 0)
                kelp.texture = f"kelp_stage{kelp.stage}.png"
                add_block(kelp)
            elif b_data.get("is_sand", False):
                add_block(SandBlock(b_data["x"], b_data["y"]))
            else:
                add_block(
                    Block(
                        b_data["x"],
                        b_data["y"],
                        BLOCK_SIZE,
                        BLOCK_SIZE,
                        (255, 255, 255),
                        b_data["texture"]
                    )
                )

        for _ in range(8):
            fishes.append(Fish(random.randint(1880, 2120) * BLOCK_SIZE, random.randint(OVERWORLD_START + 12, OVERWORLD_START + 14) * BLOCK_SIZE))

        inventory = data["inventory"]
        hotbar = data["hotbar"]
        dropped_items = []
        print("Світ успішно завантажено!")
        return True
    except Exception as ex:
        print("Помилка завантаження:", ex)
        return False

def draw_generation_progress(progress, label):
    screen.fill((18, 22, 32))
    title = pg.font.SysFont("arial", 34).render("GENERATING WORLD", True, (255, 255, 255))
    text = font.render(label, True, (190, 210, 235))
    bar = pg.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 20, 320, 20)
    pg.draw.rect(screen, (55, 65, 82), bar, border_radius=4)
    pg.draw.rect(screen, (70, 190, 120), (bar.x, bar.y, int(bar.w * max(0, min(1, progress))), bar.h), border_radius=4)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 45))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 10))
    pg.display.flip()
    pg.event.pump()

def generate_new_world():
    global dropped_items, inventory, hotbar, is_creative, solid_placed_blocks, chests_data, left_hand_slot, dragon, portal_structure_pos, portal_frame_positions, nether_portal_pairs
    draw_generation_progress(0.0, "Preparing terrain")
    clear_world_blocks()
    dropped_items = []
    is_creative = False
    solid_placed_blocks = set()
    chests_data = {}
    left_hand_slot = None
    portal_frame_positions.clear()
    nether_portal_pairs.clear()

    inventory[:] = [None for _ in range(INVENTORY_ROWS * INVENTORY_COLS)]
    hotbar[:] = [None for _ in range(HOTBAR_SIZE)]

    ground = OVERWORLD_START + 12
    surface_heights = [0] * WORLD_WIDTH

    sea_center_x = 2000
    sea_width = random.randint(150, 250)
    beach_width = random.randint(25, 40)

    sea_start_x = sea_center_x - sea_width // 2
    sea_end_x = sea_center_x + sea_width // 2

    water_level = OVERWORLD_START + 10

    desert_start_x = 2600
    desert_end_x = 3600

    volcano_start_x = 3600
    volcano_end_x = 4000

    snow_start_x = 4000
    snow_end_x = 5000

    caves = set()
    
    for _ in range(500): 
        x = random.randint(10, WORLD_WIDTH - 10)
        if sea_start_x <= x <= sea_end_x:
            y = random.randint(OVERWORLD_START + 25, OVERWORLD_HEIGHT - 5)
        else:
            y = random.randint(OVERWORLD_START + 15, OVERWORLD_HEIGHT - 5)
            
        length = random.randint(20, 45)

        for _ in range(length):
            radius = random.randint(1, 3)
            for xx in range(x - radius, x + radius + 1):
                for yy in range(y - radius, y + radius + 1):
                    if (xx - x) ** 2 + (yy - y) ** 2 <= radius ** 2:
                        caves.add((xx, yy))

            x += random.randint(-1, 1)
            y += random.randint(-1, 1)
            x = max(1, min(WORLD_WIDTH - 2, x))
            
            if sea_start_x <= x <= sea_end_x:
                y = max(OVERWORLD_START + 22, min(OVERWORLD_HEIGHT - 2, y))
            else:
                y = max(OVERWORLD_START + 12, min(OVERWORLD_HEIGHT - 2, y))

    # Збільшені великі печери в Аду
    for _ in range(350):
        x = random.randint(10, WORLD_WIDTH - 10)
        y = random.randint(OVERWORLD_HEIGHT + 5, WORLD_HEIGHT - 5)
        length = random.randint(20, 50)

        for _ in range(length):
            radius = random.randint(3, 6)
            for xx in range(x - radius, x + radius + 1):
                for yy in range(y - radius, y + radius + 1):
                    if (xx - x) ** 2 + (yy - y) ** 2 <= radius ** 2:
                        caves.add((xx, yy))

            x += random.randint(-1, 1)
            y += random.randint(-1, 1)
            x = max(1, min(WORLD_WIDTH - 2, x))
            y = max(OVERWORLD_HEIGHT + 2, min(WORLD_HEIGHT - 2, y))

    # =====================================
    # Генерація ЕНДУ
    # =====================================
    dragon = EnderDragon()
    island_center_x = 100
    island_y = -2040

    # Острів Енду
    for ix in range(island_center_x - 40, island_center_x + 40):
        dist_from_center = abs(ix - island_center_x)
        depth = max(1, 7 - int(dist_from_center * 0.15))
        for iy in range(island_y, island_y + depth):
            add_block(Block(ix * BLOCK_SIZE, iy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "end_stone.png"))

    # Обсидіанові Стовпи
    pillar_positions = [island_center_x - 25, island_center_x - 12, island_center_x + 12, island_center_x + 25]
    for px in pillar_positions:
        p_height = random.randint(8, 14)
        for py in range(island_y - p_height, island_y):
            for tx in range(px - 1, px + 2): 
                add_block(Block(tx * BLOCK_SIZE, py * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "obsidian.png"))
        add_block(Block(px * BLOCK_SIZE, (island_y - p_height - 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "end_crystal.png"))

    # =====================================
    # Генерація ПІДЗЕМНОЇ СТРУКТУРИ З ПОРТАЛОМ КРАЯ
    # =====================================
    # Кожен данж має випадкову позицію, тож портал Краю не виникає під спавном.
    struct_x = random.randint(300, WORLD_WIDTH - 300)
    struct_y = random.randint(OVERWORLD_START + 35, OVERWORLD_HEIGHT - 35)
    portal_structure_pos = (struct_x * BLOCK_SIZE, struct_y * BLOCK_SIZE) 
    biome_coords["end_dungeon"] = struct_x * BLOCK_SIZE
    
    # Кімната з кам'яної цегли
    for sx in range(struct_x - 6, struct_x + 7):
        for sy in range(struct_y - 4, struct_y + 6):
            if sx == struct_x - 6 or sx == struct_x + 6 or sy == struct_y - 4 or sy == struct_y + 5:
                add_block(Block(sx * BLOCK_SIZE, sy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "stone.png"))
            else:
                b_here = get_block_at(sx * BLOCK_SIZE, sy * BLOCK_SIZE)
                if b_here: remove_block(b_here)
                
    # Лава під порталом
    for lx in range(struct_x - 2, struct_x + 3):
        add_block(Block(lx * BLOCK_SIZE, (struct_y + 3) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "lava.png"))

    # Портал Края з 5 блоків
    for px in range(struct_x - 2, struct_x + 3):
        add_block(Block(px * BLOCK_SIZE, (struct_y + 2) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "portal_frame.png"))

    # Генерація решти світу
    for x in range(WORLD_WIDTH):
        if x % 100 == 0:
            draw_generation_progress(0.12 + 0.72 * x / WORLD_WIDTH, "Generating all world chunks")
        left_land_height = OVERWORLD_START + 8
        right_land_height = OVERWORLD_START + 8
        sea_floor_height = OVERWORLD_START + 16 + int(math.sin(x * 0.1) * 2) + random.randint(-1, 1)

        if x < (sea_start_x - beach_width) or x > (sea_end_x + beach_width):
            if desert_start_x <= x <= desert_end_x:
                ground = max(OVERWORLD_START + 6, min(OVERWORLD_START + 12, ground + random.randint(-1, 1)))
            elif volcano_start_x <= x <= volcano_end_x:
                ground = max(OVERWORLD_START + 4, min(OVERWORLD_START + 10, ground + random.randint(-1, 1)))
            elif snow_start_x <= x <= snow_end_x:
                ground = max(OVERWORLD_START + 5, min(OVERWORLD_START + 9, ground + random.randint(-1, 1)))
            else:
                ground = max(OVERWORLD_START + 5, min(OVERWORLD_START + 9, ground + random.randint(-1, 1)))
        else:
            if sea_start_x <= x <= sea_end_x:
                ground = sea_floor_height
            elif (sea_start_x - beach_width) <= x < sea_start_x:
                t = (x - (sea_start_x - beach_width)) / beach_width
                ground = int((1 - t) * left_land_height + t * sea_floor_height)
            elif sea_end_x < x <= (sea_end_x + beach_width):
                t = (x - sea_end_x) / beach_width
                ground = int((1 - t) * sea_floor_height + t * right_land_height)

        surface_heights[x] = ground

        if ground > water_level and not (desert_start_x <= x <= desert_end_x) and not (volcano_start_x <= x <= volcano_end_x):
            for y_water in range(water_level, ground):
                if not (struct_x - 6 <= x <= struct_x + 6 and struct_y - 4 <= y_water <= struct_y + 6):
                    add_block(Block(x * BLOCK_SIZE, y_water * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "water.png"))

        base_cloud_y = 50 + int(math.sin(x * 0.05) * 8) + int(math.cos(x * 0.12) * 3)
        if (x // 15) % 3 != 0: 
            cloud_thickness = random.randint(3, 6)
            for cy in range(base_cloud_y, base_cloud_y + cloud_thickness):
                if random.random() < 0.04:
                    add_block(Block(x * BLOCK_SIZE, cy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "cloud_ore.png"))
                else:
                    add_block(Block(x * BLOCK_SIZE, cy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "heaven_cloud.png"))
                
                if random.random() < 0.02:
                    add_block(Block(x * BLOCK_SIZE, cy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "gold_block.png"))

        for y in range(ground, WORLD_HEIGHT):
            if struct_x - 6 <= x <= struct_x + 6 and struct_y - 4 <= y <= struct_y + 6:
                continue
                
            if y == WORLD_HEIGHT - 1:
                add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (100, 100, 100), "bedrock.png"))
                continue

            # Два суцільні обсидіанові шари розділяють Верхній світ і Пекло.
            if y in (OVERWORLD_HEIGHT, OVERWORLD_HEIGHT + 1):
                add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "obsidian.png"))
                continue

            if (x, y) in caves:
                if y >= OVERWORLD_HEIGHT:
                    if y > OVERWORLD_HEIGHT + 15:
                        add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "lava.png"))
                continue

            if y < OVERWORLD_HEIGHT:
                if y == ground:
                    if sea_start_x <= x <= sea_end_x or (sea_start_x - beach_width) <= x <= (sea_end_x + beach_width) or desert_start_x <= x <= desert_end_x:
                        add_block(SandBlock(x * BLOCK_SIZE, y * BLOCK_SIZE))
                    elif volcano_start_x <= x <= volcano_end_x:
                        if random.random() < 0.15:
                            add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "lava.png"))
                        else:
                            add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "basalt.png"))
                    elif snow_start_x <= x <= snow_end_x:
                        add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "snow_grass.png")) 
                    else:
                        add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "grass.png"))
                elif y < ground + 3:
                    if ((sea_start_x - beach_width) <= x <= (sea_end_x + beach_width)) or (desert_start_x <= x <= desert_end_x):
                        add_block(SandBlock(x * BLOCK_SIZE, y * BLOCK_SIZE))
                    elif volcano_start_x <= x <= volcano_end_x:
                        add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "basalt.png"))
                    else:
                        add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "dirt.png"))
                else:
                    stone_type = "basalt.png" if volcano_start_x <= x <= volcano_end_x else "stone.png"
                    depth = y - ground
                    rand_val = random.random()
                    # Руди не з'являються поза власними висотними діапазонами.
                    if ORE_DEPTH_RANGES["coal_ore.png"][0] <= depth <= ORE_DEPTH_RANGES["coal_ore.png"][1] and rand_val < 0.07:
                        stone_type = "coal_ore.png"
                    elif ORE_DEPTH_RANGES["iron_ore.png"][0] <= depth <= ORE_DEPTH_RANGES["iron_ore.png"][1] and rand_val < 0.06:
                        stone_type = "iron_ore.png"
                    elif ORE_DEPTH_RANGES["gold_ore.png"][0] <= depth <= ORE_DEPTH_RANGES["gold_ore.png"][1] and rand_val < 0.045:
                        stone_type = "gold_ore.png"
                    elif ORE_DEPTH_RANGES["diamond_ore.png"][0] <= depth <= ORE_DEPTH_RANGES["diamond_ore.png"][1] and rand_val < 0.028:
                        stone_type = "diamond_ore.png"
                    add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), stone_type))

            else:
                # Ад з Базальтовим біомом та лавовими озерами
                is_basalt_delta = (x % 200 < 80)
                tile_type = "basalt.png" if is_basalt_delta else "netherrack.png"
                rand_nether = random.random()
                nether_depth = y - OVERWORLD_HEIGHT
                if rand_nether < 0.04 and ORE_DEPTH_RANGES["nether_gold_ore.png"][0] <= nether_depth <= ORE_DEPTH_RANGES["nether_gold_ore.png"][1]:
                    tile_type = "nether_gold_ore.png"
                elif rand_nether < 0.055 and ORE_DEPTH_RANGES["netherite_ore.png"][0] <= nether_depth <= ORE_DEPTH_RANGES["netherite_ore.png"][1]:
                    tile_type = "netherite_ore.png"
                elif is_basalt_delta and rand_nether < 0.12 and y > OVERWORLD_HEIGHT + 30:
                    tile_type = "lava.png"
                add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), tile_type))

        for y in range(ground, OVERWORLD_HEIGHT):
            if struct_x - 6 <= x <= struct_x + 6 and struct_y - 4 <= y <= struct_y + 6:
                continue
            if y == ground and not ((sea_start_x - beach_width) <= x <= (sea_end_x + beach_width)) and not (desert_start_x <= x <= desert_end_x) and not (volcano_start_x <= x <= volcano_end_x) and random.random() < 0.3:
                add_block(Block(x * BLOCK_SIZE, (y - 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "tall_grass.png"))

        if desert_start_x + 10 <= x <= desert_end_x - 10:
            if random.random() < 0.03:
                cac_h = random.randint(2, 3)
                for cy in range(cac_h):
                    add_block(Block(x * BLOCK_SIZE, (ground - 1 - cy) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "cactus.png"))

        if sea_start_x <= x <= sea_end_x:
            if random.random() < 0.25:
                kelp_x = x * BLOCK_SIZE
                kelp_y = (ground - 1) * BLOCK_SIZE
                target_water = get_block_at(kelp_x, kelp_y)
                if target_water and target_water.texture == "water.png":
                    remove_block(target_water)
                    kelp = KelpBlock(kelp_x, kelp_y)
                    kelp.age = random.uniform(0, 199)
                    kelp.stage = min(3, int(kelp.age / 50))
                    kelp.texture = f"kelp_stage{kelp.stage}.png"
                    add_block(kelp)

    for _ in range(12):
        fishes.append(Fish(random.randint(1880, 2120) * BLOCK_SIZE, (OVERWORLD_START + 12) * BLOCK_SIZE))

    # Пальми ростуть тільки на пляжах; берези — у виділеному березовому біомі.
    for x in range(sea_start_x - beach_width, sea_start_x, 12):
        ground_y = surface_heights[x]
        # Пальма з'являється лише на сухій частині пляжу, не у воді.
        if not (water_level - 3 <= ground_y <= water_level):
            continue

        trunk_height = random.randint(6, 8)
        for h in range(1, trunk_height + 1):
            # Легкий вигин стовбура у верхній частині.
            trunk_x = x + (1 if h >= trunk_height - 1 else 0)
            add_block(Block(trunk_x * BLOCK_SIZE, (ground_y - h) * BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "palm_wood.png"))

        crown_x = x + 1
        crown_y = ground_y - trunk_height
        add_block(Block(crown_x * BLOCK_SIZE, crown_y * BLOCK_SIZE,
                        BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "palm_leaves.png"))
        for direction in (-1, 1):
            for reach in range(1, 5):
                leaf_x = crown_x + direction * reach
                leaf_y = crown_y + (1 if reach >= 3 else 0)
                add_block(Block(leaf_x * BLOCK_SIZE, leaf_y * BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "palm_leaves.png"))
        for leaf_y in (crown_y - 1, crown_y - 2):
            add_block(Block(crown_x * BLOCK_SIZE, leaf_y * BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "palm_leaves.png"))

    birch_start_x, birch_end_x = 5100, 5700
    last_tree_x = -10
    for x in range(3, WORLD_WIDTH - 3):
        if x - last_tree_x < 7:
            continue

        ground_y = surface_heights[x]
        if (sea_start_x - beach_width - 5) <= x <= (sea_end_x + beach_width + 5) or desert_start_x <= x <= desert_end_x or volcano_start_x <= x <= volcano_end_x:
            continue
        if random.randint(1, 18) != 1:
            continue

        tree_height = random.randint(4, 6)
        for h in range(1, tree_height + 1):
            target_tall_grass = get_block_at(x * BLOCK_SIZE, (ground_y - h) * BLOCK_SIZE)
            if target_tall_grass and target_tall_grass.texture == "tall_grass.png":
                remove_block(target_tall_grass)
            add_block(Block(x * BLOCK_SIZE, (ground_y - h) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "birch_wood.png" if birch_start_x <= x <= birch_end_x else "wood.png"))

        top_y = ground_y - tree_height
        for leaf_x in range(x - 2, x + 3):
            for leaf_y in range(top_y - 2, top_y + 2):
                if abs(leaf_x - x) + abs(leaf_y - top_y) > 3:
                    continue
                if leaf_x == x and leaf_y >= top_y:
                    continue
                target_tall_grass = get_block_at(leaf_x * BLOCK_SIZE, leaf_y * BLOCK_SIZE)
                if target_tall_grass and target_tall_grass.texture == "tall_grass.png":
                    remove_block(target_tall_grass)
                add_block(Block(leaf_x * BLOCK_SIZE, leaf_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "birch_leaves.png" if birch_start_x <= x <= birch_end_x else "leaves.png"))

        last_tree_x = x

    # Химерний ліс: простора печера, трав'яний настил і дерева як у Верхньому світі.
    warped_start, warped_end, warped_floor = 4600, 4780, OVERWORLD_HEIGHT + 55
    for x in range(warped_start, warped_end):
        for y in range(warped_floor - 18, warped_floor + 2):
            old = get_block_at(x * BLOCK_SIZE, y * BLOCK_SIZE)
            if old:
                remove_block(old)
        add_block(Block(x * BLOCK_SIZE, warped_floor * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "warped_grass.png"))
        # Під травою лежить незерак — це ґрунт викривленого лісу.
        for depth in range(1, 5):
            add_block(Block(x * BLOCK_SIZE, (warped_floor + depth) * BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "netherrack.png"))

        # Ліс генерується як у Верхньому світі: високі стовбури та повні крони.
        if x % 11 == 0:
            tree_height = random.randint(5, 8)
            for h in range(1, tree_height + 1):
                add_block(Block(x * BLOCK_SIZE, (warped_floor - h) * BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "warped_wood.png"))
            crown_y = warped_floor - tree_height
            for lx in range(x - 3, x + 4):
                for ly in range(crown_y - 3, crown_y + 3):
                    dx, dy = abs(lx - x), abs(ly - crown_y)
                    if dx + dy <= 4 and not (lx == x and ly >= crown_y):
                        add_block(Block(lx * BLOCK_SIZE, ly * BLOCK_SIZE, BLOCK_SIZE,
                                        BLOCK_SIZE, (255, 255, 255), "warped_leaves.png"))
    biome_coords["warped"] = (warped_start + 20) * BLOCK_SIZE

    # Випадкова Незерська фортеця з недорогим лутом.
    fortress_x, fortress_y = random.randint(600, WORLD_WIDTH - 700), random.randint(OVERWORLD_HEIGHT + 120, WORLD_HEIGHT - 80)
    for x in range(fortress_x - 16, fortress_x + 17):
        for y in range(fortress_y - 7, fortress_y + 8):
            old = get_block_at(x * BLOCK_SIZE, y * BLOCK_SIZE)
            if old:
                remove_block(old)
            if x in (fortress_x - 16, fortress_x + 16) or y in (fortress_y - 7, fortress_y + 7):
                add_block(Block(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "nether_brick.png"))
    chest_pos = (fortress_x * BLOCK_SIZE, (fortress_y + 6) * BLOCK_SIZE)
    add_block(Block(*chest_pos, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "chest.png"))
    chests_data[chest_pos] = [{"texture": random.choice(["coal.png", "bread.png", "stick.png", "iron_ingot.png"]), "count": random.randint(1, 4)}] + [None] * 26
    biome_coords["fortress"] = fortress_x * BLOCK_SIZE

    draw_generation_progress(0.95, "Placing dungeons and biomes")
    center_block_x = 100
    player.rect.x = center_block_x * BLOCK_SIZE
    player.rect.y = (surface_heights[center_block_x] - 4) * BLOCK_SIZE
    player.vel_y = 0
    player.health = player.max_health
    player.hunger = player.max_hunger
    player.highest_y = player.rect.y
    draw_generation_progress(1.0, "World ready")

creative_inventory = [None for _ in range(120)]
for idx, img_path in enumerate(ALL_ITEMS):
    if idx < 120:
        creative_inventory[idx] = {"texture": img_path, "count": MAX_STACK_SIZE}
for idx in range(len(ALL_ITEMS), 120):
    creative_inventory[idx] = {"texture": "dirt.png", "count": MAX_STACK_SIZE}

dropped_items = []

player = Player(
    100 * BLOCK_SIZE,
    100,
    50,
    100,
    (255, 191, 0)
)

camera_x = 0
camera_y = 0

fishing_timer = 0
fishing_bite = False
fishing_catch_progress = 50.0 
fishing_particle_timer = 0

# =====================================
# Малювання та логіка інвентаря 2х2
# =====================================

def get_crafting_slot_rect(index):
    row = index // 2
    col = index % 2
    return pg.Rect(WIDTH // 2 - 85 + col * 45, 265 + row * 45, 40, 40)

def get_crafting_result_rect():
    return pg.Rect(WIDTH // 2 + 40, 287, 40, 40)

def get_inv_recipes_btn_rect():
    return pg.Rect(WIDTH // 2 - 85, 360, 165, 25)

def get_crafting_result():
    if is_creative:
        return None
    
    has_r = any(stack and stack["texture"] == "rice.png" for stack in crafting_grid)
    has_f = any(stack and stack["texture"] == "fish.png" for stack in crafting_grid)
    total = sum(1 for stack in crafting_grid if stack is not None)
    if has_r and has_f and total == 2:
        return "sushi.png", 1

    gold_block_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "gold_block.png")
    other_items = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] != "gold_block.png")
    if gold_block_count == 1 and other_items == 0:
        return "gold_ingot.png", 9

    iron_block_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "iron_block.png")
    if iron_block_count == 1 and total == 1:
        return "iron_ingot.png", 9

    diamond_block_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "diamond_block.png")
    if diamond_block_count == 1 and total == 1:
        return "diamond.png", 9

    netherite_block_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "netherite_block.png")
    if netherite_block_count == 1 and total == 1:
        return "netherite_ingot.png", 9

    wood_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "wood.png")
    other_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] != "wood.png")
    if wood_count == 1 and other_count == 0:
        return "planks.png", 4

    planks_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "planks.png")
    if planks_count == 4:
        return "crafting_table.png", 1

    if (
        (crafting_grid[0] and crafting_grid[2] and crafting_grid[0]["texture"] == "planks.png" and crafting_grid[2]["texture"] == "planks.png" and crafting_grid[1] is None and crafting_grid[3] is None) or
        (crafting_grid[1] and crafting_grid[3] and crafting_grid[1]["texture"] == "planks.png" and crafting_grid[3]["texture"] == "planks.png" and crafting_grid[0] is None and crafting_grid[2] is None)
    ):
        return "stick.png", 4

    leaves_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "leaves.png")
    if leaves_count == 2 and total == 2:
        return "string.png", 1
    
    string_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "string.png")
    if string_count == 4:
        return "wool.png", 1

    heaven_ingot_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "heaven_ingot.png")
    if heaven_ingot_count == 1 and total == 1:
        return "flight_emblem.png", 1
        
    if (crafting_grid[0] and crafting_grid[2] and crafting_grid[0]["texture"] == "coal.png" and crafting_grid[2]["texture"] == "stick.png" and crafting_grid[1] is None and crafting_grid[3] is None):
        return "torch.png", 4
    sand_count = sum(1 for stack in crafting_grid if stack is not None and stack["texture"] == "sand.png")
    if sand_count == 4:
        return "stone.png", 1

    return None

def draw_inventory_grid(offset_y=40):
    slot = 40
    spacing = 5

    rows = CREATIVE_ROWS if is_creative else INVENTORY_ROWS
    cols = CREATIVE_COLS if is_creative else INVENTORY_COLS

    bg_width = cols * slot + (cols - 1) * spacing + 40
    bg_height = rows * slot + (rows - 1) * spacing + 40

    if is_creative:
        bg_height = 360  

    bg = pg.Rect(
        WIDTH // 2 - bg_width // 2,
        offset_y,
        bg_width,
        bg_height
    )

    pg.draw.rect(screen, (70, 70, 70), bg)
    pg.draw.rect(screen, (220, 220, 220), bg, 3)

    start_x = bg.x + 20
    start_y = bg.y + 20

    index = 0
    active_inv = creative_inventory if is_creative else inventory

    for row in range(rows):
        for col in range(cols):
            if index >= len(active_inv):
                break

            rect = pg.Rect(
                start_x + col * (slot + spacing),
                start_y + row * (slot + spacing),
                slot,
                slot
            )

            if is_creative:
                rect.y = start_y + row * 23  
                rect.height = 20
                rect.width = 40
                rect.x = bg.x + 10 + col * 43

            pg.draw.rect(screen, (120, 120, 120), rect)
            pg.draw.rect(screen, (0, 0, 0), rect, 1 if is_creative else 2)

            if index == selected_inventory_slot:
                pg.draw.rect(screen, (255, 220, 0), rect, 2)

            if index < len(active_inv) and active_inv[index] is not None:
                img_size = (16, 16) if is_creative else (32, 32)
                img = load_texture(active_inv[index]["texture"], img_size)
                if is_creative:
                    screen.blit(img, (rect.x + 12, rect.y + 2))
                else:
                    screen.blit(img, (rect.x + 4, rect.y + 4))

                if not is_creative:
                    count = font.render(str(active_inv[index]["count"]), True, (255, 255, 255))
                    screen.blit(count, (rect.right - count.get_width() - 2, rect.bottom - count.get_height() - 1))

            index += 1

def draw_inventory():
    if is_creative:
        draw_inventory_grid(offset_y=15)
        craft_bg = pg.Rect(WIDTH // 2 - 115, 385, 230, 45)
        pg.draw.rect(screen, (70, 70, 70), craft_bg)
        pg.draw.rect(screen, (220, 220, 220), craft_bg, 3)
        title = font.render("CREATIVE (120 SLOTS)", True, (255, 225, 0))
        screen.blit(title, (craft_bg.centerx - title.get_width() // 2, craft_bg.y + 12))
        return

    draw_inventory_grid(offset_y=40)

    craft_bg = pg.Rect(WIDTH // 2 - 115, 230, 230, 165)
    pg.draw.rect(screen, (70, 70, 70), craft_bg)
    pg.draw.rect(screen, (220, 220, 220), craft_bg, 3)
    
    title = font.render("CRAFT", True, (255, 255, 255))
    screen.blit(title, (craft_bg.centerx - title.get_width() // 2, craft_bg.y + 5))

    for index in range(4):
        rect = get_crafting_slot_rect(index)
        pg.draw.rect(screen, (120, 120, 120), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)
        if crafting_grid[index] is not None:
            stack = crafting_grid[index]
            screen.blit(load_texture(stack["texture"], (32, 32)), (rect.x + 4, rect.y + 4))
            count = font.render(str(stack["count"]), True, (255, 255, 255))
            screen.blit(count, (rect.right - count.get_width() - 2, rect.bottom - count.get_height() - 1))

    result_rect = get_crafting_result_rect()
    pg.draw.rect(screen, (150, 150, 150), result_rect)
    pg.draw.rect(screen, (0, 0, 0), result_rect, 2)
    arrow = font.render(">", True, (255, 255, 255))
    screen.blit(arrow, (WIDTH // 2 + 5, 290))
    result = get_crafting_result()
    if result is not None:
        texture, amount = result
        screen.blit(load_texture(texture, (32, 32)), (result_rect.x + 4, result_rect.y + 4))
        count = font.render(str(amount), True, (255, 255, 255))
        screen.blit(count, (result_rect.right - count.get_width() - 2, result_rect.bottom - count.get_height() - 1))

    btn_rect = get_inv_recipes_btn_rect()
    pg.draw.rect(screen, (60, 120, 60), btn_rect, border_radius=4)
    pg.draw.rect(screen, (255, 255, 255), btn_rect, 1, border_radius=4)
    btn_txt = font.render("RECIPE BOOK", True, (255, 255, 255))
    screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width() // 2, btn_rect.y + 2))

# =====================================
# Верстак 3х3 та Книга Рецептів
# =====================================

def get_workbench_slot_rect(index):
    slot = 45
    spacing = 5
    start_x = WIDTH // 2 - (3 * slot + 2 * spacing) // 2
    start_y = 230

    row = index // 3
    col = index % 3

    return pg.Rect(
        start_x + col * (slot + spacing),
        start_y + row * (slot + spacing),
        slot,
        slot
    )

def get_workbench_result_rect():
    return pg.Rect(WIDTH // 2 + 105, 275, 45, 45)

def get_recipes_btn_rect():
    return pg.Rect(20, 10, 100, 25)

def get_workbench_result():
    def g(row, col):
        stack = workbench_grid[row * 3 + col]
        return stack["texture"] if stack else None

    if g(0,0) == "iron_ingot.png" and g(0,2) == "iron_ingot.png" and g(1,1) == "iron_ingot.png":
        total = sum(1 for stack in workbench_grid if stack is not None)
        if total == 3: return ("bucket.png", 1)

    has_r = any(stack and stack["texture"] == "rice.png" for stack in workbench_grid)
    has_f = any(stack and stack["texture"] == "fish.png" for stack in workbench_grid)
    total = sum(1 for stack in workbench_grid if stack is not None)
    if has_r and has_f and total == 2:
        return ("sushi.png", 1)

    for row in range(3):
        if g(row, 0) == "wheat.png" and g(row, 1) == "wheat.png" and g(row, 2) == "wheat.png":
            other_items = sum(1 for idx, stack in enumerate(workbench_grid) if stack is not None and (idx // 3) != row)
            if other_items == 0:
                return ("bread.png", 1)

    if all(workbench_grid[i] is not None and workbench_grid[i]["texture"] == "gold_ingot.png" for i in range(9)):
        return ("gold_block.png", 1)
    if all(workbench_grid[i] is not None and workbench_grid[i]["texture"] == "iron_ingot.png" for i in range(9)):
        return ("iron_block.png", 1)
    if all(workbench_grid[i] is not None and workbench_grid[i]["texture"] == "diamond.png" for i in range(9)):
        return ("diamond_block.png", 1)
    if all(workbench_grid[i] is not None and workbench_grid[i]["texture"] == "netherite_ingot.png" for i in range(9)):
        return ("netherite_block.png", 1)

    if g(1, 1) == "netherite_ingot.png":
        around_slots = [(0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)]
        if all(g(r, c) == "heaven_shard.png" for r, c in around_slots) and total == 9:
            return ("heaven_ingot.png", 1)

    if g(0,0) == "heaven_ingot.png" and total == 1:
        return ("flight_emblem.png", 1)

    if g(0,0) == "gold_block.png" and total == 1:
        return ("gold_ingot.png", 9)
    if g(0,0) == "iron_block.png" and total == 1:
        return ("iron_ingot.png", 9)
    if g(0,0) == "diamond_block.png" and total == 1:
        return ("diamond.png", 9)
    if g(0,0) == "netherite_block.png" and total == 1:
        return ("netherite_ingot.png", 9)

    if g(0,0) == "string.png" and g(0,1) == "string.png" and g(1,0) == "string.png" and g(1,1) == "string.png" and total == 4:
        return ("wool.png", 1)

    if g(1,0) == "wool.png" and g(1,1) == "wool.png" and g(1,2) == "wool.png":
        if g(2,0) == "planks.png" and g(2,1) == "planks.png" and g(2,2) == "planks.png" and total == 6:
            return ("bed.png", 1)

    furnace_slots = [
        (0,0), (0,1), (0,2),
        (1,0),        (1,2),
        (2,0), (2,1), (2,2)
    ]
    is_furnace = True
    for r, c in furnace_slots:
        if g(r, c) != "stone.png" and g(r, c) != "cobblestone.png":
            is_furnace = False
            break
    if is_furnace and g(1, 1) is None:
        return ("furnace.png", 1)

    is_chest = True
    for r, c in furnace_slots:
        if g(r, c) != "planks.png":
            is_chest = False
            break
    if is_chest and g(1, 1) is None:
        return ("chest.png", 1)

    for c in range(3):
        for r in range(2):
            if g(r, c) == "coal.png" and g(r+1, c) == "stick.png":
                total_items = sum(1 for stack in workbench_grid if stack is not None)
                if total_items == 2:
                    return ("torch.png", 4)

    if g(0,2) == "stick.png" and g(1,1) == "stick.png" and g(2,0) == "stick.png" and g(1,2) == "string.png" and g(2,2) == "string.png":
        return ("fishing_rod.png", 1)

    stick_combinations = [
        ((0,0), (1,0)), ((1,0), (2,0)),
        ((0,1), (1,1)), ((1,1), (2,1)),
        ((0,2), (1,2)), ((1,2), (2,2))
    ]
    for p1, p2 in stick_combinations:
        if g(p1[0], p1[1]) == "planks.png" and g(p2[0], p2[1]) == "planks.png":
            total_items = sum(1 for stack in workbench_grid if stack is not None)
            if total_items == 2:
                return ("stick.png", 4)

    wood_count = sum(1 for stack in workbench_grid if stack is not None and stack["texture"] == "wood.png")
    other_count = sum(1 for stack in workbench_grid if stack is not None and stack["texture"] != "wood.png")
    if wood_count == 1 and other_count == 0:
        return ("planks.png", 4)

    quads = [
        ((0,0), (0,1), (1,0), (1,1)),
        ((0,1), (0,2), (1,1), (1,2)),
        ((1,0), (1,1), (2,0), (2,1)),
        ((1,1), (1,2), (2,1), (2,2))
    ]
    for q in quads:
        if all(g(r, c) == "planks.png" for r, c in q):
            total_items = sum(1 for stack in workbench_grid if stack is not None)
            if total_items == 4:
                return ("crafting_table.png", 1)

    if (g(0,0) == "netherite_scrap.png" and g(0,1) == "netherite_scrap.png" and 
        g(1,0) == "netherite_scrap.png" and g(1,1) == "netherite_scrap.png" and
        g(0,2) == "gold_ingot.png" and g(1,2) == "gold_ingot.png" and
        g(2,0) == "gold_ingot.png" and g(2,1) == "gold_ingot.png"):
        total = sum(1 for stack in workbench_grid if stack is not None)
        if total == 8 and g(2,2) is None:
            return ("netherite_ingot.png", 1)

    if (g(0,0) == "planks.png" and g(0,1) == "planks.png" and
        g(1,0) == "planks.png" and g(1,1) == "planks.png" and
        g(2,0) == "planks.png" and g(2,1) == "planks.png" and total == 6):
        return ("door_closed.png", 3)

    materials = {
        "planks.png": "wood",
        "cobblestone.png": "stone",
        "stone.png": "stone",
        "iron_ingot.png": "iron",
        "gold_ingot.png": "gold",  
        "diamond.png": "diamond",
        "netherite_ingot.png": "netherite"
    }

    for mat_tex, mat_name in materials.items():
        if g(0,0) == mat_tex and g(0,1) == mat_tex and g(0,2) == mat_tex:
            if g(1,1) == "stick.png" and g(2,1) == "stick.png":
                total = sum(1 for stack in workbench_grid if stack is not None)
                if total == 5:
                    return (f"{mat_name}_pickaxe.png", 1)

        if g(0,1) == mat_tex and g(1,1) == "stick.png" and g(2,1) == "stick.png":
            total = sum(1 for stack in workbench_grid if stack is not None)
            if total == 3:
                return (f"{mat_name}_shovel.png", 1)

        if g(0,0) == mat_tex and g(0,1) == mat_tex and g(1,0) == mat_tex and g(1,1) == "stick.png" and g(2,1) == "stick.png":
            total = sum(1 for stack in workbench_grid if stack is not None)
            if total == 5:
                return (f"{mat_name}_axe.png", 1)

        if g(0,1) == mat_tex and g(0,2) == mat_tex and g(1,1) == "stick.png" and g(1,2) == mat_tex and g(2,1) == "stick.png":
            total = sum(1 for stack in workbench_grid if stack is not None)
            if total == 5:
                return (f"{mat_name}_axe.png", 1)

        if g(0,0) == mat_tex and g(0,1) == mat_tex and g(1,1) == "stick.png" and g(2,1) == "stick.png":
            total = sum(1 for stack in workbench_grid if stack is not None)
            if total == 4 and g(0,2) is None:
                return (f"{mat_name}_hoe.png", 1)

        if g(0,1) == mat_tex and g(0,2) == mat_tex and g(1,1) == "stick.png" and g(2,1) == "stick.png":
            total = sum(1 for stack in workbench_grid if stack is not None)
            if total == 4 and g(0,0) is None:
                return (f"{mat_name}_hoe.png", 1)

    return None

def draw_workbench():
    screen.fill((45,45,45))

    title = font.render("WORKBENCH", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    btn = get_recipes_btn_rect()
    pg.draw.rect(screen, (70, 100, 70), btn, border_radius=4)
    pg.draw.rect(screen, (255, 255, 255), btn, 1, border_radius=4)
    btn_txt = font.render("RECIPES", True, (255, 255, 255))
    screen.blit(btn_txt, (btn.x + 5, btn.y + 2))

    draw_inventory_grid(offset_y=40)

    for i in range(9):
        rect = get_workbench_slot_rect(i)
        pg.draw.rect(screen, (120, 120, 120), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        if workbench_grid[i]:
            stack = workbench_grid[i]
            img = load_texture(stack["texture"], (36, 36))
            screen.blit(img, (rect.x + 5, rect.y + 5))

            txt = font.render(str(stack["count"]), True, (255, 255, 255))
            screen.blit(txt, (rect.right - txt.get_width() - 2, rect.bottom - txt.get_height() - 2))

    arrow = font.render(">", True, (255, 255, 255))
    screen.blit(arrow, (WIDTH // 2 + 75, 285))

    result_rect = get_workbench_result_rect()
    pg.draw.rect(screen, (150, 150, 150), result_rect)
    pg.draw.rect(screen, (0, 0, 0), result_rect, 2)

    result = get_workbench_result()
    if result:
        texture, count = result
        img = load_texture(texture, (36, 36))
        screen.blit(img, (result_rect.x + 5, result_rect.y + 5))

        txt = font.render(str(count), True, (255, 255, 255))
        txt_pos = (result_rect.right - txt.get_width() - 2, result_rect.bottom - txt.get_height() - 2)
        screen.blit(txt, txt_pos)

def draw_recipes_menu():
    screen.fill((30, 30, 35))
    title = font.render("ALL RECIPES BOOK", True, (255, 220, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    mouse_pos = pg.mouse.get_pos()
    hovered_recipe = None

    start_x, start_y = 35, 50
    slot_size = 40
    spacing = 10
    cols = 8

    for idx, r in enumerate(ALL_RECIPES):
        row = idx // cols
        col = idx % cols
        rx = start_x + col * (slot_size + spacing)
        ry = start_y + row * (slot_size + spacing)

        cell_rect = pg.Rect(rx, ry, slot_size, slot_size)
        pg.draw.rect(screen, (50, 50, 60), cell_rect, border_radius=4)
        pg.draw.rect(screen, (100, 100, 120), cell_rect, 1, border_radius=4)

        img = load_texture(r["result"], (30, 30))
        screen.blit(img, (rx + 5, ry + 5))

        if cell_rect.collidepoint(mouse_pos):
            hovered_recipe = r
            pg.draw.rect(screen, (255, 255, 255), cell_rect, 2, border_radius=4)

    if hovered_recipe:
        preview_bg = pg.Rect(WIDTH // 2 - 130, HEIGHT - 215, 260, 155)
        pg.draw.rect(screen, (40, 40, 45), preview_bg, border_radius=8)
        pg.draw.rect(screen, (200, 200, 200), preview_bg, 2, border_radius=8)

        res_name = hovered_recipe["result"].replace(".png", "").replace("_", " ").upper()
        name_txt = font.render(f"{res_name} (x{hovered_recipe['count']})", True, (100, 255, 100))
        screen.blit(name_txt, (preview_bg.x + 15, preview_bg.y + 10))

        is_3x3 = hovered_recipe.get("is_3x3", False)
        grid_size = 3 if is_3x3 else 2
        grid_items = hovered_recipe["grid"]

        mini_slot = 30
        mini_space = 4
        grid_start_x = preview_bg.x + 20
        grid_start_y = preview_bg.y + 40

        for i in range(grid_size * grid_size):
            r_idx = i // grid_size
            c_idx = i % grid_size
            mx = grid_start_x + c_idx * (mini_slot + mini_space)
            my = grid_start_y + r_idx * (mini_slot + mini_space)

            ms_rect = pg.Rect(mx, my, mini_slot, mini_slot)
            pg.draw.rect(screen, (70, 70, 80), ms_rect)
            pg.draw.rect(screen, (20, 20, 25), ms_rect, 1)

            if i < len(grid_items) and grid_items[i]:
                m_img = load_texture(grid_items[i], (22, 22))
                screen.blit(m_img, (mx + 4, my + 4))

        arr_txt = font.render("->", True, (255, 255, 255))
        screen.blit(arr_txt, (grid_start_x + grid_size * 35 + 10, grid_start_y + 30))

        out_rect = pg.Rect(grid_start_x + grid_size * 35 + 40, grid_start_y + 20, 40, 40)
        pg.draw.rect(screen, (80, 80, 90), out_rect)
        pg.draw.rect(screen, (0, 255, 0), out_rect, 1)
        big_out_img = load_texture(hovered_recipe["result"], (32, 32))
        screen.blit(big_out_img, (out_rect.x + 4, out_rect.y + 4))

    close_btn = pg.Rect(WIDTH // 2 - 50, HEIGHT - 45, 100, 30)
    pg.draw.rect(screen, (150, 50, 50), close_btn, border_radius=5)
    c_txt = font.render("BACK", True, (255, 255, 255))
    screen.blit(c_txt, (close_btn.centerx - c_txt.get_width() // 2, close_btn.centery - c_txt.get_height() // 2))
    return close_btn

# =====================================
# Інтерфейс та сітка Сундука
# =====================================
def get_chest_slot_rect(index):
    slot = 40
    spacing = 5
    start_x = WIDTH // 2 - (CHEST_COLS * slot + (CHEST_COLS - 1) * spacing) // 2
    start_y = 240
    row = index // CHEST_COLS
    col = index % CHEST_COLS
    return pg.Rect(start_x + col * (slot + spacing), start_y + row * (slot + spacing), slot, slot)

def draw_chest_menu():
    screen.fill((60, 45, 35))
    title = font.render("CHEST (СУНДУК)", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    draw_inventory_grid(offset_y=40)

    chest_inv = chests_data.get(active_chest_pos, [None] * 27)
    for i in range(27):
        rect = get_chest_slot_rect(i)
        pg.draw.rect(screen, (100, 80, 65), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        if chest_inv[i] is not None:
            stack = chest_inv[i]
            img = load_texture(stack["texture"], (32, 32))
            screen.blit(img, (rect.x + 4, rect.y + 4))

            txt = font.render(str(stack["count"]), True, (255, 255, 255))
            screen.blit(txt, (rect.right - txt.get_width() - 2, rect.bottom - txt.get_height() - 2))

# =====================================
# Логіка та візуалізація Пічки
# =====================================

def get_furnace_slot_rect(index):
    if index == 0:
        return pg.Rect(WIDTH // 2 - 70, 230, 45, 45)
    elif index == 1:
        return pg.Rect(WIDTH // 2 - 70, 305, 45, 45)
    elif index == 2:
        return pg.Rect(WIDTH // 2 + 40, 267, 45, 45)

def draw_furnace_menu():
    screen.fill((50, 50, 55))

    title = font.render("FURNACE", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

    draw_inventory_grid(offset_y=40)

    label_input = font.render("Input", True, (180, 180, 180))
    label_fuel = font.render("Fuel", True, (180, 180, 180))
    screen.blit(label_input, (WIDTH // 2 - 130, 240))
    screen.blit(label_fuel, (WIDTH // 2 - 120, 315))

    for i in range(3):
        rect = get_furnace_slot_rect(i)
        pg.draw.rect(screen, (100, 100, 100) if i != 2 else (130, 110, 110), rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        if furnace_grid[i] is not None:
            stack = furnace_grid[i]
            img = load_texture(stack["texture"], (36, 36))
            screen.blit(img, (rect.x + 5, rect.y + 5))

            txt = font.render(str(stack["count"]), True, (255, 255, 255))
            screen.blit(txt, (rect.right - txt.get_width() - 2, rect.bottom - txt.get_height() - 2))

    arrow_rect = pg.Rect(WIDTH // 2 - 10, 275, 40, 30)
    pg.draw.rect(screen, (70, 70, 70), arrow_rect)

    if furnace_cook_time > 0:
        progress_w = int(40 * (furnace_cook_time / FURNACE_COOK_DURATION))
        pg.draw.rect(screen, (255, 165, 0), (arrow_rect.x, arrow_rect.y, progress_w, arrow_rect.height))

    arrow_txt = font.render(">", True, (255, 255, 255))
    screen.blit(arrow_txt, (arrow_rect.centerx - arrow_txt.get_width() // 2, arrow_rect.centery - arrow_txt.get_height() // 2))

def update_furnace_smelting():
    global furnace_cook_time

    inp = furnace_grid[0]
    fuel = furnace_grid[1]
    out = furnace_grid[2]

    valid_fuels = ["wood.png", "planks.png", "stick.png", "coal.png"]

    if inp and fuel and fuel["texture"] in valid_fuels:
        if inp["texture"] == "cobblestone.png":
            target_out = "stone.png"
        elif inp["texture"] == "potato.png":
            target_out = "baked_potato.png"
        elif inp["texture"] == "fish.png": 
            target_out = "cooked_fish.png"
        elif inp["texture"] == "iron_ore.png":
            target_out = "iron_ingot.png"
        elif inp["texture"] == "gold_ore.png":
            target_out = "gold_ingot.png" 
        elif inp["texture"] == "cloud_ore.png":
            target_out = "heaven_shard.png"
        elif inp["texture"] == "kelp.png":
            target_out = "dried_kelp.png"
        elif inp["texture"] == "nether_gold_ore.png":
            target_out = "gold_ingot.png" 
        else:
            target_out = None

        if target_out and (out is None or (out["texture"] == target_out and out["count"] < MAX_STACK_SIZE)):
            furnace_cook_time += 1
            if furnace_cook_time >= FURNACE_COOK_DURATION:
                inp["count"] -= 1
                if inp["count"] <= 0:
                    furnace_grid[0] = None

                fuel["count"] -= 1
                if fuel["count"] <= 0:
                    furnace_grid[1] = None

                if out is None:
                    furnace_grid[2] = {"texture": target_out, "count": 1}
                else:
                    out["count"] += 1

                furnace_cook_time = 0
        else:
            furnace_cook_time = 0
    else:
        furnace_cook_time = 0

# =====================================
# Оновлені кліки та Hotbar
# =====================================

def get_inventory_slot_at(position, offset_y=40):
    slot = 40
    spacing = 5
    rows = CREATIVE_ROWS if is_creative else INVENTORY_ROWS
    cols = CREATIVE_COLS if is_creative else INVENTORY_COLS
    
    bg_width = cols * slot + (cols - 1) * spacing + 40
    start_x = WIDTH // 2 - bg_width // 2 + 20
    start_y = offset_y + 20

    for row in range(rows):
        for col in range(cols):
            index = row * cols + col
            rect = pg.Rect(
                start_x + col * (slot + spacing),
                start_y + row * (slot + spacing),
                slot,
                slot
            )
            if is_creative:
                rect.y = start_y + row * 23
                rect.height = 20
                rect.width = 40
                rect.x = (WIDTH // 2 - bg_width // 2) + 10 + col * 43

            if rect.collidepoint(position):
                return index
    return None

def get_hotbar_slot_at(position):
    slot = 50
    spacing = 5
    start_x = WIDTH // 2 - (HOTBAR_SIZE * (slot + spacing)) // 2
    y = HEIGHT - 60

    for index in range(HOTBAR_SIZE):
        rect = pg.Rect(start_x + index * (slot + spacing), y, slot, slot)
        if rect.collidepoint(position):
            return index

    return None

def shift_move_item(slot_idx, is_from_inventory):
    global inventory, hotbar
    if is_from_inventory:
        item = inventory[slot_idx]
        if not item: return
        for i in range(HOTBAR_SIZE):
            if hotbar[i] and hotbar[i]["texture"] == item["texture"] and hotbar[i]["count"] < MAX_STACK_SIZE:
                add_amt = min(item["count"], MAX_STACK_SIZE - hotbar[i]["count"])
                hotbar[i]["count"] += add_amt
                item["count"] -= add_amt
                if item["count"] <= 0:
                    inventory[slot_idx] = None
                    return
        for i in range(HOTBAR_SIZE):
            if hotbar[i] is None:
                hotbar[i] = item
                inventory[slot_idx] = None
                return
    else:
        item = hotbar[slot_idx]
        if not item: return
        for i in range(len(inventory)):
            if inventory[i] and inventory[i]["texture"] == item["texture"] and inventory[i]["count"] < MAX_STACK_SIZE:
                add_amt = min(item["count"], MAX_STACK_SIZE - inventory[i]["count"])
                inventory[i]["count"] += add_amt
                item["count"] -= add_amt
                if item["count"] <= 0:
                    hotbar[slot_idx] = None
                    return
        for i in range(len(inventory)):
            if inventory[i] is None:
                inventory[i] = item
                hotbar[slot_idx] = None
                return

def handle_inventory_click(position):
    global selected_inventory_slot, selected_block, state
    
    offset = 15 if is_creative else 40
    inventory_slot = get_inventory_slot_at(position, offset_y=offset)
    hotbar_slot = get_hotbar_slot_at(position)
    active_inv = creative_inventory if is_creative else inventory

    mods = pg.key.get_mods()
    if mods & pg.KMOD_SHIFT:
        if inventory_slot is not None and not is_creative:
            shift_move_item(inventory_slot, is_from_inventory=True)
            return
        if hotbar_slot is not None and not is_creative:
            shift_move_item(hotbar_slot, is_from_inventory=False)
            return

    if not is_creative and inventory_open and get_inv_recipes_btn_rect().collidepoint(position):
        state = RECIPES_MENU
        return

    if is_creative:
        if inventory_slot is not None and inventory_slot < len(active_inv) and active_inv[inventory_slot] is not None:
            selected_inventory_slot = inventory_slot
            return
        if hotbar_slot is not None:
            if selected_inventory_slot is not None:
                hotbar[hotbar_slot] = {"texture": active_inv[selected_inventory_slot]["texture"], "count": MAX_STACK_SIZE}
                selected_inventory_slot = None
            else:
                selected_block = hotbar_slot
            return
        selected_inventory_slot = None
        return

    crafting_slot = next((i for i in range(4) if get_crafting_slot_rect(i).collidepoint(position)), None)

    if inventory_slot is not None:
        if selected_inventory_slot is None:
            selected_inventory_slot = inventory_slot
        elif selected_inventory_slot == inventory_slot:
            selected_inventory_slot = None
        else:
            inventory[selected_inventory_slot], inventory[inventory_slot] = inventory[inventory_slot], inventory[selected_inventory_slot]
            selected_inventory_slot = None
        return

    if crafting_slot is not None:
        if selected_inventory_slot is not None and inventory[selected_inventory_slot] is not None:
            source = inventory[selected_inventory_slot]
            target = crafting_grid[crafting_slot]
            if target is None or (target["texture"] == source["texture"] and target["count"] < MAX_STACK_SIZE):
                if target is None:
                    crafting_grid[crafting_slot] = {"texture": source["texture"], "count": 1}
                else:
                    target["count"] += 1
                source["count"] -= 1
                if source["count"] == 0:
                    inventory[selected_inventory_slot] = None
                    selected_inventory_slot = None
        elif crafting_grid[crafting_slot] is not None:
            stack = crafting_grid[crafting_slot]
            if add_to_inventory(stack["texture"], stack["count"]):
                crafting_grid[crafting_slot] = None
        return

    if get_crafting_result_rect().collidepoint(position):
        result = get_crafting_result()
        if result is not None and add_to_inventory(*result):
            for index, stack in enumerate(crafting_grid):
                if stack is not None:
                    stack["count"] -= 1
                    if stack["count"] <= 0:
                        crafting_grid[index] = None
        return

    if hotbar_slot is not None:
        if selected_inventory_slot is None:
            selected_block = hotbar_slot
        else:
            hotbar[hotbar_slot], inventory[selected_inventory_slot] = (
                inventory[selected_inventory_slot], hotbar[hotbar_slot]
            )
            selected_block = hotbar_slot
            selected_inventory_slot = None
        return

    selected_inventory_slot = None

def draw_hotbar():
    if inventory_open and state == GAME:
        draw_inventory()

    slot = 50
    spacing = 5

    start_x = WIDTH // 2 - (HOTBAR_SIZE * (slot + spacing)) // 2
    y = HEIGHT - 60

    for i in range(HOTBAR_SIZE):
        rect = pg.Rect(
            start_x + i * (slot + spacing),
            y,
            slot,
            slot
        )

        pg.draw.rect(screen, (50, 50, 50), rect)

        if i == selected_block:
            pg.draw.rect(screen, (255, 255, 255), rect, 4)
        else:
            pg.draw.rect(screen, (120, 120, 120), rect, 2)

        if hotbar[i] is not None:
            if hotbar[i]["texture"] in ["door_closed.png", "door_open.png"]:
                img = load_texture(hotbar[i]["texture"], (20, 40))
                screen.blit(img, (rect.x + 15, rect.y + 5))
            else:
                img = load_texture(hotbar[i]["texture"], (40, 40))
                screen.blit(img, (rect.x + 5, rect.y + 5))

            if not is_creative:
                count = font.render(str(hotbar[i]["count"]), True, (255, 255, 255))
                screen.blit(count, (rect.right - count.get_width() - 2, rect.bottom - count.get_height() - 1))

        txt = font.render(str(i + 1), True, (255, 255, 255))
        screen.blit(txt, (rect.x + 2, rect.y + 2))

    lh_rect = pg.Rect(start_x + HOTBAR_SIZE * (slot + spacing) + 10, y, slot, slot)
    pg.draw.rect(screen, (40, 40, 45), lh_rect)
    pg.draw.rect(screen, (0, 255, 220), lh_rect, 2)
    lh_title = font.render("F", True, (0, 255, 220))
    screen.blit(lh_title, (lh_rect.x + 4, lh_rect.y + 2))
    
    if left_hand_slot:
        img = load_texture(left_hand_slot["texture"], (40, 40))
        screen.blit(img, (lh_rect.x + 5, lh_rect.y + 5))
        if not is_creative:
            count = font.render(str(left_hand_slot["count"]), True, (255, 255, 255))
            screen.blit(count, (lh_rect.right - count.get_width() - 2, lh_rect.bottom - count.get_height() - 1))

# =====================================
# Головне меню
# =====================================

def draw_menu():
    screen.fill((20, 20, 40))

    title_font = pg.font.SysFont("arial", 50)
    button_font = pg.font.SysFont("arial", 24)

    title = title_font.render("BLOCK GAME", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

    mouse = pg.mouse.get_pos()

    new_game_rect = pg.Rect(WIDTH // 2 - 120, 180, 240, 50)
    color_new = (80, 200, 120) if not new_game_rect.collidepoint(mouse) else (120, 240, 160)
    pg.draw.rect(screen, color_new, new_game_rect, border_radius=8)
    txt_new = button_font.render("NEW GAME", True, (0, 0, 0))
    screen.blit(txt_new, (new_game_rect.centerx - txt_new.get_width() // 2, new_game_rect.centery - txt_new.get_height() // 2))

    has_save = os.path.exists(SAVE_FILE)
    load_game_rect = pg.Rect(WIDTH // 2 - 120, 250, 240, 50)

    if has_save:
        color_load = (100, 149, 237) if not load_game_rect.collidepoint(mouse) else (135, 206, 250)
    else:
        color_load = (100, 100, 100)

    pg.draw.rect(screen, color_load, load_game_rect, border_radius=8)
    txt_load = button_font.render("CONTINUE", True, (0, 0, 0) if has_save else (180, 180, 180))
    screen.blit(txt_load, (load_game_rect.centerx - txt_load.get_width() // 2, load_game_rect.centery - txt_load.get_height() // 2))

    exit_rect = pg.Rect(WIDTH // 2 - 120, 320, 240, 50)
    color_exit = (200, 80, 80) if not exit_rect.collidepoint(mouse) else (240, 120, 120)
    pg.draw.rect(screen, color_exit, exit_rect, border_radius=8)
    txt_exit = button_font.render("EXIT GAME", True, (0, 0, 0))
    screen.blit(txt_exit, (exit_rect.centerx - txt_exit.get_width() // 2, exit_rect.centery - txt_exit.get_height() // 2))

    return new_game_rect, load_game_rect, exit_rect

# =====================================
# Меню Паузи
# =====================================

def draw_pause_menu():
    overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    title_font = pg.font.SysFont("arial", 40)
    button_font = pg.font.SysFont("arial", 20)

    title = title_font.render("PAUSED", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    mouse = pg.mouse.get_pos()

    resume_rect = pg.Rect(WIDTH // 2 - 100, 120, 200, 45)
    col_res = (120, 120, 120) if not resume_rect.collidepoint(mouse) else (170, 170, 170)
    pg.draw.rect(screen, col_res, resume_rect, border_radius=5)
    pg.draw.rect(screen, (255, 255, 255), resume_rect, 2, border_radius=5)
    txt_res = button_font.render("RESUME", True, (255, 255, 255))
    screen.blit(txt_res, (resume_rect.centerx - txt_res.get_width() // 2, resume_rect.centery - txt_res.get_height() // 2))

    codes_rect = pg.Rect(WIDTH // 2 - 100, 185, 200, 45)
    col_codes = (130, 90, 180) if not codes_rect.collidepoint(mouse) else (160, 120, 220)
    pg.draw.rect(screen, col_codes, codes_rect, border_radius=5)
    pg.draw.rect(screen, (255, 255, 255), codes_rect, 2, border_radius=5)
    txt_codes = button_font.render("CODES (КОДИ)", True, (255, 255, 255))
    screen.blit(txt_codes, (codes_rect.centerx - txt_codes.get_width() // 2, codes_rect.centery - txt_codes.get_height() // 2))

    save_rect = pg.Rect(WIDTH // 2 - 100, 250, 200, 45)
    col_save = (80, 180, 120) if not save_rect.collidepoint(mouse) else (120, 220, 160)
    pg.draw.rect(screen, col_save, save_rect, border_radius=5)
    pg.draw.rect(screen, (255, 255, 255), save_rect, 2, border_radius=5)
    txt_save = button_font.render("SAVE WORLD", True, (255, 255, 255))
    screen.blit(txt_save, (save_rect.centerx - txt_save.get_width() // 2, save_rect.centery - txt_save.get_height() // 2))

    menu_rect = pg.Rect(WIDTH // 2 - 100, 315, 200, 45)
    col_menu = (180, 80, 80) if not menu_rect.collidepoint(mouse) else (220, 120, 120)
    pg.draw.rect(screen, col_menu, menu_rect, border_radius=5)
    pg.draw.rect(screen, (255, 255, 255), menu_rect, 2, border_radius=5)
    txt_menu = button_font.render("EXIT TO MENU", True, (255, 255, 255))
    screen.blit(txt_menu, (menu_rect.centerx - txt_menu.get_width() // 2, menu_rect.centery - txt_menu.get_height() // 2))

    return resume_rect, codes_rect, save_rect, menu_rect

# =====================================
# Menu Кодів
# =====================================

def draw_codes_menu():
    overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    title_font = pg.font.SysFont("arial", 30)
    button_font = pg.font.SysFont("arial", 20)

    title = title_font.render("ENTER CHEAT CODE", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    input_box = pg.Rect(WIDTH // 2 - 150, 150, 300, 45)
    pg.draw.rect(screen, (50, 50, 50), input_box, border_radius=5)
    pg.draw.rect(screen, (255, 220, 0), input_box, 2, border_radius=5)

    input_surface = font.render(code_input_text + "|", True, (255, 255, 255))
    screen.blit(input_surface, (input_box.x + 10, input_box.y + (45 - input_surface.get_height()) // 2))

    if code_feedback_text:
        col = (100, 255, 100) if "Success" in code_feedback_text or "Activated" in code_feedback_text or "Deactivated" in code_feedback_text or "Teleported" in code_feedback_text or "Time changed" in code_feedback_text else (255, 100, 100)
        feedback_surface = font.render(code_feedback_text, True, col)
        screen.blit(feedback_surface, (WIDTH // 2 - feedback_surface.get_width() // 2, 220))

    mouse = pg.mouse.get_pos()
    back_rect = pg.Rect(WIDTH // 2 - 80, 320, 160, 40)
    col_back = (100, 100, 100) if not back_rect.collidepoint(mouse) else (150, 150, 150)
    pg.draw.rect(screen, col_back, back_rect, border_radius=5)
    pg.draw.rect(screen, (255, 255, 255), back_rect, 2, border_radius=5)
    txt_back = button_font.render("BACK", True, (255, 255, 255))
    screen.blit(txt_back, (back_rect.centerx - txt_back.get_width() // 2, back_rect.centery - txt_back.get_height() // 2))

    return back_rect

# =====================================
# Малювання та Логіка Міні-гри Рибалки
# =====================================
def draw_fishing_game():
    screen.fill((10, 20, 30))  

    title = font.render("FISHING! PRESS SPACE RAPIDLY!", True, (255, 255, 100))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))

    bar_width = 300
    bar_height = 25
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = HEIGHT // 2 - 20

    pg.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
    progress_w = int(bar_width * (fishing_catch_progress / 100.0))
    
    color_r = max(0, min(255, int(255 * (1.0 - fishing_catch_progress / 100.0))))
    color_g = max(0, min(255, int(255 * (fishing_catch_progress / 100.0))))
    
    pg.draw.rect(screen, (color_r, color_g, 50), (bar_x, bar_y, progress_w, bar_height), border_radius=5)
    pg.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)

    info = font.render("Progress: " + str(int(fishing_catch_progress)) + "%", True, (255, 255, 255))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, bar_y + 35))

# =====================================
# Основний цикл гри
# =====================================

while running:

    if state == MENU:
        btn_new, btn_load, btn_exit = draw_menu()

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False

            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if btn_new.collidepoint(e.pos):
                        generate_new_world()
                        state = GAME
                    elif btn_load.collidepoint(e.pos) and os.path.exists(SAVE_FILE):
                        if load_world():
                            state = GAME
                        else:
                            generate_new_world()
                            state = GAME
                    elif btn_exit.collidepoint(e.pos):
                        running = False

            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_F11:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
                        camera_scale = 1.5
                        WIDTH, HEIGHT = screen.get_size()
                    else:
                        screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                        camera_scale = 1.0
                        WIDTH, HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT

        pg.display.flip()
        clk.tick(60)
        continue

    start_gx = int(camera_x // BLOCK_SIZE) - 1
    end_gx = int((camera_x + WIDTH / camera_scale) // BLOCK_SIZE) + 1
    start_gy = int(camera_y // BLOCK_SIZE) - 1
    end_gy = int((camera_y + HEIGHT / camera_scale) // BLOCK_SIZE) + 1

    if state in [GAME, FISHING_GAME]:
        day_time = (day_time + 1.0/60.0) % DAY_DURATION
        update_weather(1.0/60.0)
        update_liquids()  
        dragon.update()
        update_endermen(1.0 / 60.0)
        update_portal_teleport(1.0 / 60.0)
        
        # Перевірка телепортації з Порталу Края до Енду (центральні 3 блоки)
        if False and portal_structure_pos != (0, 0):  # replaced by update_portal_teleport
            struct_x = portal_structure_pos[0] // BLOCK_SIZE
            struct_y = portal_structure_pos[1] // BLOCK_SIZE
            
            player_gx = player.rect.centerx // BLOCK_SIZE
            player_gy = player.rect.bottom // BLOCK_SIZE
            
            # Телепорт спрацьовує при наступанні на центральні 3 блоки порталу
            if (struct_x - 1 <= player_gx <= struct_x + 1) and (player_gy == struct_y + 2):
                player.rect.x = 100 * BLOCK_SIZE
                player.rect.y = -2035 * BLOCK_SIZE
                player.vel_y = 0
                player.inAir = True

        # Перевірка телепортації з Порталу Пекла
        p_gx = player.rect.centerx // BLOCK_SIZE
        p_gy = player.rect.centery // BLOCK_SIZE
        current_standing_block = get_block_at(p_gx * BLOCK_SIZE, p_gy * BLOCK_SIZE)
        if False and current_standing_block and current_standing_block.texture == "potal_ad.png":  # replaced by paired portals
            if player.rect.y < OVERWORLD_HEIGHT * BLOCK_SIZE:
                player.rect.x = 100 * BLOCK_SIZE
                player.rect.y = (OVERWORLD_HEIGHT + 2) * BLOCK_SIZE
            else:
                player.rect.x = 100 * BLOCK_SIZE
                player.rect.y = (OVERWORLD_START + 2) * BLOCK_SIZE
            player.vel_y = 0
            player.inAir = True

        # Перевірка телепортації з Чаші Енду назад на Спавн
        if player.rect.y < -2000 * BLOCK_SIZE and not dragon.active:
            island_center_x = 100
            bowl_y = -2042 # Піднято чашу вище
            player_gx = player.rect.centerx // BLOCK_SIZE
            player_gy = player.rect.bottom // BLOCK_SIZE
            
            if (island_center_x - 2 <= player_gx <= island_center_x + 2) and (player_gy == bowl_y + 1):
                player.rect.x = 100 * BLOCK_SIZE
                player.rect.y = (OVERWORLD_START + 5) * BLOCK_SIZE
                player.vel_y = 0
                player.inAir = True

        for fb in dragon_fireballs[:]:
            if fb.update():
                dragon_fireballs.remove(fb)

    time_factor = (math.sin(2 * math.pi * day_time / DAY_DURATION) + 1.0) / 2.0
    
    weather_sky_darkness = 0.8 if is_raining else 1.0
    frame_sky_color = (
        int((10 + (80 * time_factor)) * weather_sky_darkness),
        int((15 + (175 * time_factor)) * weather_sky_darkness),
        int((30 + (225 * time_factor)) * weather_sky_darkness),
    )

    if state == PAUSE:
        screen.fill(get_sky_color(player.rect.y, frame_sky_color))

        for gx in range(start_gx, end_gx + 1):
            for gy in range(start_gy, end_gy + 1):
                block = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
                if block:
                    block.draw(screen, camera_x, camera_y)

        for dropped_item in dropped_items:
            dropped_item.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)
        dragon.draw(screen, camera_x, camera_y)
        for enderman in endermen:
            enderman.draw(screen, camera_x, camera_y)
        for fb in dragon_fireballs:
            fb.draw(screen, camera_x, camera_y)
        draw_weather()
        draw_hotbar()
        draw_hud()
        draw_clock()

        btn_resume, btn_codes, btn_save, btn_to_menu = draw_pause_menu()

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    state = GAME
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if btn_resume.collidepoint(e.pos):
                        state = GAME
                    elif btn_codes.collidepoint(e.pos):
                        state = CODES_MENU
                        code_input_text = ""
                        code_feedback_text = ""
                    elif btn_save.collidepoint(e.pos):
                        save_world()
                    elif btn_to_menu.collidepoint(e.pos):
                        state = MENU

        pg.display.flip()
        clk.tick(60)
        continue

    if state == CODES_MENU:
        if code_feedback_timer > 0:
            code_feedback_timer -= 1
            if code_feedback_timer == 0:
                code_feedback_text = ""

        screen.fill(get_sky_color(player.rect.y, frame_sky_color))

        for gx in range(start_gx, end_gx + 1):
            for gy in range(start_gy, end_gy + 1):
                block = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
                if block:
                    block.draw(screen, camera_x, camera_y)

        for dropped_item in dropped_items:
            dropped_item.draw(screen, camera_x, camera_y)
        player.draw(screen, camera_x, camera_y)
        dragon.draw(screen, camera_x, camera_y)
        for enderman in endermen:
            enderman.draw(screen, camera_x, camera_y)
        for fb in dragon_fireballs:
            fb.draw(screen, camera_x, camera_y)
        draw_weather()
        draw_hotbar()
        draw_hud()
        draw_clock()

        btn_back = draw_codes_menu()

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    state = PAUSE
                elif e.key == pg.K_BACKSPACE:
                    code_input_text = code_input_text[:-1]
                elif e.key == pg.K_RETURN:
                    entered_code = code_input_text.strip()
                    if entered_code == "Kitaychyk":
                        is_creative = not is_creative
                        if is_creative:
                            code_feedback_text = "Success: Creative Activated!"
                        else:
                            code_feedback_text = "Success: Creative Deactivated!"
                        code_feedback_timer = 120
                        code_input_text = ""
                    elif entered_code.lower() == "portal":
                        if portal_structure_pos != (0, 0):
                            player.rect.x = portal_structure_pos[0]
                            player.rect.y = portal_structure_pos[1] - BLOCK_SIZE * 2
                            player.vel_y = 0
                            player.inAir = True
                            code_feedback_text = "Success: Teleported to Portal Structure!"
                        else:
                            code_feedback_text = "Error: Portal structure pos not found!"
                        code_feedback_timer = 120
                        code_input_text = ""
                    elif entered_code.lower().startswith("time "):
                        try:
                            parts = entered_code.split(" ")
                            if len(parts) > 1:
                                target_hour = float(parts[1])
                                day_time = (target_hour / 24.0) * DAY_DURATION
                                code_feedback_text = f"Success: Time changed to {int(target_hour)}:00!"
                            else:
                                code_feedback_text = "Error: Use 'time [0-23]'"
                        except Exception:
                            code_feedback_text = "Error: Use 'time [0-23]'"
                        code_feedback_timer = 120
                        code_input_text = ""
                    elif entered_code.lower() == "rain":
                        is_raining = not is_raining
                        rain_timer = random.randint(2400, 4800) if is_raining else random.randint(3600, 7200)
                        code_feedback_text = f"Success: Rain {'Activated' if is_raining else 'Deactivated'}!"
                        code_feedback_timer = 120
                        code_input_text = ""
                    elif entered_code.lower() == "potato":
                        if code_potato_used:
                            code_feedback_text = "Already used!"
                        else:
                            if add_to_inventory("potato.png", 1):
                                code_feedback_text = "Success: 1 Potato added!"
                                code_potato_used = True
                            else:
                                code_feedback_text = "Error: Inventory is full!"
                        code_feedback_timer = 120
                        code_input_text = ""
                    elif entered_code.lower().startswith("tp "):
                        parts = entered_code.lower().split(" ")
                        if len(parts) > 1:
                            target_biome = parts[1]
                            if target_biome in biome_coords:
                                player.rect.x = biome_coords[target_biome]
                                if target_biome in ("nether", "warped", "fortress"):
                                    player.rect.y = (OVERWORLD_HEIGHT + 2) * BLOCK_SIZE
                                elif target_biome == "heaven":
                                    player.rect.y = 5 * BLOCK_SIZE
                                elif target_biome == "end":
                                    player.rect.y = -2035 * BLOCK_SIZE
                                elif target_biome == "end_dungeon":
                                    player.rect.y = portal_structure_pos[1] - BLOCK_SIZE * 6
                                elif target_biome == "snow" or target_biome == "volcano":
                                    player.rect.y = (OVERWORLD_START + 2) * BLOCK_SIZE
                                else:
                                    player.rect.y = (OVERWORLD_START + 5) * BLOCK_SIZE  
                                player.vel_y = 0
                                player.inAir = True
                                code_feedback_text = f"Success: Teleported to {target_biome.upper()}!"
                            else:
                                code_feedback_text = "Unknown place! Use plains, sea, desert, volcano, snow, birch, nether, warped, fortress, end_dungeon, heaven or end."
                        else:
                            code_feedback_text = "Error: Specify biome name"
                        code_feedback_timer = 120
                        code_input_text = ""
                    else:
                        code_feedback_text = "Invalid Code!"
                        code_feedback_timer = 120
                else:
                    if len(code_input_text) < 18:
                        code_input_text += e.unicode
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1 and btn_back.collidepoint(e.pos):
                    state = PAUSE

        pg.display.flip()
        clk.tick(60)
        continue

    if state == RECIPES_MENU:
        c_btn = draw_recipes_menu()
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE or e.key == pg.K_e:
                    state = GAME if inventory_open else WORKBENCH
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1 and c_btn.collidepoint(e.pos):
                    state = GAME if inventory_open else WORKBENCH
        pg.display.flip()
        clk.tick(60)
        continue

    if state == FISHING_GAME:
        fishing_catch_progress -= 0.35 
        if fishing_catch_progress < 0:
            fishing_catch_progress = 0
            state = GAME
            fishing_bite = False
            print("Рибка зірвалася з гачка!")

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    fishing_catch_progress += 8.0
                    if fishing_catch_progress >= 100.0:
                        state = GAME
                        fishing_bite = False
                        drop_item_at_pos("fish.png", player.rect.centerx, player.rect.centery - 20)

        draw_fishing_game()
        pg.display.flip()
        clk.tick(60)
        continue

    update_furnace_smelting()

    for plant in growing_plants:
        p_screen_x = int((plant.rect.x - camera_x) * camera_scale)
        p_screen_y = int((plant.rect.y - camera_y) * camera_scale)
        if -50 <= p_screen_x <= WIDTH + 50 and -50 <= p_screen_y <= HEIGHT + 50:
            plant.update_growth(1.0 / 60.0)

    for f in fishes:
        f.update()

    camera_x = player.rect.centerx - (WIDTH // 2) / camera_scale
    camera_y = player.rect.centery - (HEIGHT // 2) / camera_scale

    if state == GAME and not inventory_open:
        mouse_pressed = pg.mouse.get_pressed()
        if mouse_pressed[0]:
            mouse_x, mouse_y = pg.mouse.get_pos()
            world_x = (mouse_x / camera_scale) + camera_x
            world_y = (mouse_y / camera_scale) + camera_y

            if dragon.active and dragon.rect.collidepoint((world_x, world_y)) and player.rect.y < -2000 * BLOCK_SIZE:
                if math.hypot(dragon.rect.centerx - player.rect.centerx, dragon.rect.centery - player.rect.centery) <= PLACE_DISTANCE:
                    dragon.health -= 2
                    if dragon.health <= 0:
                        dragon.active = False
                        island_center_x = 100
                        bowl_y = -2042  # Чаша піднята на 2 блоки вище (було -2040)
                        
                        # =====================================
                        # Будуємо Чашу із Бедроку (піднята на 2 блоки вище)
                        # =====================================
                        
                        # 1. Основа чаші (Бедрок)
                        for bx in range(island_center_x - 3, island_center_x + 4):
                            add_block(Block(bx * BLOCK_SIZE, (bowl_y + 2) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "bedrock.png"))
                        
                        # 2. Лівий і правий виступи (Бедрок)
                        add_block(Block((island_center_x - 3) * BLOCK_SIZE, (bowl_y + 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "bedrock.png"))
                        add_block(Block((island_center_x + 3) * BLOCK_SIZE, (bowl_y + 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "bedrock.png"))
                        
                        # 3. Центральний високий стовп (Бедрок)
                        for cy in range(bowl_y - 2, bowl_y + 2):
                            add_block(Block(island_center_x * BLOCK_SIZE, cy * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "bedrock.png"))
                            
                        # 4. Портал у чаші (portal.png замість води)
                        for px in range(island_center_x - 2, island_center_x):
                            add_block(Block(px * BLOCK_SIZE, (bowl_y + 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "portal.png"))
                        for px in range(island_center_x + 1, island_center_x + 3):
                            add_block(Block(px * BLOCK_SIZE, (bowl_y + 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "portal.png"))

                        # 5. Червоне яйце на верхівці центрального стовпа
                        add_block(Block(island_center_x * BLOCK_SIZE, (bowl_y - 3) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "dragon_egg.png"))
            
            hit_fish = None
            for f in fishes:
                if f.rect.collidepoint((world_x, world_y)):
                    if math.hypot(f.rect.centerx - player.rect.centerx, f.rect.centery - player.rect.centery) <= PLACE_DISTANCE:
                        hit_fish = f
                        break
            if hit_fish:
                drop_item_at_pos("fish.png", hit_fish.rect.centerx, hit_fish.rect.centery)
                fishes.remove(hit_fish)
            else:
                grid_x = int(world_x // BLOCK_SIZE) * BLOCK_SIZE
                grid_y = int(world_y // BLOCK_SIZE) * BLOCK_SIZE

                distance = math.hypot(grid_x - player.rect.centerx, grid_y - player.rect.centery)

                if distance <= PLACE_DISTANCE:
                    target_block = get_block_at(grid_x, grid_y)
                    
                    if target_block is not None and target_block.texture in ["water.png", "lava.png", "portal.png", "potal_ad.png"] and not is_creative:
                        target_block = None

                    if target_block is not None and (target_block.texture != "bedrock.png" or is_creative):
                        if mining_block != target_block:
                            if mining_block is not None:
                                mining_block.mining_progress = 0.0
                            mining_block = target_block
                            mining_timer = 0.0

                        multiplier = 1.0
                        if is_creative:
                            multiplier = 999.0
                        else:
                            active_item = hotbar[selected_block]
                            if active_item is not None:
                                tool_tex = active_item["texture"]
                                block_tex = mining_block.texture

                                speed_val = 1.0
                                if "wood" in tool_tex: speed_val = 2.0
                                elif "stone" in tool_tex: speed_val = 4.0
                                elif "iron" in tool_tex: speed_val = 7.0
                                elif "gold" in tool_tex: speed_val = 9.0
                                elif "diamond" in tool_tex: speed_val = 12.0
                                elif "netherite" in tool_tex: speed_val = 16.0

                                if "pickaxe" in tool_tex and block_tex in ["stone.png", "cobblestone.png", "basalt.png", "furnace.png", "chest.png", "coal_ore.png", "iron_ore.png", "gold_ore.png", "diamond_ore.png", "netherite_ore.png", "cloud_ore.png", "netherrack.png", "nether_gold_ore.png", "gold_block.png", "iron_block.png", "diamond_block.png", "netherite_block.png", "end_stone.png", "obsidian.png"]:
                                    multiplier = speed_val
                                elif "shovel" in tool_tex and block_tex in ["dirt.png", "grass.png", "snow_grass.png", "farmland.png", "sand.png"]:
                                    multiplier = speed_val
                                elif "axe" in tool_tex and block_tex in ["wood.png", "crafting_table.png", "door_closed.png", "door_open.png"]:
                                    multiplier = speed_val

                        mining_timer += multiplier
                        max_duration = BLOCK_DURATIONS.get(mining_block.texture, DEFAULT_DURATION)
                        mining_block.mining_progress = min(1.0, mining_timer / max_duration)

                        if mining_timer >= max_duration:
                            is_kelp = isinstance(mining_block, KelpBlock)
                            bx, by = mining_block.rect.x, mining_block.rect.y

                            if not is_creative:
                                active_item = hotbar[selected_block]
                                has_pickaxe = active_item is not None and "pickaxe" in active_item["texture"]
                                has_stone_pick = active_item is not None and ("stone" in active_item["texture"] or "iron" in active_item["texture"] or "diamond" in active_item["texture"] or "netherite" in active_item["texture"])
                                has_iron_pick = active_item is not None and ("iron" in active_item["texture"] or "diamond" in active_item["texture"] or "netherite" in active_item["texture"])
                                has_diamond_pick = active_item is not None and ("diamond" in active_item["texture"] or "netherite" in active_item["texture"])
                                has_netherite_pick = active_item is not None and "netherite_pickaxe" in active_item["texture"]

                                drop_allowed = True
                                if mining_block.texture in ["stone.png", "cobblestone.png", "basalt.png", "furnace.png", "chest.png", "coal_ore.png", "iron_ore.png", "gold_ore.png", "diamond_ore.png", "netherite_ore.png", "cloud_ore.png", "netherrack.png", "nether_gold_ore.png", "gold_block.png", "iron_block.png", "diamond_block.png", "netherite_block.png", "end_stone.png", "obsidian.png"]:
                                    if not has_pickaxe:
                                        drop_allowed = False

                                if drop_allowed:
                                    if mining_block.texture == "stone.png":
                                        dropped_texture = "cobblestone.png"
                                    elif mining_block.texture == "coal_ore.png":
                                        dropped_texture = "coal.png"
                                    elif mining_block.texture == "iron_ore.png":
                                        if has_stone_pick: dropped_texture = "iron_ore.png"
                                        else: drop_allowed = False
                                    elif mining_block.texture == "gold_ore.png":
                                        if has_iron_pick: dropped_texture = "gold_ore.png"
                                        else: drop_allowed = False
                                    elif mining_block.texture == "diamond_ore.png":
                                        if has_iron_pick: dropped_texture = "diamond.png"
                                        else: drop_allowed = False
                                    elif mining_block.texture == "netherite_ore.png":
                                        if has_diamond_pick: dropped_texture = "netherite_scrap.png"
                                        else: drop_allowed = False
                                    elif mining_block.texture == "cloud_ore.png":
                                        if has_netherite_pick: dropped_texture = "cloud_ore.png"
                                        else: drop_allowed = False
                                    elif mining_block.texture == "nether_gold_ore.png":
                                        dropped_texture = "gold_ingot.png" 
                                    elif mining_block.texture in ["grass.png", "snow_grass.png"]:
                                        dropped_texture = "dirt.png"
                                    elif mining_block.texture in ["door_closed.png", "door_open.png"]:
                                        dropped_texture = "door_closed.png"
                                    elif mining_block.texture == "end_crystal.png":
                                        dropped_texture = "end_crystal.png"
                                    elif mining_block.texture == "leaves.png":
                                        drop_allowed = False
                                        if random.random() < 0.20: drop_item_at_pos("stick.png", bx + 12, by + 12)
                                        if random.random() < 0.10: drop_item_at_pos("string.png", bx + 12, by + 12)
                                    elif mining_block.texture == "tall_grass.png":
                                        drop_allowed = False
                                        if random.random() < 0.30: drop_item_at_pos("seeds.png", bx + 12, by + 12)
                                        if random.random() < 0.15: drop_item_at_pos("rice.png", bx + 12, by + 12)
                                    elif isinstance(mining_block, WheatBlock):
                                        if mining_block.stage == 3:
                                            drop_item_at_pos("wheat.png", bx + 12, by + 12)
                                            drop_item_at_pos("seeds.png", bx + 12, by + 12, count=random.randint(1, 2))
                                        else: drop_item_at_pos("seeds.png", bx + 12, by + 12)
                                        drop_allowed = False
                                    elif isinstance(mining_block, PotatoBlock):
                                        if mining_block.stage == 3:
                                            drop_item_at_pos("potato.png", bx + 12, by + 12, count=random.randint(2, 4))
                                        else: drop_item_at_pos("potato.png", bx + 12, by + 12)
                                        drop_allowed = False
                                    elif isinstance(mining_block, RiceBlock) or mining_block.texture == "rice_stage1.png":
                                        drop_item_at_pos("rice.png", bx + 12, by + 12, count=random.randint(1, 2))
                                        drop_allowed = False
                                    elif is_kelp:
                                        if mining_block.stage == 3:
                                            drop_item_at_pos("kelp.png", bx + 12, by + 12, count=random.randint(1, 2))
                                        else: drop_item_at_pos("kelp.png", bx + 12, by + 12)
                                        drop_allowed = False
                                    else:
                                        dropped_texture = mining_block.texture

                                    if drop_allowed:
                                        drop_item_at_pos(dropped_texture, bx + 12, by + 12)

                            if mining_block.texture == "chest.png":
                                pos_key = (mining_block.rect.x, mining_block.rect.y)
                                if pos_key in chests_data:
                                    for item in chests_data[pos_key]:
                                        if item:
                                            drop_item_at_pos(item["texture"], bx+12, by+12, item["count"])
                                    del chests_data[pos_key]

                            solid_placed_blocks.discard((mining_block.rect.x, mining_block.rect.y))
                            remove_block(mining_block)

                            if is_kelp:
                                add_block(Block(bx, by, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), "water.png"))

                            mining_block = None
                            mining_timer = 0.0
                    else:
                        if mining_block is not None:
                            mining_block.mining_progress = 0.0
                            mining_block = None
                            mining_timer = 0.0
                else:
                    if mining_block is not None:
                        mining_block.mining_progress = 0.0
                        mining_block = None
                        mining_timer = 0.0
        else:
            if mining_block is not None:
                mining_block.mining_progress = 0.0
                mining_block = None
                mining_timer = 0.0

    for e in pg.event.get():
        if e.type == pg.QUIT:
            running = False

        elif e.type == pg.KEYDOWN:

            if e.key == pg.K_F11:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
                    camera_scale = 1.5
                    WIDTH, HEIGHT = screen.get_size()
                else:
                    screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    camera_scale = 1.0
                    WIDTH, HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT
                continue

            if state == WORKBENCH:
                if e.key == pg.K_ESCAPE or e.key == pg.K_e:
                    for stack in workbench_grid:
                        if stack is not None:
                            add_to_inventory(stack["texture"], stack["count"])
                    workbench_grid[:] = [None] * 9
                    state = GAME
                    continue

            if state == FURNACE:
                if e.key == pg.K_ESCAPE or e.key == pg.K_e:
                    state = GAME
                    continue

            if state == CHEST_MENU:
                if e.key == pg.K_ESCAPE or e.key == pg.K_e:
                    state = GAME
                    active_chest_pos = None
                    continue

            if inventory_open and selected_inventory_slot is not None:
                if pg.K_1 <= e.key <= pg.K_9:
                    num_slot = e.key - pg.K_1
                    inventory[selected_inventory_slot], hotbar[num_slot] = hotbar[num_slot], inventory[selected_inventory_slot]
                    selected_inventory_slot = None
                    continue

            if e.key == pg.K_f and not inventory_open:
                hotbar[selected_block], left_hand_slot = left_hand_slot, hotbar[selected_block]
                continue

            if e.key == pg.K_q and not inventory_open and hotbar[selected_block] is not None:
                if hotbar[selected_block]["texture"] == "ender_pearl.png":
                    m_x, m_y = pg.mouse.get_pos()
                    world_mouse_x = int((m_x / camera_scale) + camera_x)
                    world_mouse_y = int((m_y / camera_scale) + camera_y)
                    
                    player.rect.x = world_mouse_x
                    player.rect.y = world_mouse_y
                    if not is_creative:
                        player.health -= 2
                        hotbar[selected_block]["count"] -= 1
                        if hotbar[selected_block]["count"] <= 0:
                            hotbar[selected_block] = None
                    continue

                if is_creative:
                    hotbar[selected_block] = None
                else:
                    texture = hotbar[selected_block]["texture"]
                    drop_item_towards_cursor(texture, count=1)
                    hotbar[selected_block]["count"] -= 1
                    if hotbar[selected_block]["count"] <= 0:
                        hotbar[selected_block] = None

            if state == GAME:
                if e.key == pg.K_ESCAPE:
                    state = PAUSE
                    if mining_block is not None:
                        mining_block.mining_progress = 0.0
                        mining_block = None
                        mining_timer = 0.0
                    continue

                if e.key == pg.K_e:
                    inventory_open = not inventory_open
                    if mining_block is not None:
                        mining_block.mining_progress = 0.0
                        mining_block = None
                        mining_timer = 0.0

                elif pg.K_1 <= e.key <= pg.K_9:
                    selected_block = e.key - pg.K_1

        elif e.type == pg.MOUSEBUTTONDOWN:

            if inventory_open and state == GAME:
                handle_inventory_click(e.pos)
                continue

            if state == WORKBENCH:
                if e.button == 1 and get_recipes_btn_rect().collidepoint(e.pos):
                    state = RECIPES_MENU
                    continue

                inventory_slot = get_inventory_slot_at(e.pos, offset_y=40)
                if inventory_slot is not None:
                    if selected_inventory_slot is None:
                        selected_inventory_slot = inventory_slot
                    elif selected_inventory_slot == inventory_slot:
                        selected_inventory_slot = None
                    else:
                        inventory[selected_inventory_slot], inventory[inventory_slot] = inventory[inventory_slot], inventory[selected_inventory_slot]
                        selected_inventory_slot = None
                    continue

                hotbar_slot = get_hotbar_slot_at(e.pos)
                if hotbar_slot is not None:
                    if selected_inventory_slot is None:
                        selected_block = hotbar_slot
                    else:
                        hotbar[hotbar_slot], inventory[selected_inventory_slot] = (
                            inventory[selected_inventory_slot], hotbar[hotbar_slot]
                        )
                        selected_block = hotbar_slot
                        selected_inventory_slot = None
                    continue

                if e.button != 1:
                    continue

                clicked = False

                for i in range(9):
                    rect = get_workbench_slot_rect(i)
                    if rect.collidepoint(e.pos):
                        clicked = True

                        if selected_inventory_slot is not None and inventory[selected_inventory_slot] is not None:
                            source = inventory[selected_inventory_slot]

                            if workbench_grid[i] is None:
                                workbench_grid[i] = {
                                    "texture": source["texture"],
                                    "count": 1
                                }
                                source["count"] -= 1
                                if source["count"] <= 0:
                                    inventory[selected_inventory_slot] = None
                                    selected_inventory_slot = None

                            elif workbench_grid[i]["texture"] == source["texture"] and workbench_grid[i]["count"] < MAX_STACK_SIZE:
                                workbench_grid[i]["count"] += 1
                                source["count"] -= 1
                                if source["count"] <= 0:
                                    inventory[selected_inventory_slot] = None
                                    selected_inventory_slot = None

                        elif workbench_grid[i] is not None:
                            stack = workbench_grid[i]
                            if add_to_inventory(stack["texture"], stack["count"]):
                                workbench_grid[i] = None
                        break

                if not clicked and get_workbench_result_rect().collidepoint(e.pos):
                    result = get_workbench_result()
                    if result:
                        texture, amount = result
                        if add_to_inventory(texture, amount):
                            for i in range(9):
                                if workbench_grid[i] is not None:
                                    workbench_grid[i]["count"] -= 1
                                    if workbench_grid[i]["count"] <= 0:
                                        workbench_grid[i] = None
                continue

            if state == FURNACE:
                inventory_slot = get_inventory_slot_at(e.pos, offset_y=40)
                if inventory_slot is not None:
                    if selected_inventory_slot is None:
                        selected_inventory_slot = inventory_slot
                    elif selected_inventory_slot == inventory_slot:
                        selected_inventory_slot = None
                    else:
                        inventory[selected_inventory_slot], inventory[inventory_slot] = inventory[inventory_slot], inventory[selected_inventory_slot]
                        selected_inventory_slot = None
                    continue

                hotbar_slot = get_hotbar_slot_at(e.pos)
                if hotbar_slot is not None:
                    if selected_inventory_slot is None:
                        selected_block = hotbar_slot
                    else:
                        hotbar[hotbar_slot], inventory[selected_inventory_slot] = (
                            inventory[selected_inventory_slot], hotbar[hotbar_slot]
                        )
                        selected_block = hotbar_slot
                        selected_inventory_slot = None
                    continue

                if e.button != 1:
                    continue

                for i in range(3):
                    rect = get_furnace_slot_rect(i)
                    if rect.collidepoint(e.pos):
                        if i == 2:
                            if furnace_grid[2] is not None:
                                stack = furnace_grid[2]
                                if add_to_inventory(stack["texture"], stack["count"]):
                                    furnace_grid[2] = None
                        else:
                            if selected_inventory_slot is not None and inventory[selected_inventory_slot] is not None:
                                source = inventory[selected_inventory_slot]
                                if furnace_grid[i] is None:
                                    furnace_grid[i] = {"texture": source["texture"], "count": 1}
                                    source["count"] -= 1
                                    if source["count"] <= 0:
                                        inventory[selected_inventory_slot] = None
                                        selected_inventory_slot = None
                                elif furnace_grid[i]["texture"] == source["texture"] and furnace_grid[i]["count"] < MAX_STACK_SIZE:
                                    furnace_grid[i]["count"] += 1
                                    source["count"] -= 1
                                    if source["count"] <= 0:
                                        inventory[selected_inventory_slot] = None
                                        selected_inventory_slot = None
                            elif furnace_grid[i] is not None:
                                stack = furnace_grid[i]
                                if add_to_inventory(stack["texture"], stack["count"]):
                                    furnace_grid[i] = None
                        break
                continue

            if state == CHEST_MENU:
                inventory_slot = get_inventory_slot_at(e.pos, offset_y=40)
                if inventory_slot is not None:
                    if selected_inventory_slot is None:
                        selected_inventory_slot = inventory_slot
                    elif selected_inventory_slot == inventory_slot:
                        selected_inventory_slot = None
                    else:
                        inventory[selected_inventory_slot], inventory[inventory_slot] = inventory[inventory_slot], inventory[selected_inventory_slot]
                        selected_inventory_slot = None
                    continue

                hotbar_slot = get_hotbar_slot_at(e.pos)
                if hotbar_slot is not None:
                    if selected_inventory_slot is None:
                        selected_block = hotbar_slot
                    else:
                        hotbar[hotbar_slot], inventory[selected_inventory_slot] = (
                            inventory[selected_inventory_slot], hotbar[hotbar_slot]
                        )
                        selected_block = hotbar_slot
                        selected_inventory_slot = None
                    continue

                if e.button != 1:
                    continue

                chest_inv = chests_data.get(active_chest_pos)
                for i in range(27):
                    rect = get_chest_slot_rect(i)
                    if rect.collidepoint(e.pos):
                        if selected_inventory_slot is not None and inventory[selected_inventory_slot] is not None:
                            source = inventory[selected_inventory_slot]
                            if chest_inv[i] is None:
                                chest_inv[i] = {"texture": source["texture"], "count": source["count"]}
                                inventory[selected_inventory_slot] = None
                                selected_inventory_slot = None
                            elif chest_inv[i]["texture"] == source["texture"]:
                                transfer = min(source["count"], MAX_STACK_SIZE - chest_inv[i]["count"])
                                chest_inv[i]["count"] += transfer
                                source["count"] -= transfer
                                if source["count"] <= 0:
                                    inventory[selected_inventory_slot] = None
                                    selected_inventory_slot = None
                        elif chest_inv[i] is not None:
                            if add_to_inventory(chest_inv[i]["texture"], chest_inv[i]["count"]):
                                chest_inv[i] = None
                        break
                continue

            if state == GAME and not inventory_open:
                mouse_x, mouse_y = pg.mouse.get_pos()
                world_x = (mouse_x / camera_scale) + camera_x
                world_y = (mouse_y / camera_scale) + camera_y

                grid_x = int(world_x // BLOCK_SIZE) * BLOCK_SIZE
                grid_y = int(world_y // BLOCK_SIZE) * BLOCK_SIZE

                distance = math.hypot(grid_x - player.rect.centerx, grid_y - player.rect.centery)

                if distance <= PLACE_DISTANCE:
                    if e.button == 3:
                        block = get_block_at(grid_x, grid_y)
                        active_item = hotbar[selected_block]

                        # Механіка відра
                        if active_item and active_item["texture"] == "bucket.png":
                            if block and block.texture in ["water.png", "lava.png"]:
                                fluid_type = "water_bucket.png" if block.texture == "water.png" else "lava_bucket.png"
                                remove_block(block)
                                active_item["count"] -= 1
                                if active_item["count"] <= 0:
                                    hotbar[selected_block] = {"texture": fluid_type, "count": 1}
                                else:
                                    add_to_inventory(fluid_type, 1)
                                continue

                        elif active_item and active_item["texture"] in ["water_bucket.png", "lava_bucket.png"]:
                            if block is None or block.texture in ["tall_grass.png", "potal_ad.png"]:
                                if block: remove_block(block)
                                fluid = "water.png" if active_item["texture"] == "water_bucket.png" else "lava.png"
                                add_block(Block(grid_x, grid_y, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255), fluid))
                                hotbar[selected_block] = {"texture": "bucket.png", "count": 1}
                                continue

                        if block is not None:
                            if block.texture == "obsidian.png":
                                if try_activate_nether_portal(grid_x // BLOCK_SIZE, grid_y // BLOCK_SIZE):
                                    continue
                            elif block.texture == "crafting_table.png":
                                state = WORKBENCH
                                continue
                            elif block.texture == "furnace.png":
                                state = FURNACE
                                continue
                            elif block.texture == "chest.png":
                                state = CHEST_MENU
                                active_chest_pos = (block.rect.x, block.rect.y)
                                if active_chest_pos not in chests_data:
                                    chests_data[active_chest_pos] = [None] * 27
                                continue
                            elif block.texture == "bed.png":
                                total_minutes = int((day_time / DAY_DURATION) * 24 * 60)
                                hours = (total_minutes // 60) % 24
                                if hours >= 18 or hours < 6:
                                    day_time = (6.0 / 24.0) * DAY_DURATION
                                    print("Ви поспали. Настав ранок!")
                                else:
                                    print("Спати можна лише вночі!")
                                continue
                            elif block.texture == "door_closed.png":
                                block.texture = "door_open.png"
                                continue
                            elif block.texture == "door_open.png":
                                block.texture = "door_closed.png"
                                continue
                            
                            if active_item is not None and active_item["texture"] in ["wood_hoe.png", "stone_hoe.png", "iron_hoe.png", "gold_hoe.png", "diamond_hoe.png", "netherite_hoe.png"]:
                                if block.texture in ["grass.png", "snow_grass.png", "dirt.png"]:
                                    block.texture = "farmland.png"
                                    continue

                        if block is not None:
                            continue

                        if active_item is None:
                            continue

                        if active_item["texture"] in [
                            "seeds.png", "wheat.png", "bread.png", "baked_potato.png", "potato.png", "rice.png", "sushi.png",
                            "kelp.png", "dried_kelp.png", "coal.png", "iron_ingot.png", "gold_ingot.png", "diamond.png", "netherite_scrap.png", 
                            "netherite_ingot.png", "fishing_rod.png", "fish.png", "cooked_fish.png", "heaven_shard.png", "heaven_ingot.png", "flight_emblem.png",
                            "ender_pearl.png", "bucket.png", "water_bucket.png", "lava_bucket.png"
                        ]:
                            continue

                        tex_name = active_item["texture"]
                        if "_pickaxe.png" in tex_name or "_axe.png" in tex_name or "_shovel.png" in tex_name or "_hoe.png" in tex_name or "string.png" in tex_name or "stick.png" in tex_name:
                            continue

                        if active_item["texture"] == "sand.png":
                            new_block = SandBlock(grid_x, grid_y)
                        elif active_item["texture"] == "door_closed.png":
                            above_block = get_block_at(grid_x, grid_y - BLOCK_SIZE)
                            if above_block is None:
                                new_block = Block(
                                    grid_x,
                                    grid_y - BLOCK_SIZE,
                                    BLOCK_SIZE,
                                    BLOCK_SIZE * 2,
                                    (255, 255, 255),
                                    "door_closed.png"
                                )
                            else:
                                continue
                        else:
                            new_block = Block(
                                grid_x,
                                grid_y,
                                BLOCK_SIZE,
                                BLOCK_SIZE,
                                (255, 255, 255),
                                active_item["texture"]
                            )

                        if not player.collide(new_block):
                            add_block(new_block)
                            if new_block.texture in ["wood.png", "leaves.png", "cactus.png", "door_closed.png", "chest.png", "bed.png", "wool.png", "obsidian.png"]:
                                solid_placed_blocks.add((new_block.rect.x, new_block.rect.y))

                            if not is_creative: 
                                active_item["count"] -= 1
                                if active_item["count"] <= 0:
                                    hotbar[selected_block] = None

    player.update()
    player.jump()
    player.apply_gravity()

    for dropped_item in dropped_items[:]:
        if dropped_item.update():
            dropped_items.remove(dropped_item)

    r = int((10 + (80 * time_factor)) * weather_sky_darkness)
    g = int((15 + (175 * time_factor)) * weather_sky_darkness)
    b = int((30 + (225 * time_factor)) * weather_sky_darkness)
    base_sky_color = (r, g, b)

    screen.fill(get_sky_color(player.rect.y, base_sky_color))
    
    for gx in range(start_gx, end_gx + 1):
        for gy in range(start_gy, end_gy + 1):
            block = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
            if block:
                block.draw(screen, camera_x, camera_y)

    for f in fishes:
        f.draw(screen, camera_x, camera_y)

    for dropped_item in dropped_items:
        dropped_item.draw(screen, camera_x, camera_y)

    player.draw(screen, camera_x, camera_y)
    dragon.draw(screen, camera_x, camera_y)
    for enderman in endermen:
        enderman.draw(screen, camera_x, camera_y)
    
    for fb in dragon_fireballs:
        fb.draw(screen, camera_x, camera_y)

    if dragon.active and player.rect.y < -2000 * BLOCK_SIZE and hasattr(dragon, 'crystal_link'):
        d_cx = int((dragon.rect.centerx - camera_x) * camera_scale)
        d_cy = int((dragon.rect.centery - camera_y) * camera_scale)
        c_cx = int((dragon.crystal_link[0] - camera_x) * camera_scale)
        c_cy = int((dragon.crystal_link[1] - camera_y) * camera_scale)
        pg.draw.line(screen, (255, 105, 180), (d_cx, d_cy), (c_cx, c_cy), 2)

    draw_weather()

    if fishing_bite:
        curr_time = pg.time.get_ticks()
        p_x = int((player.rect.centerx - camera_x) * camera_scale)
        p_y = int((player.rect.centery - camera_y) * camera_scale)

        if curr_time < fishing_timer:
            pg.draw.line(screen, (200, 200, 200), (p_x, p_y), (p_x + 100, p_y + 120), 1)
            pg.draw.circle(screen, (255, 0, 0), (p_x + 100, p_y + 120), 4)
        else:
            fishing_particle_timer += 1
            pg.draw.line(screen, (200, 200, 200), (p_x, p_y), (p_x + 100, p_y + 125 + (fishing_particle_timer % 5)), 1)
            pg.draw.circle(screen, (0, 191, 255), (p_x + 100, p_y + 125), 8, 2) 
            pg.draw.circle(screen, (255, 255, 255), (p_x + 100, p_y + 125), 3)

            m_buttons = pg.mouse.get_pressed()
            if m_buttons[2]:
                state = FISHING_GAME
                fishing_catch_progress = 50.0

            if curr_time > fishing_timer + 2500:
                fishing_bite = False

    # =====================================
    # СИСТЕМА ТЕМРЯВИ 
    # =====================================
    light_mask = pg.Surface((WIDTH, HEIGHT))
    light_mask.fill((0, 0, 0)) 

    sky_light_level = int(255 * time_factor * weather_sky_darkness)

    if player.rect.y < OVERWORLD_HEIGHT * BLOCK_SIZE:
        depth_factor = 1.0 - max(0.0, min(1.0, (player.rect.y - (OVERWORLD_START + 15)*BLOCK_SIZE) / (BLOCK_SIZE * 20)))
        ambient_light = int(sky_light_level * depth_factor)
        light_mask.fill((ambient_light, ambient_light, ambient_light))
    else:
        light_mask.fill((205, 125, 115))

    if player.rect.y < HEAVEN_BOTTOM * BLOCK_SIZE:
        light_mask.fill((255, 255, 255))

    light_sources = []


    

    active_item = hotbar[selected_block]
    if (active_item and active_item["texture"] == "torch.png") or (left_hand_slot and left_hand_slot["texture"] == "torch.png"):
        px_grid = int(player.rect.centerx // BLOCK_SIZE) * BLOCK_SIZE
        py_grid = int(player.rect.centery // BLOCK_SIZE) * BLOCK_SIZE
        light_sources.append((px_grid, py_grid, 3)) 

    for gx in range(start_gx, end_gx + 1):
        for gy in range(start_gy, end_gy + 1):
            block = blocks_map.get((gx * BLOCK_SIZE, gy * BLOCK_SIZE))
            if block:
                if block.texture == "torch.png":
                    light_sources.append((block.rect.x, block.rect.y, 4)) 
                elif block.texture == "lava.png":
                    light_sources.append((block.rect.x, block.rect.y, 3)) 

    for lx, ly, max_blocks_dist in light_sources:
        for dx in range(-max_blocks_dist, max_blocks_dist + 1):
            for dy in range(-max_blocks_dist, max_blocks_dist + 1):
                dist = abs(dx) + abs(dy)
                if dist <= max_blocks_dist:
                    bx = lx + dx * BLOCK_SIZE
                    by = ly + dy * BLOCK_SIZE
                    brightness = int(255 * (1.0 - (dist / (max_blocks_dist + 1))))
                    screen_bx = int((bx - camera_x) * camera_scale)
                    screen_by = int((by - camera_y) * camera_scale)
                    scaled_size = int(BLOCK_SIZE * camera_scale)
                    
                    if 0 <= screen_bx < WIDTH and 0 <= screen_by < HEIGHT:
                        block_light_surf = pg.Surface((scaled_size, scaled_size))
                        block_light_surf.fill((brightness, brightness, brightness))
                        light_mask.blit(block_light_surf, (screen_bx, screen_by), special_flags=pg.BLEND_MAX)

    screen.blit(light_mask, (0, 0), special_flags=pg.BLEND_MULT)

    if state == WORKBENCH:
        draw_workbench()
    elif state == FURNACE:
        draw_furnace_menu()
    elif state == CHEST_MENU:  
        draw_chest_menu()
    elif state == RECIPES_MENU:
        draw_recipes_menu()

    draw_hotbar()
    draw_hud()
    draw_clock()

    pg.display.flip()
    clk.tick(60)

pg.quit()


