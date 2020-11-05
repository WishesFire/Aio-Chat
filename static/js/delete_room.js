$(document).ready(function (){
    $('.delete-red-button').click(function () {
        Send_to_server($(this).parents('.room').children('.room-text').text())
        $(this).closest('.room').remove();
    });
});

function Send_to_server (room_name) {
    $.ajax ({
        url: '/rooms',
        method: 'POST',
        data: {text: room_name},
    })
}