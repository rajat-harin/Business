
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
    socket.emit('getBoardData', {});
    socket.emit('joined', {});
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
    if (properties == null) {
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
    console.log(data.rooms);
    console.log(data.players);
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
    console.log(data.rooms);
    updateBoard(playersState, data.players)
});

//Property options, puchase, sell , auction
socket.on("propertyOptions", (data) => {
    $('#finishTurn').prop("disabled", true);
    $('#roll').prop("disabled", true);
    console.log(data.playerName + "landed on unowned property!")
    console.log(data.rooms);
    if (data.playerName == playerName) {
        $('<div></div>').appendTo('body')
            .html('<div><h6>' + "want to purchase? <b>" + properties[data.propertyLoc].name + '</b> for <b>' + properties[data.players[playerName].location].price + '?</b></h6></div>')
            .dialog({
                modal: true,
                title: 'confirm?',
                zIndex: 10000,
                autoOpen: true,
                width: 'auto',
                resizable: false,
                buttons: {
                    Yes: function () {
                        // $(obj).removeAttr('onclick');                                
                        // $(obj).parents('.Parent').remove();
                        socket.emit('buyProperty', { player: playerName, propertyLoc: data.propertyLoc });
                        $(this).remove();
                    },
                    No: function () {
                        socket.emit('auctionProperty', { player: playerName, propertyLoc: data.propertyLoc });
                        $(this).remove();
                    }
                },
                close: function (event, ui) {
                    socket.emit('auctionProperty', { player: playerName, propertyLoc: data.propertyLoc });
                    $(this).remove();
                }
            });
    }
});

socket.on("auction", (data) => {
    clearInterval(countDown);
    $('#finishTurn').prop("disabled", true);
    $('#roll').prop("disabled", true);
    //console.log(data.playerName + "aution started")
    //console.log(data);
    if (data.auctionDetails.status == 'started') {
        alert("Auction Started!",);
        var sec = 10
        var countDown = setInterval(() => {
            sec -= 1;
            $('#timer').html(`${sec} seconds`)
            if (sec == 0) {
                auctionFold();
            }
        }, 1000)
    }
    if (data.auctionDetails.playerList.includes(playerName)) {
        $('.popEvent').html(`<h3>Event Name : Auction <i id="timer"><i></h3>` +
            `<br>` + `<h4>Current Highest Bid (by ${data.auctionDetails.bidder}): ${data.auctionDetails.bid}</h4>` +
            `<br>` + `<label for = "bidAmount">Bid : </lable><input id="bidAmount" name="bidAmount" type="number"/><button type = "button" onclick = auctionRaise()> Raise </button>` +
            `<button type = "button" onclick = auctionFold()> Fold </button>`);
        $('#bidAmount').focus();
        sec = 10
    }
    else{
        $('.popEvent').html(`<h3>Event Name : Auction <i id="timer"><i></h3>` +
            `<br>` + `<h4>Current Bid : ${data.auctionDetails.bid}</h4>`);
    }

    // if (data.auctionDetails.playerList.includes(playerName)) {
    //     console.log("inside");
    //     $('<div id="auction"></div>').appendTo('body')
    //         .html('<div><h6 id="autionDetails">' + 
    //         properties[data.players[playerName].location].name  + 
    //         ", want to bid? <b>"+ '</b> current bid <b>' + 
    //         data.auctionDetails.bid + 
    //         '?</b></h6><h3><label for = "bidAmount">Bid : </lable><input id="bidAmount" name="bidAmount" type="number"/></h3></div>')
    //         .dialog({
    //             modal: true,
    //             title: 'confirm?',
    //             zIndex: 10000,
    //             autoOpen: true,
    //             width: 'auto',
    //             resizable: false,
    //             buttons: {
    //                 Raise: function () {
    //                     // $(obj).removeAttr('onclick');                                
    //                     // $(obj).parents('.Parent').remove();

    //                     //$('body').append('<h1>Confirm Dialog Result: <i>Raise</i></h1>');
    //                     let bid = parseInt($('#bidAmount').val() || '0' )
    //                     socket.emit('auctionRaise', {player: playerName, bidAmount: bid});
    //                     $(this).dialog("close");

    //                 },
    //                 Fold: function () {
    //                     //$('body').append('<h1>Confirm Dialog Result: <i>Fold</i></h1>');
    //                     socket.emit('auctionFold', {player: playerName, bidAmount: bid});
    //                     $(this).dialog("close");

    //                 }
    //             },
    //             close: function (event, ui) {
    //                 socket.emit('auctionFold', {player: playerName, bidAmount: bid});
    //                 $(this).remove(); 
    //             }
    //         });
    // }
});

socket.on("purchaseComplete", (data) => {
    $('.popEvent').html('')
    alert(`Property Sold to ${data.bidder} for ${data.bid}`);
    $('#finishTurn').removeAttr("disabled");
    $('#roll').removeAttr("disabled");
});

//util functions for socket events

function updateBoard(playersState, newPlayersState) {
    // update board based on current state of players object
    console.log("checking Player state difference!")
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
    $("#b" + source + `>.playerSpace>#${player}`).detach().prependTo("#b" + target + ">.playerSpace");
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
            $("#b" + property.position + ">.spaceDetails").html(
                `
                
                    <div class="propertyGroup ${property.group}"></div>
                    <div class="propertyName">${property.name.replaceAll(/\s/g, "<br>")}</div>
                    <div class="propertyPrice">${property.price}</div>
                
                `
            );
        }
        else {
            if (property.titledeed == "FALSE") {
                $("#b" + property.position + ">.spaceDetails").html(
                    `
                    
                        <div class="propertyGroup ${property.group}"></div>
                        <div class="propertyName">${property.name.replaceAll(/\s/g, "<br>")}</div>
                        <div class="propertyPrice">${property.price}</div>
                   
                    
                    `
                );
            }
        }
    });
}

function surrender() {
    $('<div></div>').appendTo('body')
        .html('<div><h6>' + "Are you sure?" + '?</h6></div>')
        .dialog({
            modal: true,
            title: 'confirm?',
            zIndex: 10000,
            autoOpen: true,
            width: 'auto',
            resizable: false,
            buttons: {
                Yes: function () {
                    // $(obj).removeAttr('onclick');                                
                    // $(obj).parents('.Parent').remove();

                    $('body').append('<h1>Confirm Dialog Result: <i>Yes</i></h1>');
                    socket.emit('surrender', {});
                    $(this).dialog("close");
                },
                No: function () {
                    $('body').append('<h1>Confirm Dialog Result: <i>No</i></h1>');
                    $(this).dialog("close");
                }
            },
            close: function (event, ui) {
                $(this).remove();
            }
        });
};

const auctionRaise = function () {
    // $(obj).removeAttr('onclick');                                
    // $(obj).parents('.Parent').remove();

    //$('body').append('<h1>Confirm Dialog Result: <i>Raise</i></h1>');
    let bid = parseInt($('#bidAmount').val() || '0')
    socket.emit('auctionRaise', { player: playerName, bidAmount: bid });

};
const auctionFold = function () {
    //$('body').append('<h1>Confirm Dialog Result: <i>Fold</i></h1>');
    let bid = parseInt($('#bidAmount').val() || '0')
    socket.emit('auctionFold', { player: playerName, bidAmount: bid });

}