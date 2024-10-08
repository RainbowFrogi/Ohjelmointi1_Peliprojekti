import sys
import mysql.connector
import pygame as pg
import pygame_textinput
import json

from constants import SCREEN_HEIGHT
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

#initialise mysql connection
try:
    connection = mysql.connector.connect(
            host="localhost",
            user="TDuser",
            password="1234",
            database="towerdefense",
            charset='utf8mb4',  # Specify charset
            collation='utf8mb4_unicode_ci' # Specify collation
        )
    print("Connected to MySQL turretdefense database")
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL Platform: {e}")
    sys.exit(1)

#game variables
commands = [
  "create",
  "place",
  "select",
  "grid",
  "addCoins",
  "clear"
]
coins = 100
hearts = 5
wave = 0
showgrid = False
debugging = True

last_enemy_spawn = pg.time.get_ticks()

TURRET_IMAGE_MAP = {
  "mk5" : "turret_1",
  "mk10": "turret_2",
  "mk15": "turret_3",
  "mk20": "turret_4"
}

enemy_images = {
  "rogue"  : pg.image.load('assets/images/enemies/enemy_rogue.png').convert_alpha(),
  "soldier": pg.image.load('assets/images/enemies/enemy_soldier.png').convert_alpha(),
  "heavy": pg.image.load('assets/images/enemies/enemy_heavy.png').convert_alpha(),
  "elite" : pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha()
}

text_log = [("","red")]

#LOAD IMAGES

#map
map_image = pg.image.load('levels/level.png').convert_alpha()

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
  print(message)

def fetch_turret_data(turret_name):
  try:
    cursor = connection.cursor()
    query = "SELECT cooldown, turret_range, damage, cost FROM turrets WHERE name = %s"
    cursor.execute(query, (turret_name,))
    turret_data = cursor.fetchone()
    cursor.close()
    print(f"Fetched turret data: {turret_data}")
    return turret_data
  except mysql.connector.Error as e:
    print(f"Error fetching turret data: {e}")
    return None
    

def place_turret(turret_type, x, y):
  #convert 2D coordinates to 1D
  print(turret_type)
  global coins
  world_tile_num = (y * c.COLS) + x
  turret_data = fetch_turret_data(turret_type)
  if turret_data:
    cooldown, turret_range, damage, cost = turret_data
    if coins >= cost:
      #check if tile on coordinates is a grass tile
      if world.tile_map[world_tile_num] == 7:
        tile_free = True
        for turret in turret_group:
          #check if tile is already occupied by a turret
          if (x, y) == (turret.tile_x, turret.tile_y):
            tile_free = False
      
        #if tile is free, place turret and add it to a group
        if tile_free:
          turret_sheet_name = TURRET_IMAGE_MAP.get(turret_type)
          turret_sheet = pg.image.load(f'assets/images/turrets/{turret_sheet_name}.png').convert_alpha()
          new_turret = Turret(turret_sheet, x, y, cooldown, turret_range, damage)
          coins -= cost
          turret_group.add(new_turret)
        else:
          console_error_message("This tile is already occupied by a turret")
      else:
        console_error_message("This tile is not a grass tile")    
    else:
      console_error_message("Not enough coins to place turret")
  else:
    console_error_message("Turret data not found")

#Turret selection for upgrading and showing range
def select_turret(x, y):
  for turret in turret_group:
      if (x, y) == (turret.tile_x, turret.tile_y):
        return turret

def update_groups():
  enemy_group.update()
  turret_group.update(enemy_group)

def fetch_enemy_data(enemy_type):
  try:
    cursor = connection.cursor()
    query = "SELECT speed, damage, health FROM enemies WHERE name = %s"
    cursor.execute(query, (enemy_type,))
    enemy_data = cursor.fetchone()
    cursor.close()
    print(f"Fetched enemy data: {enemy_data}")
    return enemy_data
  except mysql.connector.Error as e:
    print(f"Error fetching enemy data: {e}")
    return None

def create_enemy(enemy_type):
  print(enemy_type)
  enemy_data = fetch_enemy_data(enemy_type)
  if enemy_data:
    
    speed, damage, health = enemy_data
    try:
      enemy = Enemy(enemy_type, world.waypoints, enemy_images, speed, damage, health)
    except ValueError as e:
      print(f"Error creating enemy: {e}")
    enemy_group.add(enemy)
  else:
    print("Enemy data not found")

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

#Update text log
def update_text_log(new_text):
  # Check if any valid command is present and match color
  text_log_color = "black"
  for i in commands:
    if i in textinput.value:
      text_log_color = "blue"
  #stop appending list when it reaches top of UI
  if len(text_log) <=10:
    text_log.append(text_log[-1])
  # move text higher in the list
  for i in range(1,len(text_log)+1):
    if i != len(text_log):
      text_log[-i] = text_log[-(i+1)]
  # make new first item in list
  text_log[0] = (new_text,text_log_color)

def draw_text_log():
  for i in range(len(text_log)):
    text = font.render(text_log[i][0], True, text_log[i][1])
    screen.blit(text, (gui_x, SCREEN_HEIGHT-50-i * 20))



#create world
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

enemy_type = "soldier"
enemy = Enemy(enemy_type, world.waypoints, enemy_images)
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

  #draw grid and grid numbers
  if showgrid:
    draw_grid()
    draw_gridnums()

  #draw text log
  draw_text_log()

  #draw groups
  enemy_group.draw(screen)
  for turret in turret_group:
    turret.draw(screen)
  
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
    
    if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
      print(f"You entered command {textinput.value} to the command line")
      
      #deselect all turrets whenever a command is run
      for turret in turret_group:
        turret.selected = False

      #check if command is "create"
      if commands[0] in textinput.value:
        #divide command into parts
        command_parts = textinput.value.split(" ")
        print(f"Command parts: {command_parts}")
        #get command from parts
        command = command_parts[0]
        #check if command has 2 parts
        if len(command_parts) == 2:
          try:
            enemy_type = command_parts[1]
            create_enemy(enemy_type)
          except ValueError as e:
            print(f"ValueError: {e}")
            print("Please input the command in a form 'create enemy' e.g. 'create soldier' ")

        create_enemy(enemy_type)

      #check if command is "placeTurret"
      elif commands[1] in textinput.value:
        #divide command into parts
        command_parts = textinput.value.split(" ")
        print(f"Command parts: {command_parts}")
        #get command from parts
        command = command_parts[0]
        #check if command has 4 parts
        if len(command_parts) == 4:
          try:
            turret_type = command_parts[1]
            x = int(command_parts[2])
            y = int(command_parts[3])
            #if coordinates are within window, place turret
            if 0 <= x < c.COLS and 0 <= y < c.ROWS:
              place_turret(turret_type, x, y)
            else:
              print(f"Please enter a value between 0 and {c.COLS - 1} for x and 0 and {c.ROWS - 1} for y")
          except ValueError as e:
            print(f"ValueError: {e}")
            print("Please input the command in a form 'placeTurret x y' e.g. 'placeTurret 10 5' ")
        else:
          print("Invalid command lenght")
          print("Please input the command in a form 'placeTurret x y' e.g. 'placeTurret 10 5' ")
      
      #check if command is "select"
      elif commands[2] in textinput.value:
        #divide command into parts
        command_parts = textinput.value.split(" ")
        print(f"Command parts: {command_parts}")

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
          except ValueError as e:
            print(f"ValueError: {e}")
            print("Please input the command in a form 'select x y' e.g. 'select 10 5' ")
        else:
          print("Invalid command lenght")
          print("Please input the command in a form 'select x y' e.g. 'select 10 5' ")

      #check if command is "addCoins" and debugging is enabled
      elif debugging and commands[4] in textinput.value:
        #divide command into parts
        command_parts = textinput.value.split(" ")
        #get command from parts
        command = command_parts[0]
        #check if command has 2 parts
        if len(command_parts) == 2:
          try:
            coins += int(command_parts[1])
          except ValueError:
            print("Please input the command in a form 'addCoins x' e.g. 'addCoins 50' ")

      #check if command is "Grid"
      elif commands[3] == textinput.value:
        if showgrid:
          showgrid = False
        else:
          showgrid = True

      #check if command is "Grid"
      if commands[5] in textinput.value:
        text_log.clear()
        text_log = [("", "red")]
        textinput.value = ""

      #Update text log list
      update_text_log(textinput.value)

      #clear console on enter press
      textinput.value = ""



  #update display
  pg.display.flip()

print()
pg.quit()