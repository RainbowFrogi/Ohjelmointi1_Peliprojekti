import pygame as pg
import pygame_textinput
import json
from enemy import Enemy
from world import World
from turret import Turret
import constants as c

#initialise pygame
pg.init()

#Text input GUI values
gui_width = c.COMMANDLINE_PANEL
gui_x = c.SCREEN_WIDTH
gui_y = 0

#Create TextInput-object
textinput = pygame_textinput.TextInputVisualizer()

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.COMMANDLINE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

#game variables
commands = [
  "createEnemy",
  "placeTurret",
  "select",
  "Place"
]

textinput.cursor_width = 12

#map
map_image = pg.image.load('levels/level.png').convert_alpha()
#turret spritesheets
turret_sheet = pg.image.load('assets/images/turrets/turret_1.png').convert_alpha()

#individual turret image for mouse cursor
cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
#enemies
enemy_image = pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha()


#load json data for level
with open('levels/level.tmj') as file:
  world_data = json.load(file)

def create_turret(mouse_pos):
  #attach turret pos to grid
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  print(mouse_tile_x, mouse_tile_y)
  #calculate the sequential number of the tile
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x

  #check if the tile pressed is grass
  if world.tile_map[mouse_tile_num] == 7:
    #check that there isn't already a turret on the tile
    tile_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        tile_free = False

    #if it is a free space, create turret
    if tile_free:
      new_turret = Turret(turret_sheet, mouse_tile_x, mouse_tile_y)
      turret_group.add(new_turret)

def place_turret(x, y):
  world_tile_num = (y * c.COLS) + x

  if world.tile_map[world_tile_num] == 7:
    tile_free = True
    for turret in turret_group:
      if (x, y) == (turret.tile_x, turret.tile_y):
        tile_free = False

    if tile_free:
      new_turret = Turret(turret_sheet, x, y)
      turret_group.add(new_turret)

#Turret selection for upgrading and showing range
def select_turret(x, y):

  for turret in turret_group:
      if (x, y) == (turret.tile_x, turret.tile_y):
        return turret

#Create enemy for command testing
def create_enemy():
  enemy = Enemy(world.waypoints, enemy_image)
  enemy_group.add(enemy)

#create world
world = World(world_data, map_image)
world.process_data()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

enemy = Enemy(world.waypoints, enemy_image)
enemy_group.add(enemy)

#game loop
run = True
while run:

  clock.tick(c.FPS)

  #########################
  # UPDATING SECTION
  #########################

  #update groups
  enemy_group.update()
  turret_group.update()

  #########################
  # DRAWING SECTION
  #########################

  screen.fill("white")

  #draw level
  world.draw(screen)

  #draw gui
  pg.draw.rect(screen, "grey", (gui_x, gui_y, gui_width, c.SCREEN_HEIGHT))

  #draw groups
  enemy_group.draw(screen)
  for turret in turret_group:
    turret.draw(screen)
  
  events = pg.event.get()

  textinput.update(events)

  screen.blit(textinput.surface, (gui_x, c.SCREEN_HEIGHT - 25))

  #event handler
  for event in events:
    #quit program
    if event.type == pg.QUIT:
      run = False
      #mouse click
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pg.mouse.get_pos()
      #check if mouse is within the world
      if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
        create_turret(mouse_pos)

    if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
      print(f"You entered command {textinput.value} to the command line")

      if textinput.value == commands[0]:
        create_enemy()

      if "placeTurret" in textinput.value:
        command_parts = textinput.value.split(" ")
        command = command_parts[0]
        if len(command_parts) == 3:
          try:
            x = int(command_parts[1])
            y = int(command_parts[2])
            if 0 <= x < c.COLS and 0 <= y < c.ROWS:
              place_turret(x, y)
            else:
              print(f"Please enter a value between 0 and {c.COLS - 1} for x and 0 and {c.ROWS - 1} for y")
          except ValueError:
            print("Please input the command in a form 'placeTurret x y' e.g. 'placeTurret 10 5' ")
      
      if "select" in textinput.value:
        command_parts = textinput.value.split(" ")
        command = command_parts[0]
        if len(command_parts) == 3:
          try:
            x = int(command_parts[1])
            y = int(command_parts[2])
            if 0 <= x < c.COLS and 0 <= y < c.ROWS:
              turret = select_turret(x, y)
              if turret:
                print(f"Selected turret at {x}, {y}")
                turret.selected = True
              else:
                print("No turret found at that position")
            else:
              print(f"Please enter a value between 0 and {c.COLS - 1} for x and 0 and {c.ROWS - 1} for y")
          except ValueError:
            print("Please input the command in a form 'Select x y' e.g. 'Select 10 5' ")
          
      textinput.value = ""
    
      
  #update display
  pg.display.flip()

print()
pg.quit()