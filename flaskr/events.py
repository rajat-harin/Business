import json
import os
import random
from flask import Blueprint, session
from flask_socketio import (emit, join_room, leave_room)
from . import socketio

bp = Blueprint('event', __name__)

players = dict()
#player = {'name': '', 'room':'', 'location': 0, 'balance': 0, 'avatar' : '', turn: 0, turnPlayed: False, ownedProperties: []}
rooms = dict()
#room = {'name': '', 'maxPlayers':0, 'currentPlayers': 0, 'currentTurn': -1, ownedProperties: [], bankBalance: 20580}
currentTurn = -1
properties = list()

auctionDetails = dict()

@socketio.on('joined')
def joined(data):
    """
    event handler for player joining the room. initialize players and hold the game till required players gathered in room.
    """
    #get data for the session
    name = session.get('name') 
    room = session.get('room')
    maxPlayers = session.get('maxPlayers')

    # check if room exists, if not create the room
    if room not in rooms:
        rooms[room] = {}
        rooms[room]['name'] = room
        rooms[room]['maxPlayers'] = int(maxPlayers)
        rooms[room]['currentPlayers'] = 0
        rooms[room]['currentTurn'] = -1
        rooms[room]['ownedProperties'] = []
        rooms[room]['bankBalance'] = 20580
        rooms[room]['auctionDetails'] = {'owner':'bank', 'bid':0,'status':'init', 'playerList': []}
       
        json_data = open(os.path.join(os.path.realpath(os.path.dirname(__file__)), "static", "business.json"))
        properties.extend(json.load(json_data)['properties'])
        for property in properties:
            if property['group'] != 'Special':
                rooms[room]['ownedProperties'].append({'ownership':False, 'owner': 'Bank'})
            else:
                rooms[room]['ownedProperties'].append({'ownership':True, 'owner': 'Bank'})

    if name not in players:
        player = {'name': name, 'room': room, 'location': 0, 'balance': 1500}
        players[name] = player
        rooms[room]['bankBalance'] -= 1500
        rooms[room]['currentPlayers'] += 1
    counter = 0

    # sets turn number for each player based on the sequence of them joing the room
    # can be made shorter and not repetetive with dict length
    for player in players:
        if counter > 3:
            break
        players[player]['avatar'] = 'avatar'+ str(counter) +'.png'
        players[player]['turn'] = counter
        players[player]['turnPlayed'] = False
        counter += 1

    # add player to room and set room state
    join_room(room)
    if rooms[room]['maxPlayers'] == rooms[room]['currentPlayers']:
        rooms[room]['currentTurn'] = 0
        emit('status', {'msg': session.get('room') + ': Required number of players are met!<br> Start the game...(Turns based on time of entry)'}, room=room)
    else :
        emit('status', {'msg': session.get('room') + ': waiting for required number of players!'}, room=room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)
    emit('setPlayers',{'players':players,'rooms' : rooms[room], 'currentTurn': 0}, room=room)
    #print(rooms)

@socketio.on('left')
def left(data):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    rooms[room]['currentPlayers'] -= 1
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

@socketio.on('surrender')
def surrender(data):
    """Sent by clients when they surrender the game.
    A status message is broadcast to all people in the room and reset the room data."""
    player = session.get('name')
    room = session.get('room')
    leave_room(room)
    rooms[room]['currentPlayers'] -= 1
    rooms[room]['maxPlayers'] -= 1
    emit('status', {'msg': player + ' has surrendered the game.'}, room=room)

@socketio.on("getBoardData")
def getBoardData(data):
    """Sent by clients for setting up the board.
    """
    room = session.get('room')
    json_data = open(os.path.join(os.path.realpath(os.path.dirname(__file__)), "static", "business.json"))
    data = json.load(json_data)

    emit('populateBoard',{'properties':data['properties']}, room = room)

@socketio.on('diceRolling')
def diceRolling(data):
    room = session.get('room')
    print(rooms[room]['currentTurn'])

    if players[data['player']]['turn'] == rooms[room]['currentTurn'] and not players[data['player']]['turnPlayed']:
        players[data['player']]['turnPlayed'] = True
        roll = random.randrange(1,13)
        if (players[data['player']]['location'] + roll) // 40 == 1:
            players[data['player']]['location'] = (players[data['player']]['location'] + roll) % 40
            updateBalance('bank', data['player'], room, amount=200)
        else:
            players[data['player']]['location'] = (players[data['player']]['location'] + roll) % 40
        #if players[data['player']]['location'] == 

        emit('playerMove',{'players':players, 'rooms':rooms[room]},room=room)
        emit('diceRolled',{'number':roll},room=room)

        """
        check what action to take based on ownership
        """
        if not rooms[room]['ownedProperties'][players[data['player']]['location']]['ownership'] and rooms[room]['ownedProperties'][players[data['player']]['location']]['owner'] == 'Bank':
            print("landed on unowned tile","sending puchase options")
            emit('propertyOptions',{'playerName': session.get('name'), 'players':players, 'rooms':rooms[room],'action': 'firstPurchase'}, room = room)
        else:
            print("landed on owned tile","calculating expense")
            checkAction(data['player'], room, roll)
    else:
        emit('status', {'msg': session.get('name') + ' dont be greedy. wait for your turn'}, room=room)

@socketio.on('finishTurn')
def finishTurn(data):
    room = session.get('room')
    expense = 0
    if players[data['player']]['turn'] == rooms[room]['currentTurn'] and players[data['player']]['turnPlayed']:
        players[data['player']]['turnPlayed'] = False
        rooms[room]['currentTurn'] = ( rooms[room]['currentTurn'] + 1) % rooms[room]['maxPlayers'] #chage to players in room
        #updateBalance(data['player'], expense)
    print(rooms[room]['currentTurn'])


def updateBalance(payer, receiver, room, amount):
    #update balace based on player activity
    if payer == 'bank':
        players[receiver]['balance'] += amount
        rooms[room]['bankBalance'] -= amount
    elif receiver == 'bank':
        players[payer]['balance'] -= amount
        rooms[room]['bankBalance'] += amount
    else:
        players[receiver]['balance'] += amount
        players[payer]['balance'] -= amount

def checkAction(player, room, roll):
    pass
@socketio.on('buyProperty')
def buyProperty(data):
    room = session.get('room')
    rooms[room]['ownedProperties'][players[data['player']]['location']]['ownership'] = False
    rooms[room]['ownedProperties'][players[data['player']]['location']]['owner'] = data['player']
    updateBalance(data['player'], 'bank', room, amount = properties[players[data['player']]['location']]['price'])
    emit('purchaseComplete',{'playerName': session.get('name'), 'players':players, 'rooms':rooms[room],'action': 'firstPurchase'}, room = room)

@socketio.on('auctionProperty')
def auctionProperty(data):
    room = session.get('room')
    if rooms[room]['auctionDetails']['status'] == 'init' or rooms[room]['auctionDetails']['status'] == 'finished':
        #auctionDetails = {'owner':'bank', 'bid':0,'status':'started', 'playerList': []}
        rooms[room]['auctionDetails'] = {'owner':'bank', 'bid':0,'status':'started', 'playerList': list(players.keys())}
    print(rooms[room]['auctionDetails'])
    print(data)
    if len(rooms[room]['auctionDetails']['playerList']) > 1 :
        rooms[room]['auctionDetails'] = 'InProgress'
        #bid = data.bidAmount
        emit('auction',{'playerName': session.get('name'), 'players':players, 'rooms':rooms[room],'action': 'aution','auctionDetails':rooms[room]['auctionDetails']}, room = room)
    else: 
        rooms[room]['auctionDetails'] = 'finished'
        rooms[room]['auctionDetails']['bid']
        updateBalance(rooms[room]['auctionDetails']['playerList'][0], 'bank', room, amount = rooms[room]['auctionDetails']['bid'])
        emit('purchaseComplete',{'playerName': session.get('name'), 'players':players, 'rooms':rooms[room],'action': 'firstPurchase'}, room = room)

@socketio.on('auctionRaise')
def auctionProperty(data):
    room = session.get('room')
    rooms[room]['auctionDetails']['bid'] = max(rooms[room]['auctionDetails']['bid'], data.bidAmount)
    #bid = data.bidAmount

@socketio.on('auctionFold')
def auctionProperty(data):
    room = session.get('room')
    player = session.get('name')
    if player in auctionDetails['playerList']:
        auctionDetails['playerList'].remove(player)