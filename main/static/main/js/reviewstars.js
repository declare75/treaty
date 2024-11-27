const stars = document.querySelectorAll('.star');
const hiddenRatingInput = document.querySelector('input[name="rating"]');
const reviewForm = document.querySelector('.review-form');
const cancelButton = document.querySelector('.custom-btn-cancel');

// Обработчик событий для выбора звезд
stars.forEach(star => {
    star.addEventListener('mouseenter', () => {
        const rating = star.getAttribute('data-value');
        highlightStars(rating);
    });

    star.addEventListener('mouseleave', () => {
        const currentRating = hiddenRatingInput.value;
        highlightStars(currentRating);
    });

    star.addEventListener('click', () => {
        const rating = star.getAttribute('data-value');
        hiddenRatingInput.value = rating;
        reviewForm.classList.add('show'); // Появление формы отзыва с анимацией
    });
});

// Функция для подсветки звезд
function highlightStars(rating) {
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

// Обработчик кнопки "Отмена"
cancelButton.addEventListener('click', () => {
    reviewForm.classList.remove('show'); // Скрытие формы отзыва с анимацией
    hiddenRatingInput.value = ''; // Очистить значение рейтинга
    stars.forEach(star => star.classList.remove('selected')); // Удаляем выделение
});
