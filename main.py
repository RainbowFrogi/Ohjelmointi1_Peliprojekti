import sys
import mariadb
import pygame as pg
import pygame_textinput
import json
from enemy import Enemy
from world import World
from turret import Turret
import constants as c

#initialise pygame
pg.init()

#GUI variables
gui_width = c.COMMANDLINE_PANEL
gui_x = c.SCREEN_WIDTH
gui_y = 0
grid_width = 1
grid_color = "black"
grid_num_color = "black"

#Create TextInput-object
textinput = pygame_textinput.TextInputVisualizer()
#set cursor width
textinput.cursor_width = 12

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.COMMANDLINE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

#initialise font
pg.font.init()
font = pg.font.SysFont(None, 36)

#initialise mariadb connection
try:
    connection = mariadb.connect(
            user="root",
            password="root",
            host="localhost",
            port=3306,
            database="towerdefense",
            autocommit=True
        )
    print("Connected to MariaDB turret_defence database")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

#game variables
commands = [
  "createEnemy",
  "placeTurret",
  "select",
  "Place",
  "Grid"
]
coins = 100
hearts = 5
wave = 0
showgrid = False
debugging = True

#LOAD IMAGES

#map
map_image = pg.image.load('levels/level.png').convert_alpha()

#turret spritesheet
turret_sheet = pg.image.load('assets/images/turrets/turret_1.png').convert_alpha()

#enemies
enemy_image = pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha()

#ICONS
#coin icon
coin_image = pg.image.load('assets/images/gui/coin.png').convert_alpha()

#heart icon
heart_image = pg.image.load('assets/images/gui/heart.png').convert_alpha()

#load json data for level
with open('levels/level.tmj') as file:
  world_data = json.load(file)

#FUNCTIONS

def console_error_message(message):
  textinput.value = message

def place_turret(x, y,):
  #convert 2D coordinates to 1D
  world_tile_num = (y * c.COLS) + x
  global coins
  if coins >= 50:
    #check if tile on coordinates is a grass tile
    if world.tile_map[world_tile_num] == 7:
      tile_free = True
      for turret in turret_group:
        #check if tile is already occupied by a turret
        if (x, y) == (turret.tile_x, turret.tile_y):
          tile_free = False
    
      #if tile is free, place turret and add it to a group
      if tile_free:
        new_turret = Turret(turret_sheet, x, y)
        coins -= 50
        turret_group.add(new_turret)
  else:
    console_error_message("Not enough coins to place turret")
  

#Turret selection for upgrading and showing range
def select_turret(x, y):
  for turret in turret_group:
      if (x, y) == (turret.tile_x, turret.tile_y):
        return turret

def upgrade_turret(turret):
  pass

def update_groups():
  enemy_group.update()
  turret_group.update()

#Create enemy for command testing
def create_enemy():
  enemy = Enemy(world.waypoints, enemy_image)
  enemy_group.add(enemy)

#Draw the game grid
def draw_grid():
  # draw horizontal lines
  for i in range(c.ROWS + 1):
    pg.draw.line(screen, grid_color, (0, i * c.TILE_SIZE), (c.SCREEN_WIDTH, i * c.TILE_SIZE), grid_width)
  # draw vertical lines
  for j in range(c.COLS + 1):
    pg.draw.line(screen, grid_color, (j * c.TILE_SIZE, 0), (j * c.TILE_SIZE, c.SCREEN_HEIGHT), grid_width)

#Draw grid numbers
def draw_gridnums():
  # draw horizontal nums
  for i in range(c.ROWS):
    text = font.render(str(i), True, grid_num_color)
    screen.blit(text, (5, i * c.TILE_SIZE + 5))
  # draw vertical nums
  for i in range(c.COLS):
    text = font.render(str(i), True, grid_num_color)
    screen.blit(text, (i * c.TILE_SIZE + 5, 5))

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

  update_groups()

  #########################
  # DRAWING SECTION
  #########################

  screen.fill("white")

  #draw level
  world.draw(screen)

  #DRAW PANELS
  #draw console panel
  pg.draw.rect(screen, "grey", (gui_x, gui_y+250, gui_width, c.SCREEN_HEIGHT))
  #draw GUI panel
  pg.draw.rect(screen, "purple", (gui_x, gui_y, gui_width, 250))
  
  #DRAW ICONS
  #draw coin icon to GUI
  screen.blit(coin_image, (gui_x + 10, 10))
  #draw coin text to GUI
  text = font.render(str(coins), True, "white")
  screen.blit(text, (gui_x + 50, 15))
  #draw heart icon to GUI
  screen.blit(heart_image, (gui_x + 10, 50))
  #draw heart text to GUI
  text = font.render(str(hearts), True, "white")
  screen.blit(text, (gui_x + 50, 55))


  #draw groups
  enemy_group.draw(screen)
  for turret in turret_group:
    turret.draw(screen)

  #draw grid
  if showgrid:
    draw_grid()

  #draw grid numbers
  draw_gridnums()

  #get pygame events
  events = pg.event.get()

  # Update the textinput object
  textinput.update(events)

  # Blit textinput value on screen
  screen.blit(textinput.surface, (gui_x, c.SCREEN_HEIGHT - 25))
  
  #event handler
  for event in events:
    #quit program
    if event.type == pg.QUIT:
      run = False

    if debugging and event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
      coins += 50
    
    if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
      print(f"You entered command {textinput.value} to the command line")
      
      #deselect all turrets whenever a command is run
      for turret in turret_group:
        turret.selected = False

      #check if command is "createEnemy"
      if textinput.value == commands[0]:
        create_enemy()

      #check if command is "placeTurret"
      if commands[1] in textinput.value:
        #divide command into parts
        command_parts = textinput.value.split(" ")
        #get command from parts
        command = command_parts[0]
        #check if command has 3 parts
        if len(command_parts) == 3:
          try:
            x = int(command_parts[1])
            y = int(command_parts[2])
            #if coordinates are within window, place turret
            if 0 <= x < c.COLS and 0 <= y < c.ROWS:
              place_turret(x, y)
            else:
              print(f"Please enter a value between 0 and {c.COLS - 1} for x and 0 and {c.ROWS - 1} for y")
          except ValueError:
            print("Please input the command in a form 'placeTurret x y' e.g. 'placeTurret 10 5' ")
      
      #check if command is "select"
      if commands[2] in textinput.value:
        #divide command into parts
        command_parts = textinput.value.split(" ")
        #get command from parts
        command = command_parts[0]
        #check if command has 3 parts
        if len(command_parts) == 3:
          try:
            x = int(command_parts[1])
            y = int(command_parts[2])
            #if coordinates are within window, select turret
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
            print("Please input the command in a form 'select x y' e.g. 'select 10 5' ")

      #check if command is "Grid"
      if commands[4] == textinput.value:
        if showgrid:
          showgrid = False
        else:
          showgrid = True

      #clear console on enter press
      textinput.value = ""



  #update display
  pg.display.flip()

print()
pg.quit()