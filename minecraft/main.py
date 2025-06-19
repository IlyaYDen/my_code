import pygame
from player import Player # Import the Player class
from world import World, BLOCK_SIZE # Import World and BLOCK_SIZE

# Initialize Pygame
pygame.init()
pygame.font.init() # Initialize font module

# Game constants
FPS = 60
clock = pygame.time.Clock()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# Create the game screen
screen = pygame.display.set_mode(SCREEN_SIZE)

# Set window caption
pygame.display.set_caption("2D Minecraft")

# World dimensions
WORLD_WIDTH_BLOCKS = 100
WORLD_HEIGHT_BLOCKS = 30 # Defines how many blocks tall the world is

# Colors
LIGHT_BLUE = (173, 216, 230)

# Font for inventory
inventory_font = pygame.font.Font(None, 28)

# Create World instance
game_world = World(WORLD_WIDTH_BLOCKS, WORLD_HEIGHT_BLOCKS)
game_world.generate_world()

# Player dimensions (can be based on BLOCK_SIZE)
PLAYER_WIDTH = int(BLOCK_SIZE * 0.8)
PLAYER_HEIGHT = int(BLOCK_SIZE * 1.8)

# Create Player instance
# Adjust start_y to be somewhere in the middle of the world height, above ground.
# Player should fall and land on generated terrain.
player_start_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
player_start_y = WORLD_HEIGHT_BLOCKS * BLOCK_SIZE // 3 # Start in upper third of world
player = Player(player_start_x, player_start_y, PLAYER_WIDTH, PLAYER_HEIGHT)

# Test inventory - Give some starting items for placement testing
player.collect_item("dirt", 30)
player.collect_item("stone", 20)
player.collect_item("grass", 10) # Assuming grass is a placeable block type
player.collect_item("wooden_pickaxe", 1) # Give a test pickaxe
# player.inventory.display() # Removed console display
# print("-" * 20) # Removed separator

# Game state
show_inventory = False

# Tool properties and mining constants
TOOL_PROPERTIES = {
    "wooden_pickaxe": {"tier": 1, "type": "pickaxe", "speed_modifier": 2.0},
    "stone_pickaxe": {"tier": 2, "type": "pickaxe", "speed_modifier": 4.0},
    # Add other tools like shovel, axe if needed
}
BASE_MINING_SPEED = 1.0 # Base hardness units per second for hand mining (effectively blocks per second for hardness 1)

# Game loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0 # Delta time in seconds, not strictly used by mining logic as it uses 1/FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Player movement and actions
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.move_left()
            if event.key == pygame.K_RIGHT:
                player.move_right()
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_i:
                show_inventory = not show_inventory
            # Hotbar selection
            if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                player.selected_hotbar_slot = event.key - pygame.K_1
            elif event.key == pygame.K_0:
                player.selected_hotbar_slot = 9

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.stop_moving()

        # Mouse actions for breaking/placing blocks
        mouse_pos = pygame.mouse.get_pos() # Get mouse pos once per frame if needed by multiple event types
        target_block_col = mouse_pos[0] // BLOCK_SIZE
        target_block_row = mouse_pos[1] // BLOCK_SIZE

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left-click: Start or continue mining
                target_coords = (target_block_col, target_block_row)
                block_at_target = game_world.get_block(target_coords[0], target_coords[1])
                if block_at_target and block_at_target.type_name != "air":
                    player.mining_target = target_coords
                    player.mining_progress = 0.0 # Reset progress for new target
                else:
                    player.mining_target = None

            elif event.button == 3: # Right-click to place
                selected_item_to_place = player.get_selected_item_type()
                if selected_item_to_place:
                    placed_successfully = game_world.place_block(target_block_col, target_block_row, selected_item_to_place, player.rect)
                    if placed_successfully:
                        player.inventory.remove_item(selected_item_to_place, 1)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Stop mining if left mouse is released
                player.mining_target = None
                player.mining_progress = 0.0

    # Continuous mining logic (if mouse button is held down)
    if pygame.mouse.get_pressed()[0] and player.mining_target: # [0] is left mouse button
        current_mouse_block_coords = (pygame.mouse.get_pos()[0] // BLOCK_SIZE, pygame.mouse.get_pos()[1] // BLOCK_SIZE)
        if current_mouse_block_coords == player.mining_target:
            target_coords = player.mining_target
            block_to_mine = game_world.get_block(target_coords[0], target_coords[1])

            if block_to_mine and block_to_mine.type_name != "air":
                block_props = BLOCK_TYPES.get(block_to_mine.type_name, {})
                block_hardness = block_props.get("hardness", float('inf'))
                req_tool_type = block_props.get("tool_type")
                req_tool_tier = block_props.get("required_tool_tier", 0)

                effective_mining_power = 0.0
                selected_item_type = player.get_selected_item_type()
                tool_props = TOOL_PROPERTIES.get(selected_item_type)

                can_mine_this_block_by_hand = (req_tool_tier == 0) # True if block doesn't need a tool above hand-tier

                if tool_props: # Player has a tool selected
                    if tool_props["type"] == req_tool_type and tool_props["tier"] >= req_tool_tier:
                        effective_mining_power = BASE_MINING_SPEED * tool_props["speed_modifier"]
                    elif can_mine_this_block_by_hand: # Wrong tool, but block is hand-breakable
                        effective_mining_power = BASE_MINING_SPEED * 0.25 # Penalty
                    # If tool tier is too low for a non-hand-breakable block, power remains 0
                elif can_mine_this_block_by_hand: # No tool selected, but block is hand-breakable
                    effective_mining_power = BASE_MINING_SPEED

                if effective_mining_power > 0:
                    player.mining_progress += effective_mining_power / FPS # Progress per frame
                    if player.mining_progress >= block_hardness:
                        broken_block = game_world.remove_block(target_coords[0], target_coords[1])
                        if broken_block:
                            player.collect_item(broken_block.type_name, 1)
                        player.mining_target = None
                        player.mining_progress = 0.0
            else: # Target became air or no block while mining
                player.mining_target = None
                player.mining_progress = 0.0
        else: # Mouse moved off the original target block or target is no longer valid
            player.mining_target = None
            player.mining_progress = 0.0
    # If mouse is not pressed but mining_target was set (e.g. by a previous click), ensure it's cleared.
    elif not pygame.mouse.get_pressed()[0] and player.mining_target is not None:
         player.mining_target = None
         player.mining_progress = 0.0

    # Update game state
    player.update(game_world)

    # Fill the screen
    screen.fill(LIGHT_BLUE)

    # Draw the world
    game_world.draw(screen)

    # Draw the player
    player.draw(screen)

    # Draw inventory if toggled
    if show_inventory:
        player.inventory.render(screen, inventory_font, 50, 50, selected_slot_idx=player.selected_hotbar_slot)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
