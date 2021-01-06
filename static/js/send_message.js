var block = document.getElementById("mess_form");
block.scrollTop = block.scrollHeight;

try{
    var socket = new WebSocket('ws://' + window.location.host + '/ws');
}
catch(err){
    var socket = new WebSocket('wss://' + window.location.host + '/ws');
}

socket.binaryType = 'arraybuffer';

var  msg_template = `
        <div class="container" id="message">
           <p>{text}</p>
           <p class="hidden-text">{user}</p>
              <ul>
                 <li class="dropdown">
                     <a class="invite-click" href="#">{user}</a>
                     <ul class="dropdown-menu">
                          {nothing}
                          {nothing}
                          {nothing}
                          {nothing}
                          {nothing}
                     </ul>
                 </li>
              </ul>
        </div>`,
    msg_photo_template = `
        <div class="container" id="message">
           <img class="size-photo" src="{text}" />
           <ul>
                 <li class="dropdown">
                     <a class="invite-click" href="#">{user}</a>
                     <ul class="dropdown-menu">
                          {nothing}
                          {nothing}
                          {nothing}
                          {nothing}
                          {nothing}
                     </ul>
                 </li>
              </ul>
        </div>`,
    msg_audio_template = `
        <div class="container" id="message">
           <audio controls src="{text}">
                Your browser does not support the
                <code>audio</code> element.
            </audio>
           <ul>
                 <li class="dropdown">
                     <a class="invite-click" href="#">{user}</a>
                     <ul class="dropdown-menu">
                          {nothing}
                          {nothing}
                          {nothing}
                          {nothing}
                          {nothing}
                     </ul>
                 </li>
              </ul>
        </div>`,
    $messagesContainer = $('#mess_form');


function showMessage(message) {
    console.log(message);
    var data = jQuery.parseJSON(message.data);
    if (data.user && data.text) {
        var msg = msg_template
            .replace('{user}', data.user)
            .replace('{text}', data.text)
            .replace('{user}', data.user)

        if (data.name_rooms !== '') {
            var count_room = data.name_rooms.length;
            var al = data.name_rooms
            var msg = Room_generate(msg, al, count_room)
        }

    }
    else if (data.image) {
        var msg = msg_photo_template
            .replace('{user}', data.user)
            .replace('{text}', data.image)
            .replace('{user}', data.user)

        if (data.name_rooms !== '') {
            var count_room = data.name_rooms.length;
            var al = data.name_rooms
            var msg = Room_generate(msg, al, count_room)
        }
    }

    else if (data.audio) {
        var msg = msg_audio_template
            .replace('{user}', data.user)
            .replace('{text}', data.audio)
            .replace('{user}', data.user)

        if (data.name_rooms !== '') {
            var count_room = data.name_rooms.length;
            var al = data.name_rooms
            var msg = Room_generate(msg, al, count_room)
        }
    }

    else if (data.connection) {
        console.log(data.connection)
        $('#count_online').text(data.connection);
        return;
    }

    else if (data.disconnect) {
        console.log(data.disconnect)
        $('#count_online').text(data.disconnect);
        return;
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

    function Room_generate (a, al, count_room) {
        if (count_room === 1) {
            var b = a
                    .replace('{nothing}', '<li><button class="inviter">' + al[0] + '</button></li>')
        }

        else if (count_room === 2) {
            var b = a
                    .replace('{nothing}', '<li><button class="inviter">' + al[0] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[1] + '</button></li>')
        }

        else if (count_room === 3) {
            var b = a
                    .replace('{nothing}', '<li><button class="inviter">' + al[0] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[1] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[2] + '</button></li>')
        }

        else if (count_room === 4) {
            var b = a
                    .replace('{nothing}', '<li><button class="inviter">' + al[0] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[1] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[2] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[3] + '</button></li>')
        }

        else if (count_room === 5) {
            var b = a
                    .replace('{nothing}', '<li><button class="inviter">' + al[0] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[1] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[2] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[3] + '</button></li>')
                    .replace('{nothing}', '<li><button class="inviter">' + al[4] + '</button></li>')
        }

        return b
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
            socket.send($message.val());
            $message.val('').focus();
        }
        else if ($message !== '' && data !== '') {
            createPhotoFile(data)
        }
    });

    function createPhotoFile(data){
        console.log(data.size)
        var file_size = data.size

        if (file_size < 2000000) {
            var reader = new FileReader();
            reader.onload = function (evt){
            var element = data.name + ' ' + evt.target.result
            socket.send(element);
            };
            reader.readAsDataURL(data);
        }
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