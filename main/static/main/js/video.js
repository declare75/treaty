document.addEventListener("DOMContentLoaded", function () {
    const videos = document.querySelectorAll(".video-container video");
    const indicators = document.querySelectorAll(".indicator");
    let currentVideo = 0;
    const fadeTime = 1;

    function playNextVideo() {
        const current = videos[currentVideo];
        const nextVideoIndex = (currentVideo + 1) % videos.length;
        const next = videos[nextVideoIndex];

        // Смена активного индикатора
        indicators[currentVideo].classList.remove("active");
        indicators[nextVideoIndex].classList.add("active");


        next.currentTime = 0;
        next.classList.add("active");
        next.play();


        setTimeout(() => {
            current.classList.remove("active");
            current.classList.add("inactive");
            current.nextTriggered = false;
        }, fadeTime * 1000);


        currentVideo = nextVideoIndex;
    }


    videos.forEach((video) => {
        video.addEventListener("timeupdate", () => {
            if (video.duration - video.currentTime <= fadeTime && !video.nextTriggered) {
                video.nextTriggered = true;
                playNextVideo();
            }
        });

        video.addEventListener("loadeddata", () => {

            if (video === videos[0]) {
                video.classList.add("no-transition");
                video.classList.add("active");
                indicators[0].classList.add("active");


                setTimeout(() => {
                    video.classList.remove("no-transition");
                }, 100);
            }
        });
    });


    videos[currentVideo].play();
});
