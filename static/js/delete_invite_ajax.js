$(document).ready(function (){
    $('.join_invite').click(function (){
        var whom_to_send = $(this).parents('.invites').children('.whom_to_send').text()
        Send_to_server_whom_invite(whom_to_send)
    });
});

function delete_all_invites(){
    $.ajax({
        url: '/messages',
        method: 'POST',
        data: {'whom_to_send': '1-1'},
        success: function (){
            window.location.reload()
        }
    })
}

function Send_to_server_whom_invite(whom_to_send){
    $.ajax({
        url: '/messages',
        method: 'POST',
        data: {'whom_to_send': whom_to_send}
    })
}