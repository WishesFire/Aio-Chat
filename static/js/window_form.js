$(document).ready(function (){
    $('#red-button').click(function (event) {
        event.preventDefault()
        var numItems = $('.room').length;
        if (numItems === 5) {
            $('#DialogWindow').dialog({
                draggable: false,
                resizable: false,
                modal: true,
                width: 100,
                height: 100,
                button: {
                    "OK": function () {
                        this.dialog('close');
                    }
                }
            });
        }
        else {
            $('#my_overlay').fadeIn(297, function () {
            $('#myModal')
                .css('display', 'block')
                .animate({opacity: 1}, 198);
        });
        }
    });
    $('#close, #my_overlay').click(function () {
        $('#myModal').animate({opacity: 0}, 198,
            function () {
            $(this).css('display', 'none');
            $('#my_overlay').fadeOut(297);
        });
    });
});
