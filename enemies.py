enemySpeed = 0.8
enemyHp = 30
enemyDmg = 10
base_spawn_rate = 5 #enemies per second, 5

sprinterSpeed = 1.5 #1.5

enemyInfo = {
    "norm1" : {
        "hp" : 20,
        "dmg" : 10,
        "spd" : .8,
        "mana" : 5,
        "weight" : 100
    },
    
    "norm2" : {
        "hp" : 40,
        "dmg" : 15,
        "spd" : .8,
        "mana" : 10,
        "weight" : 75
    },

    "norm3" : {
        "hp" : 80,
        "dmg" : 20,
        "spd" : .8,
        "mana" : 20,
        "weight" : 50
    },

    "sprinter" : {
        "hp" : 20,
        "dmg" : 10,
        "spd" : 1.5,
        "mana" : 5,
        "weight" : 15
    },

    "splitter" : {
        "hp" : 200,
        "dmg" : 20,
        "spd" : .5,
        "mana" : 25,
        "weight" : 10
    },

    "red1" : {
        "hp" : 100,
        "dmg" : 20,
        "spd" : 1,
        "mana" : 25,
        "weight" : 50
    },

    "red2" : {
        "hp" : 250,
        "dmg" : 40,
        "spd" : .9,
        "mana" : 50,
        "weight" : 25
    },

    "bignorm" : {
        "hp" : 1000,
        "dmg" : 50,
        "spd" : .5,
        "mana" : 100,
        "weight" : 1
    },

}

spawn_pattern = {
    "0" : ["norm1", "norm2"],
    "2" : ["norm1", "norm2", "sprinter"],
    "4" : ["norm1", "norm2", "norm3"],
    "7" : ["norm2", "norm3", "sprinter", "splitter"],
    "9" : ["norm2", "norm3", "red1"],
    "12" : ["norm3", "red1", "sprinter", "splitter"],
    "17" : ["norm3", "splitter", "bignorm"],
    "21" : ["norm3", "splitter", "red1", "red2", "sprinter"],
    "27" : ["norm3", "splitter", "red1", "red2", "bignorm"],
}

if __name__ == "__main__": pass