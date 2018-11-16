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

game_directory = (os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
game_directory = os.path.abspath(os.path.join(game_directory, ''))
sys.path.append(game_directory)

bg = (0,51,102)
best = None
totalTime = 60
score = 0
time1 = 0
seq = []
usrSeq = []
lvl = 1
lastCorrect = 0

startfont = pygame.font.SysFont("monospace", 60)
startfont1 = pygame.font.SysFont("monospace", 85)
myfont = pygame.font.SysFont("monospace", 100)
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


def generateSeq(n):
    seq = ''
    for x in range(n):
        seq += (str(random.randrange(0,10)))

    return seq


def showSeq():
    global seq, lvl, time1, win, lastCorrect
    lvl += 1
    seq = generateSeq(lvl//2)

    next = button('Next', 40, 150, 50, (0, 128, 0))
    s = myfont.render(seq, 1, (255,255,255))
    run = True
    while run:
        if totalTime < -.0001:
            run = False
        if lastCorrect > 0:
            l = startfont1.render('Correct +' + str(lastCorrect), 1, (0, 128, 0))
            win.blit(l, (w_width / 2 - l.get_width() / 2, 100))
        elif lastCorrect == -1:
            l = startfont1.render('Incorrect :(', 1, (128, 0, 0))
            win.blit(l, (w_width / 2 - l.get_width() / 2, 100))
        pygame.display.update()
        update()
        win.blit(s, (w_width/2 - s.get_width()/2, w_height/2 - s.get_height()/2))
        next.draw(win, w_width/2 - next.width/2, w_height- 60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type  == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if next.isMouseOver(pos):
                    next.hover(win)
                else:
                    next.update(win)

            if event.type  == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if next.isMouseOver(pos):
                    run = False
        pygame.display.update()


def update():
    global time1, totalTime, usrSeq
    pygame.draw.rect(win, bg, (0,0,w_width,100))
    totalTime = 60 - (time.time() - time1)
    label = displayFont.render('Time: ' + str(round(totalTime,2)),1,(255,255,255))
    win.blit(label,(10,10))
    label = displayFont.render('Score: ' + str(score),1,(255,255,255))
    win.blit(label, (w_width - 10 - label.get_width(), 10))


def showInfoScreen():
    pass

def spacedOut(se, guessed=[]):
    spacedWord = ''
    guessedNumbers = guessed
    seq = str(se)
    for x in range(len(se)):
        try:
            spacedWord += guessed[x] + ' '
        except:
            spacedWord += '_ '

    return spacedWord


def endScreen():
    global score, best

    win.fill(bg)
    pygame.display.update()
    if best == -1:
        best = 'None'
    text = startfont1.render('Score: ' + str(round(score,2)),1, (255,255,255))
    win.blit(text, (w_width/2 - text.get_width()/2, w_height/2 - text.get_height()/2 - 30))
    text = startfont.render('Previous Best: ' + str(best),1, (255,255,255))
    win.blit(text, (w_width/2 - text.get_width()/2, w_height/2 - text.get_height()/2 + 45))
    text = displayFont.render('Press any Key To Continue',1, (255,255,255))
    win.blit(text, (w_width/2 - text.get_width()/2, w_height - 40))
    pygame.display.update()
    loop = True
    leaderboard.addTimePlayed(curUsr, 'integerrecall', round(totalTime, 2))
    leaderboard.addGamesPlayed(curUsr, 'integerrecall')
    if score > best:
        leaderboard.addHighscore(curUsr, 'integerrecall', score)
        best = score
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                loop = False

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
        best = response['Item']['integerrecall']
    except:
        best = -1

    win = pygame.display.set_mode((w_width, w_height))
    pygame.display.set_caption('Integer Recall')
    title = startfont1.render('Integer Recall',1,(255,255,255))

    startBtn = button('Start Game', 30, 250, 50, (64,64,64))
    infoBtn = button('Learn to Play', 30, 250, 50, (64,64,64))
    btns = [startBtn, infoBtn]
    run = True
    globalTable = Leaderboard(curUsr, 'integerrecall', 'global', win, 300, 380, 150, 130)
    friendTable = Leaderboard(curUsr, 'integerrecall', 'friend', win, 300, 380, 550, 130)
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
    global time1, totalTime, win, lvl, score, lastCorrect, score

    play = True
    time1 = 0
    next = button('Next', 40, 150, 50, (0, 128, 0))
    while play:
        label = startfont.render('Press Any Key to Begin...', 1, (255,255,255))
        win.blit(label, (w_width/2 - label.get_width()/2,w_height/2-label.get_height()/2))
        pygame.display.update()
        pygame.time.delay(100)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
            if event.type == pygame.KEYDOWN:
                update()
                time1 = time.time()
                totalTime = time.time() - time1
                while totalTime > -0.001:
                    win.fill(bg)

                    gameLoop = True
                    showSeq()
                    usrPressed = ''
                    pygame.display.update()
                    while gameLoop:
                        if totalTime < -0.0001:
                            gameLoop = False
                        win.fill(bg)
                        pygame.time.delay(25)
                        if len(usrPressed) > len(seq):
                            usrPressed = usrPressed[-1]

                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                gameLoop = False
                                pygame.quit()
                            if event.type == pygame.KEYDOWN:
                                pressed = pygame.key.get_pressed()
                                for i in range(len(pressed)):
                                    if pressed[i] == 1:
                                        if str(pygame.key.name(i)).isdigit():
                                            usrPressed += pygame.key.name(i)
                                        if pygame.key.name(i) == 'backspace':
                                            usrPressed = usrPressed[:-1]
                                        if pygame.key.name(i) == 'return':
                                            if usrPressed == seq:
                                                score += (lvl // 2) * 10
                                                gameLoop = False
                                                lastCorrect = (lvl // 2) * 10
                                            else:
                                                lvl -= 1
                                                gameLoop = False
                                                lastCorrect = -1

                            if event.type == pygame.MOUSEMOTION:
                                pos = pygame.mouse.get_pos()
                                if next.isMouseOver(pos):
                                    next.hover(win)
                                else:
                                    next.update(win)

                            if event.type == pygame.MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()
                                if next.isMouseOver(pos):
                                    if usrPressed == seq:
                                        score += (lvl//2) * 10
                                        gameLoop = False
                                        lastCorrect = (lvl//2) * 10
                                    else:
                                        if lvl != 1:
                                            lvl -= 1
                                        gameLoop = False
                                        lastCorrect = -1


                        display = spacedOut(seq, list(usrPressed))
                        l = myfont.render(display, 1, (255, 255, 255))
                        win.blit(l, (w_width / 2 - l.get_width() / 2 + 30, w_height / 2 - l.get_height() / 2))
                        next.draw(win, w_width / 2 - next.width / 2, w_height - 60)
                        update()
                        pygame.display.update()
                endScreen()
                play = False
                start(curUsr)




