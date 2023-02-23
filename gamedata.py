#Constants
#trueSpeed represents pixels per second (p/s)
#fps represents iterations per second (i/s)
#gameSpeed represents pixels per iteration (p/i)
fpsLimit = 60 #60
trueSpeed = 200 #300
gameSpeed = trueSpeed/fpsLimit

#Coefficients
playerSpeed = 1.0
attractSpeed = 1.6
score = 0
total_mana = 0

#View screen box
xmax, ymax = 1160, 610
xmin, ymin = 0, 0
screenBox = [[xmin,ymin], [xmax,ymax]]

#Enemy render box
ex, ey = 800, 500
e_xmin, e_ymin = -ex, -ey
e_xmax, e_ymax = ex+xmax, ey+ymax
enemyBox = [[e_xmin,e_ymin], [e_xmax,e_ymax]]

#Background render box
bx, by = 500, 300
bg_xmin, bg_ymin = -bx, -by
bg_xmax, bg_ymax = bx+xmax, by+ymax
bgBox = [[bg_xmin,bg_ymin], [bg_xmax,bg_ymax]]

#Field item spawn and render box
max_mana = 30 #To increase spawn rate, just increase max mana
max_chests = 1
frx, fry = 580, 305
fsx, fsy = 1160, 610
fr_xmin, fr_ymin = -frx, -fry
fr_xmax, fr_ymax = frx+xmax, fry+ymax
fs_xmin, fs_ymin = -fsx, -fsy
fs_xmax, fs_ymax = fsx+xmax, fsy+ymax

fontType = "freesansbold.ttf"
mainFontSize = 40
subFontSize = 15
textWidth = 600
textHeight = 100
textMargin = 50
textPadding = (20, (textHeight-60)/2)
textX = (xmax-textWidth)/2
textY = (ymax-((textHeight*3) + (textMargin*2)))/2

blizRad = 300
blizNum = 0
min_shocks = 1

if __name__ == "__main__": pass