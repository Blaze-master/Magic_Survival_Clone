import pygame as pg
import math as m
import numpy as np
import random as rd
import os
from gamedata import textWidth, textHeight, textPadding

class Text:
    def __init__(self, fontType, size, color, pos, text, magic):
        self.mainFont = pg.font.Font(fontType, size[0])
        self.subFont = pg.font.Font(fontType, size[1])
        self.mainText = self.mainFont.render(text[0], True, color[0])
        self.subText = self.subFont.render(text[1], True, color[1])
        self.bgPos = np.array(pos, dtype="float64")
        self.bg = pg.rect.Rect(pos[0], pos[1], textWidth, textHeight)
        self.bgColor = (0,0,0)
        self.pos = self.bgPos + textPadding
        self.highlighted = False
        self.magic = magic
        self.box = [self.bgPos, self.bgPos+[textWidth, textHeight]]
    
    def highlight(self):
        self.highlighted = True
        self.bgColor = (50,50,50)
    
    def dehighlight(self):
        self.highlighted = False
        self.bgColor = (0,0,0)
    
    def draw(self, screen):
        pg.draw.rect(screen, self.bgColor, self.bg)
        screen.blit(self.mainText, self.pos)
        screen.blit(self.subText, self.pos+(0,50))

class Object:
    def __init__(self, position, image):
        self.pos = np.array(position, dtype="float64")
        self.image = self.loadImage(image) if image else None
        self.moveHitbox()
        self.dim = self.hitbox[1] - self.hitbox[0]
        self.animType = {}
    
    def moveHitbox(self):
        if self.image:
            self.hitbox = np.array([self.pos,self.pos+[self.image.get_width(),self.image.get_height()]])
            self.center = self.pos+[self.image.get_width()/2, self.image.get_height()/2]
        else:
            self.hitbox = self.pos
            self.center = self.pos

    def loadImage(self, image):
        return pg.image.load(os.path.join(os.path.dirname(__file__),"assets", image))
    
    def runAnimation(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.pos)

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

class Player(Object):
    def __init__(self, position, images):
        super().__init__(position, images[0])
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
    
    def keyMove(self, direction, pSpeed):
        con1 = ("left" in direction or "right" in direction)
        con2 = ("up" in direction or "down" in direction)
        con = con1 and con2
        coeff = (2**0.5)/2 if con else 1
        for direct in direction:
            m = self.movement[direct]
            self.pos[m[0]] += m[1] * pSpeed * coeff
        self.moveHitbox()
    
    def mouseMove(self, direction, pSpeed):
        self.pos -= direction * pSpeed * self.speed
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


class Enemy(NonPlayerObject):
    def __init__(self, position, images, hp, dmg, speed, enemyType, gSpeed):
        super().__init__(position, images[0], gSpeed)
        self.hp = hp
        self.dmg = dmg
        self.moveSpeed = speed
        self.type = enemyType
        self.rad = self.image.get_width()/2
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
        super().mainMove(self.target)

class Background(NonPlayerObject):
    def __init__(self, position, image, gSpeed):
        super().__init__(position, image, gSpeed)

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
    def __init__(self, position, image, target, speed, gSpeed):
        super().__init__(position, image[0], gSpeed)
        self.target = target-self.pos
        self.target /= m.sqrt(self.target[0]**2 + self.target[1]**2)
        self.angle = np.arctan(self.target[0]/self.target[1]) * (180/m.pi)
        x,y = self.target[0],self.target[1]
        if y>0:
            self.angle += 180
        elif x>0:
            self.angle += 360
        self.image = pg.transform.rotate(self.image, self.angle)
        self.moveHitbox()
        self.moveSpeed = speed
        self.hits = []
    
    def mainMove(self):
        self.pos += self.target*self.moveSpeed*self.speed
        self.moveHitbox()

class PiercingProjectile(Projectile):
    def __init__(self, position, image, target, speed, gSpeed):
        self.thickness = self.loadImage(image[0]).get_width()
        super().__init__(position, image, target, speed, gSpeed)

class Tsunami(Projectile):
    def __init__(self, position, image, target, speed, size, gSpeed):
        super().__init__(position, image, target, speed, gSpeed)
        self.image = self.loadImage(image[0])
        self.image = pg.transform.scale(self.image, size)
        self.image = pg.transform.rotate(self.image, self.angle)
        self.thickness = size[0]

class Zone(NonPlayerObject):
    def __init__(self, position, images, diameter, duration, gSpeed):
        super().__init__(position, images[0], gSpeed)
        self.image = pg.transform.scale(self.image, (diameter, diameter)) if diameter else self.image
        self.rad = diameter/2 if diameter else self.image.get_width()
        self.duration = duration
        self.hits = []
        self.moveHitbox()
    
    def respawn(self, coord):
        self.image = pg.transform.scale(self.image, (self.rad*2,self.rad*2))
        self.pos = coord - (self.rad,self.rad)
        self.moveHitbox()

class MovingZone(Projectile):
    def __init__(self, position, image, target, speed, diameter, duration, gSpeed, growth=None):
        super().__init__(position, image, target, speed, gSpeed)
        self.image = pg.transform.scale(self.image, (diameter, diameter))
        self.imgName = image[0]
        self.rad = diameter/2
        self.duration = duration
        self.growth = growth
        self.moveHitbox()
    
    def grow(self, timer):
        self.growth[0] += timer
        if self.growth[0]>=self.growth[1]:
            self.rad += self.growth[2]
            self.image = pg.transform.scale(self.loadImage(self.imgName), (self.rad*2,self.rad*2))
            self.pos -= self.growth[2]
            self.moveHitbox()
            self.growth[0] = 0

class Line(NonPlayerObject):
    def __init__(self, position, image, target, size, thickness, gSpeed):
        super().__init__(position, image[0], gSpeed)
        self.target = target-self.pos
        self.image = pg.transform.scale(self.image, size)
        self.angle = np.arctan(self.target[0]/self.target[1]) * (180/m.pi)
        self.image = pg.transform.rotate(self.image, self.angle)
        self.thickness = thickness
        self.size = size

        x,y = self.target[0],self.target[1]
        if (x>0 and y<0) or (x<0 and y<0):
            self.angle += 180
        if x<0 and y>0:
            self.angle += 360
        
        if self.angle > 90 and self.angle <= 180:
            self.pos -= [0, np.cos((180-self.angle)*m.pi/180)*size[1]]
        if self.angle > 180 and self.angle <= 270:
            self.pos -= [np.sin((self.angle-180)*m.pi/180)*size[1], np.cos((180-self.angle)*m.pi/180)*size[1]]
        if self.angle > 270 and self.angle <= 360:
            self.pos -= [np.sin((self.angle-180)*m.pi/180)*size[1], 0]
        
        self.moveHitbox()

    def draw(self, screen, showImage, colour):
        if showImage:
            super().draw(screen)
        else:
            start, end = [], []
            if (self.angle > 0 and self.angle <= 90) or (self.angle > 180 and self.angle <= 270):
                start, end = self.hitbox[0], self.hitbox[1]
            if (self.angle > 90 and self.angle <= 180) or (self.angle > 270 and self.angle <= 360):
                start, end = self.hitbox[0]+[0,self.image.get_height()], self.hitbox[1]-[0,self.image.get_height()]
            pg.draw.line(screen, colour, start, end)

class ArcaneRay(Line):
    def __init__(self, position, image, target, size, thickness, duration, gSpeed):
        super().__init__(position, image, target, size, thickness, gSpeed)
        self.duration = duration
        self.hits = []
        self.target /= m.sqrt(self.target[0]**2 + self.target[1]**2)
        self.pos += self.target*30
        self.moveHitbox()
        
    def draw(self, screen):
        super().draw(screen, False, (200,0,200))

class Explosion(NonPlayerObject):
    def __init__(self, position, image, rad, dmg, gSpeed):
        super().__init__(position, image, gSpeed)
        self.rad = rad
        self.dmg = dmg

class Bombard(Projectile):
    def __init__(self, position, image, target, speed, gSpeed):
        self.tarPoint = Background(target, None, gSpeed)
        super().__init__(position, image, target, speed, gSpeed)
    
    def move(self, direction, pSpeed):
        super().move(direction, pSpeed)
        self.tarPoint.move(direction, pSpeed)
    
    def mouseMove(self, direction, pSpeed):
        super().mouseMove(direction, pSpeed)
        self.tarPoint.mouseMove(direction, pSpeed)
    
    def changeSpeed(self, speed):
        super().changeSpeed(speed)
        self.tarPoint.changeSpeed(speed)

class Satellite(Zone):
    def __init__(self, position, images, diameter, duration, speed, rad, orbitCen, gSpeed):
        super().__init__(position, images, diameter, duration, gSpeed)
        self.duration = np.inf
        self.angularSpeed = speed
        self.orbitRad = rad
        self.orbitAngle = 0
        self.orbitCen = orbitCen
    
    def mainMove(self):
        self.orbitAngle += self.angularSpeed*self.speed/np.pi
        reset = self.orbitAngle >= 360
        self.orbitAngle -= 360 if reset else 0
        self.hits = [] if reset else self.hits
        pos = np.array([0,0], dtype=np.float64) - [np.sin((self.orbitAngle)*m.pi/180), np.cos((self.orbitAngle)*m.pi/180)]
        pos *= self.orbitRad
        pos = self.orbitCen + pos
        self.pos = pos - (self.rad, self.rad)
        self.moveHitbox()

        

if __name__ == "__main__": pass