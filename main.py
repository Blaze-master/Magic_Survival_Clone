import pygame as pg
import random as rd
import math as m
import time
import os
import random as rd

from objects import Player 
from objects import Enemy
from objects import Background

#Constants
fpsLimit = 60
trueSpeed = 300
gameSpeed = trueSpeed/fpsLimit

timer = 0
ticks = 0

xmax, ymax = 1160, 610
xmin, ymin = 0, 0

ex, ey = 800, 500
e_xmin, e_ymin = -ex, -ey
e_xmax, e_ymax = ex+xmax, ey+ymax

bx, by = 500, 300
bg_xmin, bg_ymin = -bx, -by
bg_xmax, bg_ymax = bx+xmax, by+ymax

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
    x = x1 if x==1 else x2
    y = rd.randint(1,2)
    y = y1 if y==1 else y2
    return Enemy([x, y], img, hp, dmg, sp, gameSpeed)

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
    global gameSpeed, timer, ticks

    screen = pg.display.set_mode((xmax, ymax))
    running = True
    pg.display.set_caption("Magic survival")

    playerImg = pg.image.load(os.path.join(os.path.dirname(__file__),"assets","player1.png"))
    ph = playerImg.get_height()
    pw = playerImg.get_width()
    player = Player([(xmax-pw)/2, (ymax-ph)/2], ["player1.png"])
    
    background = []
    n = 50
    for x in range(n):
        bg = Background([rd.randint(bg_xmin, bg_xmax), rd.randint(bg_ymin, bg_ymax)], "grass.png", gameSpeed)
        background.append(bg)
    
    enemies = []
    n = 5
    for x in range(0, n):
        obj = Enemy([rd.randint(e_xmin, e_xmax), rd.randint(e_ymin, e_ymax)], ["enemy.png"], 200, 10, 4.0, gameSpeed)
        obj = spawnEnemy(["enemy.png"], 200, 10, 4.0)
        enemies.append(obj)

    direct = []

    while running:
        start = time.time()
        screen.fill((0,200,0))

        #Events o(n) can't do anything about this one's time complexity tho
        for event in pg.event.get():
            #Quit
            if event.type == pg.QUIT:
                running = False
            
            direct = checkMovement(direct, event)
        
        #Background movement o(n)
        for i, bgy in enumerate(background):
            background[i].move(direct)

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

            enemies[i].draw(screen)

            oor = (enemies[i].pos[0]<e_xmin) or (enemies[i].pos[0]>e_xmax) or (enemies[i].pos[1]<e_ymin) or (enemies[i].pos[1]>e_ymax)
            if oor:
                del enemies[i]
        
        #Collision detection o(n^2)
        for i,enemy in enumerate(enemies):
            for j,other in enumerate(enemies):
                if(i!=j) and ballCollision(enemy, other):
                    dist = enemy.center - other.center
                    res = m.sqrt((dist[0]**2)+(dist[1]**2))
                    factor = enemy.rad*2/res             
                    move = dist*(factor-1)/5
                    enemies[i].pos += move


        #Tick rate Manager o(1) for now
        if timer % int(round(fpsLimit/10)) == 0 and timer != 0:
            ticks += 1
            if ticks%10 == 0:
                obj = spawnEnemy(["enemy.png"], 200, 10, 4.0)
                enemies.append(obj)

        player.draw(screen)

        pg.display.update()
        timer += 1

        #FPS Manager
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