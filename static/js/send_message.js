var messagecontainer = document.getElementById('message');
var interval = null;
var sendForm = document.getElementById('chat-form');
var messageInput = document.getElementById('chat-text');

// Create Connection
const socket = new WebSocket('ws://localhost:8000');

// Connection Opened
socket.addEventListener('open', function (event) {
    console.log('Connect Ws Server')
});

socket.addEventListener('close', function (event) {
    console.log('Close connect Ws Server')
});

socket.addEventListener('message', function (event) {
    console.log('Message from server ', event.data)
});

const sendMsg = () => {
    socket.send('Hello from My')
}