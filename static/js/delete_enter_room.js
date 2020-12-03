$(document).ready(function (){
    $('.delete-red-button').click(function () {
        Send_to_server_delete($(this).parents('.room').children('.room-text').text(), csrfToken)
        $(this).closest('.room').remove();
    });
    $('.random-color-div').click(function () {
        Send_to_server_enter($(this).parents('.room').children('.room-text').text(), csrfToken)
    })
});

function Send_to_server_delete (room_name, csrf_token) {
    $.ajax ({
        url: '/rooms',
        method: 'POST',
        headers: {'X-CSRF-Token': csrf_token},
        data: {'name-room': room_name, 'password': '#'},
    });
}

function Send_to_server_enter (room_name, csrf_token) {
    $.ajax ({
        url: '/rooms',
        method: 'POST',
        headers: {'X-CSRF-Token': csrf_token},
        data: {'name-room': room_name, 'password': '1'},
    });
}