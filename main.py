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
    xmin = 0
    ymin = 0

    timer = 0
    ticks = 0

    screen = pg.display.set_mode((xmax, ymax))
    running = True
    pg.display.set_caption("Magic survival")

    playerImg = pg.image.load(os.path.join(os.path.dirname(__file__),"assets","player1.png"))
    ph = playerImg.get_height()
    pw = playerImg.get_width()
    player = Player([(xmax-pw)/2, (ymax-ph)/2], ["player1.png"])
    
    background = []
    n = 50
    bx, by = 500, 300
    bg_xmin, bg_ymin = -bx, -by
    bg_xmax, bg_ymax = bx+xmax, by+ymax
    for x in range(n):
        bg = Background([rd.randint(bg_xmin, bg_xmax), rd.randint(bg_ymin, bg_ymax)], "grass.png", gameSpeed)
        background.append(bg)
    
    enemies = []
    n = 5
    for x in range(0, n):
        obj = Enemy([rd.randint(0, xmax), rd.randint(0, ymax)], ["player1.png"], 200, 10, .5, gameSpeed)
        enemies.append(obj)

    direct = []

    while running:
        start = time.time()
        screen.fill((0,200,0))

        for event in pg.event.get():
            #Quit
            if event.type == pg.QUIT:
                running = False
            
            direct = checkMovement(direct, event)
        
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
        
        for i, obj in enumerate(enemies):
            enemies[i].move(direct)
            enemies[i].draw(screen)

        #Tick rate Manager
        if timer % int(round(fpsLimit/10)) == 0 and timer != 0:
            ticks += 1

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