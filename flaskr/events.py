import random
from flask import Blueprint, session
from flask_socketio import (emit, join_room, leave_room)
from . import socketio

bp = Blueprint('event', __name__)

players = dict()
#player = {'name': '', 'room':'', 'location': 0, 'balance': 0, 'avatar' : '', turn: 0, turnPlayed: False}
rooms = dict()
currentTurn = -1

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
        rooms[room]['maxPlayers'] = int(maxPlayers)
        rooms[room]['currentPlayers'] = 0
        rooms[room]['currentTurn'] = -1
    player = {'name': name, 'room': room, 'location': 0, 'balance': 0}
    players[name] = player
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
    rooms[room]['currentPlayers'] += 1
    if rooms[room]['maxPlayers'] == rooms[room]['currentPlayers']:
        rooms[room]['currentTurn'] = 0
        emit('status', {'msg': session.get('room') + ': Required number of players are met!<br> Start the game...(Turns based on time of entry)'}, room=room)
    else :
        emit('status', {'msg': session.get('room') + ': waiting for required number of players!'}, room=room)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)
    emit('setPlayers',{'players':players, 'currentTurn': 0}, room=room)
    print(rooms)

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
    room = session.get('room')
    leave_room(room)
    rooms[room]['currentPlayers'] -= 1
    rooms[room]['maxPlayers'] -= 1
    emit('status', {'msg': session.get('name') + ' has surrendered the game.'}, room=room)

@socketio.on('diceRolling')
def diceRolling(data):
    room = session.get('room')
    print(rooms[room]['currentTurn'])

    if players[data['player']]['turn'] == rooms[room]['currentTurn'] and not players[data['player']]['turnPlayed']:
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
    expense = 0
    if players[data['player']]['turn'] == rooms[room]['currentTurn'] and players[data['player']]['turnPlayed']:
        players[data['player']]['turnPlayed'] = False
        rooms[room]['currentTurn'] = ( rooms[room]['currentTurn'] + 1) % rooms[room]['maxPlayers'] #chage to players in room
        updateBalance(data['player'], expense)
    print(rooms[room]['currentTurn'])


def updateBalance(player, expense):
    #update balace based on player activity
    pass