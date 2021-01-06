$('#submit').on('click', function () {

    $(this).prop('disabled', true);
        setTimeout(function () {
            $(this).prop('disabled', false);
        }.bind(this), 5e3);

});