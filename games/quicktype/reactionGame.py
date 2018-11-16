# Game 1 Reaction Time Game, A letter shows up and you have to click the key
# on the keyboard

import pygame
import time
import random
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import sys, os.path
leader_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
leader_dir = os.path.abspath(os.path.join(leader_dir, '../library'))
sys.path.append(leader_dir)
import leaderboard
from leaderboard import Leaderboard

pygame.init()

bg = (32,32,32)
best = 10000
curUsr = ''
right = 0
wrong = 0
tries = 0
totalTime = 0
last = ''

startfont = pygame.font.SysFont("monospace", 60)
startfont1 = pygame.font.SysFont("monospace", 85)
myfont = pygame.font.SysFont("monospace", 150)
displayFont = pygame.font.SysFont("monospace", 30)

w_width = 1000
w_height = 600

class button(object):
    def __init__(self, text, textSize, width, height, color):
        self.text = text
        self.width = width
        self.height = height
        self.original = color
        self.color = self.original
        self.x = 0
        self.y = 0
        self.isHover = True
        self.fontSize = textSize
        self.textColor = (255,255,255)

    def draw(self, surface, x, y):
        self.x = x
        self.y = y
        font = pygame.font.SysFont("monospace", self.fontSize)
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, self.color, (self.x+2, self.y+2, self.width-4, self.height-4))
        text = font.render(self.text, 1, self.textColor)
        surface.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def hover(self, surface):
        if not self.isHover:
            self.color = (round(self.color[0]*(3/4)), round(self.color[1]*(3/4)), round(self.color[2]*(3/4)))
        self.draw(surface, self.x, self.y)
        self.isHover = True

    def isMouseOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width and pos[1] > self.y and pos[1] < self.y + self.height:
            return True
        else:
            return False

    def update(self, surface):
        self.isHover = False
        self.color = self.original
        self.draw(surface, self.x, self.y)

    def textColor(self, color):
        self.textColor = color


def update():
    global time1, totalTime
    pygame.draw.rect(win, bg, (0,0,w_width,100))
    totalTime = time.time() - time1
    label = displayFont.render('Time: ' + str(round(totalTime,2)),1,(255,255,255))
    win.blit(label,(10,10))
    label = displayFont.render('Remaining: ' + str(26 - tries),1,(255,255,255))
    win.blit(label, (w_width - 20 - label.get_width(),10))
    label = displayFont.render('Correct: ' + str(right),1,(0,255,0))
    win.blit(label, (w_width-38-label.get_width(),40))
    label = displayFont.render('Incorrect: ' + str(wrong),1,(255,0,0))
    win.blit(label, (w_width - 37 - label.get_width(),70))
    label = displayFont.render('+' + str(2.5*wrong) + 's', 1, (255,0,0))
    win.blit(label, (220, 10))
    pygame.display.update()

def showLetter():
    global last
    letter = generateKey()
    while letter == last:
        letter = generateKey()
    last = letter
    label = myfont.render(letter, 1, (255,255,255))
    win.blit(label, (random.randrange(100,w_width - 100 - label.get_width()), random.randrange(100,w_height-label.get_height())))
    pygame.display.update()
    return letter

def correct():
    global right
    right += 1

def incorrect():
    global wrong
    wrong += 1

def generateKey():
    r = random.randrange(0,26)
    return chr(65 + r)

def startCount():
    win.fill(bg)
    label = myfont.render('3',1,(255,255,255))
    win.blit(label, (w_width/2 - label.get_width()/2,w_height/2-label.get_height()/2))
    pygame.display.update()
    pygame.time.delay(1000)
    win.fill(bg)
    label = myfont.render('2',1,(255,255,255))
    win.blit(label, (w_width/2 - label.get_width()/2,w_height/2-label.get_height()/2))
    pygame.display.update()
    pygame.time.delay(1000)
    win.fill(bg)
    label = myfont.render('1',1,(255,255,255))
    win.blit(label, (w_width/2 - label.get_width()/2,w_height/2-label.get_height()/2))
    pygame.display.update()
    pygame.time.delay(1000)


def endScreen():
    global totalTime, best
    totalTime += 2.5 * wrong

    if tries == 26:
        win.fill(bg)
        pygame.display.update()
        text = startfont1.render('Time: ' + str(round(totalTime,2)),1, (255,255,255))
        win.blit(text, (w_width/2 - text.get_width()/2, w_height/2 - text.get_height()/2 - 30))
        text = startfont.render('Previous Best: ' + str(best),1, (255,255,255))
        win.blit(text, (w_width/2 - text.get_width()/2, w_height/2 - text.get_height()/2 + 45))
        text = displayFont.render('Press any Key To Continue',1, (255,255,255))
        win.blit(text, (w_width/2 - text.get_width()/2, w_height - 40))
        pygame.display.update()
        loop = True
        leaderboard.addTimePlayed(curUsr, 'quicktype', round(totalTime, 2))
        leaderboard.addGamesPlayed(curUsr, 'quicktype')
        if best == 0:
            best = 1000000

        if totalTime < best:
            leaderboard.addHighscore(curUsr, 'quicktype', round(totalTime, 2))
            best = round(totalTime, 2)
        while loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    loop = False


def showInfoScreen():
    global win
    win.fill(bg)
    label = startfont1.render('How to Play',1,(255,255,255))
    win.blit(label, (w_width/2 - label.get_width()/2, 20))
    backBtn = button('< Back', 30, 130, 50, (40,40,40))
    backBtn.draw(win, 15, w_height-65)

    l = displayFont.render('In this game your reflexes will be tested, Your mind', 1, (255,255,255))
    win.blit(l, (20, 120))
    l = displayFont.render('will be exercised and your fingers will move faster ', 1, (255,255,255))
    win.blit(l, (20, 160))
    l = displayFont.render('than ever before. Once you hit start a timer will ', 1, (255,255,255))
    win.blit(l, (20, 200))
    l = displayFont.render('start and you will see letters appear in random', 1, (255,255,255))
    win.blit(l, (20, 240))
    l = displayFont.render('positions on the screen. You have to click the', 1, (255,255,255))
    win.blit(l, (20, 280))
    l = displayFont.render('cooresponding key on your keyboard for the next letter', 1, (255,255,255))
    win.blit(l, (20, 320))
    l = displayFont.render('to appear. The goal is to complete the sequence of 26', 1, (255,255,255))
    win.blit(l, (20, 360))
    l = displayFont.render('letters as fast as possible. But be careful as if you', 1, (255,255,255))
    win.blit(l, (20, 400))
    l = displayFont.render('hit the wrong key you will have 2.5seconds added to', 1, (255, 255, 255))
    win.blit(l, (20, 440))
    l = displayFont.render('your final time. Goodluck!', 1, (255, 255, 255))
    win.blit(l, (20, 480))
    pygame.display.update()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if backBtn.isMouseOver(pos):
                    backBtn.hover(win)
                else:
                    backBtn.update(win)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if backBtn.isMouseOver(pos):
                    run = False

    pass

#pass the string user name of the current user so that we can access their information
def start(currentUser):
    global win, curUsr, best
    curUsr = currentUser
    session = boto3.resource('dynamodb',
                             aws_access_key_id='AKIAIOPUXE2QS7QN2MMQ',
                             aws_secret_access_key='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',
                             region_name="ca-central-1"
                             )
    table = session.Table('highscores')

    try:
        response = table.get_item(
            Key={
                'peopleid':curUsr
            }
        )
        best = response['Item']['quicktype']
    except:
        best = 10000000

    win = pygame.display.set_mode((w_width, w_height))
    pygame.display.set_caption('Quick Type')
    title = startfont1.render('Quick Type',1,(255,255,255))

    startBtn = button('Start Game', 30, 250, 50, (40,40,40))
    infoBtn = button('Learn to Play', 30, 250, 50, (40,40,40))
    btns = [startBtn, infoBtn]
    run = True
    globalTable = Leaderboard(curUsr, 'quicktype', 'global', win, 300, 380, 150, 130)
    friendTable = Leaderboard(curUsr, 'quicktype', 'friend', win, 300, 380, 550, 130)
    while run:
        pygame.time.delay(50)
        win.fill(bg)
        globalTable.draw()
        friendTable.draw()
        win.blit(title, (w_width / 2 - title.get_width() / 2, 0))
        startBtn.draw(win, 175, w_height - 80)
        infoBtn.draw(win, w_width - 425, w_height - 80)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                for btn in btns:
                    if btn.isMouseOver(pos):
                        btn.hover(win)
                    else:
                        btn.update(win)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if startBtn.isMouseOver(pos):
                    run = False
                elif infoBtn.isMouseOver(pos):
                    showInfoScreen()
        pygame.display.update()

    win.fill(bg)
    pygame.display.update()
    main()


def main():
    global time1, tries, right, wrong, totalTime, win

    play = True
    time1 = 0
    while play:
        label = startfont.render('Press Any Key to Begin...', 1, (255,255,255))
        win.blit(label, (w_width/2 - label.get_width()/2,w_height/2-label.get_height()/2))
        pygame.display.update()
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            if event.type == pygame.KEYDOWN:
                #startCount()
                update()
                totalTime = 0
                tries = 0
                right = 0
                wrong = 0
                time1 = time.time()
                while tries < 26:
                    tries += 1
                    win.fill(bg)
                    correctKey = showLetter()
                    gameLoop = True
                    while gameLoop:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                gameLoop = False
                                tries = 100
                                play = False
                                pygame.quit()
                            if event.type == pygame.KEYDOWN:
                                pressed = pygame.key.get_pressed()
                                for i in range(len(pressed)):
                                    if pressed[i] == 1:
                                        usrPressed = pygame.key.name(i)

                                if usrPressed.lower() == correctKey.lower() or usrPressed == correctKey:
                                    correct()
                                else:
                                    incorrect()
                                gameLoop = False
                        update()
                endScreen()
                play = False
                start(curUsr)

# Call the start function with an argument of the string name of the user to start the game
start('nickiscool123')
