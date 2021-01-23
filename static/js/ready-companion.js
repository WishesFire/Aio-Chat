$('#find-companion').click(function (){
    $.ajax({
        url: '/companion',
        method: 'POST',
        data: {'status': 'go'},
    })
});