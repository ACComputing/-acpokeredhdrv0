import pygame
import random
import sys
from enum import Enum

# Initialize Pygame
pygame.init()
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokémon Red (Simplified)")
clock = pygame.time.Clock()
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 150, 0)
GRAY = (128, 128, 128)

# Directions as vectors
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# ==================== Player Class ====================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = Direction.DOWN
        self.speed = 16  # grid size (tile size)
        self.rect = pygame.Rect(x, y, 16, 16)
        self.in_battle = False

    def move(self, dx, dy, game_map):
        # Check collision with walls
        new_rect = self.rect.move(dx, dy)
        if not game_map.check_collision(new_rect):
            self.rect = new_rect
            self.x += dx
            self.y += dy
            return True
        return False

    def update(self, keys, game_map):
        if self.in_battle:
            return
        moved = False
        if keys[pygame.K_LEFT]:
            self.direction = Direction.LEFT
            moved = self.move(-self.speed, 0, game_map)
        elif keys[pygame.K_RIGHT]:
            self.direction = Direction.RIGHT
            moved = self.move(self.speed, 0, game_map)
        elif keys[pygame.K_UP]:
            self.direction = Direction.UP
            moved = self.move(0, -self.speed, game_map)
        elif keys[pygame.K_DOWN]:
            self.direction = Direction.DOWN
            moved = self.move(0, self.speed, game_map)

        # If moved and standing on grass, possibly trigger battle
        if moved and game_map.is_grass(self.rect):
            # 10% chance to encounter a wild Pokémon
            if random.randint(1, 100) <= 10:
                self.in_battle = True
                # Return a wild Pokémon (random level and species)
                return Battle(self, random.choice(game_map.wild_pokemon))
        return None

    def draw(self, surface):
        # Draw player as a yellow square (for simplicity)
        pygame.draw.rect(surface, YELLOW, self.rect)

# ==================== Map Class ====================
class Map:
    def __init__(self, name, width, height, grid, walls, grass, wild_pokemon, exits):
        self.name = name
        self.width = width
        self.height = height
        self.grid = grid  # 2D list of tile types (unused here except for drawing)
        self.walls = walls  # list of pygame.Rect for collision
        self.grass = grass  # list of pygame.Rect where grass tiles are
        self.wild_pokemon = wild_pokemon  # list of possible encounters
        self.exits = exits  # dict: direction -> (new_map_name, new_player_x, new_player_y)

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

    def get_exit(self, player_rect):
        # Check if player is at any exit boundary
        # For simplicity, we check if player's center is at the edge of the map
        # and then use the exit dict.
        # But easier: in main loop we'll check map boundaries and call this.
        pass

    def draw(self, surface):
        # Draw ground (simple gray)
        surface.fill(GRAY)
        # Draw walls as brown squares
        for wall in self.walls:
            pygame.draw.rect(surface, BROWN, wall)
        # Draw grass as green squares
        for g in self.grass:
            pygame.draw.rect(surface, DARK_GREEN, g)

# ==================== Battle Class ====================
class Battle:
    def __init__(self, player, wild_pokemon):
        self.player = player
        self.wild = wild_pokemon
        self.player_pokemon = {"name": "Charmander", "hp": 20, "max_hp": 20, "attack": 10}
        self.wild_pokemon = {"name": wild_pokemon, "hp": 15, "max_hp": 15, "attack": 8}
        self.turn = "player"  # or "enemy"
        self.message = f"A wild {wild_pokemon} appeared!"
        self.battle_over = False
        self.player_won = False

    def handle_input(self, keys):
        if self.battle_over:
            return
        if self.turn == "player":
            # Simple: press A (K_a) to attack
            if keys[pygame.K_a]:
                self.player_attack()
        # Enemy turn is automatic after player attack

    def player_attack(self):
        # Calculate damage
        damage = self.player_pokemon["attack"] - 2  # simplified
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
            # After enemy attack, turn goes back to player automatically

    def draw(self, surface):
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        # Battle UI
        font = pygame.font.Font(None, 24)
        # Player Pokémon info
        player_text = f"{self.player_pokemon['name']} HP: {self.player_pokemon['hp']}/{self.player_pokemon['max_hp']}"
        player_surf = font.render(player_text, True, WHITE)
        surface.blit(player_surf, (50, 250))

        # Enemy Pokémon info
        enemy_text = f"Wild {self.wild_pokemon['name']} HP: {self.wild_pokemon['hp']}/{self.wild_pokemon['max_hp']}"
        enemy_surf = font.render(enemy_text, True, WHITE)
        surface.blit(enemy_surf, (350, 50))

        # Message
        msg_surf = font.render(self.message, True, WHITE)
        surface.blit(msg_surf, (50, 300))

        # Instructions
        inst_surf = font.render("Press A to attack", True, WHITE)
        surface.blit(inst_surf, (50, 350))

        if self.battle_over:
            over_surf = font.render("Battle over! Press SPACE to continue.", True, WHITE)
            surface.blit(over_surf, (150, 200))

# ==================== Define Maps ====================
# Map 1: Pallet Town
pallet_walls = [
    pygame.Rect(0, 0, 600, 16),  # top border
    pygame.Rect(0, 0, 16, 400),  # left border
    pygame.Rect(584, 0, 16, 400), # right border
    pygame.Rect(0, 384, 600, 16), # bottom border
    # Some houses (simple rectangles)
    pygame.Rect(100, 100, 50, 50),
    pygame.Rect(400, 200, 60, 60),
]
pallet_grass = []  # no grass in town
pallet_wild = []
pallet_exits = {
    Direction.UP: ("Route 1", 300, 380),
    # Other directions could lead elsewhere
}
pallet = Map("Pallet Town", 600, 400, [], pallet_walls, pallet_grass, pallet_wild, pallet_exits)

# Map 2: Route 1
route1_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    # Some trees as walls
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
    Direction.DOWN: ("Pallet Town", 300, 20),
    Direction.UP: ("Viridian City", 300, 380),
}
route1 = Map("Route 1", 600, 400, [], route1_walls, route1_grass, route1_wild, route1_exits)

# Map 3: Viridian City
viridian_walls = [
    pygame.Rect(0, 0, 600, 16),
    pygame.Rect(0, 0, 16, 400),
    pygame.Rect(584, 0, 16, 400),
    pygame.Rect(0, 384, 600, 16),
    pygame.Rect(150, 150, 80, 40),
    pygame.Rect(400, 80, 60, 60),
]
viridian_grass = []
viridian_wild = []
viridian_exits = {
    Direction.DOWN: ("Route 1", 300, 20),
}
viridian = Map("Viridian City", 600, 400, [], viridian_walls, viridian_grass, viridian_wild, viridian_exits)

# Map dictionary for transitions
maps = {
    "Pallet Town": pallet,
    "Route 1": route1,
    "Viridian City": viridian,
}

# ==================== Main Game Loop ====================
def main():
    current_map = maps["Pallet Town"]
    player = Player(300, 200)
    battle = None

    running = True
    while running:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and battle and battle.battle_over:
                    # Exit battle
                    player.in_battle = False
                    battle = None

        if player.in_battle and battle is None:
            # Start a new battle if just entered
            battle = Battle(player, random.choice(current_map.wild_pokemon))

        if battle:
            # Battle mode
            battle.handle_input(keys)
            battle.update()
        else:
            # Overworld mode
            new_battle = player.update(keys, current_map)
            if new_battle:
                battle = new_battle

            # Check map transitions (if player goes off-screen edges)
            # We'll implement simple edge-based transitions
            if player.rect.top <= 0:
                # Try to go up exit
                if Direction.UP in current_map.exits:
                    target = current_map.exits[Direction.UP]
                    current_map = maps[target[0]]
                    player.rect.topleft = (target[1], target[2])
            elif player.rect.bottom >= SCREEN_HEIGHT:
                if Direction.DOWN in current_map.exits:
                    target = current_map.exits[Direction.DOWN]
                    current_map = maps[target[0]]
                    player.rect.topleft = (target[1], target[2])
            elif player.rect.left <= 0:
                if Direction.LEFT in current_map.exits:
                    target = current_map.exits[Direction.LEFT]
                    current_map = maps[target[0]]
                    player.rect.topleft = (target[1], target[2])
            elif player.rect.right >= SCREEN_WIDTH:
                if Direction.RIGHT in current_map.exits:
                    target = current_map.exits[Direction.RIGHT]
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
