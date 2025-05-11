document.addEventListener('DOMContentLoaded', () => {

    const filters = {
        engimg: 'Английский язык',
        ruimg: 'Русский язык',
        informimg: 'Информатика',
        bioimg: 'Биология',
        historyimg: 'История',
        chemistryimg: 'Химия',
        economyimg: 'Экономика',
        astroimg: 'Астрономия',
        germimg: 'Немецкий язык',
        literimg: 'Литература',
        geoimg: 'География'
    };


    Object.keys(filters).forEach(className => {
        const overlay = document.querySelector(`.${className} .overlay`);
        if (overlay) {
            overlay.addEventListener('click', () => {
                const filter = filters[className];
                if (filter) {
                    window.location.href = `/catalog2?filter=${encodeURIComponent(filter)}`;
                }
            });
        }
    });
});