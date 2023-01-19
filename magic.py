projBaseDmg = 10
projDmgMultiplier = 1
projSpeed = 4.0 
projDmg = projBaseDmg * projDmgMultiplier
projBaseCd = 1.0
projCdMultiplier = 1.0
projTimer = [0, projBaseCd*projCdMultiplier] #[time since last attack, cooldown]
projUpgrades = [
    [0, -0.1],
    [0.1, 0],
    [0, -0.1],
    [0.1, 0],
    [0, -0.1],
    [0.1, 0],
    [0, -0.1],
    [0.1, 0],
    [0, -0.1],
    [0.1, 0]
]

if __name__ == "__main__": pass