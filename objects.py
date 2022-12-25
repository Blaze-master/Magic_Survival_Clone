from tkinter import Y
import pygame as pg
import math as m
import numpy as np
import random as rd
import time
import os

class Object:
    def __init__(self, position, image):
        self.pos = np.array(position, dtype="float64")
        self.image = pg.image.load(os.path.join(os.path.dirname(__file__),"assets", image))
        self.hitbox = np.array([self.pos,self.pos+[self.image.get_width(),self.image.get_height()]])
        self.animType = {}
    
    def moveHitbox(self):
        self.hitbox = np.array([self.pos,self.pos+[self.image.get_width(),self.image.get_height()]])

    def loadImage(self, image):
        self.image = pg.image.load(os.path.join(os.path.dirname(__file__),"assets", image))
    
    def runAnimation(self):
        pass

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
    
    def move(self, direction, pSpeed):
        con1 = ("left" in direction and "up" in direction) or ("left" in direction and "down" in direction)
        con2 = ("right" in direction and "up" in direction) or ("right" in direction and "down" in direction)
        con = con1 or con2
        coeff = (2**0.5)/2 if con else 1
        for direct in direction:
            m = self.movement[direct]
            self.pos[m[0]] += m[1] * pSpeed * coeff
        self.moveHitbox()
        self.center = self.pos+(self.image.get_width()/2)
    
    def mouseMove(self, direction, pSpeed):
        self.pos -= direction * pSpeed * self.speed
        self.center = self.pos+(self.image.get_width()/2)
    
    def changeSpeed(self, speed):
        self.speed = speed
        self.movement = {
            "left" : [0, self.speed],
            "right" : [0, -self.speed],
            "up" : [1, self.speed],
            "down" : [1, -self.speed]
        }
    
    def respawn(self, spawnBound, renderBound):
        if self.pos[0] < spawnBound[0]:
            self.pos[0] = rd.randint(renderBound[1], spawnBound[1])
            self.pos[1] = rd.randint(spawnBound[2], spawnBound[3])
        if self.pos[0] > spawnBound[1]:
            self.pos[0] = rd.randint(spawnBound[0], renderBound[0])
            self.pos[1] = rd.randint(spawnBound[2], spawnBound[3])
        if self.pos[1] < spawnBound[2]:
            self.pos[0] = rd.randint(spawnBound[0], spawnBound[1])
            self.pos[1] = rd.randint(renderBound[3], spawnBound[3])
        if self.pos[1] > spawnBound[3]:
            self.pos[0] = rd.randint(spawnBound[0], spawnBound[1])
            self.pos[1] = rd.randint(spawnBound[2], renderBound[2])
        pass

class Player(Object):
    def __init__(self, position, images):
        super().__init__(position, images[0])
        self.center = self.pos + [self.image.get_width()/2, self.image.get_height()/2]
        self.pickupRad = (self.image.get_height()/2) + 50
        self.hp = 100
        self.mana = 0
        self.artifacts = 0

    def move(self, direction):
        pass #Later

class Enemy(NonPlayerObject):
    def __init__(self, position, images, hp, dmg, speed, gSpeed):
        super().__init__(position, images[0], gSpeed)
        self.hp = hp
        self.dmg = dmg
        self.moveSpeed = speed
        self.rad = (self.image.get_width()/2) + 20
        self.trueRad = self.image.get_width()/2
        self.center = self.pos+self.rad
    
    def mainMove(self, target):
        center = np.array(target) - [self.image.get_width()/2, self.image.get_height()/2]
        dist = center - self.pos
        add = abs(dist[0]) + abs(dist[1])
        self.pos += dist*self.moveSpeed*self.speed/add
        self.moveHitbox()

class Background(NonPlayerObject):
    def __init__(self, position, image, gSpeed):
        super().__init__(position, image, gSpeed)
        self.center = self.pos + (self.image.get_width()/2)

class Mana(NonPlayerObject):
    def __init__(self, position, mana, speed, gSpeed):
        image = mana+"_mana.png"
        self.mana = 150 if mana=="large" else 40 if mana=="medium" else 10
        super().__init__(position, image, gSpeed)
        self.rad = self.image.get_width()/2
        self.center = self.pos+self.rad
        self.moveSpeed = speed
    
    def attract(self, target):
        center = np.array(target) - [self.image.get_width()/2, self.image.get_height()/2]
        dist = center - self.pos
        add = abs(dist[0]) + abs(dist[1])
        self.pos += dist*self.moveSpeed*self.speed/add
        self.moveHitbox()
        self.center = self.pos+(self.image.get_width()/2)
    
    def changeRarity(self):
        rarity = rd.randint(1,100)
        rarity = "small" if rarity < 81 else "medium" if rarity < 96 else "large"
        self.loadImage(rarity+"_mana.png")
        self.mana = 150 if rarity=="large" else 40 if rarity=="medium" else 10

class Projectile(NonPlayerObject):
    def __init__(self, position, image, target, speed, dmg, gSpeed):
        super().__init__(position, image, gSpeed)
        self.target = target-self.pos
        self.target /= m.sqrt(self.target[0]**2 + self.target[1]**2)
        self.moveSpeed = speed
        self.angle = m.atan(self.target[0]/self.target[1]) * (180/m.pi)
        self.image = pg.transform.rotate(self.image, self.angle)
        self.dmg = dmg
    
    def mainMove(self):
        self.pos += self.target*self.moveSpeed*self.speed
        

if __name__ == "__main__":
    pass