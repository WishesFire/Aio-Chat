var block = document.getElementById("mess_form");
block.scrollTop = block.scrollHeight;

try{
    var socket = new WebSocket('ws://' + window.location.host + '/ws');
}
catch(err){
    var socket = new WebSocket('wss://' + window.location.host + '/ws');
}

var  msg_template = `
        <div class="container" id="message">
           <p>{text}</p>
           <span class="name-right">{user}</span>
        </div>`,
    $messagesContainer = $('#mess_form');


function showMessage(message) {
    console.log(message);
    var data = jQuery.parseJSON(message.data);
    if (data.user) {
        var msg = msg_template
            .replace('{user}', data.user)
            .replace('{text}', data.text)

    }

    else if (data.connection) {
        console.log(data.connection)
        $('#count_online').text(data.connection);
        return;
    }

    $messagesContainer.append(msg);
    if ($('#prev_messages').is(':not(:checked)')){
        block.scrollTop = document.getElementById('mess_form').scrollHeight;
    }

}

$(document).ready(function(){
    $('#chat-form').on('submit', function (event) {
        event.preventDefault();
        var $message = $(event.target).find('textarea[name="chat-text"]');
        socket.send($message.val());
        $message.val('').focus();
    });

    socket.onopen = function (event) {
        console.log(event);
        console.log('Connection to server started');
    };

    socket.onclose = function (event) {
        console.log(event);
        if(event.wasClean){
            console.log('Clean connection end');
        } else {
            console.log('Connection broken');
        }
        window.location.assign('/');
    };

    socket.onerror = function (error) {
        console.log(error);
    };

    socket.onmessage = showMessage;
});