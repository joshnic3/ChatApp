// Response handlers.
function connectedResponse(data) {
    console.log(data);
    if ("error" in data) {
        alert(data.error);
    } else {
        response = data.accepted;
        document.cookie = "userId=" + response.user_id.toString();
        document.cookie = "displayName=" + response.display_name;
        location.replace("/" + response.chat_id.toString());
    }
}


//Event handlers.
function joinButtonSubmit() {
    let displayName = document.getElementById("displayNameInput").value;
    if (displayName !== '') {
        let chatId = getChatIdFromURL();
        let data = {'display_name': displayName, 'chat_id': chatId};
        apiPost('new_user', data, connectedResponse);
    }
}

var contentDiv = document.getElementById("displayNameInput");
contentDiv.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    joinButtonSubmit();
  }
});

document.getElementById("displayNameInput").focus();