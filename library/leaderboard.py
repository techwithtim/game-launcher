#HEADER COMMENT FOR LEADERBOARD CLASS BY TIM RUSCICA
# This class is used to display the leaderboard tables you see
# in the games and in the launcher.It has two main types of leaderboards
# and two variations of those types. Type 1 is the friend leaderboard which
# shows only the users friends. Type 2, the global leaderboard shows the top users
# for the given game. For each of these types you can have a three column table or
# a 5 column grid. The three column grid shows (Rank,User,Score), while the 5 column
# table shows (Rank, User, Score, Time Played, Games Played)

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import decimal
import pygame

pygame.init()

session = boto3.resource('dynamodb',
                         aws_access_key_id='AWS ACCESS KEY',
                         aws_secret_access_key='AWS SECRET KEY',
                         region_name="ca-central-1"
                         )


# Main abstract class (parent)
# This class is capable of creating a grid containing different rows and different columns, bases upon those arguments it
# will automatically alter the pixel size. To display the grid simply call ____.drawGrid(). To find the item in the grid
# that was clicked on call ____.clicked().
class grid(object):
    def __init__(self, win, width, height, cols, rows, showGrid=False, startx=0, starty=0, bg=(255, 255, 255)):
        self.font = pygame.font.SysFont('freesansbold', 15)
        self.width = width
        self.height = height
        self.cols = cols
        self.rows = rows
        self.bg = bg
        self.startx = startx
        self.starty = starty
        self.showGrid = showGrid  # If we should show the black outline
        self.grid = None
        self.lineThick = 1
        self.screen = win
        pygame.display.update()

    def getGrid(self):
        return self.grid  # Return the grid list

    def draw(self, lineColor=(0, 0, 0)):  # This will draw the lines to create the grid, this is done so by simply creating overlapping boxes
        x = self.startx
        y = self.starty

        for i in range(self.cols):
            y = self.starty + self.height
            if i > 0:
                x += round(self.width / self.cols)
            for j in range(self.rows):
                y -= round(self.height / self.rows)
                pygame.draw.rect(self.screen, lineColor, (x, y, round(self.width / self.cols), round(self.height / self.rows)), 1)

    def clicked(self, pos):  # Return the position in the grid that user clicked on
        try:
            t = pos[0]
            w = pos[1]
            g1 = int((t - self.startx) / self.grid[0][0].w)
            g2 = int((w - self.starty) / self.grid[0][0].h)

            self.selected = self.grid[g1][g2]

            return self.grid[g1][g2]

        except IndexError:  # If we run into an index error that means that the user did not click on a position in the grid
            return False


# This class creates basic grid menus that can contain text.
# It uses all of the methods from the parent grid class and is a concrete class
# The setText method takes a list of strings and displays them in the grid.
class menu(grid):
    def setText(self, textList, color=(255,255,255)):  # The textList argument passed must be equal to the number of spots in the grid

        self.grid = []
        # Create textObjects in the grid
        for i in range(self.rows):
            self.grid.append([])
            for j in range(self.cols):
                self.grid[i].append(
                    textObject(j, i, self.width, self.height, self.cols, self.rows, self.startx, self.starty, 30, color))

        # Set the text for each of those objects
        c = 0
        h = 0
        for spots in self.getGrid():
            for s in spots:
                if h == 0:
                    s.fontsize = 35
                if h == len(self.getGrid())- 1:
                    s.color = (255,0,0)
                s.showText(self.screen, textList[c])
                c += 1
            h += 1


# This class is responsible for displaying text and these objects are added into the grid.
# The showText() method will display the text while the show() method will draw a square showing thr grid.
class textObject():
    def __init__(self, i, j, width, height, cols, rows, startx=0, starty=0, fontsize=30, color=(255,255,255)):
        self.fontsize = fontsize
        self.font = pygame.font.SysFont('freesansbold', fontsize)
        self.color = color
        self.col = i  # The column of the current instance in the grid
        self.row = j  # The row of the current instance in the grid
        self.rows = rows  # Total amount of rows
        self.cols = cols  # Total amount of columns
        self.w = width / cols
        self.h = height / rows
        self.x = self.col * self.w + startx
        self.y = self.row * self.h + starty
        self.text = ''

    def showText(self, win, txt):  # This will render and draw the text on the screen
        self.text = txt

        text = self.font.render(self.text, 1, self.color)
        while text.get_width() > self.w - 5:
            self.fontsize -= 1
            self.font = pygame.font.SysFont('freesansbold', self.fontsize)
            text = self.font.render(self.text, 1, self.color)
        win.blit(text, (self.x + (self.w / 2 - text.get_width() / 2), self.y + (
                self.h / 2 - text.get_height() / 2)))  # This will make sure the text is center in the screen.

    def show(self, screen, color, st, outline=False):  # Draws a square displaying the area in the grid
        pygame.draw.rect(screen, color, (self.x, self.y, self.w, self.h), st)


#This leaderboard class will find the top scores of each users freinds or the top global scores for a given game
class Leaderboard(object):
    def __init__(self, usr, game, type, win , width, height, x, y, extra=False):
        #The extra parameter will add an extra two columns, (play time and games played)
        #game parameter is to allow us to determine what game leaderboard we need to get
        #type is either freind or global
        #example use: quickTypeHighscores = leaderboard('quicktype', 'freind', win, 400, 300, 45, 45)
        self.win = win
        self.usr = usr
        self.game = game
        self.type  = type
        self.width = width
        self.height = height
        self.showGrid = True
        self.textColor = (255,255,255)
        self.cols = 3
        self.rows = 5 # this will show top 5, if you want to make it show more change this number by calling the changeRows method
        self.x = x
        self.y = y
        self.extra = extra
        if self.extra:
            self.cols = 5
        self.text = []
        self.setup()

    def changeRows(self, rows):
        self.rows  = rows

    #Do not call this method from outside the class
    def setup(self):
        if self.type == 'global':
            table = session.Table('highscores')
            response = table.scan()

            topScore = []
            topName = []
            allScores = []
            for i in response['Items']:
                try:
                    score = i[self.game]
                    if score != 0:
                        allScores.append(score)
                        name = i['peopleid']
                        if len(topScore) < self.rows:
                            topScore.append(score)
                            topName.append(name)
                        else:
                            if not(self.game == 'quicktype'):
                                if score > min(topScore):
                                    ind = topScore.index(min(topScore))
                                    topScore[ind] = score
                                    topName[ind] = name
                            else:
                                if score < max(topScore):
                                    ind = topScore.index(max(topScore))
                                    topScore[ind] = score
                                    topName[ind] = name
                except:
                    print('no highscore exsists')

        else:
            topScore = []
            topName = []
            allScores=[]
            table = session.Table('people')
            response = table.query(
                KeyConditionExpression=Key('peopleid').eq(self.usr)
            )

            li = []
            for i in response['Items']:
                li = i['friends']

            for x in li:
                name = x
                table = session.Table('highscores')
                response = table.query(
                    KeyConditionExpression=Key('peopleid').eq(x)
                )

                for i in response['Items']:
                    score = i[self.game]
                if score != 0:
                    allScores.append(score)
                    if len(topScore) < self.rows:
                        topScore.append(score)
                        topName.append(name)
                    else:
                        if not (self.game == 'quicktype'):
                            if score > min(topScore):
                                ind = topScore.index(min(topScore))
                                topScore[ind] = score
                                topName[ind] = name
                        else:
                            if score < max(topScore):
                                ind = topScore.index(max(topScore))
                                topScore[ind] = score
                                topName[ind] = name

        self.grid = menu(self.win, self.width, self.height, self.cols, self.rows+2, self.showGrid, self.x, self.y)
        self.grid.bg = self.textColor
        if not(self.extra):
            nList = ['Rank', 'User', 'Score']
        else:
            nList = ['Rank', 'User', 'Score', 'Time Played(m)', 'Games Played']
            
        #Bubble sort the names
        if self.game == 'quicktype':
            for passnum in range(len(topScore) - 1, 0, -1):
                for i in range(passnum):
                    if topScore[i] > topScore[i + 1]:
                        temp = topScore[i]
                        topScore[i] = topScore[i + 1]
                        topScore[i + 1] = temp
                        temp = topName[i]
                        topName[i] = topName[i + 1]
                        topName[i + 1] = temp
        else:
            for passnum in range(len(topScore) - 1, 0, -1):
                for i in range(passnum):
                    if topScore[i] < topScore[i + 1]:
                        temp = topScore[i]
                        topScore[i] = topScore[i + 1]
                        topScore[i + 1] = temp
                        temp = topName[i]
                        topName[i] = topName[i + 1]
                        topName[i + 1] = temp
                        
        if not(self.extra):
            for x in range(len(topScore)):
                nList.append(str(x + 1))
                nList.append(str(topName[x]))
                nList.append(str(topScore[x]))
        else:
            for x in range(len(topScore)):
                nList.append(str(x + 1))
                nList.append(str(topName[x]))
                nList.append(str(topScore[x]))
                table = session.Table('playtime')
                response = table.get_item(
                    Key={
                        'peopleid':topName[x]
                    }
                )
                nList.append(str(round(response['Item'][self.game],1)))

                table = session.Table('games_played')
                response = table.get_item(
                    Key={
                        'peopleid':topName[x]
                    }
                )
                nList.append(str(response['Item'][self.game]))
        if self.extra:
            while len(nList) < (self.rows + 1) * self.cols:
                nList.append('')
                nList.append('')
                nList.append('')
                nList.append('')
                nList.append('')
        else:
            while len(nList) < (self.rows + 1) * self.cols:
                nList.append('')
                nList.append('')
                nList.append('')

        table = session.Table('highscores')
        try:
            response = table.get_item(
                Key={
                    'peopleid':self.usr
                }
            )
        except:
            print('error')
            pass
        
        if self.game == 'quicktype':
            rank = sorted(allScores)
        else:
            rank = sorted(allScores)
            rank = rank[-1::-1]
            
        if response['Item'][self.game] != 0:
            nList.append(str(rank.index(response['Item'][self.game])+1))
            nList.append(self.usr)
            nList.append(str(response['Item'][self.game]))
            table = session.Table('playtime')
            response = table.get_item(
                Key={
                    'peopleid':self.usr
                }
            )
            nList.append(str(round(response['Item'][self.game],1)))

            table = session.Table('games_played')
            response = table.get_item(
                Key={
                    'peopleid':self.usr
                }
            )
            nList.append(str(response['Item'][self.game]))
        else:
            nList.append('-')
            nList.append(self.usr)
            nList.append('None')
        self.text = nList

    #Call this method to display the leaderboard on the screen
    def draw(self, line=(255,255,255), title=False):
        if title:
            font = pygame.font.SysFont('freesansbold', 25)
            if self.type == 'global':
                label = font.render('Global Leaderboard',1,line)
            else:
                label = font.render('Friend Leaderboard', 1, line)
            self.grid.screen.blit(label, (self.x + self.width/2 - label.get_width()/2,self.y - 30 + (15 - label.get_height()/2 )))
            pygame.draw.rect(self.grid.screen,line, (self.x, self.y -30,self.width, 30), 1)

        self.grid.startx,self.grid.starty = self.x,self.y
        self.grid.draw(line)
        if self.extra and len(self.text) < self.rows * (self.cols+2):
            for x in range(self.rows * (self.cols+2) - len(self.text)):
                self.text.append('None')
        self.grid.setText(self.text, line)

    def update(self):
        self.setup()
    
    #call this method to change the font
    def font(self, font, size):
        self.grid.font(font, size)

#Function to add time played to amazon ws table
def addTimePlayed(usr, game, ntime):
    global session, window
    ntime = round(ntime/60,1)
    table = session.Table('playtime')
    response = table.get_item(
        Key={
            'peopleid': usr
        }
    )
    time = response['Item'][game]
    response = table.update_item(
        Key={
            'peopleid':usr
        },
        UpdateExpression="set " + game + " = :r",
        ExpressionAttributeValues={
            ':r': decimal.Decimal(str(time + decimal.Decimal(ntime))),
        }
    )

#Function to add games played to amazon ws table
def addGamesPlayed(usr, game):
    global session, window
    table = session.Table('games_played')
    response = table.get_item(
        Key={
            'peopleid': usr
        }
    )
    games = response['Item'][game]
    response = table.update_item(
        Key={
            'peopleid':usr
        },
        UpdateExpression="set " + game + " = :r",
        ExpressionAttributeValues={
            ':r': decimal.Decimal(str(games + 1)),
        }
    )

#Function to add highscore to amazon ws table
def addHighscore(usr, game, score):
    global table, session, window
    table = session.Table('highscores')
    response = table.update_item(
        Key={
            'peopleid': usr,
        },
        UpdateExpression="set " + game + " = :r",
        ExpressionAttributeValues={
            ':r': decimal.Decimal(str(score)),
        }
    )
