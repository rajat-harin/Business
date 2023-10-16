
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
socket.on("diceRolled", (data) => {
    $("#Dice").text(data.number)
});
socket.on("setPlayers", (data) => {
    console.log("setting Players!");
    $("#b0").html(``)
    newPlayersState = data.players
    for (player in data.players) {
        $("#b" + data.players[player].location)
            .append(`<img id="player1" class="avatar" src = "/static/${data.players[player].avatar}" />`)
        // if (Object.hasOwnProperty.call(object, key)) {
        //     const element = object[key];

        // }
    };
});
socket.on("playerMove", (data) => {
    console.log("moving Player!");
    $("#b" + data.sourceLocation + ">#player1").detach().prependTo("#b" + data.targetLocation);
    playerLocation[0] = data.targetLocation
});
function rollDice() {
    $("#Dice").text("Rolling...")
    socket.emit("diceRolling", { player: playerName, location: playerLocation[0] });
};

function updateBoard(playersState, newPlayersState) {
    // update board based on current state of players object
}
