document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.containerscroll'); // Контейнер, который будет двигаться
    const platform = document.querySelector('.web-platform1');

    let maxScroll = 200; // Максимальное расстояние, на которое элементы могут двигаться
    let offset = 0;

    // Следим за прокруткой страницы
    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;

        // Двигаем контейнер, пока скроллим
        if (scrollY < maxScroll) {
            offset = scrollY;
        } else {
            offset = maxScroll; // Не даем прокрутке выходить за 250px
        }

        // Обновляем позицию контейнера
        container.style.transform = `translateY(${offset}px)`;
    });
});
