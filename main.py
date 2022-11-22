import pygame as pg
import random as rd
import math as m
import time
import os
import random as rd

from objects import Player 
from objects import Enemy
from objects import Background
from objects import Mana

#Constants
fpsLimit = 60
trueSpeed = 300
gameSpeed = trueSpeed/fpsLimit

#View screen box
xmax, ymax = 1160, 610
xmin, ymin = 0, 0

#Enemy render box
ex, ey = 800, 500
e_xmin, e_ymin = -ex, -ey
e_xmax, e_ymax = ex+xmax, ey+ymax

#Background render box
bx, by = 500, 300
bg_xmin, bg_ymin = -bx, -by
bg_xmax, bg_ymax = bx+xmax, by+ymax

#Field item spawn and render box
max_mana = 30 #To increase spawn rate, just increase max mana
frx, fry = 580, 305
fsx, fsy = 1160, 610
fr_xmin, fr_ymin = -frx, -fry
fr_xmax, fr_ymax = frx+xmax, fry+ymax
fs_xmin, fs_ymin = -fsx, -fsy
fs_xmax, fs_ymax = fsx+xmax, fsy+ymax
item_left, item_up = True, True

#Metrics for recording passage of time
timer = 0 #Frame counter
ticks = 0 #1/10th of a second

def checkMovement(direct, event):
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_RIGHT:
            direct.append("right")
        if event.key == pg.K_LEFT:
            direct.append("left")
        if event.key == pg.K_DOWN:
            direct.append("down")
        if event.key == pg.K_UP:
            direct.append("up")
    try:
        if event.type == pg.KEYUP:
            if event.key == pg.K_LEFT:
                direct.remove("left")
            if event.key == pg.K_RIGHT:
                direct.remove("right")
            if event.key == pg.K_UP:
                direct.remove("up")
            if event.key == pg.K_DOWN:
                direct.remove("down")
    except:
        pass
    return direct

def spawnEnemy(img, hp, dmg, sp):
    x1, y1 = rd.randint(e_xmin, xmin), rd.randint(e_ymin, ymin)
    x2, y2 = rd.randint(xmax, e_xmax), rd.randint(ymax, e_ymax)
    x = rd.randint(1,2)
    y = rd.randint(1,2)
    z = rd.choice([True, False])
    if z:
        x = x1 if x==1 else x2
        y = rd.randint(e_ymin, e_ymax)
    else:
        x = rd.randint(e_xmin, e_xmax)
        y = y1 if y==1 else y2
    return Enemy([x, y], img, hp, dmg, sp, gameSpeed)

def spawnMana():
    rarity = rd.randint(1,100)
    rarity = "small" if rarity < 91 else "medium" if rarity < 100 else "large"
    x1, y1 = rd.randint(fs_xmin, fr_xmin), rd.randint(fs_ymin, fr_ymin)
    x2, y2 = rd.randint(fr_xmax, fs_xmax), rd.randint(fr_ymax, fs_ymax)
    x = rd.randint(1,2)
    y = rd.randint(1,2)
    z = rd.choice([True, False])
    if z:
        x = x1 if x==1 else x2
        y = rd.randint(e_ymin, e_ymax)
    else:
        x = rd.randint(e_xmin, e_xmax)
        y = y1 if y==1 else y2
    return Mana([x, y], gameSpeed, rarity)

def boxCollision(obj1, obj2):
    X1 = obj1.hitbox[1][0] < obj2.hitbox[0][0]
    X2 = obj1.hitbox[0][0] > obj2.hitbox[1][0]
    Y1 = obj1.hitbox[1][1] < obj2.hitbox[0][1]
    Y2 = obj1.hitbox[0][1] > obj2.hitbox[1][1]
    col = not(X1 or X2) and not(Y1 or Y2)
    return col

def ballCollision(obj1, obj2):
    distance = m.sqrt(m.pow(obj1.center[0]-obj2.center[0],2)+m.pow(obj1.center[1]-obj2.center[1],2))
    return distance < obj1.rad

def main():
    pg.init()
    global gameSpeed, timer, ticks, max_mana

    screen = pg.display.set_mode((xmax, ymax))
    running = True
    playerImg = pg.image.load(os.path.join(os.path.dirname(__file__),"assets","player1.png"))
    pg.display.set_caption("Magic survival")
    pg.display.set_icon(playerImg)

    #Spawn player
    ph = playerImg.get_height()
    pw = playerImg.get_width()
    player = Player([(xmax-pw)/2, (ymax-ph)/2], ["player1.png"])
    
    #Spawn backgrounds
    background = []
    n = 50
    for x in range(n):
        bg = Background([rd.randint(bg_xmin, bg_xmax), rd.randint(bg_ymin, bg_ymax)], "grass.png", gameSpeed)
        background.append(bg)
    
    #Spawn enemies
    enemies = []
    n = 5
    for x in range(n): 
        enemies.append(spawnEnemy(["enemy.png"], 200, 10, 4.0))
    
    field_items = []
    n = 20
    for x in range(n):
        field_items.append(spawnMana())

    direct = []

    while running:
        start = time.time()
        screen.fill((0,150,0))

        #Events o(n) can't do anything about this one's time complexity tho
        for event in pg.event.get():
            #Quit
            if event.type == pg.QUIT:
                running = False
            
            direct = checkMovement(direct, event)
        
        #Background movement o(n)
        for i, bg in enumerate(background):
            background[i].move(direct)

            #Background respawns if out of range
            if background[i].pos[0] < bg_xmin:
                background[i].pos[0] = rd.randint(xmax, bg_xmax)
                background[i].pos[1] = rd.randint(bg_ymin, bg_ymax)
            if background[i].pos[0] > bg_xmax:
                background[i].pos[0] = rd.randint(bg_xmin, 0)
                background[i].pos[1] = rd.randint(bg_ymin, bg_ymax)
            if background[i].pos[1] < bg_ymin:
                background[i].pos[0] = rd.randint(bg_xmin, bg_xmax)
                background[i].pos[1] = rd.randint(ymax, bg_ymax)
            if background[i].pos[1] > bg_ymax:
                background[i].pos[0] = rd.randint(bg_xmin, bg_xmax)
                background[i].pos[1] = rd.randint(bg_ymin, 0)

            background[i].draw(screen)
        
        #Enemy movement o(n)
        for i, obj in enumerate(enemies):
            #Enemy movement
            enemies[i].mainMove([xmax/2, ymax/2])
            enemies[i].move(direct)

            #Enemy despawns if out of range
            oor = (enemies[i].pos[0]<e_xmin) or (enemies[i].pos[0]>e_xmax) or (enemies[i].pos[1]<e_ymin) or (enemies[i].pos[1]>e_ymax)
            if oor:
                del enemies[i]
        
        #Field item movement
        for i, mana in enumerate(field_items):
            field_items[i].move(direct)

            if field_items[i].pos[0] < fs_xmin:
                field_items[i].pos[0] = rd.randint(fr_xmax, fs_xmax)
                field_items[i].pos[1] = rd.randint(fs_ymin, fs_ymax)
            if field_items[i].pos[0] > fs_xmax:
                field_items[i].pos[0] = rd.randint(fs_xmin, fr_xmin)
                field_items[i].pos[1] = rd.randint(fs_ymin, fs_ymax)
            if field_items[i].pos[1] < fs_ymin:
                field_items[i].pos[0] = rd.randint(fs_xmin, fs_xmax)
                field_items[i].pos[1] = rd.randint(fr_ymax, fs_ymax)
            if field_items[i].pos[1] > fs_ymax:
                field_items[i].pos[0] = rd.randint(fs_xmin, fs_xmax)
                field_items[i].pos[1] = rd.randint(fs_ymin, fr_ymin)
            
            field_items[i].draw(screen)
        
        #Collision detection o(n^2) > o(n?) i.e sumtorial ~28-33% faster
        for i,enemy in enumerate(enemies):
            for j,other in enumerate(enemies):
                if(i>j) and ballCollision(enemy, other): #changed i!=j to i>j to reduce time complexity
                    dist = enemy.center - other.center
                    res = m.sqrt((dist[0]**2)+(dist[1]**2))
                    factor = enemy.rad*2/res             
                    move = dist*(factor-1)/10
                    enemies[i].pos += move
            enemies[i].draw(screen)


        #Tick rate Manager o(1) for now
        if timer % int(round(fpsLimit/10)) == 0 and timer != 0:
            ticks += 1
            if ticks%10 == 0:
                enemies.append(spawnEnemy(["enemy.png"], 200, 10, 4.0))
            mana_spawn = rd.randint(1, 5)
            if mana_spawn < 5 and len(field_items) < max_mana:
                field_items.append(spawnMana())

        player.draw(screen)

        pg.display.update()
        timer += 1

        #FPS Limiter
        while(time.time()-start < 1/fpsLimit):
            pass
        # loopTime = time.time()-start
        # gameSpeed = trueSpeed*loopTime*3
        # for i,obj in enumerate(enemies):
        #     enemies[i].changeSpeed(gameSpeed)
        # for i,obj in enumerate(background):
        #     for j,ob in enumerate(background):
        #         background[i].changeSpeed(gameSpeed)

main()
print(ticks)