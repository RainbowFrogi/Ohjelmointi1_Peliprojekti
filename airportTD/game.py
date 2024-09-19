import pygame
import game_map

# Initialize pygame
pygame.init()

screen = game_map.screen
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
    game_map.draw_map()
    
    # Draw the HUD
    draw_hud()
    
    # Update the display
    pygame.display.update()

# Quit pygame when the game loop ends
pygame.quit()
