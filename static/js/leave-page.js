window.onbeforeunload = function() {
  return "Are you sure? You leave the queue"
};

window.onunload = function() {
   	$.ajax({
        url: '/companion',
        method: 'POST',
        data: {'status': 'leave'},
    })
}