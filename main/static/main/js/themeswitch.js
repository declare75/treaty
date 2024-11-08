document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.getElementById("theme-toggle");
    const themeImage = document.getElementById("themeImage");
    const body = document.body;

    const savedTheme = localStorage.getItem("theme");
    console.log("Сохраненная тема:", savedTheme);

    if (savedTheme === "dark") {
        body.classList.add("dark-theme");
        toggle.checked = true;
        themeImage.src = "/static/main/img/themedark.svg";
    } else {
        body.classList.remove("dark-theme");
        themeImage.src = "/static/main/img/themelight.svg";
    }

    toggle.addEventListener("change", function() {
        if (toggle.checked) {
            body.classList.add("dark-theme");
            themeImage.src = "/static/main/img/themedark.svg";
            localStorage.setItem("theme", "dark");
        } else {
            body.classList.remove("dark-theme");
            themeImage.src = "/static/main/img/themelight.svg";
            localStorage.setItem("theme", "light");
        }
        console.log("Активная тема после переключения:", localStorage.getItem("theme"));
    });
});
