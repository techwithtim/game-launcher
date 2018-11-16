from .loading_screen import session_var,user_login
from configparser import ConfigParser
from boto3.dynamodb.conditions import Key, Attr

session = session_var
people_table = session.Table('people')

def get_players(query):
    response = people_table.scan()
    names = []
    for i in response['Items']:
        name = i['peopleid']
        if query in name.lower() and len(query) is not 0:
            names.append(name)
        elif len(query) is 0:
            names.append(name)
    if user_login in names: names.remove(user_login)
    return names

def get_table_data(data):
    names = []
    response = people_table.query(KeyConditionExpression=Key('peopleid').eq(user_login))
    for i in response['Items']: names = i[data]
    if user_login in names: names.remove(user_login)
    return names

def get_game_data(game,data_type,target_user):
    game_table = session.Table(data_type)
    response = game_table.query(KeyConditionExpression=Key('peopleid').eq(target_user))
    for i in response['Items']: names = i[game]
    return names

def get_chat_log(primary_user,secondary_user):
    chat_found = None
    chat_table = session.Table('chat_sessions')
    response = chat_table.scan()
    for i in response['Items']:
        name = i['users']
        if str(primary_user+','+secondary_user) == name or str(secondary_user+','+primary_user) == name:
            response2 = chat_table.query(KeyConditionExpression=Key('users').eq(name))
            for x in response2['Items']:
                chat_found = x['chat_log']
                return chat_found
    else:
        chat_found = create_chat_session(primary_user,secondary_user)

def create_chat_session(primary_user,secondary_user):
    chat_table = session.Table('chat_sessions')
    resposnse = chat_table.put_item(
           Item={
                'users': primary_user+','+secondary_user,
                'chat_log':[]
                }
        )
    return None

def get_launcher_settings():
    launcher_table = session.Table('launcher')
    playerofweek = ''
    news1=[]
    news2=[]
    news3=[]
    response = launcher_table.scan()
    names = []
    for i in response['Items']:
        playerofweek = i['playerofweek']
        news1 = i['news1']
        news2 = i['news2']
        news3 = i['news3']
    return playerofweek,news1,news2,news3


def send_message(primary_user,secondary_user,message_to_send):
    chat_table = session.Table('chat_sessions')
    response = chat_table.scan()
    final_name = ''
    for i in response['Items']:
        name = i['users']
        if str(primary_user+','+secondary_user) == name or str(secondary_user+','+primary_user) == name:
            final_name = name
    chat_to_edit = get_chat_log(primary_user,secondary_user)
    response = chat_table.put_item(
           Item={
                'users': final_name,
                'chat_log':chat_to_edit +[[[primary_user],[message_to_send]]]
                }
        )

def accept_friend_request(friend):
    response = people_table.get_item(
        Key={
            'peopleid': user_login
        }
    )
    nFriends = response['Item']['friends']
    nFriends.append(friend)
    
    response = people_table.update_item(
        Key={
            'peopleid':user_login
        },
        UpdateExpression="set " + 'friends' + " = :r",
        ExpressionAttributeValues={
            ':r': nFriends,
        }
    )

    response = people_table.get_item(
        Key={
            'peopleid': friend
        }
    )
    nFreinds = response['Item']['friends']
    nFreinds.append(user_login)
    
    response = people_table.update_item(
        Key={
            'peopleid':friend
        },
        UpdateExpression="set " + 'friends' + " = :r",
        ExpressionAttributeValues={
            ':r': nFreinds,
        }
    )

    #update requests

    decline_friend_request(friend)
    

def decline_friend_request(friend):
    response = people_table.get_item(
        Key={
            'peopleid': user_login
        }
    )
    oldRequests = response['Item']['requests']
    x = oldRequests.index(friend)
    del oldRequests[x]
    
    response = people_table.update_item(
        Key={
            'peopleid':user_login
        },
        UpdateExpression="set " + 'requests' + " = :r",
        ExpressionAttributeValues={
            ':r': oldRequests,
        }
    )
    

def send_friend_request(friend):
    response = people_table.get_item(
        Key={
            'peopleid': friend
            }
        )

    oldRequests = response['Item']['requests']
    oldFriends = response['Item']['friends']
    if user_login not in oldRequests and user_login not in oldFriends:
        response = people_table.get_item(
            Key={
                'peopleid': friend
            }
        )
        oldRequests = response['Item']['requests']
        oldRequests.append(user_login)
        
        response = people_table.update_item(
            Key={
                'peopleid':friend
            },
            UpdateExpression="set " + 'requests' + " = :r",
            ExpressionAttributeValues={
                ':r': oldRequests,
            }
        )

def remove_friend(friend):
    response = people_table.get_item(
        Key={
            'peopleid': user_login
        }
    )
    oldRequests = response['Item']['friends']
    x = oldRequests.index(friend)
    del oldRequests[x]
    
    response = people_table.update_item(
        Key={
            'peopleid':user_login
        },
        UpdateExpression="set " + 'friends' + " = :r",
        ExpressionAttributeValues={
            ':r': oldRequests,
        }
    )

    response = people_table.get_item(
        Key={
            'peopleid': friend
        }
    )
    oldRequests = response['Item']['friends']
    x = oldRequests.index(user_login)
    del oldRequests[x]
    
    response = people_table.update_item(
        Key={
            'peopleid':friend
        },
        UpdateExpression="set " + 'friends' + " = :r",
        ExpressionAttributeValues={
            ':r': oldRequests,
        }
    )
