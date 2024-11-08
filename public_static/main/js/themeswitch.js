document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.getElementById("theme-toggle");
    const themeImage = document.getElementById("themeImage");
    const editprofileImage = document.getElementById("editprofileImage");
    const logregOpenBtn = document.getElementById("logregOpenBtn");
    const body = document.body;

    // Проверка сохраненной темы при загрузке страницы
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        body.classList.add("dark-theme");
        console.log("Темная тема активирована при загрузке");
        toggle.checked = true;
        themeImage.src = "/static/main/img/themedark.svg";
        editprofileImage.src = "/static/main/img/editprofiledark.svg";
        logregOpenBtn.src = "/static/main/img/logregdark.svg"; // Меняем изображение на темное
        console.log("Кнопка логина сейчас указывает на: " + logregOpenBtn.src); // Логируем путь
    } else {
        console.log("Светлая тема активирована при загрузке");
        themeImage.src = "/static/main/img/themelight.svg";
        editprofileImage.src = "/static/main/img/editprofile.svg";
        logregOpenBtn.src = "/static/main/img/logreg.svg"; // Меняем изображение на светлое
        console.log("Кнопка логина сейчас указывает на: " + logregOpenBtn.src); // Логируем путь
    }

    // Слушатель переключения темы
    toggle.addEventListener("change", function() {
        if (toggle.checked) {
            console.log("Темная тема включена");
            body.classList.add("dark-theme");
            themeImage.src = "/static/main/img/themedark.svg";
            editprofileImage.src = "/static/main/img/editprofiledark.svg";
            logregOpenBtn.src = "/static/main/img/logregdark.svg"; // Меняем изображение на темное
            console.log("Кнопка логина сейчас указывает на: " + logregOpenBtn.src); // Логируем путь
            localStorage.setItem("theme", "dark");
        } else {
            console.log("Светлая тема включена");
            body.classList.remove("dark-theme");
            themeImage.src = "/static/main/img/themelight.svg";
            editprofileImage.src = "/static/main/img/editprofile.svg";
            logregOpenBtn.src = "/static/main/img/logreg.svg"; // Меняем изображение на светлое
            console.log("Кнопка логина сейчас указывает на: " + logregOpenBtn.src); // Логируем путь
            localStorage.setItem("theme", "light");
        }
    });
});
