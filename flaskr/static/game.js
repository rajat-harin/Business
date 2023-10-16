
var playerLocation = [0, 0, 0, 0]
var playerName = ''
var playersState = {}
var newPlayersState = {}
$(document).ready(function(){
    playerName = $("#playerName").text()
  
});
var socket = io.connect();
socket.on("connect", () => {
    console.log('connected!')
    socket.emit('joined', {});
});

socket.on("disconnect", () => {
    console.log('disconnected!')
});

socket.on('status', (data) => {
    $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
    $('#chat').scrollTop($('#chat')[0].scrollHeight);
});

socket.on("diceRolled", (data) => {
    $("#Dice").text(data.number)
});
socket.on("setPlayers", (data) => {
    console.log("setting Players!");
    $("#b0").html(``)
    playersState = data.players
    newPlayersState = data.players
    for (player in data.players) {
        $("#b" + data.players[player].location)
            .append(`<img id="${player}" class="avatar" src = "/static/${data.players[player].avatar}" />`)
        // if (Object.hasOwnProperty.call(object, key)) {
        //     const element = object[key];

        // }
    };
});
socket.on("playerMove", (data) => {
    console.log("moving player!")
    updateBoard(playersState, data.players)
});
function rollDice() {
    $("#Dice").text("Rolling...")
    socket.emit("diceRolling", { player: playerName, location: playerLocation[0] });
};

function updateBoard(playersState, newPlayersState) {
    // update board based on current state of players object
    console.log("checking Player state difference!")
    console.log(playersState);
    console.log(newPlayersState);
    for(player in playersState) {
        if(playersState[player].location != newPlayersState[player].location) {
            updateLocation(player, playersState[player].location, newPlayersState[player].location)
            playersState[player].location = newPlayersState[player].location
        }
    }
}

function updateLocation(player, source, target) {
    //update location of player avatar
    console.log("updating Location!");
    $("#b" + source + `>#${player}`).detach().prependTo("#b" + target);
}

function finishTurn() {
    $("#Dice").text("finishing...")
    socket.emit("finishTurn", { player: playerName, location: playerLocation[0] });
}
