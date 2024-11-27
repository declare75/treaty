document.addEventListener("DOMContentLoaded", function () {
    const videos = document.querySelectorAll(".video-container video");
    const indicators = document.querySelectorAll(".indicator");
    let currentVideo = 0;
    const fadeTime = 1; // Время наложения (в секундах)

    function playNextVideo() {
        const current = videos[currentVideo];
        const nextVideoIndex = (currentVideo + 1) % videos.length;
        const next = videos[nextVideoIndex];

        // Смена активного индикатора
        indicators[currentVideo].classList.remove("active");
        indicators[nextVideoIndex].classList.add("active");

        // Установить следующее видео активным
        next.currentTime = 0; // Обнуляем следующее видео
        next.classList.add("active");
        next.play();

        // Отключить текущее видео через fadeTime
        setTimeout(() => {
            current.classList.remove("active");
            current.classList.add("inactive");
            current.nextTriggered = false; // Сбрасываем состояние для текущего видео
        }, fadeTime * 1000);

        // Обновить текущий индекс
        currentVideo = nextVideoIndex;
    }

    // Добавить плавный переход перед концом текущего видео
    videos.forEach((video) => {
        video.addEventListener("timeupdate", () => {
            if (video.duration - video.currentTime <= fadeTime && !video.nextTriggered) {
                video.nextTriggered = true; // Гарантируем, что это событие не будет вызвано дважды
                playNextVideo();
            }
        });

        video.addEventListener("loadeddata", () => {
            // Первое видео отображается сразу
            if (video === videos[0]) {
                video.classList.add("no-transition"); // Убираем анимацию
                video.classList.add("active");
                indicators[0].classList.add("active");

                // После первой загрузки можно включить переходы для следующих видео
                setTimeout(() => {
                    video.classList.remove("no-transition");
                }, 100);
            }
        });
    });

    // Убедиться, что первое видео играет сразу
    videos[currentVideo].play();
});
