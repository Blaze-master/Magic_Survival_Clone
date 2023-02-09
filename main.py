import pygame as pg
import random as rd
import math as m
import time
import os
import numpy as np
from pygame import mixer
import matplotlib.pyplot as plt

from objects import *
from gamedata import *
from magic import *
from functions import *
from artifacts import *
from enemies import *

#Metrics for recording passage of time
timer = 0 #Frame counter
ticks = 0 #1/10th of a second
graph = False

pg.init()

screen = pg.display.set_mode((xmax, ymax))
running = True

# mixer.music.load("Blizzard.mp3")
# mixer.music.play(-1)

keyMove = True
pause = False
lvlUp = False
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
n = 0 #5
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
healthBar = Bar((player.pos+np.array([-3, 50])), "health_bar.png", 30, 4)
healthBar.setLength(player.hp, 100)

magic_bullets = []
lavazones = []
electricZone = Zone(
    (player.center-[magic["electric_zone"]["size"]/2, magic["electric_zone"]["size"]/2]),
    ["electric_zone.png"],
    magic["electric_zone"]["dmg"],
    magic["electric_zone"]["size"],
    np.inf,
    gameSpeed
    )

arcane_rays = []

direct = []
if graph: fps = [[],[]]
options = []
optionScroll = 0

while running:
    start = time.time()
    if not lvlUp: screen.fill((0,100,0)) #0,150,0

    #Events o(n) can't do anything about this one's time complexity tho
    events = []
    while pg.event.peek():
        events.append(pg.event.poll())
    for event in events:
        #Quit
        if event.type == pg.QUIT:
            running = False
        if not lvlUp:
            if not pause:
                if keyMove:
                    direct = checkMovement(direct, event)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouseMove = not mouseMove
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    pause = not pause
    
    if pause or lvlUp:
        direct = []

    if not (pause or lvlUp):
        if not keyMove:
            mousePos = np.array(pg.mouse.get_pos(), dtype="float64")
            mousePos -= player.center
            magn = magnitude(mousePos)
            magn = magn if magn != 0 else 1
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
        
        #Mana item movement o(n)
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
            
            if inRange(player.pickupRad, player.center, mana_items[i].center):
                mana_items[i].attract(player.center)

            if boxCollision(player, mana_items[i]):
                player.mana["amt"] += manaObj.mana
                total_mana += manaObj.mana
                manaBar.setLength(player.mana["amt"], player.mana["cap"])
                del mana_items[i]
                continue

            mana_items[i].draw(screen)
        
        #Chest item movement o(n)
        for i,chest in enumerate(chests):
            if keyMove: chests[i].move(direct, playerSpeed)
            if mouseMove: chests[i].mouseMove(mouseDir, playerSpeed)

            #Chest despawns if out of range
            if boxCollision(player, chests[i]):
                player.artifacts += 1
                del chests[i]
                continue
            elif not inBox(chests[i].center, [[fs_xmin, fs_ymin],[fs_xmax, fs_ymax]]):
                del chests[i]
                continue

            chests[i].draw(screen)
        
        #Enemy movement o(n)
        for i, obj in enumerate(enemies):
            #Enemy movement
            if keyMove: enemies[i].move(direct, playerSpeed)
            if mouseMove: enemies[i].mouseMove(mouseDir, playerSpeed)
            if obj.type!= "sprinter": 
                enemies[i].mainMove(player.center) # np.array(pg.mouse.get_pos())
            else: 
                enemies[i].mainMove()
                if inBox(enemies[i].target, enemies[i].hitbox):
                    del enemies[i]
                    continue

            #Enemy despawns if out of range
            if not inBox(enemies[i].center, [[e_xmin, e_ymin],[e_xmax, e_ymax]]):
                del enemies[i]
                continue

        #Magic bullet movement & damage o(n^2)
        for i,bullet in enumerate(magic_bullets):
            if keyMove: magic_bullets[i].move(direct, playerSpeed)
            if mouseMove: magic_bullets[i].mouseMove(mouseDir, playerSpeed)
            magic_bullets[i].mainMove()
            magic_bullets[i].draw(screen)
            
            #magic_bullet despawns if out of range
            if not inBox(magic_bullets[i].center, [[e_xmin, e_ymin],[e_xmax, e_ymax]]):
                del magic_bullets[i]
                continue

            #Enemy hit
            for j,enemy in enumerate(enemies):
                if boxCollision(magic_bullets[i], enemy):
                    enemies[j].hp -= (bullet.dmg*magic["magic_bullet"]["multiplier"]["dmg"])
                    del magic_bullets[i]
                    break
        
        #Lavazone movement & damage o(n^2)
        if  magic["lavazone"]["level"] > 0:
            magic["lavazone"]["interval"][0] += gameSpeed*magic["lavazone"]["multiplier"]["interval"]/trueSpeed
            for i,lavazone in enumerate(lavazones):
                if keyMove: lavazones[i].move(direct, playerSpeed)
                if mouseMove: lavazones[i].mouseMove(mouseDir, playerSpeed)
                lavazones[i].draw(screen)

                lavazones[i].duration -= gameSpeed/trueSpeed
                if lavazone.duration <= 0:
                    del lavazones[i]
                    continue

                if magic["lavazone"]["interval"][0] >= magic["lavazone"]["interval"][1]:
                    for j,enemy in enumerate(enemies):
                        if ballCollision(lavazones[i], enemy):
                            enemies[j].hp -= (lavazone.dmg*magic["lavazone"]["multiplier"]["dmg"])
                    magic["lavazone"]["interval"][0] = 0
        
        #Electric zone damage
        if magic["electric_zone"]["level"] > 0:
            magic["electric_zone"]["interval"][0] += gameSpeed*magic["electric_zone"]["multiplier"]["interval"]/trueSpeed
            if magic["electric_zone"]["interval"][0] >= magic["electric_zone"]["interval"][1]:
                for i,enemy in enumerate(enemies):
                    if ballCollision(electricZone, enemy):
                        enemies[i].hp -= (electricZone.dmg*magic["electric_zone"]["multiplier"]["dmg"])
                magic["electric_zone"]["interval"][0] = 0
            electricZone.draw(screen)
        
        #Arcane ray damage
        if magic["arcane_ray"]["level"] > 0:
            for i,ray in enumerate(arcane_rays):
                arcane_rays[i].draw(screen)

                arcane_rays[i].duration -= gameSpeed/trueSpeed
                if arcane_rays[i].duration <= 0:
                    del arcane_rays[i]
                    continue

                for j,enemy in enumerate(enemies):
                    if boxCollision(enemy, arcane_rays[i]):
                        if lineCollision(enemy, ray) and (not id(enemy) in ray.hits):
                            arcane_rays[i].hits.append(id(enemy))
                            enemies[j].hp -= ray.dmg*magic["arcane_ray"]["multiplier"]["dmg"]

        #Enemy Death
        for j,enemy in enumerate(enemies):
            if enemies[j].hp <= 0:
                player.mana["amt"] += enemies[j].mana
                manaBar.setLength(player.mana["amt"], player.mana["cap"])
                enemies.remove(enemy)
                score += 1
        
        #Enemy Collision detection o(n^2) --> o(n?) i.e sumtorial ~28-33% faster
        for i,enemy in enumerate(enemies):
            for j,other in enumerate(enemies):
                if(enemy.type=="sprinter" or other.type=="sprinter"): continue
                if(i>j) and ballCollision(enemy, other): #changed i!=j to i>j to cut execution time in half
                    dist = enemy.center - other.center
                    res = magnitude(dist)
                    factor = enemy.rad*2/res             
                    move = dist*(factor-1)/2 #10
                    enemies[i].pos += move
            enemies[i].draw(screen)


        #Tick rate Manager
        tmp = int(round((trueSpeed/gameSpeed)/10))
        tmp = tmp if tmp>0 else 1
        if timer % tmp == 0 and timer != 0:
            ticks += 1

            if graph:
                fps[0].append(ticks/10)
                fps[1].append(trueSpeed/gameSpeed)

            #Enemy spawn
            if ticks%2 == 0:
                n = 2
                for _ in range(n):
                    enemies.append(spawnObj("enemy", [["enemy.png"], enemyHp, enemyDmg, enemySpeed]))
                enemies.append(spawnObj("sprinter", [["enemy.png"], enemyHp, enemyDmg, sprinterSpeed]))

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
                        healthBar.setLength(player.hp, 100)
                        plyrDmgCd = ticks + 5
                        if player.hp <= 0:
                            running = False
                        break

        #Attack cooldowns
        #Magic Bullet spawn
        magic["magic_bullet"]["cd"][0] += gameSpeed*magic["magic_bullet"]["multiplier"]["cd"]/trueSpeed
        if magic["magic_bullet"]["cd"][0] >= magic["magic_bullet"]["cd"][1]:
            #Magic bullet spawn o(n)
            if len(enemies)>0:
                closest = []
                for enemy in enemies:
                    dist = enemy.center-player.center
                    dist = magnitude(dist)
                    closest.append(dist)
                closest = np.array([closest]).argmin()
                magic_bullets.append(spawnObj("magic_bullet", [
                    player.center,
                    "bullet.png",
                    enemies[closest].center,
                    magic["magic_bullet"]["speed"]*magic["magic_bullet"]["multiplier"]["speed"],
                    magic["magic_bullet"]["dmg"]
                    ])
                )
            magic["magic_bullet"]["cd"][0] = 0

        #Lavazone spawn
        magic["lavazone"]["cd"][0] += gameSpeed*magic["lavazone"]["multiplier"]["cd"]/trueSpeed
        if magic["lavazone"]["cd"][0] >= magic["lavazone"]["cd"][1] and magic["lavazone"]["level"] > 0:
            pos = (np.random.rand(2) * [xmax, ymax]) - magic["lavazone"]["size"]*magic["lavazone"]["multiplier"]["size"]
            lavazones.append(spawnObj("lavazone", [
                pos,
                ["lava_zone.png"],
                magic["lavazone"]["dmg"],
                magic["lavazone"]["size"]*magic["lavazone"]["multiplier"]["size"],
                magic["lavazone"]["duration"]*magic["lavazone"]["multiplier"]["duration"]
                ]))
            magic["lavazone"]["cd"][0] = 0

        #Arcane ray spawn
        magic["arcane_ray"]["cd"][0] += gameSpeed*magic["arcane_ray"]["multiplier"]["cd"]/trueSpeed
        if magic["arcane_ray"]["cd"][0] >= magic["lavazone"]["cd"][1] and magic["arcane_ray"]["level"] > 0 and len(enemies) > 0:
            copy = enemies
            for n in range(round(magic["arcane_ray"]["num"]*magic["arcane_ray"]["multiplier"]["num"])):
                if len(copy)<1: break
                closest = getClosest(copy, player.center)
                arcane_rays.append(spawnObj("arcane_ray", [
                    player.center,
                    "arcane_ray.png",
                    copy[closest].center,
                    magic["arcane_ray"]["size"],
                    1,
                    magic["arcane_ray"]["dmg"],
                    magic["arcane_ray"]["duration"]*magic["arcane_ray"]["multiplier"]["duration"],
                ]))
                copy.pop(closest)
            magic["arcane_ray"]["cd"][0] = 0
            

        #Mana level up
        if player.mana["amt"] >= player.mana["cap"]:
            player.mana["amt"] -= player.mana["cap"]
            player.mana["lvl"] += 1
            player.mana["cap"] += 50

            avail = False
            for n in range(3):
                if len(availableMagic)>0:
                    avail = True
                    mg = rd.choice(availableMagic)
                    availableMagic.remove(mg)
                    mgt = mg.replace("_"," ").capitalize()
                    upgrade = Text(
                        fontType,
                        fontSize,
                        mgt+" lvl "+str(magic[mg]["level"]+1),
                        (255,255,255),
                        [textX, textY+(n*(textHeight+textMargin))],
                        mg
                        )
                    options.append(upgrade)
            if avail: options[optionScroll].highlight()            
            lvlUp = avail

            manaBar.setLength(player.mana["amt"], player.mana["cap"])
        
        player.draw(screen)
        manaBar.draw(screen)
        healthBar.draw(screen)

        pg.display.update()
        pg.display.flip()
        timer += 1

        #FPS Limiter
        while(time.time()-start < 1/fpsLimit):
            pass
        loopTime = time.time()-start
        loopTime = loopTime if loopTime >= 1/fpsLimit else 1/fpsLimit
        gameSpeed = trueSpeed*loopTime
        # o(n) operations
        for i,obj in enumerate(enemies):
            enemies[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(background):
            background[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(mana_items):
            mana_items[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(chests):
            chests[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(magic_bullets):
            magic_bullets[i].changeSpeed(gameSpeed)
        for i,obj in enumerate(lavazones):
            lavazones[i].changeSpeed(gameSpeed)
    
    elif lvlUp:
        mousePos = mousePos = np.array(pg.mouse.get_pos())
        for i,upgrade in enumerate(options):
            if inBox(mousePos, upgrade.box) and not upgrade.highlighted:
                options[i].highlight()
                optionScroll = i
            if upgrade.highlighted and not inBox(mousePos, upgrade.box):
                options[i].highlight()
            options[i].draw(screen)
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                for i,upgrade in enumerate(options):
                    if upgrade.highlighted:
                        mag = magic[upgrade.magic]
                        up = mag["upgrades"][mag["level"]-1]
                        if mag["level"]>0:
                            magic[upgrade.magic]["multiplier"][up[0]] += up[1]
                        magic[upgrade.magic]["level"] += 1
                        lvlUp = False 

                        if upgrade.magic=="electric_zone" and up[0]=="size":
                            size = magic["electric_zone"]["size"] * magic["electric_zone"]["multiplier"]["size"]
                            electricZone = Zone(
                                (player.center-[size/2, size/2]),
                                ["electric_zone.png"],
                                magic["electric_zone"]["dmg"],
                                size,
                                np.inf,
                                gameSpeed
                                )
        pg.display.update()
        if not lvlUp:
            options = []
            optionScroll = 0
            availableMagic = [x if magic[x]["level"] < magic[x]["max"] else None for x in magic.keys()]
            while None in availableMagic:
                availableMagic.remove(None)

print("Mana level :", player.mana["lvl"])
print("Total mana collected:", total_mana)
print("Artifacts collected :", player.artifacts)
print("Enemies killed :", score)
print("Player health :", player.hp)
print("Time :", ticks/10, "secs")

if graph:
    plt.plot(fps[0], fps[1])
    plt.show()