from gamedata import *
from objects import *

def checkMovement(direct, event):
    if event.type == pg.KEYDOWN:
        if event.key == pg.K_LEFT:
            direct.append("left")
        if event.key == pg.K_RIGHT:
            direct.append("right")
        if event.key == pg.K_UP:
            direct.append("up")
        if event.key == pg.K_DOWN:
            direct.append("down")
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

def spawnObj(objType, props=[]):
    if objType=="enemy":
        xl0, yl0, xh0, yh0 = e_xmin, e_ymin, e_xmax, e_ymax
        xl1, yl1, xh1, yh1 = xmin, ymin, xmax, ymax
    if objType=="mana item" or "chest":
        xl0, yl0, xh0, yh0 = fs_xmin, fs_ymin, fs_xmax, fs_ymax
        xl1, yl1, xh1, yh1 = fr_xmin, fr_ymin, fr_xmax, fr_ymax
        rarity = rd.randint(1,100)
        rarity = "small" if rarity < 61 else "medium" if rarity < 91 else "large"
    x1, y1 = rd.randint(xl0, xl1), rd.randint(yl0, yl1)
    x2, y2 = rd.randint(xh1, xh0), rd.randint(yh1, yh0)
    x = rd.randint(1,2)
    y = rd.randint(1,2)
    z = rd.choice([True, False])
    if z:
        x = x1 if x==1 else x2
        y = rd.randint(yl0, yh0)
    else:
        x = rd.randint(xl0, xh0)
        y = y1 if y==1 else y2
    pos = [x,y]
    if objType=="enemy":
        return Enemy(pos, props[0], props[1], props[2], props[3], objType, gameSpeed)
    if objType=="sprinter":
        tar = 2*np.array([xmax/2,ymax/2]) - np.array(pos)
        return Sprinter(pos, props[0], props[1], props[2], props[3], objType, tar, gameSpeed)
    if objType=="mana item":
        return Mana(pos, rarity, props[0], gameSpeed)
    if objType=="chest":
        return Background(pos, "chest.png", gameSpeed)
    if objType=="explosion":
        return Explosion(props[0], props[1], props[2], props[3], gameSpeed)
    if objType=="magic_bullet":
        return Projectile(props[0], props[1], props[2], props[3], gameSpeed)
    if objType=="lavazone":
        return Zone(props[0], props[1], props[2], props[3], gameSpeed)
    if objType=="arcane_ray":
        return ArcaneRay(props[0], props[1], props[2], props[3], props[4], props[5], gameSpeed)
    if objType=="blizzard":
        d = rd.randint(0, blizRad)
        a = rd.randint(0, 360)*np.pi/180
        pos = np.array([np.cos(a)*d, np.sin(a)*d]) + props[2]
        return Bombard(pos-[150,500], props[0], pos, props[1], gameSpeed)
    if objType=="cyclone":
        return MovingZone(props[0], props[1], props[2], props[3], props[4], props[5], props[6], gameSpeed)
    if objType=="electric_shock":
        target = np.random.rand(2) * [xmax, ymax]
        return PiercingProjectile(props[0], props[1], target, props[2], gameSpeed)
    if objType=="fireball":
        return Projectile(props[0], props[1], props[2], props[3], gameSpeed)

def magnitude(vec):
    return m.sqrt((vec[0]**2)+(vec[1]**2))

def getClosest(array, target):
    closest = map(lambda x : magnitude(x.center-target), array)
    closest = np.array(list(closest)).argmin()
    return closest

def boxCollision(box1, box2):
    X1 = box1[1][0] < box2[0][0]
    X2 = box1[0][0] > box2[1][0]
    Y1 = box1[1][1] < box2[0][1]
    Y2 = box1[0][1] > box2[1][1]
    col = not(X1 or X2) and not(Y1 or Y2)
    return col

def inBox(point, box):
    return (point[0]>box[0][0] and point[0]<box[1][0]) and (point[1]>box[0][1] and point[1]<box[1][1])

def ballCollision(obj1, obj2):
    distance = magnitude([obj1.center[0]-obj2.center[0], obj1.center[1]-obj2.center[1]])
    return distance < (obj1.rad+obj2.rad)

def inRange(rad, cen1, cen2):
    distance = magnitude([cen1[0]-cen2[0], cen1[1]-cen2[1]])
    return distance < rad

def distToLine(objPoint, point, angle): #angle represents pygame rotation angle
    angle = ((360-angle)+90)/(180/np.pi) #converted to numpy angle
    m = np.tan(angle)
    x = ((objPoint[1]-point[1])+((objPoint[0]+point[0]*m**2)/m))/((1+m**2)/m)
    y = point[1]+m*(x-point[0])
    return np.array([x,y])

def lineCollision(obj, line):
    vec = distToLine(obj.center, line.center, line.angle)
    d = magnitude([vec[0]-obj.center[0],vec[1]-obj.center[1]])
    return d < line.thickness+obj.rad # and (inBox(vec, line.hitbox) or boxCollision(line, obj))

def lineBoxCollision(obj, line):
    d1 = distToLine(obj.hitbox[0], line.center, line.angle)
    d2 = distToLine(obj.hitbox[1], line.center, line.angle)
    d3 = distToLine([obj.hitbox[0][0], obj.hitbox[1][1]], line.center, line.angle)
    d4 = distToLine([obj.hitbox[1][0], obj.hitbox[0][1]], line.center, line.angle)
    d1 /= np.abs(d1)
    d2 /= np.abs(d2)
    d3 /= np.abs(d3)
    d4 /= np.abs(d4)
    con = d1==d2 and d2==d3 and d3==d4
    return (not con) and (boxCollision(line, obj))

def decipherUpgrade(magic):
    lvl = magic["level"]
    if lvl>0:
        upgrade = magic["upgrades"][lvl-1]
        convDic = {
            "dmg" : "Damage",
            "spd" : "Speed",
            "size" : "Size",
            "int" : "Interval",
            "cd" : "Cooldown",
            "dur" : "Duration",
            "num" : "Number",
            "pen" : "Penetration",
            "rad" : "Explosion radius"
        }
        change = "reduces" if upgrade[0]=="int" or upgrade[0]=="cd" else "increases"
        upgradeText = convDic[upgrade[0]]
        val = upgrade[1] if upgrade[0]=="num" or upgrade[0]=="pen" else str(int(upgrade[1]*100))+"%"
        return f"{upgradeText} {change} by {val}"
    else:
        return magic["description"]

if __name__ == "__main__": pass