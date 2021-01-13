$('.size-photo').click(function (event) {
    var path = $(this).attr('src');
    $('body').append('<div class="my_overlay"></div>' +
                        '<div id="magnify">' +
                            '<img src="'+ path +'"><div id="close-popup"><i>' + '</i></div></div>');
    var css_style = $('#magnify')

    css_style.css({
        left: ($(document).width() - css_style.outerWidth()) / 2,
        top: ($(window).height() - css_style.outerHeight()) / 2
    })
    $('.my_overlay, #magnify').fadeIn('fast');
})

$('body').on('click', '#close-popup, .my_overlay', function(event) {
    event.preventDefault();
    $('.my_overlay, #magnify').fadeOut('fast', function() {
      $('#close-popup, #magnify, .my_overlay').remove();
    });
});