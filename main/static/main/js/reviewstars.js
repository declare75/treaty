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
            reviewForm.classList.add('show');
        });
    });


    if (cancelButton) {
        cancelButton.addEventListener('click', () => {
            reviewForm.classList.remove('show');
            hiddenRatingInput.value = '';
            stars.forEach(star => star.classList.remove('selected'));
        });
    }


    function highlightStars(container, rating) {
        const stars = container.querySelectorAll('.star');
        stars.forEach(star => {
            if (star.getAttribute('data-value') <= rating) {
                star.style.color = '#466ee5';
                star.style.borderColor = '#466ee5';
            } else {
                star.style.color = '#ccc';
                star.style.borderColor = '#466ee5';
            }
        });
    }
});
