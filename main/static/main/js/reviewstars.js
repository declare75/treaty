document.addEventListener('DOMContentLoaded', function () {
    const stars = document.querySelectorAll('.star');
    const radios = document.querySelectorAll('input[name="rating"]');

    stars.forEach((star, index) => {
        star.addEventListener('mouseenter', function () {
            // При наведении выделяем все звезды до текущей
            stars.forEach((s, i) => {
                s.classList.toggle('selected', i <= index);
            });
        });
        star.addEventListener('mouseleave', function () {
            // При уходе с наведения восстанавливаем состояние
            stars.forEach((s) => {
                s.classList.remove('selected');
            });
        });
    });

    radios.forEach((radio, index) => {
        radio.addEventListener('change', function () {
            // Когда радио выбран, выделяем все звезды до выбранной
            stars.forEach((star, i) => {
                star.classList.toggle('selected', i <= index);
            });
        });
    });
});

