
function sanitizeChatName(chatName) {
    // TODO muucccch more sanitizing
    // How much should be done server side?
    return chatNameInput.value.toLowerCase();
}


function dynamicForm() {
    let chatNameInput = document.getElementById("chatNameInput");
    let createChatButton = document.getElementById("createChatButton");
    let chatName = sanitizeChatName(chatNameInput.value)
    if (chatName.length > 1) {
        createChatButton.disabled = false;
    }
    createChatButton.innerHTML = "create " + chatName;
}

function newChatResponse(data) {
    console.log(data.accepted);
    let chatId = data.accepted.chat_id;
    window.location.href="/" + chatId;
}

function createChatClick() {
    let chatNameInput = document.getElementById("chatNameInput")
    let inviteOnlyCheck = document.getElementById("inviteOnlyCheck")
    let data = {
        'chat_name': sanitizeChatName(chatNameInput.value),
        'invite_only': inviteOnlyCheck.checked
    };
    apiPost('new_chat', data, newChatResponse);
}

window.onload = function(){
    document.getElementById("chatNameInput").focus();
};