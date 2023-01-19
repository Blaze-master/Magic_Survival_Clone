import pygame as pg
import random as rd
import math as m
import time
import os
import random as rd
import numpy as np
from pygame import mixer

from objects import *
from gamedata import *
from magic import *
from functions import *
from artifacts import *
from enemies import *

#Metrics for recording passage of time
timer = 0 #Frame counter
ticks = 0 #1/10th of a second

pg.init()

screen = pg.display.set_mode((xmax, ymax))
running = True

# mixer.music.load("Blizzard.mp3")
# mixer.music.play(-1)

keyMove = True
pause = False
mouseMove = not keyMove

playerImg = pg.image.load(os.path.join(os.path.dirname(__file__),"assets","player1.png"))
pg.display.set_caption("Magic survival")
pg.display.set_icon(playerImg)

#Spawn player
ph = playerImg.get_height()
pw = playerImg.get_width()
player = Player([(xmax-pw)/2, (ymax-ph)/2], ["player1.png"])
plyrDmgCd = 0

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
    enemies.append(spawnObj("enemy", [["enemy.png"], enemyHp, enemyDmg, enemySpeed]))#Health, damage, speed

mana_items = []
n = max_mana
for x in range(n):
    mana_items.append(spawnObj("mana item", [attractSpeed]))

chests = []
n = 1
for x in range(n):
    chests.append(spawnObj("chest"))

manaBar = Bar([0,0], "mana_bar.png", xmax, 10)

projectiles = []

direct = []

while running:
    start = time.time()
    screen.fill((0,150,0))

    #Events o(n) can't do anything about this one's time complexity tho
    for event in pg.event.get():
        #Quit
        if event.type == pg.QUIT:
            running = False
        if keyMove:
            direct = checkMovement(direct, event)
        elif not pause:
            if event.type == pg.MOUSEBUTTONDOWN:
                mouseMove = not mouseMove
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                pause = not pause

    if not pause:
        if not keyMove:
            mousePos = np.array(pg.mouse.get_pos(), dtype="float64")
            mousePos -= player.center
            sqrSum = mousePos[0]**2 + mousePos[1]**2
            sqrSum = sqrSum if sqrSum != 0 else 1
            magn = sqrSum**0.5
            mouseDir = mousePos/magn

        
        #Background movement o(n)
        for i, bg in enumerate(background):
            if keyMove: background[i].move(direct, playerSpeed) 
            if mouseMove: background[i].mouseMove(mouseDir, playerSpeed)

            #Background respawns if out of range
            background[i].respawn(
                [bg_xmin, bg_xmax, bg_ymin, bg_ymax],
                [xmin, xmax, ymin, ymax]
                )

            background[i].draw(screen)
        
        #Enemy movement o(n)
        for i, obj in enumerate(enemies):
            #Enemy movement
            if keyMove: enemies[i].move(direct, playerSpeed)
            if mouseMove: enemies[i].mouseMove(mouseDir, playerSpeed)
            enemies[i].mainMove(player.center)

            #Enemy despawns if out of range
            if not inBox(enemies[i].center, [[e_xmin, e_ymin],[e_xmax, e_ymax]]):
                del enemies[i]
                continue
        
        #Mana item movement
        for i, manaObj in enumerate(mana_items):
            if keyMove: mana_items[i].move(direct, playerSpeed)
            if mouseMove: mana_items[i].mouseMove(mouseDir, playerSpeed)
            
            #If oor, respawn and change rarity
            if not inBox(mana_items[i].center, [[fs_xmin, fs_ymin],[fs_xmax, fs_ymax]]):
                mana_items[i].changeRarity
                mana_items[i].respawn(
                    [fs_xmin, fs_xmax, fs_ymin, fs_ymax],
                    [fr_xmin, fr_xmax, fr_ymin, fr_ymax]
                    )
            
            dist = m.sqrt(m.pow(player.center[0]-mana_items[i].center[0],2)+m.pow(player.center[1]-mana_items[i].center[1],2))
            if dist < player.pickupRad:
                mana_items[i].attract(player.center)
            
            mana_items[i].draw(screen)

            if boxCollision(player, mana_items[i]):
                player.mana["amt"] += manaObj.mana
                manaBar.setLength(player.mana["amt"], player.mana["cap"])
                del mana_items[i]
        
        #Chest item movement
        for i,chest in enumerate(chests):
            if keyMove: chests[i].move(direct, playerSpeed)
            if mouseMove: chests[i].mouseMove(mouseDir, playerSpeed)
            
            chests[i].draw(screen)

            #Chest despawns if out of range
            if boxCollision(player, chests[i]):
                player.artifacts += 1
                del chests[i]
            elif not inBox(chests[i].center, [[fs_xmin, fs_ymin],[fs_xmax, fs_ymax]]):
                del chests[i]
        
        #Projectile movement
        for i,bullet in enumerate(projectiles):
            if keyMove: projectiles[i].move(direct, playerSpeed)
            if mouseMove: projectiles[i].mouseMove(mouseDir, playerSpeed)
            projectiles[i].mainMove()
            projectiles[i].draw(screen)
            
            #Projectile despawns if out of range
            if not inBox(projectiles[i].center, [[e_xmin, e_ymin],[e_xmax, e_ymax]]):
                del projectiles[i]
                continue

            #Enemy hit
            for j,enemy in enumerate(enemies):
                if boxCollision(projectiles[i], enemy):
                    enemies[j].hp -= bullet.dmg
                    del projectiles[i]
                    if enemies[j].hp <= 0:
                        player.mana["amt"] += enemies[j].mana
                        manaBar.setLength(player.mana["amt"], player.mana["cap"])
                        del enemies[j]
                        score += 1
                    break
            
        
        #Enemy Collision detection o(n^2) > o(n?) i.e sumtorial ~28-33% faster
        for i,enemy in enumerate(enemies):
            for j,other in enumerate(enemies):
                if(i>j) and ballCollision(enemy, other): #changed i!=j to i>j to cut execution time in half
                    dist = enemy.center - other.center
                    res = m.sqrt((dist[0]**2)+(dist[1]**2))
                    factor = enemy.rad*2/res             
                    move = dist*(factor-1)/10 #10
                    enemies[i].pos += move
            enemies[i].draw(screen)


        #Tick rate Manager
        tmp = int(round((trueSpeed/gameSpeed)/10))
        tmp = tmp if tmp>0 else 1
        if timer % tmp == 0 and timer != 0:
            ticks += 1

            #Enemy spawn
            if ticks%2 == 0:
                enemies.append(spawnObj("enemy", [["enemy.png"], enemyHp, enemyDmg, enemySpeed]))

            #Mana spawn
            mana_spawn = rd.randint(1, 5)
            if mana_spawn == 5 and len(mana_items) < max_mana:
                mana_items.append(spawnObj("mana item", [attractSpeed]))

            #Chest spawn
            chest_spawn = rd.randint(1, 10)
            if chest_spawn == 10 and len(chests) < max_chests:
                chests.append(spawnObj("chest"))
            
            #Player damage (takes damage only every 5 ticks)
            if plyrDmgCd<ticks:
                for enemy in enemies:
                    if ballCollision(player, enemy):
                        player.hp -= enemy.dmg
                        plyrDmgCd = ticks + 5
                        if player.hp <= 0:
                            running = False
                        break

        #Attack cooldowns
        projTimer[0] += gameSpeed/trueSpeed
        if projTimer[0] >= projTimer[1]:
            #Projectile spawn o(n)
            if len(enemies)>0:
                closest = []
                for enemy in enemies:
                    dist = enemy.center-player.center
                    dist = m.sqrt(dist[0]**2 + dist[1]**2)
                    closest.append(dist)
                closest = np.array([closest]).argmin()
                projectiles.append(spawnObj(
                    "projectile", [player.center, "bullet.png", enemies[closest].center, projSpeed, projDmg])#Speed, damage
                )
            projTimer[0] = 0

        #Mana level up
        if player.mana["amt"] >= player.mana["cap"]:
            player.mana["amt"] -= player.mana["cap"]
            player.mana["lvl"] += 1
            player.mana["cap"] += 50

            if len(projUpgrades) > 0:
                upgrade = projUpgrades.pop(0)
                projDmgMultiplier += upgrade[0]
                projCdMultiplier += upgrade[1]                
                projDmg = projBaseDmg * projDmgMultiplier
                projTimer[1] = projBaseCd*projCdMultiplier

            manaBar.setLength(player.mana["amt"], player.mana["cap"])
        
        player.draw(screen)
        manaBar.draw(screen)

        pg.display.update()
        timer += 1

        #FPS Limiter
        while(time.time()-start < 1/fpsLimit):
            pass
        loopTime = time.time()-start
        loopTime = loopTime if loopTime >= 1/fpsLimit else 1/fpsLimit
        gameSpeed = trueSpeed*loopTime
        for i,obj in enumerate(enemies):
            enemies[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(background):
            background[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(mana_items):
            mana_items[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(chests):
            chests[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(projectiles):
            projectiles[i].changeSpeed(gameSpeed)

print("Mana level :", player.mana["lvl"])
print("Artifacts collected :", player.artifacts)
print("Enemies killed :", score)
print("Player health :", player.hp)
print("Projectile damage :", projDmg)
print("Projectile cooldown :", projTimer[1])
print("Time :", ticks/10, "secs")