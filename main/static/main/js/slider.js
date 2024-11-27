let currentIndex = 1; // Устанавливаем начальный индекс на 1, чтобы показывалось второе изображение
const slides = document.querySelectorAll('.imgslide div');
const totalSlides = slides.length;
const slideWidth = 350;  // Ширина одного слайда

// Получаем кнопки
const leftButton = document.querySelector('.leftimg');
const rightButton = document.querySelector('.rightimg');

// Обработчик для кнопки "влево"
leftButton.addEventListener('click', () => {
    moveSlide('prev');
});

// Обработчик для кнопки "вправо"
rightButton.addEventListener('click', () => {
    moveSlide('next');
});

// Функция для движения слайдера
function moveSlide(direction) {
    if (direction === 'next') {
        if (currentIndex < totalSlides - 1) {
            currentIndex++;
        }
    } else if (direction === 'prev') {
        if (currentIndex > 0) {
            currentIndex--;
        }
    }

    updateSlider();
    updateButtonStates();
}

// Обновление положения слайдера
function updateSlider() {
    const offset = -currentIndex * slideWidth; // Сдвиг на ширину одного слайда (300px)
    document.querySelector('.imgslide').style.transform = `translateX(${offset}px)`;
}

// Обновление состояния кнопок
function updateButtonStates() {
    // Если первая картинка (engimg), блокируем кнопку "влево"
    if (currentIndex === 0) {
        leftButton.style.pointerEvents = 'none';  // Отключаем кнопку
    } else {
        leftButton.style.pointerEvents = 'auto'; // Включаем кнопку
    }

    // Если последняя картинка (chemistryimg), блокируем кнопку "вправо"
    if (currentIndex === 6) {
        rightButton.style.pointerEvents = 'none'; // Отключаем кнопку
    } else {
        rightButton.style.pointerEvents = 'auto'; // Включаем кнопку
    }
}

// Инициализация состояния кнопок при загрузке
updateSlider();
updateButtonStates();
