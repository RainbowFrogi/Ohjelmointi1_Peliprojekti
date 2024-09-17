import pygame

# Initialize pygame
pygame.init()

# Window setup
TILE_SIZE = 80
GRID_WIDTH = 10
GRID_HEIGHT = 10

# Window is sized by the grid width and height
WINDOW_WIDTH = TILE_SIZE * GRID_WIDTH
WINDOW_HEIGHT = TILE_SIZE * GRID_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tower Defense Game")

# Map grid (1 is path, 0 is terrain)
map_grid = [
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 1, 1, 0, 1],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [0, 1, 1, 1, 0, 0, 0, 1, 0, 1],
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
]

def draw_map():
    for row in range(len(map_grid)):
        for col in range(len(map_grid[row])):
            # Set color based on the map value (path or terrain)
            color = (0, 255, 0) if map_grid[row][col] == 1 else (100, 100, 100)
            
            # Draw each tile
            pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

# HUD font setup
font = pygame.font.SysFont("Arial", 30)

# HUD elements (static values for now)
player_health = 100
player_money = 50
current_wave = 1

def draw_hud():
    # Create the HUD text
    hud_text = f"Health: {player_health} | Money: {player_money} | Wave: {current_wave}"
    
    # Render the text
    hud_surface = font.render(hud_text, True, (255, 255, 255))  # White text
    
    # Blit the text surface to the screen
    screen.blit(hud_surface, (350, 10))

# Main game loop
running = True
while running:
    # Handle events (e.g., quitting the game)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))  # Black background
    
    # Draw the map
    draw_map()
    
    # Draw the HUD
    draw_hud()
    
    # Update the display
    pygame.display.update()

# Quit pygame when the game loop ends
pygame.quit()
