import pygame as pg
import math as m
import numpy as np
import random as rd
import os
from gamedata import textWidth, textHeight, textPadding

class Text:
    def __init__(self, fontType, size, text, color, pos, magic):
        self.font = pg.font.Font(fontType, size)
        self.text = self.font.render(text, True, color)
        self.bgPos = np.array(pos, dtype="float64")
        self.bg = pg.rect.Rect(pos[0], pos[1], textWidth, textHeight)
        self.bgColor = (0,0,0)
        self.pos = self.bgPos + textPadding
        self.highlighted = False
        self.magic = magic
        self.box = [self.bgPos, self.bgPos+[textWidth, textHeight]]
    
    def highlight(self):
        self.highlighted = not self.highlighted
        if self.highlighted:
            self.bgColor = (50,50,50)
        else:
            self.bgColor = (0,0,0)
    
    def draw(self, screen):
        pg.draw.rect(screen, self.bgColor, self.bg)
        screen.blit(self.text, self.pos)

class Object:
    def __init__(self, position, image):
        self.pos = np.array(position, dtype="float64")
        self.image = pg.image.load(os.path.join(os.path.dirname(__file__),"assets", image))
        self.hitbox = np.array([self.pos,self.pos+[self.image.get_width(),self.image.get_height()]])
        self.animType = {}
    
    def moveHitbox(self):
        self.hitbox = np.array([self.pos,self.pos+[self.image.get_width(),self.image.get_height()]])
        self.center = self.pos+[self.image.get_width()/2, self.image.get_height()/2]

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
    
    def mouseMove(self, direction, pSpeed):
        self.pos -= direction * pSpeed * self.speed
        self.center = self.pos+(self.image.get_width()/2)
        self.moveHitbox()
    
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
        self.rad = self.image.get_width()/2
        self.hp = 100
        self.mana = {
            "amt" : 0,
            "lvl" : 1,
            "cap" : 50
        }
        self.artifacts = 0

    def move(self, direction):
        pass #Later

class Enemy(NonPlayerObject):
    def __init__(self, position, images, hp, dmg, speed, enemyType, gSpeed):
        super().__init__(position, images[0], gSpeed)
        self.hp = hp
        self.dmg = dmg
        self.moveSpeed = speed
        self.type = enemyType
        self.rad = (self.image.get_width()/2) + -5 #10, slightly bigger than the sprite's actual radius
        self.trueRad = self.image.get_width()/2
        self.center = self.pos+self.rad
        self.mana = 5
    
    def mainMove(self, target):
        center = np.array(target) - [self.image.get_width()/2, self.image.get_height()/2]
        dist = center - self.pos
        add = abs(dist[0]) + abs(dist[1])
        self.pos += dist*self.moveSpeed*self.speed/add
        self.moveHitbox()

class Sprinter(Enemy):
    def __init__(self, position, images, hp, dmg, speed, enemyType, target, gSpeed):
        super().__init__(position, images, hp, dmg, speed, enemyType, gSpeed)
        self.target = target
    def mainMove(self):
        return super().mainMove(self.target)

class Background(NonPlayerObject):
    def __init__(self, position, image, gSpeed):
        super().__init__(position, image, gSpeed)
        self.center = self.pos + (self.image.get_width()/2)

class Mana(NonPlayerObject):
    def __init__(self, position, mana, speed, gSpeed):
        image = mana+"_mana.png"
        self.mana = 60 if mana=="large" else 20 if mana=="medium" else 10
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
    
    def changeRarity(self):
        rarity = rd.randint(1,100)
        rarity = "small" if rarity < 81 else "medium" if rarity < 96 else "large"
        self.loadImage(rarity+"_mana.png")
        self.mana = 100 if rarity=="large" else 25 if rarity=="medium" else 10

class Projectile(NonPlayerObject):
    def __init__(self, position, image, target, speed, dmg, gSpeed):
        super().__init__(position, image, gSpeed)
        self.target = target-self.pos
        self.moveSpeed = speed
        self.target /= m.sqrt(self.target[0]**2 + self.target[1]**2)
        self.angle = np.arctan(self.target[0]/self.target[1]) * (180/m.pi)
        self.image = pg.transform.rotate(self.image, self.angle)
        self.dmg = dmg
    
    def mainMove(self):
        self.pos += self.target*self.moveSpeed*self.speed
        self.moveHitbox()

class Bar(Object):
    def __init__(self, position, image, maxLen, height):
        super().__init__(position, image)
        self.max = maxLen
        self.height = height
        self.image = pg.transform.scale(self.image, (1, self.height))
    
    def setLength(self, amount, limit):
        length = self.max*(amount/limit)
        length = length if length>0 else 1
        self.image = pg.transform.scale(self.image, (length, self.height))
        self.moveHitbox()

class Zone(NonPlayerObject):
    def __init__(self, position, images, dmg, diameter, duration, gSpeed):
        super().__init__(position, images[0], gSpeed)
        self.image = pg.transform.scale(self.image, (diameter, diameter))
        self.rad = diameter/2
        self.dmg = dmg
        self.duration = duration
        self.moveHitbox()
    
    def respawn(self, coord):
        self.image = pg.transform.rescale(self.image, (self.rad/2,self.rad/2))
        self.pos = coord - (self.rad,self.rad)
        self.moveHitbox()

class MovingZone(Zone):
    def __init__(self, position, images, dmg, diameter, duration, target, speed, gSpeed):
        super().__init__(position, images, dmg, diameter, duration, gSpeed)
        self.target = target
        self.moveSpeed = speed

    def mainMove(self):
        self.pos += self.target*self.moveSpeed*self.speed
        self.moveHitbox()

class Line(NonPlayerObject):
    def __init__(self, position, image, dmg, duration, size, thickness, target, gSpeed):
        super().__init__(position, image, gSpeed)
        self.duration = duration
        self.hits = []
        self.size = size
        self.thickness = thickness
        self.image = pg.transform.scale(self.image, size)
        self.target = target-self.pos
        self.angle = np.arctan(self.target[0]/self.target[1]) * (180/m.pi)
        self.image = pg.transform.rotate(self.image, self.angle)

        x,y = self.target[0],self.target[1]
        if x>0 and y>0:
            self.angle = self.angle
        if (x>0 and y<0) or (x<0 and y<0):
            self.angle += 180
        if x<0 and y>0:
            self.angle += 360
        
        self.target /= m.sqrt(self.target[0]**2 + self.target[1]**2)
        self.pos += self.target*35

        pos = self.pos
        if self.angle > 0 and self.angle <= 90:
            pos = self.pos
        if self.angle > 90 and self.angle <= 180:
            pos = self.pos - [0, np.cos((180-self.angle)*m.pi/180)*size[1]]
        if self.angle > 180 and self.angle <= 270:
            pos = self.pos - [np.sin((self.angle-180)*m.pi/180)*size[1], np.cos((180-self.angle)*m.pi/180)*size[1]]
        if self.angle > 270 and self.angle <= 360:
            pos = self.pos - [np.sin((self.angle-180)*m.pi/180)*size[1], 0]
        self.pos = pos
        self.center = self.pos + [self.image.get_width()/2, self.image.get_height()/2]
        self.dmg = dmg
        self.moveHitbox()
        

if __name__ == "__main__": pass