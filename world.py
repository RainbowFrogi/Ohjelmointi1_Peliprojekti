import pygame as pg
import random
import constants as c
from enemy_spawn_data import ENEMY_SPAWN_DATA

class World():
  def __init__(self, data, map_image):
    self.level = 1
    self.money = c.MONEY
    self.health = c.HEALTH
    self.tile_map = []
    self.waypoints = []
    self.level_data = data
    self.image = map_image
    self.enemy_list = []
    self.spawned_enemies = 0

  def process_data(self):
    #look through data to extract relevant info
    for layer in self.level_data["layers"]:
      if layer["name"] =="tilemap":
        self.tile_map = layer["data"]
        print(self.tile_map)
        
      elif layer["name"] == "waypoints":
        for obj in layer["objects"]:
          waypoint_data = obj["polyline"]
          self.process_waypoints(waypoint_data)

  def process_waypoints(self, data):
    #iterate through waypoints to extract individual sets of x and y coordinates
    for point in data:
      temp_x = point.get("x")
      temp_y = point.get("y")
      self.waypoints.append((temp_x, temp_y))

  def process_enemies(self):
    enemies = ENEMY_SPAWN_DATA[self.level - 1]
    for enemy_type in enemies:
      enemies_to_spawn = enemies[enemy_type]
      for enemy in range(enemies_to_spawn):
        self.enemy_list.append(enemy_type)
    #randomize enemy list to shuffle enemy spawning
    random.shuffle(self.enemy_list)    

  def draw(self, surface):
    surface.blit(self.image, (0, 0))