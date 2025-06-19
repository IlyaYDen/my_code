import pygame
from block import Block, BLOCK_TYPES

BLOCK_SIZE = 32

class World:
    def __init__(self, width, height):
        self.width = width  # in blocks
        self.height = height  # in blocks
        self.blocks = {}  # Using a dictionary: (col, row) -> Block instance

    def generate_world(self):
        for col in range(self.width):
            for row in range(self.height):
                block_type = "air"  # Default to air
                if row > self.height * 0.7:  # Lower part is stone
                    block_type = "stone"
                    # Simple ore generation
                    if row > self.height * 0.75 and col % 10 == 0:
                        block_type = "coal_ore"
                    if row > self.height * 0.8 and col % 15 == 5: # Ensure different modulo for variety
                        block_type = "iron_ore"
                elif row > self.height * 0.6:  # Dirt layer
                    block_type = "dirt"
                elif row == int(self.height * 0.6):  # Grass surface
                    block_type = "grass"

                if block_type != "air":
                    self.blocks[(col, row)] = Block(block_type)

        # Add simple trees
        for col in range(self.width): # Iterate again for trees, or integrate into main loop if surface logic allows
            surface_row_candidate = -1
            # Find the surface for tree placement. Search from mid-air down to typical ground level.
            # We need a grass or dirt block with air above it.
            for r_check in range(int(self.height * 0.4), int(self.height * 0.7) + 2):
                # Need to check block at (col, r_check) and (col, r_check -1)
                block_at_r_check = self.get_block(col, r_check)
                block_above_r_check = self.get_block(col, r_check - 1)

                if block_at_r_check and block_at_r_check.type_name in ["grass", "dirt"] and block_above_r_check is None:
                    surface_row_candidate = r_check -1 # This is the air block where the base of the tree trunk will go
                    break

            if surface_row_candidate != -1 and col > 2 and col < self.width - 3 and col % 7 == 0: # Spread trees out
                tree_base_air_row = surface_row_candidate
                trunk_height = 3
                # Trunk
                for i in range(trunk_height):
                    if tree_base_air_row - i >= 0:
                        # Ensure we are placing on the original surface, not overwriting part of trunk
                        if self.get_block(col, tree_base_air_row - i) is None:
                             self.blocks[(col, tree_base_air_row - i)] = Block("wood_log")

                # Leaves (simple 3x2 layer on top of trunk)
                # leaf_start_row is the row of the lowest leaves
                leaf_start_row = tree_base_air_row - trunk_height
                for r_offset in range(2): # 2 rows of leaves
                    for c_offset in range(-1, 2): # 3 columns of leaves: -1, 0, 1
                        current_leaf_row = leaf_start_row - r_offset
                        current_leaf_col = col + c_offset

                        # Ensure leaves are within world bounds
                        if current_leaf_row >= 0 and 0 <= current_leaf_col < self.width:
                            # Place leaf if the spot is currently air
                            if self.get_block(current_leaf_col, current_leaf_row) is None:
                                self.blocks[(current_leaf_col, current_leaf_row)] = Block("leaves")


    def get_block(self, col, row):
        return self.blocks.get((col, row))

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        for (col, row), block_instance in self.blocks.items():
            if block_instance.color:  # Only draw if it has a color (not air)
                rect = pygame.Rect(
                    col * BLOCK_SIZE - camera_offset_x,
                    row * BLOCK_SIZE - camera_offset_y,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                pygame.draw.rect(screen, block_instance.color, rect)

    def remove_block(self, col, row):
        block_to_remove = self.blocks.pop((col, row), None)
        return block_to_remove # So we know what item to give to player

    def place_block(self, col, row, block_type_name, player_rect):
        # Check if the space is empty (no block there currently)
        # and ensure block_type_name is valid and placeable.
        if BLOCK_TYPES.get(block_type_name) and BLOCK_TYPES[block_type_name].get("color") is not None:
            if self.get_block(col, row) is None:
                target_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                # Check if player is occupying the target space
                if player_rect.colliderect(target_rect):
                    # Potentially print a message or log this
                    return False # Cannot place where player is

                self.blocks[(col, row)] = Block(block_type_name)
                return True
        return False
