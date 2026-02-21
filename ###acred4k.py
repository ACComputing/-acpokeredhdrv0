import pygame
import random
import sys

# ==================== INITIALIZATION ====================
pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokémon Red (All Maps with Houses)")
clock = pygame.time.Clock()
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 150, 0)
BLUE = (0, 0, 255)          # For doors

# ==================== MAP CLASS ====================
class Map:
    def __init__(self, name, width, height, walls, grass, wild_pokemon, exits, doors=None):
        self.name = name
        self.width = width
        self.height = height
        self.walls = walls                # list of pygame.Rect (collidable)
        self.grass = grass                # list of pygame.Rect (wild encounters)
        self.wild_pokemon = wild_pokemon  # list of species names
        self.exits = exits                 # dict: "up"/"down"/"left"/"right" -> (map_name, x, y)
        self.doors = doors if doors else [] # list of (rect, target_map, spawn_x, spawn_y)

    def check_collision(self, rect):
        for wall in self.walls:
            if wall.colliderect(rect):
                return True
        return False

    def is_grass(self, rect):
        for g in self.grass:
            if g.colliderect(rect):
                return True
        return False

    def get_door(self, rect):
        for door_rect, target_map, spawn_x, spawn_y in self.doors:
            if door_rect.colliderect(rect):
                return target_map, spawn_x, spawn_y
        return None

    def draw(self, surface):
        surface.fill(GRAY)
        for wall in self.walls:
            pygame.draw.rect(surface, BROWN, wall)
        for g in self.grass:
            pygame.draw.rect(surface, DARK_GREEN, g)
        for door_rect, _, _, _ in self.doors:
            pygame.draw.rect(surface, BLUE, door_rect)

# ==================== PLAYER CLASS ====================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 16
        self.rect = pygame.Rect(x, y, 16, 16)
        self.in_battle = False

    def move(self, dx, dy, game_map):
        new_rect = self.rect.move(dx, dy)
        if not game_map.check_collision(new_rect):
            self.rect = new_rect
            self.x += dx
            self.y += dy
            return True
        return False

    def update(self, keys, game_map):
        if self.in_battle:
            return None
        moved = False
        if keys[pygame.K_LEFT]:
            moved = self.move(-self.speed, 0, game_map)
        elif keys[pygame.K_RIGHT]:
            moved = self.move(self.speed, 0, game_map)
        elif keys[pygame.K_UP]:
            moved = self.move(0, -self.speed, game_map)
        elif keys[pygame.K_DOWN]:
            moved = self.move(0, self.speed, game_map)

        if moved and game_map.is_grass(self.rect):
            if random.randint(1, 100) <= 10:
                self.in_battle = True
                return Battle(self, random.choice(game_map.wild_pokemon))
        return None

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)

# ==================== BATTLE CLASS ====================
class Battle:
    def __init__(self, player, wild_pokemon):
        self.player = player
        self.player_pokemon = {"name": "Charmander", "hp": 20, "max_hp": 20, "attack": 10}
        self.wild_pokemon = {"name": wild_pokemon, "hp": 15, "max_hp": 15, "attack": 8}
        self.turn = "player"
        self.message = f"A wild {wild_pokemon} appeared!"
        self.battle_over = False
        self.player_won = False

    def handle_input(self, keys):
        if self.battle_over or self.turn != "player":
            return
        if keys[pygame.K_a]:
            self.player_attack()

    def player_attack(self):
        damage = self.player_pokemon["attack"] - 2
        self.wild_pokemon["hp"] -= damage
        self.message = f"Charmander dealt {damage} damage!"
        if self.wild_pokemon["hp"] <= 0:
            self.wild_pokemon["hp"] = 0
            self.message = f"Wild {self.wild_pokemon['name']} fainted!"
            self.battle_over = True
            self.player_won = True
            return
        self.turn = "enemy"

    def enemy_attack(self):
        damage = self.wild_pokemon["attack"] - 2
        self.player_pokemon["hp"] -= damage
        self.message = f"{self.wild_pokemon['name']} dealt {damage} damage!"
        if self.player_pokemon["hp"] <= 0:
            self.player_pokemon["hp"] = 0
            self.message = "Your Charmander fainted!"
            self.battle_over = True
            self.player_won = False
            return
        self.turn = "player"

    def update(self):
        if self.battle_over:
            return
        if self.turn == "enemy":
            self.enemy_attack()

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 24)
        player_text = f"{self.player_pokemon['name']} HP: {self.player_pokemon['hp']}/{self.player_pokemon['max_hp']}"
        player_surf = font.render(player_text, True, WHITE)
        surface.blit(player_surf, (50, 250))
        enemy_text = f"Wild {self.wild_pokemon['name']} HP: {self.wild_pokemon['hp']}/{self.wild_pokemon['max_hp']}"
        enemy_surf = font.render(enemy_text, True, WHITE)
        surface.blit(enemy_surf, (350, 50))
        msg_surf = font.render(self.message, True, WHITE)
        surface.blit(msg_surf, (50, 300))
        inst_surf = font.render("Press A to attack", True, WHITE)
        surface.blit(inst_surf, (50, 350))
        if self.battle_over:
            over_surf = font.render("Battle over! Press SPACE to continue.", True, WHITE)
            surface.blit(over_surf, (150, 200))

# ==================== DEFINE ALL MAPS ====================

# ----- Interior Maps (Houses) -----
# House 1 in Pallet Town
house1_walls = [
    pygame.Rect(0, 0, 600, 16),    # top border
    pygame.Rect(0, 0, 16, 400),    # left border
    pygame.Rect(584, 0, 16, 400),  # right border
    pygame.Rect(0, 384, 600, 16),  # bottom border
    pygame.Rect(200, 150, 16, 16), # table/object
    pygame.Rect(300, 200, 32, 32), # bed/couch
]
house1_grass = []
house1_wild = []
house1_exits = {}  # no edge exits, only door
house1_doors = [
    (pygame.Rect(300, 350, 32, 16), "Pallet Town", 120, 120)  # door near bottom; exit to outside near house
]
house1 = Map("Pallet House 1", 600, 400, house1_walls, house1_grass, house1_wild, house1_exits, house1_doors)

# House 2 in Pallet Town
house2_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(150, 100, 64, 64),  # big table
    pygame.Rect(400, 250, 16, 16),
]
house2_grass = []
house2_wild = []
house2_exits = {}
house2_doors = [
    (pygame.Rect(300, 350, 32, 16), "Pallet Town", 420, 220)  # exit to near second house
]
house2 = Map("Pallet House 2", 600, 400, house2_walls, house2_grass, house2_wild, house2_exits, house2_doors)

# House in Viridian City
viridian_house_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(250, 150, 50, 50),  # counter
]
viridian_house_grass = []
viridian_house_wild = []
viridian_house_exits = {}
viridian_house_doors = [
    (pygame.Rect(300, 350, 32, 16), "Viridian City", 170, 170)  # exit to near the building in Viridian
]
viridian_house = Map("Viridian House", 600, 400, viridian_house_walls, viridian_house_grass, viridian_house_wild, viridian_house_exits, viridian_house_doors)

# ----- Overworld Maps (with doors) -----

# 1. Pallet Town (modified: houses become doors)
pallet_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    # No house walls here; they are replaced by doors
]
pallet_grass = []
pallet_wild = []
pallet_exits = {"up": ("Route 1", 300, 380)}
pallet_doors = [
    (pygame.Rect(100, 100, 50, 50), "Pallet House 1", 300, 350),   # door to house1, spawn inside near door
    (pygame.Rect(400, 200, 60, 60), "Pallet House 2", 300, 350)    # door to house2
]
pallet = Map("Pallet Town", 600, 400, pallet_walls, pallet_grass, pallet_wild, pallet_exits, pallet_doors)

# 2. Route 1 (unchanged, no doors)
route1_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(200, 100, 16, 16),
    pygame.Rect(216, 100, 16, 16),
    pygame.Rect(200, 116, 16, 16),
]
route1_grass = [
    pygame.Rect(100, 200, 16, 16),
    pygame.Rect(116, 200, 16, 16),
    pygame.Rect(132, 200, 16, 16),
    pygame.Rect(100, 216, 16, 16),
    pygame.Rect(116, 216, 16, 16),
    pygame.Rect(132, 216, 16, 16),
    pygame.Rect(400, 300, 16, 16),
    pygame.Rect(416, 300, 16, 16),
    pygame.Rect(432, 300, 16, 16),
]
route1_wild = ["Rattata", "Pidgey"]
route1_exits = {
    "down": ("Pallet Town", 300, 20),
    "up": ("Viridian City", 300, 380),
}
route1 = Map("Route 1", 600, 400, route1_walls, route1_grass, route1_wild, route1_exits)

# 3. Viridian City (modified: add door for house)
viridian_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    # Buildings that are not enterable? Keep one as wall, one as door
    pygame.Rect(400, 80, 60, 60),   # this one remains a wall
]
viridian_grass = []
viridian_wild = []
viridian_exits = {
    "down": ("Route 1", 300, 20),
    "up": ("Route 2", 300, 380),
}
viridian_doors = [
    (pygame.Rect(150, 150, 80, 40), "Viridian House", 300, 350)   # door to house
]
viridian = Map("Viridian City", 600, 400, viridian_walls, viridian_grass, viridian_wild, viridian_exits, viridian_doors)

# 4. Route 2 (unchanged)
route2_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(250, 150, 16, 16),
    pygame.Rect(266, 150, 16, 16),
]
route2_grass = [
    pygame.Rect(100, 100, 16, 16),
    pygame.Rect(116, 100, 16, 16),
    pygame.Rect(132, 100, 16, 16),
    pygame.Rect(400, 200, 16, 16),
    pygame.Rect(416, 200, 16, 16),
]
route2_wild = ["Caterpie", "Weedle", "Pidgey"]
route2_exits = {
    "down": ("Viridian City", 300, 20),
    "up": ("Viridian Forest", 300, 380),
}
route2 = Map("Route 2", 600, 400, route2_walls, route2_grass, route2_wild, route2_exits)

# 5. Viridian Forest (unchanged)
forest_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    # Trees
    pygame.Rect(100, 100, 16, 16),
    pygame.Rect(116, 100, 16, 16),
    pygame.Rect(132, 100, 16, 16),
    pygame.Rect(148, 100, 16, 16),
    pygame.Rect(100, 116, 16, 16),
    pygame.Rect(148, 116, 16, 16),
    pygame.Rect(100, 132, 16, 16),
    pygame.Rect(148, 132, 16, 16),
    pygame.Rect(400, 250, 16, 16),
    pygame.Rect(416, 250, 16, 16),
    pygame.Rect(432, 250, 16, 16),
    pygame.Rect(400, 266, 16, 16),
    pygame.Rect(432, 266, 16, 16),
]
forest_grass = [
    pygame.Rect(200, 200, 16, 16),
    pygame.Rect(216, 200, 16, 16),
    pygame.Rect(232, 200, 16, 16),
    pygame.Rect(200, 216, 16, 16),
    pygame.Rect(232, 216, 16, 16),
    pygame.Rect(200, 232, 16, 16),
    pygame.Rect(216, 232, 16, 16),
]
forest_wild = ["Caterpie", "Metapod", "Weedle", "Kakuna", "Pikachu"]
forest_exits = {
    "down": ("Route 2", 300, 20),
    "up": ("Pewter City", 300, 380),
}
forest = Map("Viridian Forest", 600, 400, forest_walls, forest_grass, forest_wild, forest_exits)

# 6. Pewter City (add a door later if desired, but keep as is for now)
pewter_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(80, 80, 70, 50),
    pygame.Rect(300, 200, 80, 60),
    pygame.Rect(450, 100, 50, 50),
]
pewter_grass = []
pewter_wild = []
pewter_exits = {
    "down": ("Viridian Forest", 300, 20),
    "up": ("Route 3", 300, 380),
}
pewter = Map("Pewter City", 600, 400, pewter_walls, pewter_grass, pewter_wild, pewter_exits)

# 7. Route 3 (unchanged)
route3_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(200, 150, 16, 16),
    pygame.Rect(216, 150, 16, 16),
    pygame.Rect(232, 150, 16, 16),
    pygame.Rect(200, 166, 16, 16),
    pygame.Rect(232, 166, 16, 16),
]
route3_grass = [
    pygame.Rect(100, 200, 16, 16),
    pygame.Rect(116, 200, 16, 16),
    pygame.Rect(132, 200, 16, 16),
    pygame.Rect(400, 250, 16, 16),
    pygame.Rect(416, 250, 16, 16),
    pygame.Rect(432, 250, 16, 16),
]
route3_wild = ["Jigglypuff", "Sandshrew", "Spearow"]
route3_exits = {
    "down": ("Pewter City", 300, 20),
    "up": ("Mt. Moon", 300, 380),
}
route3 = Map("Route 3", 600, 400, route3_walls, route3_grass, route3_wild, route3_exits)

# 8. Mt. Moon (unchanged)
mtmoon_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(150, 100, 16, 16),
    pygame.Rect(166, 100, 16, 16),
    pygame.Rect(182, 100, 16, 16),
    pygame.Rect(150, 116, 16, 16),
    pygame.Rect(182, 116, 16, 16),
    pygame.Rect(150, 132, 16, 16),
    pygame.Rect(166, 132, 16, 16),
    pygame.Rect(182, 132, 16, 16),
    pygame.Rect(400, 250, 16, 16),
    pygame.Rect(416, 250, 16, 16),
    pygame.Rect(432, 250, 16, 16),
]
mtmoon_grass = [
    pygame.Rect(250, 200, 16, 16),
    pygame.Rect(266, 200, 16, 16),
    pygame.Rect(282, 200, 16, 16),
    pygame.Rect(250, 216, 16, 16),
    pygame.Rect(282, 216, 16, 16),
]
mtmoon_wild = ["Zubat", "Geodude", "Paras", "Clefairy"]
mtmoon_exits = {
    "down": ("Route 3", 300, 20),
    "up": ("Route 4", 300, 380),
}
mtmoon = Map("Mt. Moon", 600, 400, mtmoon_walls, mtmoon_grass, mtmoon_wild, mtmoon_exits)

# 9. Route 4 (unchanged)
route4_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(300, 150, 16, 16),
    pygame.Rect(316, 150, 16, 16),
]
route4_grass = [
    pygame.Rect(100, 200, 16, 16),
    pygame.Rect(116, 200, 16, 16),
    pygame.Rect(132, 200, 16, 16),
    pygame.Rect(400, 250, 16, 16),
    pygame.Rect(416, 250, 16, 16),
    pygame.Rect(432, 250, 16, 16),
]
route4_wild = ["Ekans", "Sandshrew", "Mankey"]
route4_exits = {
    "down": ("Mt. Moon", 300, 20),
    "up": ("Cerulean City", 300, 380),
}
route4 = Map("Route 4", 600, 400, route4_walls, route4_grass, route4_wild, route4_exits)

# 10. Cerulean City (with a possible door later)
cerulean_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(100, 100, 60, 50),
    pygame.Rect(350, 200, 70, 60),
    pygame.Rect(200, 300, 50, 40),
]
cerulean_grass = []
cerulean_wild = []
cerulean_exits = {
    "down": ("Route 4", 300, 20),
    "left": ("Route 5", 580, 200),
}
cerulean = Map("Cerulean City", 600, 400, cerulean_walls, cerulean_grass, cerulean_wild, cerulean_exits)

# 11. Route 5 (unchanged)
route5_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(250, 150, 16, 16),
]
route5_grass = [
    pygame.Rect(300, 200, 16, 16),
    pygame.Rect(316, 200, 16, 16),
    pygame.Rect(332, 200, 16, 16),
]
route5_wild = ["Meowth", "Psyduck"]
route5_exits = {
    "right": ("Cerulean City", 20, 200),
}
route5 = Map("Route 5", 600, 400, route5_walls, route5_grass, route5_wild, route5_exits)

# ==================== MAP DICTIONARY ====================
maps = {
    "Pallet Town": pallet,
    "Pallet House 1": house1,
    "Pallet House 2": house2,
    "Route 1": route1,
    "Viridian City": viridian,
    "Viridian House": viridian_house,
    "Route 2": route2,
    "Viridian Forest": forest,
    "Pewter City": pewter,
    "Route 3": route3,
    "Mt. Moon": mtmoon,
    "Route 4": route4,
    "Cerulean City": cerulean,
    "Route 5": route5,
}

# ==================== MAIN GAME LOOP ====================
def main():
    current_map = maps["Pallet Town"]
    player = Player(300, 200)
    battle = None

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and battle and battle.battle_over:
                    player.in_battle = False
                    battle = None

        if player.in_battle and battle is None:
            # Start a new battle if just entered battle mode
            battle = Battle(player, random.choice(current_map.wild_pokemon))

        if battle:
            battle.handle_input(keys)
            battle.update()
        else:
            # Overworld movement
            new_battle = player.update(keys, current_map)
            if new_battle:
                battle = new_battle

            # Check door transitions
            door_result = current_map.get_door(player.rect)
            if door_result:
                target_map, spawn_x, spawn_y = door_result
                if target_map in maps:
                    current_map = maps[target_map]
                    player.rect.topleft = (spawn_x, spawn_y)
                    # No need to check edge transitions after door

            # Edge transitions (only if no door triggered)
            else:
                if player.rect.top <= 0 and "up" in current_map.exits:
                    target = current_map.exits["up"]
                    current_map = maps[target[0]]
                    player.rect.topleft = (target[1], target[2])
                elif player.rect.bottom >= SCREEN_HEIGHT and "down" in current_map.exits:
                    target = current_map.exits["down"]
                    current_map = maps[target[0]]
                    player.rect.topleft = (target[1], target[2])
                elif player.rect.left <= 0 and "left" in current_map.exits:
                    target = current_map.exits["left"]
                    current_map = maps[target[0]]
                    player.rect.topleft = (target[1], target[2])
                elif player.rect.right >= SCREEN_WIDTH and "right" in current_map.exits:
                    target = current_map.exits["right"]
                    current_map = maps[target[0]]
                    player.rect.topleft = (target[1], target[2])

        # Drawing
        screen.fill(BLACK)
        current_map.draw(screen)
        player.draw(screen)
        if battle:
            battle.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
