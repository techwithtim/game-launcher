#HEADER COMMENT, LOGIN SCRIPTS - TIM RUSCICA
# To use these simply import the module and call either
# - runLogin() #This will run the login window for exsisting users
# - runCreate() #This will run the registartion window for new users
import os
from tkinter import *
from tkinter import messagebox
import random
import boto3
import json
import time
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime
import os


currentUser = ''


import hashlib,uuid

class register(object):
    @staticmethod
    def hash_password(password):
        salt = str(uuid.uuid4().hex)
        return(hashlib.sha256(salt.encode() + str(password).encode()).hexdigest() + ':' + salt)
    @staticmethod
    def check_password(hashed_password, user_password):
        password, salt = hashed_password.split(':')
        return(password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest())


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

#Class for a login form, you must pass this a tkinter window, see above for example of tkinter window
class loginWindow(object):
    loop = False
    attempts = 0

    def __init__(self, master): #This will create a tkinter window for loggining in
        self.user = 0
        self.passw = 0
        top = self.top = Toplevel(master)

        top.geometry('345x265+830+400')
        top.title('Sign In')
        top.configure(background='#282828')
        top.overrideredirect(1)
        top.resizable(width=False, height=False)
        self.b = Button(top, text='X', command=self.xBtn, font=('freesansbold', 14), highlightthickness = 0, bd = 0)
        self.b.configure(background="#282828", foreground='#c8c8c8')
        self.b.grid(row=0, column=1, sticky=E)
        self.l = Label(top, text='SIGN IN', font=('freesansbold', 20), justify=CENTER)
        self.l.configure(background='#282828', foreground='#c8c8c8')
        self.l.grid(row=1,columnspan=2, sticky=W+E+N+S)
        self.l = Label(top, text=" USERNAME: ", font=('freesansbold', 15), justify=CENTER)
        self.l.configure(background='#282828', foreground='#c8c8c8')
        self.l.grid(row=2,column=0,pady=10, sticky=W+E+N+S)
        self.e1 = Entry(top, width=15, font=('freesansbold', 15))
        self.e1.configure(background="#3c3c3c", foreground='#c8c8c8')
        self.e1.grid(row=2,column=1, pady=10,padx=7, sticky=W+E+N+S)
        self.l = Label(top, text=" PASSWORD: ", font=('freesansbold', 15), justify=CENTER)
        self.l.configure(background='#282828', foreground='#c8c8c8')
        self.l.grid(row=3,column=0,padx=7,pady=10, sticky=W+E+N+S)
        self.e = Entry(top, show='*', width=15, font=('freesansbold', 15))
        self.e.configure(background="#3c3c3c", foreground='#c8c8c8')
        self.e.grid(row=3,column=1,padx=7,pady=10,sticky=W+E+N+S)
        self.b = Button(top, text='Don\'t have an account? Sign up here!', command=self.createAccount, font=('freesansbold', 11), highlightthickness = 0, bd = 0)
        self.b.configure(background="#282828", foreground='#c8c8c8')
        self.b.grid(row=4,columnspan=2,pady=5, sticky=W+E+N+S,padx=10)
        self.b = Button(top, text='SUBMIT', command=self.getValues, font=('freesansbold', 18))
        self.b.configure(background="#3c3c3c", foreground='#c8c8c8')
        self.b.grid(row=5,columnspan=2,pady=5, sticky=W+E+N+S,padx=30)
        self.top.bind('<Return>', self.getValues)

    def xBtn(self):
        self.top.destroy()
        window.deiconify()
        window.destroy()
        window.quit()
        raise SystemExit

    def createAccount(self):
        self.top.destroy()
        window.deiconify()
        window.destroy()
        window.quit()
        runCreate()

    #Once the submit button is clicked then this will be called
    def getValues(self, x=0):
        global currentUser
        self.user = self.e1.get() 
        self.passw = self.e.get()

        if self.user != '' and self.passw != '':
            if self.checkServer():
                self.code = 0
                if self.code != self.getCode():
                    d = myDialog(self.top)
                    self.top.wait_window(d.top1)
                    self.code = d.code
                    if self.code != self.getCode():
                        messagebox.showerror("Incorrect Code", 'This is not the correct code, please try again.')
                    else:
                        messagebox.showinfo("Success!", "You have succesfully validated your email. Please sign in by clicking submit to access your account.")

                        response = table.query(
                            KeyConditionExpression=Key('peopleid').eq(self.user)
                            )
                        
                        for i in response['Items']:
                            email = i['email']
                        
                        response = table.delete_item(
                            Key={
                                'peopleid': self.user
                            }   
                        )

                        response = table.put_item(
                            Item={
                                 'peopleid': self.user,
                                 'password': register.hash_password(self.passw),
                                 'email': email,
                                 'code': 0,
                                 'datetime':str(datetime.now()),
                                 'friends':[],
                                 'requests':[]
                             }
                         )

                else:
                    #messagebox.showinfo('Suucesful Login', 'This is to notify you of a succesful login')
                    currentUser = self.user
                    #Destroy the window once they sign in
                    self.top.destroy()
                    window.deiconify()
                    window.destroy()
                    window.quit()
                    
            else:
                messagebox.showerror('Invalid Form', 'There was an issue with the submitted form, username or password was incorrect')               
        else:
            messagebox.showerror('Invalid Form', 'There was an issue with the submitted form, username or password was incorrect')


    def checkServer(self):
        try:#See if username exsists
            response = table.get_item(
                Key={
                    'peopleid': self.user,
                    }
                )
        except ClientError as e:
            return False
        else: #Check if password is correct
            
            response = table.query(
            KeyConditionExpression=Key('peopleid').eq(self.user)
            )

            for i in response['Items']:
                if register.check_password(i['password'], self.passw):
                    return True
                else:
                    return False
                
    def getCode(self):
        response = table.query(
            KeyConditionExpression=Key('peopleid').eq(self.user)
            )

        for i in response['Items']:
            return i['code']
    
    

class registerWindow(object):
    def __init__(self, master):
        self.user = None
        self.passw = None
        self.email = None

        top = self.top = Toplevel(master)
        top.overrideredirect(1)
        top.geometry('375x360+830+400')
        self.b = Button(top, text='X', command=self.xBtn, font=('freesansbold', 14), highlightthickness = 0, bd = 0)
        self.b.configure(background="#282828", foreground='#c8c8c8')
        self.b.grid(row=0, column=1, sticky=E)
        top.title('Register')
        top.configure(background='#282828')
        top.resizable(width=False, height=False)
        self.l = Label(top, text='REGISTER', font=('freesansbold', 20), justify=CENTER)
        self.l.configure(background='#282828', foreground='#c8c8c8')
        self.l.grid(row=1,columnspan=2, sticky=W+E+N+S)
        self.l = Label(top, text=" USERNAME: ", font=('freesansbold', 15), justify=CENTER)
        self.l.configure(background='#282828', foreground='#c8c8c8')
        self.l.grid(row=2,column=0,pady=10, sticky=W+E+N+S)
        self.usr = Entry(top, width=15, font=('freesansbold', 15))
        self.usr.configure(background='#3c3c3c', foreground = '#c8c8c8')
        self.usr.grid(row=2,column=1, pady=10,padx=7, sticky=W+E+N+S)
        self.l = Label(top, text=" EMAIL ADRESS: ", font=('freesansbold', 15), justify=CENTER)
        self.l.configure(background='#282828', foreground='#c8c8c8')
        self.l.grid(row=3,column=0,pady=10, sticky=W+E+N+S)
        self.em = Entry(top, width=15, font=('freesansbold', 15))
        self.em.configure(background='#3c3c3c', foreground = '#c8c8c8')
        self.em.grid(row=3,column=1, pady=10, padx=7, sticky=W+E+N+S)
        self.l = Label(top, text=" PASSWORD: ", font=('freesansbold', 15), justify=CENTER)
        self.l.configure(background='#282828', foreground='#c8c8c8')
        self.l.grid(row=4,column=0,padx=7,pady=10, sticky=W+E+N+S)
        self.passWord = Entry(top, show='*', width=15, font=('freesansbold', 15))
        self.passWord.grid(row=4,column=1,padx=7,pady=10,sticky=W+E+N+S)
        self.passWord.configure(background='#3c3c3c', foreground = '#c8c8c8')
        self.l = Label(top, text=" RE-PASSWORD: ", font=('freesansbold', 15), justify=CENTER)
        self.l.configure(background='#282828', foreground='#c8c8c8')
        self.l.grid(row=5,column=0,padx=7,pady=10, sticky=W+E+N+S)
        self.passWord2 = Entry(top, show='*', width=15, font=('freesansbold', 15))
        self.passWord2.configure(background='#3c3c3c', foreground = '#c8c8c8')
        self.passWord2.grid(row=5,column=1,padx=7,pady=10,sticky=W+E+N+S)

        self.b = Button(top, text='Already have an account? Sign in here!', command=self.loginAccount, font=('freesansbold', 11), highlightthickness = 0, bd = 0)
        self.b.configure(background="#282828", foreground='#c8c8c8')
        self.b.grid(row=6,columnspan=2,pady=5, sticky=W+E+N+S,padx=10)

        self.b = Button(top, text='SUBMIT', command=self.submitForm, font=('freesansbold', 18))
        self.b.configure(background='#3c3c3c', foreground='#c8c8c8')
        self.b.grid(row=7,columnspan=2,pady=5, sticky=W+E+N+S,padx=30)
        self.top.bind('<Return>', self.submitForm)

    def xBtn(self):
        self.top.destroy()
        window.deiconify()
        window.destroy()
        window.quit()
        raise SystemExit
        
    def loginAccount(self):
        self.top.destroy()
        window.deiconify()
        window.destroy()
        window.quit()
        runLogin()

    @staticmethod
    def checkEmail(email):
        #Can be modified to make more advanced, just checks that we get some kind of valid email
        if email.count('@') == 1 and email.count('.') > 0:
            return True
        else:
            return False

    @staticmethod
    def generateCode():
        code = ''
        for x in range(6):
            r = random.randrange(0,10)
            code += str(r)
        return code


    def addToTable(self, code=0):
        global currentUser
        currentUser = self.user
        respons = table.put_item(
           Item={
                'peopleid': self.user,
                'password': register.hash_password(self.passw),
                'email': self.email,
                'code': 0, #change this to 'code' to set up email validation !!!!!!
                'datetime':str(datetime.now()),
                'friends':[self.user],
                'requests':[]
                }
        )
        tabl = session.Table('highscores')

        respons = tabl.put_item(
           Item={
                'peopleid': self.user,
                'quicktype': 0,
                'integerrecall':0,
                'golf':0
                }
        )
        
        tabl = session.Table('playtime')

        respons = tabl.put_item(
            Item={
                'peopleid': self.user,
                'quicktype':0,
                'integerrecall':0,
                'golf':0
                }
        )
        
        tabl = session.Table('games_played')

        respons = tabl.put_item(
            Item={
                'peopleid': self.user,
                'quicktype':0,
                'integerrecall':0,
                'golf':0
            }
        )

    def checkIfUsername(self, username):
        try:
            response = table.get_item(
            Key={
                'peopleid': username,
                }
            )
        
        except ClientError as e:
            print(e.response['Error']['Message'])
            return True
        else:
            try:
                item = response['Item']                

                return False
            except:
                return True
        
    def sendEmail(self, code):
        import smtplib
        try:
            TO = [self.email] # must be a list

            # Prepare actual message

            message = """
            Welcome to ______, thank you for registering for an account!
                
            
            Username: %s
            
            Your code is: %s
            
            If this code is not used within 24 hours your account will be deleted.
            
            If you have not recently registered for an account on ______ please ignore this message.
            """ % (self.user,code)

            # Send the mail

            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.ehlo()
            server.login('noReplyTimAndNick@gmail.com','TimandNick') #Uses a gmail i set up
            server.sendmail('noReplyTimAndNick@gmail.com', TO, message)
            server.quit()
        except:
            print('did not send')

    def submitForm(self, x=0):
        #Once they click submit
        pass1 = self.passWord.get()
        pass2 = self.passWord2.get()
        self.user = self.usr.get()
        self.email = self.em.get()

        if self.user.count(' ') == 0:

            if self.checkIfUsername(self.user):

                if pass1 == pass2 and self.user != '' and self.checkEmail(self.email) and pass1 != '':
                    #if self.user not taken and if self.email not taken
                    self.passw = pass1
                    theCode = self.generateCode() # Generate a code to use to verify email
                    #We need to save this code to the cloud to the users account as they will have to type it in when they try to sign in
                    
                    #messagebox.showinfo('Account Created', "Please check your email as a validation code has been sent. You will have to type this in before you can sign in.")
                    messagebox.showinfo('Account Created', "Please login to your account in the next window.")

                    #Send validation email
                    #self.sendEmail(theCode) - Currently not working on school computers
                    
                    #Create Account here
                    currentUser = self.user
                    #-------------------
                    self.addToTable(theCode)
                    
                    self.top.destroy()
                    window.deiconify()
                    window.destroy()
                    window.quit()
                    runLogin()
                else:
                    messagebox.showerror('Incomplete Form', 'There was an issue with the submitted form, please ensure \n that you have completed all the boxes and that your passwords match.')
            else:
                messagebox.showerror('Username Taken', 'Sorry, that username is already taken. Please try another.')
        else:
            messagebox.showerror('Invalid Username', 'Your username cannot contain any spaces!')


class myDialog:
    def __init__(self, parent):
        self.code = 0
        top1 = self.top1 = Toplevel(parent)
        top1.title('Enter Code')
        top1.resizable(width=False, height=False)
        l = Label(top1, text='Please Enter Code Here', font=('Courier', 14), justify=CENTER)
        l.grid(columnspan=2, sticky=W+E+N+S)
        l = Label(top1, font=('Courier', 11), justify=CENTER)
        l.grid(row=1,columnspan=2,pady=10, sticky=W+E+N+S)
        self.cod = Entry(top1, width=20)
        self.cod.grid(row=1,column=1, pady=10,padx=7, sticky=W+E+N+S)
        b = Button(top1, text='Submit', command=self.onclick, font=('Courier', 12))
        b.grid(row=2,columnspan=2,pady=5, sticky=W+E+N+S,padx=20)

    def onclick(self):
        var = self.cod.get()
        self.top1.destroy()
        self.code = var

#Initialization function for module, declared global variables and logs into database
def init():
    global table, session, window
    session = boto3.resource('dynamodb',
    aws_access_key_id='AKIAIOPUXE2QS7QN2MMQ',
    aws_secret_access_key='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',
    region_name="ca-central-1"
    )
    table = session.Table('people')
    
    window = Tk()
    window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel())
    window.withdraw()
    window.title('Tim and Nick')


#Call these functions from main module to run the login form and the new account form
def runLogin():
    init()
    win = loginWindow(window)
    mainloop()

    return currentUser


def runCreate():
    init()
    win = registerWindow(window)
    mainloop()

    return currentUser

# For debugging
def printTable():
    print('-----------------------------')
    response = table.scan()
    li = []
    for i in response['Items']:
        print(i)
