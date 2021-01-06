$(document).ready(function(){
    $(".dropdown").click(function(){
        $(this).find(".dropdown-menu").slideToggle("fast");
    });

    $('.inviter').click(function (){
        var room_name = $(this).text()
        Send_to_server_invite($(this).parents('.container').children('.hidden-text').text(), room_name);
    })
});

$(document).on("click", function(event){
    var $trigger = $(".dropdown");
    if($trigger !== event.target && !$trigger.has(event.target).length){
        $(".dropdown-menu").slideUp("fast");
    }
});

function Send_to_server_invite(whom_to_send, room_name) {
    $.ajax ({
        url: '/',
        method: 'POST',
        data: {'whom_to_send': whom_to_send, 'room_name': room_name},
    })
}