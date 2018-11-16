import pygame
import os
import tkinter as tk
from tkinter import messagebox
import sys, os.path
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

pygame.init()
win = pygame.display.set_mode((1080, 600))
title = pygame.image.load(os.path.join('img', 'title.png'))
back = pygame.image.load(os.path.join('img', 'back.png'))
course = pygame.image.load(os.path.join('img', 'course1.png'))
course1 = pygame.transform.scale(course, (200, 200))

font = pygame.font.SysFont('comicsansms', 24)

buttons = [[1080/2 - course1.get_width()/2, 260, course1.get_width(), course1.get_height(), 'Grassy Land']]
shopButton = []
ballObjects = []
surfaces = []
curUsr = ''

session = boto3.resource('dynamodb',
                             aws_access_key_id='AKIAIOPUXE2QS7QN2MMQ',
                             aws_secret_access_key='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',
                             region_name="ca-central-1"
                             )
table = session.Table('highscores')

import sys, os.path
leader_dir = (os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
leader_dir = os.path.abspath(os.path.join(leader_dir, '..'))
sys.path.append(leader_dir)
import leaderboard
from leaderboard import Leaderboard

def getBest():
    #Use dynamodb here to get prev best
    try:
        response = table.get_item(
            Key={
                'peopleid':curUsr
            }
        )
        best = response['Item']['golf']
    except:
        best = 'None'
        
    return str(best)


def getCoins():
    return 0


def getBallColor():
    global ballObjects
    for balls in ballObjects:
        if balls.equipped == True:
            return balls.color
    return None


def mainScreen(usr, hover=False):
    global shopButton, title, curUsr
    curUsr = usr
    surf = pygame.Surface((1080, 600))
    w = title.get_width()
    h = title.get_height()
    surf.blit(back, (0,0))
    surf.blit(title, ((1080/2 - (w/2)), 50))
    # For Shop Button
    '''
    if hover == True:S
        text = font.render('Ball Shop', 1,(0, 0, 0))
    else:
        text = font.render('Ball Shop', 1, (51, 51, 153))
    surf.blit(text, (960, 12))
    shopButton = text.get_rect()
    shopButton[0] = 960
    shopButton[1] = 12'''
    # For course Button
    i = buttons[0]
    surf.blit(course1, (i[0], i[1]))
    text = font.render(i[4], 1, (51,51,153))
    surf.blit(text, (i[0] + ((i[3] - text.get_width())/2), i[1] + i[3] + 10))
    text = font.render('Best: ' + getBest(), 1, (51, 51, 153))
    surf.blit(text, (i[0] + ((i[3] - text.get_width())/2), i[1] + i[3] + 40))
    #text = font.render('Coins: ' + getCoins(), 1, (51,51,153))
    #surf.blit(text, (10, 10))
    
    #draw leaderboard

    globalTable = Leaderboard(curUsr, 'golf', 'global', surf, 300, 380, 90, 200)
    friendTable = Leaderboard(curUsr, 'golf', 'friend', surf, 300, 380, 680, 200)
    globalTable.draw((0,0,0))
    friendTable.draw((0,0,0))
    
    win.blit(surf, (0,0))
    pygame.display.update()


def mouseOver(larger=False):
    global course1
    if larger:
        buttons[0][0] = 415
        buttons[0][1] = 220
        buttons[0][2] = 250
        buttons[0][3] = 250
        course1 = pygame.transform.scale(course, (250, 250))
    else:
        buttons[0][1] = 240
        buttons[0][0] = 440
        buttons[0][2] = 200
        buttons[0][3] = 200
        course1 = pygame.transform.scale(course, (200, 200))
    mainScreen(curUsr)


def shopClick(pos):
    global shopButton
    pass


def click(pos):
    for i in buttons:
        if pos[0] > i[0] and pos[0] < i[0] + i[2]:
            if pos[1] > i[1] and pos[1] < i[1] + i[3]:
                return i[4]
                break
    return None
