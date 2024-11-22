document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.getElementById("theme-toggle");
    const themeImage = document.getElementById("themeImage");
    const body = document.body;

    // Получаем сохраненную тему из localStorage
    const savedTheme = localStorage.getItem("theme");

    // Применяем сохраненную тему сразу, до рендера контента
    if (savedTheme === "dark") {
        body.classList.add("dark-theme");
        if (toggle) toggle.checked = true;  // Устанавливаем состояние переключателя
        if (themeImage) themeImage.src = "/static/main/img/themedark.svg";
    } else {
        body.classList.remove("dark-theme");
        if (themeImage) themeImage.src = "/static/main/img/themelight.svg";
    }

    // После того как тема загружена, показываем страницу
    body.classList.add("theme-loaded");

    // Слушаем изменение переключателя темы
    if (toggle) {
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
    }
});
