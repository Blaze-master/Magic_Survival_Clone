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

#Testing variables
graph = False #Enable to record fps
fuckIt = False #Ignore this
immortal = False #Infinite health
keyMove = True #Keyboard/mouse movement

pg.init()

screen = pg.display.set_mode((xmax, ymax))
running = True

# mixer.music.load("Blizzard.mp3")
# mixer.music.play(-1)

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
n = 50 #50
for x in range(n):
    bg = Background([rd.randint(bg_xmin, bg_xmax), rd.randint(bg_ymin, bg_ymax)], "grass.png", gameSpeed)
    background.append(bg)
    
#Spawn enemies
enemies = []
# n = 0 #5
# for x in range(n): 
#     enemies.append(spawnObj("enemy", [["enemy.png"], enemyHp, enemyDmg, enemySpeed]))#Health, damage, speed

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
playerAngle = 0.01

#Attacks
attacks = {x : [] for x in magic.keys()} #All attacks integrated into one dictionary
explosions = []
attacks["electric_zone"].append(Zone(
    (player.center-[magic["electric_zone"]["size"]/2, magic["electric_zone"]["size"]/2]),
    ["electric_zone.png"],
    magic["electric_zone"]["size"],
    np.inf,
    gameSpeed
    ))

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
        if keyMove:
            if direct != []:
                mDic = {
                    "left" : [0, 90],
                    "right" : [0, -90],
                    "up" : [1, 1],
                    "down" : [1, -1],
                }
                a = [0,0]
                for mv in direct:
                    mv = mDic[mv]
                    a[mv[0]] -= mv[1]
                if a[0]!=0 and a[1]!=0: #if all values are non zero
                    v = a[0]*a[1]/2
                else:
                    v = a[0]+a[1]
                playerAngle = v if abs(v)>0 else 0.01
                if a[1]>=0:
                    playerAngle += 180
                elif a[0]>0:
                    playerAngle += 360
        else:
            mousePos = np.array(pg.mouse.get_pos(), dtype="float64")
            mouseVec = mousePos - player.center
            magn = magnitude(mouseVec)
            magn = magn if magn != 0 else 1
            mouseDir = mouseVec/magn
            playerAngle = getAngle(mouseDir)
            if mouseDir[1]>0:
                playerAngle += 180
            elif mouseDir[0]>0:
                playerAngle += 360

        #Object movements
        #Background movement o(n)
        for i, bg in enumerate(background):
            if keyMove: background[i].move(direct, playerSpeed) 
            if mouseMove: background[i].mouseMove(mouseDir, playerSpeed)

            #Background respawns if out of range
            background[i].respawn(
                [bg_xmin, bg_xmax, bg_ymin, bg_ymax],
                [xmin, xmax, ymin, ymax]
            )
            # print(background[i].hitbox, screenBox)
            if boxCollision(background[i].hitbox, screenBox) or fuckIt:
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

            if boxCollision(player.hitbox, mana_items[i].hitbox):
                player.mana["amt"] += manaObj.mana
                total_mana += manaObj.mana
                manaBar.setLength(player.mana["amt"], player.mana["cap"])
                del mana_items[i]
                continue
            if boxCollision(mana_items[i].hitbox, screenBox) or fuckIt:
                mana_items[i].draw(screen)
        
        #Chest item movement o(n)
        for i,chest in enumerate(chests):
            if keyMove: chests[i].move(direct, playerSpeed)
            if mouseMove: chests[i].mouseMove(mouseDir, playerSpeed)

            #Chest despawns if out of range
            if boxCollision(player.hitbox, chests[i].hitbox):
                player.artifacts += 1
                del chests[i]
                continue
            elif not inBox(chests[i].center, [[fs_xmin, fs_ymin],[fs_xmax, fs_ymax]]):
                del chests[i]
                continue
            if boxCollision(chests[i].hitbox, screenBox):
                chests[i].draw(screen)
        
        #Enemy movement o(n)
        for i, obj in enumerate(enemies):
            #Enemy movement
            if keyMove: enemies[i].move(direct, playerSpeed)
            if mouseMove: enemies[i].mouseMove(mouseDir, playerSpeed)
            if obj.type=="sprinter": 
                enemies[i].mainMove()
                if inBox(enemies[i].target, enemies[i].hitbox):
                    del enemies[i]
                    continue
            else: 
                enemies[i].mainMove(player.center) # np.array(pg.mouse.get_pos())

            #Enemy despawns if out of range
            if not inBox(enemies[i].center, [[e_xmin, e_ymin],[e_xmax, e_ymax]]):
                del enemies[i]
                continue
        
        #Execute movement and damage for all attacks
        for mag in attacks.keys():
            if magic[mag]["level"]>0:
                for i,att in enumerate(attacks[mag]):
                    det = magic[mag]["deets"]
                    dead = False

                    #Movement and despawn
                    if not "static" in det:
                        if keyMove: attacks[mag][i].move(direct, playerSpeed)
                        if mouseMove: attacks[mag][i].mouseMove(mouseDir, playerSpeed)
                    if "main_move" in det:
                        attacks[mag][i].mainMove()
                    if "despawn" in det:
                        if not inBox(attacks[mag][i].center, [[e_xmin, e_ymin],[e_xmax, e_ymax]]):
                            dead = True
                    if "expand" in det:
                        attacks[mag][i].grow(gameSpeed/trueSpeed)
                    if mag == "energy_bullet":
                        attacks[mag][i].moveSpeed -= 0.05
                        attacks[mag][i].moveSpeed = 0 if att.moveSpeed<=0 else att.moveSpeed

                    #Timers
                    interval = "int" in magic[mag].keys()
                    duration = "dur" in magic[mag].keys()
                    int_over = False
                    if interval:
                        magic[mag]["int"][0] += gameSpeed*magic[mag]["mul"]["int"]/trueSpeed
                        if magic[mag]["int"][0]>=magic[mag]["int"][1]:
                            int_over = True
                            magic[mag]["int"][0] = 0
                            attacks[mag][i].hits = []
                    if duration:
                        attacks[mag][i].duration -= gameSpeed/trueSpeed
                        dead = attacks[mag][i].duration<=0
                    
                    #Damage
                    pen = "pen" in magic[mag].keys()
                    hit = False
                    for j,enemy in enumerate(enemies):
                        if (not id(enemy) in attacks[mag][i].hits) and (not interval or (interval and int_over)):
                            if "box_col" in det:
                                if boxCollision(attacks[mag][i].hitbox, enemy.hitbox):
                                    enemies[j].hp -= (magic[mag]["dmg"]*magic[mag]["mul"]["dmg"])
                                    hit = True
                                    attacks[mag][i].hits.append(id(enemy))
                            if "ball_col" in det:
                                if ballCollision(attacks[mag][i], enemy):
                                    enemies[j].hp -= (magic[mag]["dmg"]*magic[mag]["mul"]["dmg"])
                                    hit = True
                                    attacks[mag][i].hits.append(id(enemy))
                            if "line_col" in det:
                                if (boxCollision(enemy.hitbox, attacks[mag][i].hitbox) or inBox(distToLine(enemies[j].center, attacks[mag][i].center, att.angle), attacks[mag][i].hitbox)):
                                    if lineCollision(enemy, attacks[mag][i]):
                                        enemies[j].hp -= (magic[mag]["dmg"]*magic[mag]["mul"]["dmg"])
                                        attacks[mag][i].hits.append(id(enemy))
                                        hit = True
                            if pen and len(attacks[mag][i].hits)>=magic[mag]["pen"]+magic[mag]["mul"]["pen"]: 
                                dead = True
                                break
                            
                    if "bombard" in det:
                        if inBox(attacks[mag][i].tarPoint.pos, attacks[mag][i].hitbox):
                            hit = True
                            dead = True
                            attacks[mag][i].center = attacks[mag][i].tarPoint.pos
                    
                    if "explode" in det and hit:
                        explosions.append(spawnObj(
                            "explosion",
                            [
                                attacks[mag][i].center,
                                None,
                                magic[mag]["rad"]*magic[mag]["mul"]["rad"],
                                magic[mag]["dmg"]*magic[mag]["mul"]["dmg"],
                            ]))
                    
                    if dead:
                        del attacks[mag][i]

        #Explosions
        for i,exp in enumerate(explosions):
            for j,enemy in enumerate(enemies):
                if ballCollision(exp, enemy):
                    enemies[j].hp -= exp.dmg
            explosions.remove(exp)

        #Enemy Death
        for j,enemy in enumerate(enemies):
            if enemies[j].hp <= 0:
                player.mana["amt"] += enemies[j].mana
                manaBar.setLength(player.mana["amt"], player.mana["cap"])
                enemies.remove(enemy)
                score += 1
        
        #Draw attacks below enemies
        for mag in attacks.keys():
            if magic[mag]["level"]>0 and ("below" in magic[mag]["deets"]):
                for att in attacks[mag]:
                    if boxCollision(att.hitbox, screenBox) or fuckIt:
                        att.draw(screen)
        
        #Enemy Collision detection o(n^2) --> o(n?) i.e sumtorial ~28-33% faster
        for i,enemy in enumerate(enemies):
            for j,other in enumerate(enemies):
                if(enemy.type=="sprinter" or other.type=="sprinter"): continue
                if(i>j) and ballCollision(enemy, other): #changed i!=j to i>j to cut execution time in half
                    dist = enemy.center - other.center
                    res = magnitude(dist)
                    factor = (enemy.rad+other.rad)/res             
                    move = dist*(factor-1)/2 #10
                    enemies[i].pos += move
            if boxCollision(enemies[i].hitbox, screenBox) or fuckIt:
                enemies[i].draw(screen)

        #Draw attacks above enemies
        for mag in attacks.keys():
            if magic[mag]["level"]>0 and not ("below" in magic[mag]["deets"]):
                for att in attacks[mag]:
                    if boxCollision(att.hitbox, screenBox) or fuckIt:
                        att.draw(screen)


        #Event ticks
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
                n = 1
                for _ in range(n):
                    enemies.append(spawnObj("enemy", [["enemy.png"], enemyHp, enemyDmg, enemySpeed]))
                # enemies.append(spawnObj("sprinter", [["enemy.png"], enemyHp, enemyDmg, sprinterSpeed]))

            #Mana spawn
            mana_spawn = rd.randint(1, 5)
            if mana_spawn == 5 and len(mana_items) < max_mana:
                mana_items.append(spawnObj("mana item", [attractSpeed]))

            #Chest spawn
            if ticks%1 == 0:
                chest_spawn = rd.randint(1, 100)
                if chest_spawn == 1 and len(chests) < max_chests:
                    chests.append(spawnObj("chest"))
            
            #Player damage (takes damage only every 5 ticks)
            if plyrDmgCd<ticks:
                for enemy in enemies:
                    if ballCollision(player, enemy) and not immortal:
                        player.hp -= enemy.dmg
                        healthBar.setLength(player.hp, 100)
                        plyrDmgCd = ticks + 5
                        if player.hp <= 0:
                            running = False
                        break

        #Attack cooldowns
        # for mag in attacks.keys():
        #     if magic[mag]["level"]>0:
        #         #Cooldown count
        #         strike = False
        #         if "cd" in magic[mag].keys():
        #             magic[mag]["cd"][0] += gameSpeed*magic[mag]["mul"]["cd"]/trueSpeed
        #             if magic[mag]["cd"][0]>=magic[mag]["cd"][1]:
        #                 strike = True
        #                 magic[mag]["cd"][0] = 0
        #         if strike:
        #             if "rd_spawn" in magic[mag]["deets"]:
        #             else:
        #                 if len(enemies)>0
        #             attacks[mag].append(object)


        #Magic Bullet spawn
        magic["magic_bullet"]["cd"][0] += gameSpeed*magic["magic_bullet"]["mul"]["cd"]/trueSpeed
        if magic["magic_bullet"]["cd"][0] >= magic["magic_bullet"]["cd"][1]:
            #Magic bullet spawn o(n)
            if len(enemies)>0:
                closest = getClosest(enemies, player.center)
                attacks["magic_bullet"].append(spawnObj("magic_bullet", [
                    player.center,
                    ["bullet.png"],
                    enemies[closest].center,
                    magic["magic_bullet"]["spd"]*magic["magic_bullet"]["mul"]["spd"],
                    ])
                )
            magic["magic_bullet"]["cd"][0] = 0

        #Lavazone spawn
        if magic["lavazone"]["level"] > 0:
            magic["lavazone"]["cd"][0] += gameSpeed*magic["lavazone"]["mul"]["cd"]/trueSpeed
            if magic["lavazone"]["cd"][0] >= magic["lavazone"]["cd"][1] and magic["lavazone"]["level"] > 0:
                pos = (np.random.rand(2) * [xmax, ymax]) - magic["lavazone"]["size"]*magic["lavazone"]["mul"]["size"]
                attacks["lavazone"].append(spawnObj("lavazone", [
                    pos,
                    ["lava_zone.png"],
                    magic["lavazone"]["size"]*magic["lavazone"]["mul"]["size"],
                    magic["lavazone"]["dur"]*magic["lavazone"]["mul"]["dur"]
                    ]))
                magic["lavazone"]["cd"][0] = 0

        #Arcane ray spawn
        if magic["arcane_ray"]["level"] > 0:
            magic["arcane_ray"]["cd"][0] += gameSpeed*magic["arcane_ray"]["mul"]["cd"]/trueSpeed
            if magic["arcane_ray"]["cd"][0] >= magic["arcane_ray"]["cd"][1] and len(enemies) > 0:
                copy = enemies
                for n in range(round(magic["arcane_ray"]["num"]+magic["arcane_ray"]["mul"]["num"])):
                    if len(copy)<1: break
                    closest = getClosest(copy, player.center)
                    attacks["arcane_ray"].append(spawnObj("arcane_ray", [
                        player.center,
                        ["arcane_ray.png"],
                        copy[closest].center,
                        magic["arcane_ray"]["size"],
                        1,
                        magic["arcane_ray"]["dur"]*magic["arcane_ray"]["mul"]["dur"],
                    ]))
                    copy.pop(closest)
                magic["arcane_ray"]["cd"][0] = 0
        
        #Blizzard spawn
        if magic["blizzard"]["level"]>0:
            if blizNum<=0:
                magic["blizzard"]["cd"][0] += gameSpeed*magic["blizzard"]["mul"]["cd"]/trueSpeed
                if magic["blizzard"]["cd"][0] >= magic["blizzard"]["cd"][1]:
                    blizNum = magic["blizzard"]["num"]+magic["blizzard"]["mul"]["num"]
                    magic["blizzard"]["cd"][0] = 0
            else: #Blizzard spawning sequence
                magic["blizzard"]["int"][0] += gameSpeed*magic["blizzard"]["mul"]["int"]/trueSpeed
                if magic["blizzard"]["int"][0] >= magic["blizzard"]["int"][1]:
                    attacks["blizzard"].append(spawnObj("blizzard", [
                        ["blizzard.png"],
                        magic["blizzard"]["spd"]*magic["blizzard"]["mul"]["spd"],
                        player.center
                    ]))
                    blizNum -= 1
                    magic["blizzard"]["int"][0] = 0
            
        #Cyclone spawn
        if magic["cyclone"]["level"] > 0:
            magic["cyclone"]["cd"][0] += gameSpeed*magic["cyclone"]["mul"]["cd"]/trueSpeed
            if magic["cyclone"]["cd"][0] >= magic["cyclone"]["cd"][1] and len(enemies) > 0:
                closest = enemies[getClosest(enemies, player.center)]
                g = magic["cyclone"]["growth"]
                g.append(magic["cyclone"]["mul"]["size"])
                attacks["cyclone"].append(spawnObj("cyclone", [
                    player.center,
                    ["cyclone.png"],
                    closest.center,
                    magic["cyclone"]["spd"]*magic["cyclone"]["mul"]["spd"],
                    magic["cyclone"]["size"]*magic["cyclone"]["mul"]["size"],
                    magic["cyclone"]["dur"]*magic["cyclone"]["mul"]["dur"],
                    g
                    ]))
                magic["cyclone"]["cd"][0] = 0
        
        #Electric shock spawn
        if magic["electric_shock"]["level"] > 0:
            magic["electric_shock"]["cd"][0] += gameSpeed*magic["electric_shock"]["mul"]["cd"]/trueSpeed
            if magic["electric_shock"]["cd"][0] >= magic["electric_shock"]["cd"][1] and len(enemies) > 0:
                # num = round(magic["electric_shock"]["num"]+magic["electric_shock"]["mul"]["num"])
                num = rd.randint(min_shocks, round(magic["electric_shock"]["num"]+magic["electric_shock"]["mul"]["num"]))
                for n in range(num):
                    attacks["electric_shock"].append(spawnObj("electric_shock", [
                        player.center,
                        ["electric_shock.png"],
                        magic["electric_shock"]["spd"]*magic["electric_shock"]["mul"]["spd"],
                    ]))
                magic["electric_shock"]["cd"][0] = 0

        #Fire ball spawn
        if magic["fireball"]["level"] > 0:
            magic["fireball"]["cd"][0] += gameSpeed*magic["fireball"]["mul"]["cd"]/trueSpeed
            if magic["fireball"]["cd"][0] >= magic["fireball"]["cd"][1]:
                #Fire ball spawn o(n)
                if len(enemies)>0:
                    closest = getClosest(enemies, player.center)
                    attacks["fireball"].append(spawnObj("fireball", [
                        player.center,
                        ["fireball.png"],
                        enemies[closest].center,
                        magic["fireball"]["spd"]*magic["fireball"]["mul"]["spd"],
                        ])
                    )
                magic["fireball"]["cd"][0] = 0
        
        #Flash shock spawn
        if magic["flash_shock"]["level"] > 0:
            magic["flash_shock"]["cd"][0] += gameSpeed*magic["flash_shock"]["mul"]["cd"]/trueSpeed
            if magic["flash_shock"]["cd"][0] >= magic["flash_shock"]["cd"][1]:
                box = screenBox
                hor = getCollPoint(playerAngle, 90, player.center, box[0])
                vert = getCollPoint(playerAngle, 0, player.center, box[0])
                diag = np.arctan((box[1][1])/(box[1][0]))*180/np.pi
                p = vert if inBox(vert, box) else hor
                target = box[1] - p if playerAngle>=diag+90 and playerAngle<=diag+270 else p
                pos = box[1] - target
                shock = spawnObj("flash_shock", [
                    pos,
                    ["flash_shock.png"],
                    target,
                    magic["flash_shock"]["spd"]*magic["flash_shock"]["mul"]["spd"],
                    magic["flash_shock"]["size"]*magic["flash_shock"]["mul"]["size"]
                ])
                shock.pos -= shock.target*500 if playerAngle>=diag+90 and playerAngle<=diag+270 else 0
                if (playerAngle>90 and playerAngle<180) or (playerAngle>270 and playerAngle<360):
                    shock.pos -= (shock.hitbox[1]-shock.hitbox[0])/2
                attacks["flash_shock"].append(shock)
                magic["flash_shock"]["cd"][0] = 0

        #Energy bullet spawn
        if magic["energy_bullet"]["level"] > 0:
            magic["energy_bullet"]["cd"][0] += gameSpeed*magic["energy_bullet"]["mul"]["cd"]/trueSpeed
            if magic["energy_bullet"]["cd"][0] >= magic["energy_bullet"]["cd"][1] and len(enemies) > 0:
                closest = enemies[getClosest(enemies, player.center)]
                dist = magnitude([closest.center[0]-player.center[0], closest.center[1]-player.center[1]])*1.5
                num = magic["energy_bullet"]["num"]+magic["energy_bullet"]["mul"]["num"]
                for _ in range(num):
                    si, sp = rd.randint(65, 135)/100, rd.randint(65, 135)/100
                    attacks["energy_bullet"].append(spawnObj("energy_bullet", [
                        player.center,
                        ["energy_bullet.png"],
                        closest.center+((np.random.rand(2)-0.5)*dist),
                        magic["energy_bullet"]["spd"]*magic["energy_bullet"]["mul"]["spd"]*sp,
                        magic["energy_bullet"]["size"]*magic["energy_bullet"]["mul"]["size"]*si,
                        magic["energy_bullet"]["dur"]*magic["energy_bullet"]["mul"]["dur"]
                        ]))
                magic["energy_bullet"]["cd"][0] = 0

        #Frost nova spawn
        if magic["frost_nova"]["level"] > 0:
            magic["frost_nova"]["cd"][0] += gameSpeed*magic["frost_nova"]["mul"]["cd"]/trueSpeed
            if magic["frost_nova"]["cd"][0] >= magic["frost_nova"]["cd"][1] and magic["frost_nova"]["level"] > 0:
                pos = player.center - (magic["frost_nova"]["rad"]*magic["frost_nova"]["mul"]["rad"])
                attacks["frost_nova"].append(spawnObj("frost_nova", [
                    pos,
                    ["frost_nova.png"],
                    magic["frost_nova"]["rad"]*magic["frost_nova"]["mul"]["rad"]*2,
                    magic["frost_nova"]["dur"]*magic["frost_nova"]["mul"]["dur"]
                    ]))
                explosions.append(spawnObj(
                    "explosion",
                    [
                        player.center,
                        None,
                        magic["frost_nova"]["rad"]*magic["frost_nova"]["mul"]["rad"],
                        magic["frost_nova"]["dmg"]*magic["frost_nova"]["mul"]["dmg"],
                    ]))
                magic["frost_nova"]["cd"][0] = 0

        #Thunderstorm spawn
        if magic["thunderstorm"]["level"] > 0:
            magic["thunderstorm"]["cd"][0] += gameSpeed*magic["thunderstorm"]["mul"]["cd"]/trueSpeed
            if magic["thunderstorm"]["cd"][0] >= magic["thunderstorm"]["cd"][1] and len(enemies) > 0:
                copy = enemies
                size = pg.image.load(os.path.join(os.path.dirname(__file__),"assets", "lightening.png"))
                size = [size.get_width(), size.get_height()]
                for n in range(round(magic["thunderstorm"]["num"]+magic["thunderstorm"]["mul"]["num"])):
                    if len(copy)<1: break
                    closest = copy[getClosest(copy, player.center)]
                    pos = closest.center
                    attacks["thunderstorm"].append(spawnObj("thunderstorm", [
                        pos-[size[0]/2,size[1]],
                        ["lightening.png"],
                        magic["thunderstorm"]["dur"]*magic["thunderstorm"]["mul"]["dur"]
                        ]))
                    explosions.append(spawnObj(
                        "explosion",
                        [
                            pos,
                            None,
                            magic["thunderstorm"]["rad"]*magic["thunderstorm"]["mul"]["rad"],
                            magic["thunderstorm"]["dmg"]*magic["thunderstorm"]["mul"]["dmg"],
                        ]))
                    copy.remove(closest)
                magic["thunderstorm"]["cd"][0] = 0

        #Meteor spawn
        if magic["meteor"]["level"]>0:
            magic["meteor"]["cd"][0] += gameSpeed*magic["meteor"]["mul"]["cd"]/trueSpeed
            if magic["meteor"]["cd"][0] >= magic["meteor"]["cd"][1]:
                attacks["meteor"].append(spawnObj("meteor", [
                    ["meteor.png"],
                    magic["meteor"]["spd"]*magic["meteor"]["mul"]["spd"],
                    player.center
                ]))
                magic["meteor"]["cd"][0] = 0


        #Mana level up
        if player.mana["amt"] >= player.mana["cap"]:
            player.mana["amt"] -= player.mana["cap"]
            player.mana["lvl"] += 1
            player.mana["cap"] += 20 #Mana upgrade rate

            avail = False
            for n in range(3):
                if len(availableMagic)>0:
                    avail = True
                    mg = rd.choice(availableMagic)
                    availableMagic.remove(mg)
                    mgt = mg.replace("_"," ").capitalize()
                    upgrade = Text(
                        fontType,
                        (mainFontSize, subFontSize),
                        ((255,255,255),(0,255,0)),
                        [textX, textY+(n*(textHeight+textMargin))],
                        (mgt+" lvl "+str(magic[mg]["level"]+1), decipherUpgrade(magic[mg])),
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
        for mag in attacks.keys():
            if magic[mag]["level"]>0:
                for i,att in enumerate(attacks[mag]):
                    attacks[mag][i].changeSpeed(gameSpeed)
    
    #Level up display
    elif lvlUp:
        selected = False
        for i,upgrade in enumerate(options):
            options[i].draw(screen)
            options[i].dehighlight()
        options[optionScroll].highlight()

        mousePos = mousePos = np.array(pg.mouse.get_pos())
        for event in events:
            if event.type == pg.MOUSEMOTION:
                #Highlight upgrade on mouse hover
                for i,upgrade in enumerate(options):
                    if inBox(mousePos, upgrade.box) and not upgrade.highlighted:
                        optionScroll = i
            if event.type == pg.KEYDOWN:
                if event.key==pg.K_UP:
                    optionScroll -= 1
                if event.key==pg.K_DOWN:
                    optionScroll += 1
                if event.key==pg.K_RETURN:
                    selected = True
                optionScroll = 0  if optionScroll>len(options)-1 else len(options)-1 if optionScroll<0 else optionScroll
        #Checks for mouse click on upgrades
            if event.type==pg.MOUSEBUTTONDOWN:
                for i,upgrade in enumerate(options):
                    if inBox(mousePos, upgrade.box):
                        selected = True
                        break
        
        if selected:
            upgrade = options[optionScroll]
            #Upgrade selected magic
            if upgrade.highlighted:
                mag = magic[upgrade.magic]
                up = mag["upgrades"][mag["level"]-1]
                if mag["level"]>0:
                    magic[upgrade.magic]["mul"][up[0]] += up[1]
                magic[upgrade.magic]["level"] += 1
                lvlUp = False 
                
                #Resize Electric Zone
                if upgrade.magic=="electric_zone" and up[0]=="size":
                    size = magic["electric_zone"]["size"] * magic["electric_zone"]["mul"]["size"]
                    attacks["electric_zone"][0].rad = size/2
                    attacks["electric_zone"][0].respawn(player.center)
                
                #Spawn Satellite
                if upgrade.magic=="satellite":
                    attacks["satellite"] = []
                    num = magic["satellite"]["num"]+magic["satellite"]["mul"]["num"]
                    for _ in range(num):
                        attacks["satellite"].append(spawnObj("satellite", [
                            [0,0],
                            ["satellite.png"],
                            magic["satellite"]["size"]*magic["satellite"]["mul"]["size"],
                            magic["satellite"]["spd"]*magic["satellite"]["mul"]["spd"],
                            150,
                            player.center
                        ]))
                    for i,sat in enumerate(attacks["satellite"]):
                        attacks["satellite"][i].orbitAngle = 360*i/len(attacks["satellite"])

        pg.display.update()
        #Refresh available magic upgrades
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
    print("Average fps: ", np.array(fps[1]).mean())
    plt.plot(fps[0], fps[1])
    plt.show()