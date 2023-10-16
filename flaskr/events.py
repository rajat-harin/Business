import random
from flask import Blueprint, session
from flask_socketio import (emit, join_room, leave_room)
from . import socketio

bp = Blueprint('event', __name__)

players = dict()
#player = {'name': '', 'room':'', 'location': 0, 'balance': 0, 'avatar' : '', turn: 0, turnPlayed: False}
rooms = list()
currentTurn = 0

@socketio.on('joined')
def joined(data):
    name = session.get('name') 
    room = session.get('room')
    maxPlayers = session.get('maxPlayers')
    if room not in rooms:
        rooms.append((room,maxPlayers))
    player = {'name': name, 'room': room, 'location': 0, 'balance': 0}
    players[name] = player
    counter = 0
    for player in players:
        if counter > 3:
            break
        players[player]['avatar'] = 'avatar'+ str(counter) +'.png'
        players[player]['turn'] = counter
        players[player]['turnPlayed'] = False
        counter += 1

    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)
    emit('setPlayers',{'players':players, 'currentTurn': 0}, room=room)

@socketio.on('diceRolling')
def diceRolling(data):
    room = session.get('room')
    print(currentTurn)

    if players[data['player']]['turn'] == currentTurn and not players[data['player']]['turnPlayed']:
        players[data['player']]['turnPlayed'] = True
        roll = random.randrange(1,13)
        if players[data['player']]['location'] // 40 == 1:
            players[data['player']]['location'] = (players[data['player']]['location'] + roll) % 40
            updateBalance(data['player'], expense=0)
        else:
            players[data['player']]['location'] = (players[data['player']]['location'] + roll) % 40
        emit('playerMove',{'players':players,'sourceLocation':data['location'], 'targetLocation':(data['location']+roll)%40},room=room)
        emit('diceRolled',{'number':roll},room=room)
    else:
        emit('status', {'msg': session.get('name') + ' dont be greedy. wait for your turn'}, room=room)

@socketio.on('finishTurn')
def finishTurn(data):
    room = session.get('room')
    global currentTurn
    expense = 0
    if players[data['player']]['turn'] == currentTurn and players[data['player']]['turnPlayed']:
        players[data['player']]['turnPlayed'] = False
        currentTurn = (currentTurn + 1) % 2 #chage to players in room
        updateBalance(data['player'], expense)
    print(currentTurn)

def checkTurn(playerTurn):
    if playerTurn == currentTurn :
        return True
    return False

def updateBalance(player, expense):
    #update balace based on player activity
    pass