document.querySelectorAll('.containerPrepods').forEach(container => {
    const stars = container.querySelectorAll('.star');
    const hiddenRatingInput = container.querySelector('input[name="rating"]');
    const reviewForm = container.querySelector('.review-form');
    const cancelButton = container.querySelector('.custom-btn-cancel');

    // Обработчик событий для выбора звезд
    stars.forEach(star => {
        star.addEventListener('mouseenter', () => {
            const rating = star.getAttribute('data-value');
            highlightStars(container, rating);
        });

        star.addEventListener('mouseleave', () => {
            const currentRating = hiddenRatingInput.value;
            highlightStars(container, currentRating);
        });

        star.addEventListener('click', () => {
            const rating = star.getAttribute('data-value');
            hiddenRatingInput.value = rating;
            reviewForm.classList.add('show'); // Появление формы отзыва с анимацией
        });
    });

    // Обработчик кнопки "Отмена"
    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            reviewForm.classList.remove('show'); // Скрытие формы отзыва с анимацией
            hiddenRatingInput.value = ''; // Очистить значение рейтинга
            stars.forEach(star => star.classList.remove('selected')); // Удаляем выделение
        });
    }

    // Функция для подсветки звезд
    function highlightStars(container, rating) {
        const stars = container.querySelectorAll('.star');
        stars.forEach(star => {
            if (star.getAttribute('data-value') <= rating) {
                star.style.color = '#466ee5'; // Подсвечиваем звезды
                star.style.borderColor = '#466ee5'; // Синий цвет для рамки
            } else {
                star.style.color = '#ccc'; // Серый цвет для незаполненных звезд
                star.style.borderColor = '#466ee5'; // Рамка остается синей
            }
        });
    }
});
