import math
import pygame as pg
import constants as c
from pygame.sprite import Group


class Turret(pg.sprite.Sprite):
    def __init__(self, sprite_sheet, tile_x, tile_y, cooldown, range, damage, shot_fx):
        pg.sprite.Sprite.__init__(self)
        self.cooldown = cooldown
        self.range = range
        self.damage = damage
        self.last_shot = pg.time.get_ticks()
        self.selected = False
        self.target = None
        self.laser_level = 1
        self.laser_level_progress = 0
        self.firing = False
        self.laser_damage = 2


        #position variables
        self.tile_x = tile_x
        self.tile_y = tile_y
        
        #calculate center coordinates
        self.x = (self.tile_x + 0.5) * c.TILE_SIZE
        self.y = (self.tile_y + 0.5) * c.TILE_SIZE

        #shot sound fx
        self.shot_fx = shot_fx

        #animation variables
        self.sprite_sheet = sprite_sheet
        self.animation_list = self.load_images()
        self.frame_index = 0
        self.update_time = pg.time.get_ticks()

        #update image
        self.angle = 90
        self.original_image = self.animation_list[self.frame_index]
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        #draw range circle
        self.range_image = pg.Surface((self.range * 2, self.range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
        self.range_image.set_alpha(100)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = self.rect.center

    def load_images(self):
        #extract images from spritesheet
        size = self.sprite_sheet.get_height()
        animation_list = []
        for x in range(c.ANIMATION_STEPS):
            temp_img = self.sprite_sheet.subsurface((x * size, 0, size, size))
            animation_list.append(temp_img)
        return animation_list
    
    def update(self, enemy_group):
        #if firing, play firing animation
        if self.firing:
            self.play_animation()
        else:
            #fire again after cooldown
            if pg.time.get_ticks() - self.last_shot > self.cooldown:
                # search for new target if needed
                self.pick_target(enemy_group)
                if self.target is not None:
                    self.firing = True
                    #damage and sfx
                    self.damage_target()



    def pick_target(self, enemy_group):
        if self.target is None or self.target not in enemy_group:
            #decrease lasers level when its target dies
            self.laser_level = 1
            self.target = None
            #find an enemy to target
            x_dist = 0
            y_dist = 0
            closest_distance = self.range
            #loop through enemies and find the closest one within range
            for enemy in enemy_group:
                if enemy.health > 0:
                    x_dist = enemy.pos[0] - self.x
                    y_dist = enemy.pos[1] - self.y
                    dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
                    #check if distance is shorter than last shortest and store
                    if dist < closest_distance:
                        closest_enemy = enemy
                        closest_distance = dist
            #check if stored distance is in range and assign target and angle to target
            if closest_distance < self.range:
                self.target = closest_enemy
                self.angle = math.degrees(math.atan2(-(self.target.pos[1] - self.y), self.target.pos[0] - self.x))
        else:
            self.angle = math.degrees(math.atan2(-(self.target.pos[1] - self.y), self.target.pos[0] - self.x))

    def play_animation(self):
        #update image
        self.original_image = self.animation_list[self.frame_index]
        #check if enough time has passed since the last update
        if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1

            #check if animation ended
            if self.frame_index >= len(self.animation_list):
                self.frame_index = 0
                #record completed time and end firing so cooldown can begin
                self.last_shot = pg.time.get_ticks()
                self.firing = False

                #clear target if target out of range
                x_dist = self.target.pos[0] - self.x
                y_dist = self.target.pos[1] - self.y
                dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
                if dist > self.range:
                    self.target = None
                    print("out of range")

    def damage_target(self):
        # check turret type and damage enemy
        if self.cooldown == 0:
            self.target.health -= self.damage * self.laser_damage * 2**(self.laser_level -1)
        else:
            self.target.health -= self.damage
        #increase laser level
        if self.laser_level_progress <= 15:
            self.laser_level_progress += 1
        if self.laser_level_progress >= 15 and self.laser_level <= 3:
            self.laser_level += 1
            self.laser_level_progress = 0
        # play sound fx
        #self.shot_fx.play()
    
    def draw(self, surface):
        #Check if base turret or laser and rotate image if laser
        if self.cooldown != 0:
            self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        else:
            self.image = self.original_image

        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.selected:
            surface.blit(self.range_image, self.range_rect)

        # draw laser turret laser
        if self.cooldown == 0 and self.target != None:
            pg.draw.line(surface, "red", (self.x, self.y), (self.target.pos[0], self.target.pos[1]), self.laser_level**2)