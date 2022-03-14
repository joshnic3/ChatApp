function getChatIdFromURL() {
    return window.location.pathname.split("/").pop();
}

function getCookie(cookieName) {
  let cookie = {};
  document.cookie.split(';').forEach(function(el) {
    let [key,value] = el.split('=');
    cookie[key.trim()] = value;
  })
  return cookie[cookieName];
}

function deleteCookie(cookieName) {
    document.cookie = cookieName + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

function apiPost(endpoint, data, responseFunction) {
    endpoint = "/api/" + endpoint;
    fetch(endpoint, {
        method: "POST",
        headers: {'Accept': 'application/json', 'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(response => response.json())
    .then(data => {
        responseFunction(data);
    });
}