document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.getElementById("theme-toggle");
    const themeImage = document.getElementById("themeImage");

    toggle.addEventListener("change", function() {
        if (toggle.checked) {
            themeImage.src = "/static/main/img/themedark.svg";
        } else {
            themeImage.src = "/static/main/img/themelight.svg";
        }
    });
});