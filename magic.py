import numpy as np

magic = {
    "magic_bullet": {
        "dmg" : 35.0,
        "spd" : 4.0,
        "cd" : [0, .62], #[time since last attack, cooldown]
        "pen" : 1,
        "mul" : {
            "dmg" : 1,
            "spd" : 1,
            "cd" : 1,
            "pen" : 0
        },
        "level" : 1,
        "max" : 8, #8
        "upgrades" : [
            ("dmg", .2),
            ("cd", .2),
            ("dmg", .3),
            #Traits
            ("cd", .3),
            ("dmg", .3),
            ("cd", .5),
            ("dmg", .5)
            #Traits
        ],
        "description" : "Fires a magic bullet",
        "deets" : ["main_move", "despawn", "pen", "box_col"]
    },

    "lavazone" : {
        "dmg" : 100.0,
        "cd" : [0, 5.0],
        "int" : [0, .5],
        "size" : 100.0,
        "dur" : 3.8,
        "mul" : {
            "dmg" : 1,
            "cd" : 1,
            "size" : 1,
            "dur" : 1,
            "int" : 1
        },
        "level" : 0,
        "max" : 7, #7
        "upgrades" : [
            ("size", .1),
            ("dmg", .3),
            ("dur", .3),
            ("dmg", .3),
            ("dur", .5),
            ("dmg", .5)
            #Traits
        ],
        "description" : "Creates a lava zone that damages enemies for a certain period of time",
        "deets" : ["ball_col"]
    },

    "electric_zone" : {
        "dmg" : 25.0,
        "size" : 100.0,
        "int" : [0, .2],
        "mul" : {
            "dmg" : 1,
            "size" : 1,
            "int" : 1
        },
        "level" : 0,
        "max" : 7, #7
        "upgrades" : [
            ("size", .15),
            ("dmg", .3),
            ("size", .15),
            ("dmg", .3),
            ("size", .25),
            ("dmg", .5),
            #Traits
        ],
        "description" : "Creates a thunderstorm electric circle to continuously damage enemies",
        "deets" : ["static", "ball_col"]
    },

    "arcane_ray" : {
        "dmg" : 110,
        "dur" : 0.8,
        "num" : 1,
        "cd" : [0, 3.8],
        "size" : [1,650],
        "level" : 0,
        "max" : 9, #9
        "mul" : {
            "dmg" : 1,
            "dur" : 1,
            "num" : 0,
            "cd" : 1,
        },
        "upgrades" : [
            ("num", 1),
            ("dmg", .3),
            ("dur", .5),
            ("num", 2),
            ("dmg", .3),
            ("cd", .2),
            ("num", 3),
            ("dmg", .5),
            #Traits
        ],
        "description" : "Fires a ray that penetrates all objects",
        "deets" : ["static", "line_col"]
    },

    "blizzard" : {
        "dmg" : 100,
        "rad" : 50,
        "num" : 20,
        "cd" : [0, 6.0],
        "spd" : 4.5,
        "int" : [0, .1],
        "mul" : {
            "dmg" : 1,
            "rad" : 1,
            "num" : 0,
            "cd" : 1,
            "spd" : 1,
            "int" : 1
        },
        "level" : 0,
        "max" : 9, #9
        "upgrades" : [
            ("num", 6),
            ("dmg", .3),
            ("cd", .1),
            ("num", 6),
            ("dmg", .3),
            ("cd", .2),
            ("num", 10),
            ("dmg", .5)
            #Traits
        ],
        "description" : "Creates an ice storm to freeze enemies",
        "deets" : ["main_move", "bombard", "explode"]
    },

    "cyclone" : {
        "dmg" : 60,
        "cd" : [0, 2.8],
        "int" : [0, .25],
        "size" : 50.0,
        "dur" : 1.9,
        "spd" : 0.5,
        "growth" : [0, 0.1],
        "mul" : {
            "dmg" : 1,
            "cd" : 1,
            "size" : 1,
            "dur" : 1,
            "int" : 1,
            "spd" : 1,
        },
        "level" : 0,
        "max" : 9, #9
        "upgrades" : [
            ("dur", .2),
            ("dmg", .3),
            ("cd", .1),
            ("dur", .3),
            ("dmg", .3),
            ("int", .2),
            ("dur", .5),
            ("dmg", .5),
            #Traits
        ],
        "description" : "Casts an expanding whirlwind",
        "deets" : ["main_move", "despawn", "ball_col", "expand"]
    },

    "electric_shock": {
        "dmg" : 75,
        "spd" : 3,
        "cd" : [0, 1.5], #[time since last attack, cooldown]
        "num" : 2,
        "mul" : {
            "dmg" : 1,
            "spd" : 1,
            "cd" : 1,
            "num" : 0
        },
        "level" : 0,
        "max" : 9, #9
        "upgrades" : [
            ("num", 2),
            ("dmg", .3),
            ("cd", .1),
            ("num", 2),
            ("dmg", .3),
            ("cd", .2),
            ("num", 3),
            ("dmg", .5),
            #Traits
        ],
        "description" : "Thunderstorm will shock enemies in a random direction",
        "deets" : ["main_move", "despawn", "line_col"]
    },

    "energy_bullet": {
        "dmg" : 75,
        "spd" : 2,
        "cd" : [0, 3.3],
        "size" : 30,
        "dur" : 0.75,
        "num" : 6,
        "mul" : {
            "dmg" : 1,
            "size" : 1,
            "spd" : 1,
            "cd" : 1,
            "dur" : 1,
            "num" : 0,
        },
        "level" : 0,
        "max" : 1, #9
        "upgrades" : [
            ("num", 1),
            ("dmg", .3),
            ("size", .3),
            ("num", 2),
            ("dmg", .3),
            ("cd", .2),
            ("num", 3),
            ("dmg", .5),
        ],
        "description" : "Fires a circle of energy that burns through enemies",
        "deets" : ["main_move", "ball_col"]
    },

    "fireball": {
        "dmg" : 80,
        "spd" : 2.0,
        "cd" : [0, .95], #[time since last attack, cooldown]
        "pen" : 1,
        "rad" : 50,
        "mul" : {
            "dmg" : 1,
            "spd" : 1,
            "cd" : 1,
            "pen" : 0,
            "rad" : 1
        },
        "level" : 0,
        "max" : 9, #9
        "upgrades" : [
            ("cd", .1),
            ("dmg", .3),
            ("rad", .2),
            ("cd", .1),
            ("dmg", .3),
            ("cd", .2),
            ("pen", 1),
            ("dmg", .5),
            #Traits
        ],
        "description" : "Fires an explosive projectile",
        "deets" : ["main_move", "despawn", "pen", "box_col", "explode"]
    },

    "flash_shock": {
        "dmg" : 500,
        "spd" : 20,
        "cd" : [0, 12], #[time since last attack, cooldown]
        "size" : 150,
        "num" : 1,
        "mul" : {
            "dmg" : 1,
            "spd" : 1,
            "cd" : 1,
            "size" : 1,
            "num" : 0
        },
        "level" : 0,
        "max" : 9, #9
        "upgrades" : [
            ("cd", .1),
            ("dmg", .3),
            ("size", .1),
            ("cd", .1),
            ("dmg", .3),
            ("cd", .2),
            ("size", .2),
            ("dmg", .5),
            #Traits
        ],
        "description" : "Creates a flash that crosses the field in the direction of character's movement",
        "deets" : ["main_move", "despawn", "line_col"]
    },
    
}


testMagic = None
if testMagic:
    for x in magic.keys():
        if x != testMagic:
            magic[x]["max"] = 0
    magic["magic_bullet"]["cd"][1] = np.inf
    magic[testMagic]["level"] = 1
    # magic["electric_zone"]["max"] = 1

availableMagic = [x if magic[x]["level"] < magic[x]["max"] else None for x in magic.keys()]
while None in availableMagic:
    availableMagic.remove(None)

if __name__ == "__main__": pass