document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                observer.unobserve(entry.target); // Прекращаем наблюдение после появления
            }
        });
    }, {
        threshold: 0.1 // Процент видимой области элемента
    });

    elements.forEach(element => observer.observe(element));
});
