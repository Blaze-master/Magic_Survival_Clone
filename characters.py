import pygame as pg
import math as m
import time
import os

class Object:
    def __init__(self, position, image):
        self.pos = position
        self.image = pg.image.load(os.path.join(os.path.dirname(__file__),"assets", image))
        self.hitbox = [self.pos[0],
            self.pos[0]+self.image.get_width(),
            self.pos[1],
            self.pos[1]+self.image.get_height()
            ]
    
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
        self.hitbox = [self.pos[0],
            self.pos[0]+self.image.get_width(),
            self.pos[1],
            self.pos[1]+self.image.get_height()
            ]
    
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
    
    def mainMove(self, playerPos):
        pass #Later

class Background(NonPlayerObject):
    def __init__(self, position, image, gSpeed):
        super().__init__(position, image, gSpeed)

if __name__ == "__main__":
    pass