document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.getElementById("notification-toggle");
    const themeImage = document.getElementById("notificationImage");

    toggle.addEventListener("change", function() {
        if (toggle.checked) {
            themeImage.src = "/static/main/img/notificationon.svg";
        } else {
            themeImage.src = "/static/main/img/notificationoff.svg";
        }
    });
});