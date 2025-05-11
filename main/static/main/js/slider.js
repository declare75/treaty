let currentIndex = 1;
const slides = document.querySelectorAll('.imgslide div');
const totalSlides = slides.length;
const slideWidth = 350;


const leftButton = document.querySelector('.leftimg');
const rightButton = document.querySelector('.rightimg');


leftButton.addEventListener('click', () => {
    moveSlide('prev');
});


rightButton.addEventListener('click', () => {
    moveSlide('next');
});


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


function updateSlider() {
    const offset = -currentIndex * slideWidth; // Сдвиг на ширину одного слайда (300px)
    document.querySelector('.imgslide').style.transform = `translateX(${offset}px)`;
}


function updateButtonStates() {

    if (currentIndex === 0) {
        leftButton.style.pointerEvents = 'none';
    } else {
        leftButton.style.pointerEvents = 'auto';
    }


    if (currentIndex === 6) {
        rightButton.style.pointerEvents = 'none';
    } else {
        rightButton.style.pointerEvents = 'auto';
    }
}


updateSlider();
updateButtonStates();
