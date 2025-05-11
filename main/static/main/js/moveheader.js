document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.containerscroll');
    const platform = document.querySelector('.web-platform1');

    let maxScroll = 200;
    let offset = 0;


    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;


        if (scrollY < maxScroll) {
            offset = scrollY;
        } else {
            offset = maxScroll;
        }


        container.style.transform = `translateY(${offset}px)`;
    });
});
