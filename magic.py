import numpy as np
projBaseDmg = 35
projDmgMultiplier = 1
projSpeed = 4.0 
projDmg = projBaseDmg * projDmgMultiplier
projBaseCd = np.inf #.62
projCdMultiplier = 1.0
projTimer = [0, projBaseCd/projCdMultiplier] #[time since last attack, cooldown]
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
lavaBaseCd = np.inf #5
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

eZoneBaseDmg = 20
eZoneDmgMultiplier = 1
eZoneDmg = eZoneBaseDmg * eZoneDmgMultiplier
eZoneBaseSize = 200
eZoneSizeMultiplier = 1
eZoneSize = eZoneBaseSize * eZoneSizeMultiplier
eZoneBaseInterval = .2
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