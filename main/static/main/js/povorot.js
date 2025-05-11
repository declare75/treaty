
const onlineBox = document.querySelector('.onlinebox');
let initialRotation = 3.757;

window.addEventListener('scroll', () => {
    // Рассчитываем, насколько нужно повернуть
    const scrollRotation = window.scrollY * 0.01;


    onlineBox.style.transform = `rotate(${initialRotation - scrollRotation}deg)`;
});