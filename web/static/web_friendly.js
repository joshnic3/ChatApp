// Hacky resize for mobile.
if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
    chatDiv = document.getElementById("rootContainer");
    chatDiv.classList.remove("w-50");
    chatDiv.classList.add("w-100");
    var scrollableNavBar = document.getElementById("scrollableNavBar");
    scrollableNavBar.scrollLeft = scrollableNavBar.scrollWidth;
}

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

