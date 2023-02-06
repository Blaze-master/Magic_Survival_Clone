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
        "level" : 1,
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
        "level" : 1,
        "upgrades" : [
            ("", ),
            ("", ),
            ("", ),
            ("", ),
            ("", ),
            ("", ),
            ("", ),
            #Traits
        ],
        "max" : 1
    }
}

availableMagic = [x if magic[x]["level"] < magic[x]["max"] else None for x in magic.keys()]
while None in availableMagic:
    availableMagic.remove(None)

projBaseDmg = 35
projDmgMultiplier = 1
projSpeed = 4.0 
projDmg = projBaseDmg * projDmgMultiplier
projBaseCd = .62 #.62
projCdMultiplier = 1.0
projTimer = [0, projBaseCd/projCdMultiplier]
projLevel = 1
projUpgrades = [
    [0.2, 0],
    [0, 0.2],
    [0.3, 0],
    #Traits
    [0, 0.3],
    [0.3, 0],
    [0, 0.5],
    [0.5, 0],
    #Traits
]

lavaBaseDmg = 100
lavaDmgMultiplier = 1
lavaDmg = lavaBaseDmg * lavaDmgMultiplier
lavaBaseCd = 5 #5
lavaCdMultiplier = 1
lavaCdTimer = [0, lavaBaseCd/lavaCdMultiplier]
lavaBaseInterval = .5
lavaIntervalMultiplier = 1
lavaIntervalTimer = [0, lavaBaseInterval/lavaIntervalMultiplier]
lavaBaseSize  = 100
lavaSizeMultiplier = 1
lavaSize = lavaBaseSize * lavaSizeMultiplier
lavaBaseDuration = 3.8
lavaDurationMultiplier = 1
lavaDuration = lavaBaseDuration * lavaDurationMultiplier
lavaLevel = 1
lavaUpgrades = [
    #[size, dmg, dur]
    [0.1, 0, 0],
    [0, 0.3, 0],
    [0, 0, 0.3],
    [0, 0.3, 0],
    [0, 0, 0.5],
    [0, 0.5, 0],
    #Traits
]

eZoneBaseDmg = 25
eZoneDmgMultiplier = 1
eZoneDmg = eZoneBaseDmg * eZoneDmgMultiplier
eZoneBaseSize = 100 #100
eZoneSizeMultiplier = 1
eZoneSize = eZoneBaseSize * eZoneSizeMultiplier
eZoneBaseInterval = .2 #.2
eZoneIntervalMultiplier = 1
eZoneIntervalTimer = [0, eZoneBaseInterval/eZoneIntervalMultiplier]
eZoneLevel = 1
eZoneUpgrades = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
    #Traits
]

#Passive
intelligence = [0, 0]

if __name__ == "__main__": pass