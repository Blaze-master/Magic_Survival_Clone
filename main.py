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

#Testing variables
graph = False #Enable to record fps
fuckIt = False
immortal = False

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
blizNum = 0
min_shocks = 1

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
            mouseVec = mousePos - player.center
            magn = magnitude(mouseVec)
            magn = magn if magn != 0 else 1
            mouseDir = mouseVec/magn

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
                    #Movement and despawn
                    if not "static" in det:
                        if keyMove: attacks[mag][i].move(direct, playerSpeed)
                        if mouseMove: attacks[mag][i].mouseMove(mouseDir, playerSpeed)
                    if "main_move" in det:
                        attacks[mag][i].mainMove()
                    if "despawn" in det:
                        if not inBox(attacks[mag][i].center, [[e_xmin, e_ymin],[e_xmax, e_ymax]]):
                            del attacks[mag][i]
                            continue
                    if "expand" in det:
                        attacks[mag][i].grow(gameSpeed/trueSpeed)
                    
                    dead = False

                    #Timers
                    interval = "int" in magic[mag].keys()
                    duration = "dur" in magic[mag].keys()
                    int_over = False
                    if interval:
                        magic[mag]["int"][0] += gameSpeed*magic[mag]["mul"]["int"]/trueSpeed
                        if magic[mag]["int"][0]>=magic[mag]["int"][1]:
                            int_over = True
                            magic[mag]["int"][0] = 0
                    if duration:
                        attacks[mag][i].duration -= gameSpeed/trueSpeed
                        dead = attacks[mag][i].duration<=0
                    
                    #Damage
                    pen = "pen" in magic[mag].keys()
                    hit = False
                    for j,enemy in enumerate(enemies):
                        if not interval or (interval and int_over):
                            if not pen or (pen and not id(enemy) in attacks[mag][i].hits):
                                if "box_col" in det:
                                    if boxCollision(attacks[mag][i].hitbox, enemy.hitbox):
                                        enemies[j].hp -= (magic[mag]["dmg"]*magic[mag]["mul"]["dmg"])
                                        hit = True
                                        if pen: attacks[mag][i].hits.append(id(enemy))
                                if "ball_col" in det:
                                    if ballCollision(attacks[mag][i], enemy):
                                        enemies[j].hp -= (magic[mag]["dmg"]*magic[mag]["mul"]["dmg"])
                                        hit = True
                                        if pen: attacks[mag][i].hits.append(id(enemy))
                            if "line_col" in det:
                                if (not id(enemy) in attacks[mag][i].hits) and boxCollision(enemy.hitbox, attacks[mag][i].hitbox):
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

        #Draw attacks
        for mag in attacks.keys():
            if magic[mag]["level"]>0:
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
            if ticks%1 == 0:
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