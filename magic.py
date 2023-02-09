import numpy as np

magic = {
    "magic_bullet": {
        "dmg" : 35.0,
        "speed" : 4.0,
        "cd" : [0, .62], #[time since last attack, cooldown]
        "multiplier" : {
            "dmg" : 1,
            "speed" : 1,
            "cd" : 1
        },
        "level" : 1,
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
        "max" : 8
    },

    "lavazone" : {
        "dmg" : 100.0,
        "cd" : [0, 5.0],
        "interval" : [0, .5],
        "size" : 100.0,
        "duration" : 3.8,
        "multiplier" : {
            "dmg" : 1,
            "cd" : 1,
            "size" : 1,
            "duration" : 1,
            "interval" : 1
        },
        "level" : 0,
        "upgrades" : [
            ("size", .1),
            ("dmg", .3),
            ("duration", .3),
            ("dmg", .3),
            ("duration", .5),
            ("dmg", .5)
            #Traits
        ],
        "max" : 7
    },

    "electric_zone" : {
        "dmg" : 25.0,
        "size" : 100.0,
        "interval" : [0, .2],
        "multiplier" : {
            "dmg" : 1,
            "size" : 1,
            "interval" : 1
        },
        "level" : 0,
        "upgrades" : [
            ("size", .15),
            ("dmg", .3),
            ("size", .15),
            ("dmg", .3),
            ("size", .25),
            ("dmg", .5),
            #Traits
        ],
        "max" : 7
    },

    "arcane_ray" : {
        "dmg" : 110,
        "duration" : 0.8,
        "num" : 1,
        "cd" : [0, 3.8],
        "size" : [1,650],
        "level" : 0,
        "max" : 9,
        "multiplier" : {
            "dmg" : 1,
            "duration" : 1,
            "num" : 1,
            "cd" : 1,
        },
        "upgrades" : [
            ("num", 1),
            ("dmg", .3),
            ("duration", .5),
            ("num", 2),
            ("dmg", .3),
            ("cd", .2),
            ("num", 3),
            ("dmg", .5),
        ],
    }
}

availableMagic = [x if magic[x]["level"] < magic[x]["max"] else None for x in magic.keys()]
while None in availableMagic:
    availableMagic.remove(None)

if __name__ == "__main__": pass