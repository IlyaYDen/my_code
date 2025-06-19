import pygame
from inventory import Inventory # Import Inventory
from world import BLOCK_SIZE # Import BLOCK_SIZE for player physics

class Player:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = 5
        self.color = (255, 0, 0)  # Red color for the player
        self.inventory = Inventory()

        self.velocity_y = 0
        self.gravity = 1  # Keep it simple for now
        self.is_jumping = False
        self.jump_strength = -15 # Max jump height factor

        self.dx = 0 # Change in x for current frame
        self.BLOCK_SIZE = BLOCK_SIZE # Store world's block size

        self.selected_hotbar_slot = 0
        self.hotbar_size = 10 # Should match inventory capacity or be a view into it
        self.inventory = Inventory(capacity=self.hotbar_size) # Match inventory capacity to hotbar size

        self.mining_target = None  # Stores (col, row) tuple
        self.mining_progress = 0.0

    def get_selected_item_type(self):
        if 0 <= self.selected_hotbar_slot < len(self.inventory.slots):
            slot_content = self.inventory.slots[self.selected_hotbar_slot]
            if slot_content:
                return slot_content[0] # Return item_type
        return None

    def collect_item(self, item_type, quantity=1):
        return self.inventory.add_item(item_type, quantity)

    def move_left(self):
        self.dx = -self.speed

    def move_right(self):
        self.dx = self.speed

    def stop_moving(self):
        self.dx = 0

    def jump(self):
        if not self.is_jumping: # Allow jump only if not already in a jump
            self.velocity_y = self.jump_strength
            self.is_jumping = True

    def get_collision_tiles(self, world):
        tiles = []
        start_col = self.rect.left // self.BLOCK_SIZE
        end_col = self.rect.right // self.BLOCK_SIZE
        start_row = self.rect.top // self.BLOCK_SIZE
        end_row = self.rect.bottom // self.BLOCK_SIZE

        for r in range(start_row, end_row + 1):
            for c in range(start_col, end_col + 1):
                block = world.get_block(c, r)
                if block: # If a solid block exists
                    tiles.append(pygame.Rect(c * self.BLOCK_SIZE,
                                             r * self.BLOCK_SIZE,
                                             self.BLOCK_SIZE, self.BLOCK_SIZE))
        return tiles

    def update(self, world):
        # --- Horizontal Movement and Collision ---
        self.rect.x += self.dx

        horizontal_collision_tiles = self.get_collision_tiles(world)
        for tile_rect in horizontal_collision_tiles:
            if self.rect.colliderect(tile_rect):
                if self.dx > 0: # Moving right
                    self.rect.right = tile_rect.left
                elif self.dx < 0: # Moving left
                    self.rect.left = tile_rect.right

        # --- Vertical Movement and Collision ---
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        vertical_collision_tiles = self.get_collision_tiles(world)
        for tile_rect in vertical_collision_tiles:
            if self.rect.colliderect(tile_rect):
                if self.velocity_y > 0: # Moving down / falling
                    self.rect.bottom = tile_rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
                elif self.velocity_y < 0: # Moving up / jumping
                    self.rect.top = tile_rect.bottom
                    self.velocity_y = 0 # Stop upward movement if hit ceiling

        # Reset dx after processing for this frame. Keyup events will also set it to 0.
        # This ensures player stops if no key is pressed in the next frame.
        self.dx = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
