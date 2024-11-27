// Находим элемент .onlinebox
const onlineBox = document.querySelector('.onlinebox');
let initialRotation = 3.757; // начальный угол поворота в градусах

window.addEventListener('scroll', () => {
    // Рассчитываем, насколько нужно повернуть
    const scrollRotation = window.scrollY * 0.01; // Коэффициент вращения

    // Обновляем поворот элемента, уменьшая его
    onlineBox.style.transform = `rotate(${initialRotation - scrollRotation}deg)`;
});