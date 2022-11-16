import pygame as pg
import random as rd
import math as m
import time
import os
import random as rd

from characters import Player 
from characters import Enemy
from characters import Background

#Constants
fpsLimit = 60
trueSpeed = 300
gameSpeed = trueSpeed/fpsLimit

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

def main():
    pg.init()
    global gameSpeed

    xmax = 1160
    ymax = 610

    timer = 0
    ticks = 0

    screen = pg.display.set_mode((xmax, ymax))
    running = True
    pg.display.set_caption("Magic survival")

    player = Player([570, 288], ["player1.png"])
    #x=(-216, 1376) y=(-192.5, 802.5)
    background = []
    n = 50
    bx, by = 500, 300
    init_x, init_y = -bx, -by
    max_x, max_y = bx+xmax, by+ymax
    for x in range(n):
        bg = Background([rd.randint(init_x, max_x), rd.randint(init_y, max_y)], "grass.png", gameSpeed)
        background.append(bg)
    
    enemies = []
    n = 5
    for x in range(0, n):
        obj = Enemy([rd.randint(0, xmax), rd.randint(0, ymax)], ["player1.png"], 200, 10, .5, gameSpeed)
        enemies.append(obj)

    direct = []

    while running:
        start = time.time()
        screen.fill((120,120,120))

        for event in pg.event.get():
            #Quit
            if event.type == pg.QUIT:
                running = False
            
            direct = checkMovement(direct, event)
        
        for i, bgy in enumerate(background):
                background[i].move(direct)

                if background[i].pos[0] < init_x:
                    background[i].pos[0] = rd.randint(xmax, max_x)
                    background[i].pos[1] = rd.randint(init_y, max_y)
                if background[i].pos[0] > max_x:
                    background[i].pos[0] = rd.randint(init_x, 0)
                    background[i].pos[1] = rd.randint(init_y, max_y)
                if background[i].pos[1] < init_y:
                    background[i].pos[0] = rd.randint(init_x, max_x)
                    background[i].pos[1] = rd.randint(ymax, max_y)
                if background[i].pos[1] > max_y:
                    background[i].pos[0] = rd.randint(init_x, max_x)
                    background[i].pos[1] = rd.randint(init_y, 0)

                background[i].draw(screen)
        
        for i, obj in enumerate(enemies):
            enemies[i].move(direct)
            enemies[i].draw(screen)

        #Tick rate Manager
        if timer % int(round(fpsLimit/10)) == 0 and timer != 0:
            ticks += 1

        player.draw(screen)

        pg.display.update()

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
        timer += 1

main()