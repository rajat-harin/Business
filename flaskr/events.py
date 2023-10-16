import random
from flask import Blueprint, session
from flask_socketio import (emit, join_room, leave_room)
from . import socketio

bp = Blueprint('event', __name__)

players = dict()
#player = {'name': '', 'room':'', 'location': 0, 'balance': 0, 'avatar' : '', turn: 0}
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
        counter += 1

    join_room(room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)
    emit('setPlayers',{'players':players, 'currentTurn': 0}, room=room)

@socketio.on('diceRolling')
def diceRolling(data):
    room = session.get('room')
    number = random.randrange(1,13)
    print(data)
    emit('playerMove',{'sourceLocation':data['location'], 'targetLocation':(data['location']+number)%40},room=room)
    emit('diceRolled',{'number':number},room=room)

def checkTurn(playerTurn):
    if playerTurn == currentTurn :
        return True
    return False
