const send_event = 'message_send';
const connected_event = 'new_connection';
const receive_event = 'broadcast_message';

var currentURL = document.domain + ':' + location.port + window.location.pathname;
var socket = io.connect('http://' + document.domain + ':' + location.port);


function sendMessage() {
    var contentDiv = document.getElementById("contentInput");
    var content = contentDiv.value;
    var userId = getCookie('userId');
    if (userId != undefined && content !== '') {
        let chatId = getChatIdFromURL();
        socket.emit(send_event, {chat_id: chatId, userId: userId, content: content});
        contentDiv.value = '';
        contentDiv.focus();
    }
}


// Dynamic UI.
function displayNameHTML(user) {
    let displayName = '';
    let colour = 'secondary';
    if (user == null) {
        displayName = 'server';
    } else {
        displayName = user.display_name;
        colour = user.colour;
    }
    let fromText = document.createElement("strong")
    fromText.innerHTML = displayName;
    fromText.classList.add("text-" + colour);
    return fromText
}

function displayMessage(message) {
    const messageDiv = document.createElement("li");
    messageDiv.classList.add("list-group-item");
    messageDiv.setAttribute("data-bs-toggle", "tooltip");
    messageDiv.setAttribute("data-bs-placement", "top");
    messageDiv.setAttribute("title", "sent at: " + message.sent_at );
    messageDiv.appendChild(displayNameHTML(message.sent_by));
    messageDiv.innerHTML += ": " + message.content;
    document.getElementById("messageBoard").appendChild(messageDiv);
}

function scrollToBottom() {
    var myDiv = document.getElementById("messageBoard");
    myDiv.scrollTop = myDiv.scrollHeight;
}

function copyToClipboard(elementId) {
    var copyText = document.getElementById(elementId);
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    console.log(copyText.value);
}


// Response callback functions.
function displayMessages(data) {
    for (var message in data.messages) {
        displayMessage(data.messages[message]);
    }
    scrollToBottom();
}

function leaveResponse(data) {
    deleteCookie('userId');
    deleteCookie('displayName');
    window.location.reload();
}


// API calls.
function getMessages() {
    apiPost('get_messages', {chat_id: getChatIdFromURL(), limit: 100}, displayMessages);
}

function leave() {
    apiPost('leave', {chat_id: getChatIdFromURL()}, leaveResponse);
}


// Event handlers.
socket.on(receive_event, function(message) {
    displayMessage(message);
    scrollToBottom();
});

document.getElementById("contentInput").addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    sendMessage();
  }
});

window.onload = function(){
    getMessages();
    document.getElementById("contentInput").focus();
    document.getElementById("returnLink").value = currentURL+'?u='+getCookie('userId');
    document.getElementById("inviteLink").value = currentURL+'?i=NotImplementedYet';
};