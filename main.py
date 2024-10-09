import sys
from tkinter.messagebox import showinfo

import mysql.connector
import pygame as pg
import pygame_textinput
import json

from constants import SCREEN_HEIGHT
from enemy import Enemy
from turret import Turret
import constants as c
from game_manager import Game_Manager

#initialise pygame
pg.init()
#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             GUI
#-------------------------------------------------------------------------------------------------------------------------------------------------
# VARIABLES
gui_width = c.COMMANDLINE_PANEL
gui_x = c.SCREEN_WIDTH
gui_y = 0
grid_width = 1
grid_color = "black"
grid_num_color = "black"
text_log_rows = 15
clock = pg.time.Clock()
#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             WINDOW
#-------------------------------------------------------------------------------------------------------------------------------------------------
# CREATE OBJECTS
textinput = pygame_textinput.TextInputVisualizer()
# Set cursor width
textinput.cursor_width = 12
# GAME WINDOW
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.COMMANDLINE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")
# initialise font
pg.font.init()
font = pg.font.SysFont(None, 36)
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36, bold = True)

#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             MySQL
#-------------------------------------------------------------------------------------------------------------------------------------------------
# INITIALISE CONNECTION
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

#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             GAME MANAGEMENT
#-------------------------------------------------------------------------------------------------------------------------------------------------
# VARIABLES
text_log = [("","red")]
commands = [
  "create",
  "place",
  "select",
  "grid",
  "addmoney",
  "clear",
  "info",
  "beginwave",
  "restart"
]
wave = 0
showgrid = False
debugging = True
showinfo = False

last_enemy_spawn = pg.time.get_ticks()

game_over = False
game_outcome = 0    # -1 = loss, 0 = ongoing, 1 = win
level_started = False

#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             CHARACTERS
#-------------------------------------------------------------------------------------------------------------------------------------------------
# VARIABLES
TURRET_IMAGE_MAP = {
  "mk5" : "turret_1",
  "mk10": "turret_2",
  "mk15": "turret_3",
  "mk20": "turret_4"
}


#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             LOAD ASSETS
#-------------------------------------------------------------------------------------------------------------------------------------------------

enemy_images = {
  "rogue"  : pg.image.load('assets/images/enemies/enemy_rogue.png').convert_alpha(),
  "soldier": pg.image.load('assets/images/enemies/enemy_soldier.png').convert_alpha(),
  "heavy": pg.image.load('assets/images/enemies/enemy_heavy.png').convert_alpha(),
  "elite" : pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha()
}



#map
map_image = pg.image.load('levels/level.png').convert_alpha()

#enemies
enemy_image = pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha()

#ICONS
#coin icon
coin_image = pg.image.load('assets/images/gui/coin.png').convert_alpha()

#heart icon
heart_image = pg.image.load('assets/images/gui/heart.png').convert_alpha()

#load sfx
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.35)


#load json data for level
with open('levels/level.tmj') as file:
  world_data = json.load(file)


#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             FUNCTIONS
#-------------------------------------------------------------------------------------------------------------------------------------------------
def draw_text(text, font, text_color, x, y):
  img = font.render(text, True, text_color)
  screen.blit(img, (x, y))

def console_error_message(message):
  print(message)
  update_text_log(textinput.value,False)
  update_text_log(message,True)
  textinput.value = ""


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
  world_tile_num = (y * c.COLS) + x
  turret_data = fetch_turret_data(turret_type)
  if turret_data:
    cooldown, turret_range, damage, cost = turret_data
    if game_manager.money >= cost:
      #check if tile on coordinates is a grass tile
      if game_manager.tile_map[world_tile_num] == 7:
        tile_free = True
        for turret in turret_group:
          #check if tile is already occupied by a turret
          if (x, y) == (turret.tile_x, turret.tile_y):
            tile_free = False
      
        #if tile is free, place turret and add it to a group
        if tile_free:
          turret_sheet_name = TURRET_IMAGE_MAP.get(turret_type)
          turret_sheet = pg.image.load(f'assets/images/turrets/{turret_sheet_name}.png').convert_alpha()
          new_turret = Turret(turret_sheet, x, y, cooldown, turret_range, damage, shot_fx)
          game_manager.money -= cost
          turret_group.add(new_turret)
        else:
          print("This tile is already occupied by a turret")
      else:
        print("This tile is not a grass tile")    
    else:
      print("Not enough money to place turret")
  else:
    print("Turret data not found")

#Turret selection for upgrading and showing range
def select_turret(x, y):
  for turret in turret_group:
      if (x, y) == (turret.tile_x, turret.tile_y):
        return turret

def update_groups():
  enemy_group.update(game_manager)
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
      enemy = Enemy(enemy_type, game_manager.waypoints, enemy_images, speed, damage, health)
    except ValueError as e:
      print(f"Error creating enemy: {e}")
    enemy_group.add(enemy)
  else:
    print("Enemy data not found")

def save_player_data(name, highest_wave, enemies_killed, damage_taken, money):
  try:
    cursor = connection.cursor()
    query = "INSERT INTO users (name, highest_wave, enemies_killed, damage_taken, money) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (name, highest_wave, enemies_killed, damage_taken, money))
    connection.commit()
    cursor.close()
    print("Player data saved")
  except mysql.connector.Error as e:
    print(f"Error saving player data: {e}")

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
def update_text_log(new_text,is_error_message):
  # turn text red if error message
  if is_error_message:
    text_log_color = "red"
  else:
    # Check if any valid command is present and match color
    text_log_color = "black"
    for i in commands:
      if i in textinput.value:
        text_log_color = "blue"
  #stop appending list when it reaches top of UI
  if len(text_log) <= text_log_rows:
    text_log.append(text_log[-1])
  # move text higher in the list
  for i in range(1,len(text_log)+1):
    if i != len(text_log):
      text_log[-i] = text_log[-(i+1)]
  # make new first item in list
  text_log[0] = (new_text,text_log_color)

#Draw the text log
def draw_text_log():
  for i in range(len(text_log)):
    text = font.render(text_log[i][0], True, text_log[i][1])
    screen.blit(text, (gui_x, SCREEN_HEIGHT-50-i * 20))

#draw info screen
def draw_info_screen():
  pg.draw.rect(screen,"lightblue",(0,0,c.COLS*c.TILE_SIZE,c.ROWS*c.TILE_SIZE))

#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             GAME MANAGEMENT
#-------------------------------------------------------------------------------------------------------------------------------------------------
# Create GAME MANAGER
game_manager = Game_Manager(world_data, map_image)
game_manager.process_data()
game_manager.process_enemies()

# Create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()


#-------------------------------------------------------------------------------------------------------------------------------------------------
#                                                             INITIALIZE GUI
#-------------------------------------------------------------------------------------------------------------------------------------------------
run = True
# GAME LOOP
while run:
  clock.tick(c.FPS)

  # Check if player has won or loss
  if game_over == False:
    #update groups only if game is not over
    update_groups()
    # Check if player has lost
    if game_manager.health <= 0:
      game_over = True
      game_outcome = -1 #loss 
    # Check if player has won
    elif game_manager.level > c.TOTAL_WAVES:
      game_over = True
      game_outcome = 1 #won
  #--------------------------------------------------------------------
  #                           SCREEN DRAWING
  #--------------------------------------------------------------------
  # RESET SCREEN
  screen.fill("white")

  #---------------------------------------------------------  
  ## DRAW PANELS
  # CONSOLE PANEL
  pg.draw.rect(screen, "grey", (gui_x, gui_y+250, gui_width, c.SCREEN_HEIGHT))
  # PLAYER STATUS PANEL
  pg.draw.rect(screen, "purple", (gui_x, gui_y, gui_width, 250))
  # MAP (LEVEL) PANEL
  game_manager.draw(screen)

  #---------------------------------------------------------  
  ## DRAW ICONS -> PLAYER STATUS PANEL
  # COIN
  screen.blit(coin_image, (gui_x + 10, 10))
  # COIN TEXT
  draw_text(str(game_manager.money), text_font, "white", gui_x + 50, 15)
  # HEART
  screen.blit(heart_image, (gui_x + 10, 50))
  # HEART TEXT
  draw_text(str(game_manager.health), text_font, "white", gui_x + 50, 55)
  # WAVE TEXT
  draw_text(f"Wave: {game_manager.level}", text_font, "white", gui_x + 10, 90)
  
  #---------------------------------------------------------  
  ## DRAW -> CONSOLE PANEL
  draw_text_log()
  
  #---------------------------------------------------------  
  ## DRAW -> MAP (LEVEL)
  # GRID
  if showgrid:
    draw_grid()
    draw_gridnums()
  # GROUPS
  enemy_group.draw(screen)
  for turret in turret_group:
    turret.draw(screen)

  #---------------------------------------------------------  
  ## DRAW PANEL
  # MAP (INFO SCREEN) PANEL
  if showinfo:
    draw_info_screen()
  #--------------------------------------------------------------------
  #                           GAME LOGIC
  #--------------------------------------------------------------------
  if game_over == False:
    ## SPAWN ENEMY
    if level_started == True:
      if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
        if game_manager.spawned_enemies < len(game_manager.enemy_list):
          enemy_type = game_manager.enemy_list[game_manager.spawned_enemies]
          create_enemy(enemy_type)
          game_manager.spawned_enemies += 1
          last_enemy_spawn = pg.time.get_ticks()
    
    ## ON WAVE END
    if game_manager.check_wave_complete():
      game_manager.money += c.WAVE_COMPLETE_REWARD
      game_manager.level += 1
      level_started = False
      last_enemy_spawn = pg.time.get_ticks()
      game_manager.reset_level()
      game_manager.process_enemies()

  else:
    pg.draw.rect(screen, "lightblue", (150, 200, 500, 200), border_radius = 30)
    if game_outcome == -1:
      draw_text("Game Over", large_font, "red", 300, 250)
      draw_text("Write player name to play again!", text_font, "black", 200, 300)
    else:
      draw_text("You Win!", large_font, "darkgreen", 315, 250)
      draw_text("Write player name to play again!", text_font, "black", 200, 300)



  
  #--------------------------------------------------------------------
  #                           CONTROLS
  #--------------------------------------------------------------------
  # PYGAME EVENTS
  events = pg.event.get()

  # UPDATE CONSOLE INPUT
  textinput.update(events)

  # BLIT: textinput value on screen
  screen.blit(textinput.surface, (gui_x, c.SCREEN_HEIGHT - 25))
  
  #----------------------------------
  #             EVENTS
  #----------------------------------
  for event in events:
    ## CLOSE GAME
    if event.type == pg.QUIT:
      run = False
    
    #----------------------------------
    #       CONSOLE PANEL LOGIC
    #----------------------------------
    if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
      print(f"You entered command {textinput.value} to the command line")
      
      # Deselect all turrets whenever a command is run
      for turret in turret_group:
        turret.selected = False

      #----------------------------------
      #           COMMANDS
      #----------------------------------
      input = textinput.value
      input_split = input.split(" ")
      command = input_split[0]
      # COMMAND: CREATE
      if commands[0] == command and not game_over:
        print(f"Command parts: {input_split}")
        #get command from parts
        #check if command has 2 parts
        if len(input_split) == 2:
          try:
            enemy_type = input_split[1]
            create_enemy(enemy_type)
          except ValueError as e:
            print(f"ValueError: {e}")
            print("Please input the command in a form 'create enemy' e.g. 'create soldier' ")

      # COMMAND: PLACE
      elif commands[1] == command and not game_over:
        print(f"Command parts: {input_split}")
        #check if command has 4 parts
        if len(input_split) == 4:
          try:
            turret_type = input_split[1]
            x = int(input_split[2])
            y = int(input_split[3])
            #if coordinates are within window, place turret
            if 0 <= x < c.COLS and 0 <= y < c.ROWS:
              place_turret(turret_type, x, y)
            else:
              print(f"Please enter a value between 0 and {c.COLS - 1} for x and 0 and {c.ROWS - 1} for y")
          except ValueError as e:
            print(f"ValueError: {e}")
            print("Please input the command in a form 'place turret_name x y' e.g. 'place turret_name 10 5' ")
        else:
          print("Invalid command lenght")
          print("Please input the command in a form 'place turret_name x y' e.g. 'place turret_name 10 5' ")
      
      # COMMAND: SELECT
      elif commands[2] == command and not game_over:
        print(f"Command parts: {input_split}")

        #check if command has 3 parts
        if len(input_split) == 3:
          try:
            x = int(input_split[1])
            y = int(input_split[2])
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

      # COMMAND: GRID
      elif commands[3] == command:
        showgrid = not showgrid

      # COMMAND: ADDMONEY
      elif debugging and commands[4] == command and not game_over:
        #check if command has 2 parts
        if len(input_split) == 2:
          try:
            game_manager.money += int(input_split[1])
          except ValueError:
            print("Please input the command in a form 'addMoney x' e.g. 'addMoney 50' ")

      # COMMAND: CLEAR
      elif commands[5] == command and not game_over:
        text_log.clear()
        text_log = [("", "red")]
        textinput.value = ""

      # COMMAND: INFO
      elif commands[6] == command:
        if showinfo:
          showinfo = False
        else:
          showinfo = True


      # check if command is "beginWave" and no enemies are left alive
      elif commands[7] == command and not game_over:
        if len(enemy_group) == 0:
          level_started = True
        else:
          print("There are still enemies on the map")

      #if game is over, write anything to save player data with the text input value
      elif game_over and textinput.value != "":
        #save player data
        player_name = textinput.value
        highest_wave = game_manager.level
        enemies_killed = game_manager.total_killed_enemies
        damage_taken = c.HEALTH - game_manager.health
        money = game_manager.money
        save_player_data(player_name, highest_wave, enemies_killed, damage_taken, money)

        #restart game
        game_over = False
        level_started = False
        game_outcome = 0
        game_manager = Game_Manager(world_data, map_image)
        game_manager.process_data()
        game_manager.process_enemies()
        enemy_group.empty()
        turret_group.empty()
        #empty groups
        enemy_group.empty()
        turret_group.empty()
        
      
      elif game_over and textinput.value == "":
        console_error_message("Please enter a player name")

      else:
        print("Invalid command")


      
      #----------------------------------
      #       CONSOLE UPDATE
      #----------------------------------
      # UPDATE CONSOLE_LOGS[]
      update_text_log(textinput.value,False)

      # CLEAR CONSOLE INPUT(ENTER pressed)
      textinput.value = ""

  # UPDATE DISPLAY
  pg.display.flip()

# print()
pg.quit()