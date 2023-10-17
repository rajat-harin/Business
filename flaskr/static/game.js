
var playerLocation = [0, 0, 0, 0]
var playerName = ''
var playersState = {}
var newPlayersState = {}
var properties = null
$(document).ready(() => {
    playerName = $("#playerName").text()
});
var socket = io.connect();

// connect to socket
socket.on("connect", () => {
    console.log('connected!');
    socket.emit('joined', {});
    socket.emit('getBoardData',{});
});

// disconnect from socket
socket.on("disconnect", () => {
    console.log('disconnected!')
});

// get status messages from server
socket.on('status', (data) => {
    $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
    $('#chat').scrollTop($('#chat')[0].scrollHeight);
});

//update board based on properties board data
socket.on('populateBoard', (data) => {
    if(properties == null){
        properties = data.properties
        generateBoard(properties)
    }
});

// update dice based on rolled number
socket.on("diceRolled", (data) => {
    $("#Dice").text(data.number)
});

//initial setting of player avatars on board
socket.on("setPlayers", (data) => {
    console.log("setting Players!");
    $("#b0>.playerSpace").html(``)
    playersState = data.players
    newPlayersState = data.players
    for (player in data.players) {
        $(`#${player}`).remove()
        $("#b" + data.players[player].location + ">.playerSpace")
            .append(`<img id="${player}" class="avatar" src = "/static/${data.players[player].avatar}" />`)
    };
});

// player movement based on the rolled number
socket.on("playerMove", (data) => {
    console.log("moving player!")
    updateBoard(playersState, data.players)
});

//util functions for socket events

function updateBoard(playersState, newPlayersState) {
    // update board based on current state of players object
    console.log("checking Player state difference!")
    console.log(playersState);
    console.log(newPlayersState);
    for (player in playersState) {
        if (playersState[player].location != newPlayersState[player].location) {
            updateLocation(player, playersState[player].location, newPlayersState[player].location)
            playersState[player].location = newPlayersState[player].location
        }
    }
}

function updateLocation(player, source, target) {
    //update location of player avatar
    console.log("updating Location!");
    $("#b" + source + `>.playerSpace>#${player}`).detach().prependTo("#b" + target+">.playerSpace");
}

//util function for dom objects

//onclick event for dice roll button
function rollDice() {
    $("#Dice").text("Rolling...")
    socket.emit("diceRolling", { player: playerName, location: playerLocation[0] });
};

//onclick event for dice roll button
function finishTurn() {
    $("#Dice").text("finishing...")
    socket.emit("finishTurn", { player: playerName, location: playerLocation[0] });
}

function propertyCard(property) {

}

//board related functions
//generate bord based on passed data
function generateBoard(properties) {
    properties.forEach(property => {
        if (property.titledeed == "TRUE") {
            $("#b" + property.position).html(
                `
                <div class="spaceDetails">
                    <div class="propertyGroup ${property.group}"></div>
                    <div class="propertyName">${property.name.replaceAll(/\s/g,"<br>")}</div>
                    <div class="propertyPrice">${property.price}</div>
                </div>
                <div class="playerSpace"></div>
                `
            );
        }
        else {
            if (property.titledeed == "FALSE") {
                $("#b" + property.position).html(
                    `
                    <div class="spaceDetails">
                        <div class="propertyGroup ${property.group}"></div>
                        <div class="propertyName">${property.name.replaceAll(/\s/g,"<br>")}</div>
                        <div class="propertyPrice">${property.price}</div>
                    </div>
                    <div class="playerSpace"></div>
                    `
                );
            }
        }
    });
}