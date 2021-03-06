const send_event = 'message_send';
const receive_event = 'broadcast_message';
const join_event = 'join_room';
const leave_event = 'leave_room';

var currentURL = document.domain + ':' + location.port + window.location.pathname;
var socket = io.connect('http://' + document.domain + ':' + location.port);


function sendMessage() {
    var contentDiv = document.getElementById("contentInput");
    var content = contentDiv.value;
    var userId = getCookie('userId');
    if (userId != undefined && content !== '') {
        let chatId = getChatIdFromURL();
        // TODO Probs should only send to room?
        socket.emit(send_event, {chat_id: chatId, userId: userId, content: content});
        contentDiv.value = '';
        contentDiv.focus();
    }
}


// Dynamic UI.
function displayNameHTML(user) {
    let displayName = '';
    let colour = '#a1a1a1';
    if (user == null) {
        displayName = '~';
    } else {
        displayName = user.display_name;
        colour = user.colour;
    }
    let fromText = document.createElement("strong")
    fromText.innerHTML = displayName;
    fromText.style.color = colour;
    fromText.classList.add("pe-1");
    return fromText
}

function messageContextHTML(message) {
    let messageHTML =  message.content;
    if (message.sent_by == null) {
        messageHTML =  '<i>'+message.content+'</i>';
    }
    return messageHTML;
}

function displayMessage(message) {
    const messageDiv = document.createElement("li");
    messageDiv.classList.add("list-group-item");
    messageDiv.setAttribute("data-bs-toggle", "tooltip");
    messageDiv.setAttribute("data-bs-placement", "top");
    messageDiv.setAttribute("title", "sent at: " + message.sent_at);
    messageDiv.appendChild(displayNameHTML(message.sent_by));
    messageDiv.innerHTML += messageContextHTML(message);
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

function colourUpdate() {
    var colorPicker = document.getElementById("colorPicker");
    var saveColourButton = document.getElementById("saveColourButton");
    saveColourButton.innerHTML = 'apply ' + colorPicker.value;
//    saveColourButton.style.borderColor=colorPicker.value;
//    saveColourButton.style.backgroundColor=colorPicker.value;
    saveColourButton.disabled=false
}

function focusOnMessageInput() {
    if (! /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
        document.getElementById("contentInput").focus();
        console.log('focused');

    }
}


// Response callback functions.
function displayMessages(data) {
    for (var message in data.messages) {
        displayMessage(data.messages[message]);
    }
    document.getElementById("loadingImage").remove();
    scrollToBottom();
}

function leaveResponse(data) {
    deleteCookie('userId');
    deleteCookie('displayName');
    window.location.reload();
}

function generateInviteResponse(data) {
    document.getElementById("generateInviteButton").innerHTML = 'generate a new invite';
    inviteLink = document.getElementById("inviteLink");
    inviteLink.focus();
    inviteLink.value = 'http://'+currentURL+'?i='+data.accepted.key;
    inviteLink.disabled = false;

    copyToClipboard("inviteLink");

    inviteLinkForm = document.getElementById("inviteLinkForm");
    inviteLinkForm.classList.remove('d-none')
}


// API calls.
function saveColour() {
    var colorPicker = document.getElementById("colorPicker");
    apiPost('change_user_colour', {'chat_id': getChatIdFromURL(), 'colour': colorPicker.value}, console.log);
    location.reload();
}


function getMessages() {
    apiPost('get_messages', {chat_id: getChatIdFromURL(), limit: 100}, displayMessages);
}

function leave() {
    socket.emit(leave_event, {chat_id: getChatIdFromURL()});
    apiPost('leave', {chat_id: getChatIdFromURL()}, leaveResponse);
}

function generateInvite() {
    apiPost('invite', {chat_id: getChatIdFromURL()}, generateInviteResponse);
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
    focusOnMessageInput();
    document.getElementById("returnLink").value = 'http://'+currentURL+'?u='+getCookie('userId');
    socket.emit(join_event, {chat_id: getChatIdFromURL()});
};
