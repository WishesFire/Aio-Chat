var block = document.getElementById("mess_form");
const Secret_key = ''
block.scrollTop = block.scrollHeight;

try{
    var socket = new WebSocket('ws://' + window.location.host + WS_URL);
}
catch(err){
    var socket = new WebSocket('wss://' + window.location.host + WS_URL);
}

socket.binaryType = 'arraybuffer';

var  msg_template = `
        <div class="container" id="message">
           <p>{text}</p>
           <span class="name-right">{user}</span>
        </div>`,
    msg_photo_template = `
        <div class="container" id="message">
           <img class="size-photo" src="{text}" />
           <span class="name-right">{user}</span>
        </div>`,
    msg_audio_template = `
        <div class="container" id="message">
           <audio controls src="{text}">
                Your browser does not support the
                <code>audio</code> element.
            </audio>
           <span class="name-right">{user}</span>
        </div>`,
    $messagesContainer = $('#mess_form');


function showMessage(message) {
    var data = jQuery.parseJSON(message.data);
    console.log(data)

    if (data.user && data.text && data.info) {
        var msg = msg_template
            .replace('{user}', data.user)
            .replace('{text}', data.text)
        console.log(data.info)
        var indexes = data.info.slice(-1)
        if (indexes === '@') {
            var data_text = data.info.slice(0, 44)
        }
        else {
            var data_text = data.info.slice(11)
        }

        localStorage.setItem('publicKey', data_text);
    }

    else if (data.user && data.text) {
        var msg = msg_template
            .replace('{user}', data.user)
            .replace('{text}', data.text)

    }

    else if (data.image) {
        var msg = msg_photo_template
            .replace('{user}', data.user)
            .replace('{text}', data.image)
    }

    else if (data.audio) {
        var msg = msg_audio_template
            .replace('{user}', data.user)
            .replace('{text}', data.audio)
    }


    else if (data.not_command) {
        console.log(data.not_command)
        $('#myOverlay').fadeIn(297, function (){
            $('#modalWindow').css('display', 'block').animate({opacity: 1}, 198);
        });

        $('#modalWindow_close, #myOverlay').click(function (){
            $('#modalWindow').animate({opacity: 0}, 198, function (){
                $(this).css('display', 'none');
                $('#myOverlay').fadeOut(297);
            })

        })
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
        var data = document.querySelector('input[name="chat-picture"]').files[0];

        if ($message === '') {
            createPhotoFile(data)
        }

        else if (data === undefined){
            // Encrypt
            var data_message = $message.val()
            const cipher_key = localStorage.getItem('publicKey')
            console.log(cipher_key)

            socket.send(encryptMessage(data_message, cipher_key));
            $message.val('').focus();
        }

        else if ($message !== '' && data !== '') {
            createPhotoFile(data)
        }
    });

    function encryptMessage(msg, key) {
        var secret = new fernet.Secret(key);
        var token = new fernet.Token({secret: secret})
        var mess_token = token.encode(msg)
        return mess_token
    }

    function createPhotoFile(data){
        console.log(data.size)

        var reader = new FileReader();
        reader.onload = function (evt){
            var element = data.name + ' ' + evt.target.result
            socket.send(element);
        };
        reader.readAsDataURL(data);

    }

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