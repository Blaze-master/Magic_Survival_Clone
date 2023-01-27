#Constants
fpsLimit = 60 #60
trueSpeed = 300 #300
gameSpeed = trueSpeed/fpsLimit
playerSpeed = 1.5
attractSpeed = 1.6
score = 0
total_mana = 0

#View screen box
xmax, ymax = 1160, 610
xmin, ymin = 0, 0

#Enemy render box
ex, ey = 800, 500
e_xmin, e_ymin = -ex, -ey
e_xmax, e_ymax = ex+xmax, ey+ymax

#Background render box
bx, by = 500, 300
bg_xmin, bg_ymin = -bx, -by
bg_xmax, bg_ymax = bx+xmax, by+ymax

#Field item spawn and render box
max_mana = 30 #To increase spawn rate, just increase max mana
max_chests = 3
frx, fry = 580, 305
fsx, fsy = 1160, 610
fr_xmin, fr_ymin = -frx, -fry
fr_xmax, fr_ymax = frx+xmax, fry+ymax
fs_xmin, fs_ymin = -fsx, -fsy
fs_xmax, fs_ymax = fsx+xmax, fsy+ymax

if __name__ == "__main__": pass