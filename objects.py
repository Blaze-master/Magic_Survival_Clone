from tkinter import Y
import pygame as pg
import math as m
import numpy as np
import time
import os

class Object:
    def __init__(self, position, image):
        self.pos = np.array(position, dtype="float64")
        self.image = pg.image.load(os.path.join(os.path.dirname(__file__),"assets", image))
        self.hitbox = np.array([self.pos,self.pos+[self.image.get_width(),self.image.get_height()]])
    
    def moveHitbox(self):
        self.hitbox = np.array([self.pos,self.pos+[self.image.get_width(),self.image.get_height()]])

    def loadImage(self, image):
        self.image = pg.image.load(os.path.join(os.path.dirname(__file__),"assets", image))

    def draw(self, screen):
        screen.blit(self.image, self.pos)

class NonPlayerObject(Object):
    def __init__(self, position, image, gSpeed):
        super().__init__(position, image)
        self.speed = gSpeed
        self.movement = {
            "left" : [0, self.speed],
            "right" : [0, -self.speed],
            "up" : [1, self.speed],
            "down" : [1, -self.speed]
        }
    
    def move(self, direction):
        for direct in direction:
            m = self.movement[direct]
            self.pos[m[0]] += m[1]
        self.moveHitbox()
    
    def changeSpeed(self, speed):
        self.speed = speed
        self.movement = {
            "left" : [0, self.speed],
            "right" : [0, -self.speed],
            "up" : [1, self.speed],
            "down" : [1, -self.speed]
        }

class Player(Object):
    def __init__(self, position, images):
        super().__init__(position, images[0])

    def move(self, direction):
        pass #Later

class Enemy(NonPlayerObject):
    def __init__(self, position, images, hp, dmg, speed, gSpeed):
        super().__init__(position, images[0], gSpeed)
        self.hp = hp
        self.dmg = dmg
        self.movementSpeed = speed
        self.rad = (self.image.get_width()/2) + 20
        self.center = self.pos+self.rad
    
    def mainMove(self, target):
        center = np.array(target) - [self.image.get_width()/2, self.image.get_height()/2]
        dist = center - self.pos
        add = abs(dist[0]) + abs(dist[1])
        self.pos += dist*self.movementSpeed/add
        self.moveHitbox()
        self.center = self.pos+(self.image.get_width()/2)

class Background(NonPlayerObject):
    def __init__(self, position, image, gSpeed):
        super().__init__(position, image, gSpeed)

if __name__ == "__main__":
    pass