let selectedSubject = '';  // Для хранения выбранного предмета

function filterSearch() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const results = document.getElementById('resultsContainer');
    const items = results.getElementsByClassName('containerPrepods');

    for (let i = 0; i < items.length; i++) {
        const title = items[i].getElementsByClassName('FIO')[0].textContent.toLowerCase();
        const subject = items[i].getElementsByClassName('subject')[0].textContent.toLowerCase();
        const description = items[i].getElementsByClassName('desc')[0].textContent.toLowerCase();

        if ((title.includes(filter) || description.includes(filter)) &&
            (selectedSubject === '' || subject.includes(selectedSubject))) {
            items[i].style.display = "";
        } else {
            items[i].style.display = "none";
        }
    }
}

function filterBySubject(subject) {
    const input = document.getElementById('searchInput');
    input.value = '';
    selectedSubject = subject.toLowerCase();
    input.placeholder = `Поиск по предмету: ${subject}`;

    const filterButtonContainer = document.getElementById('filterButtonContainer');
    const filterButton = document.createElement('button');
    filterButton.textContent = `${subject} `;

    const closeButton = document.createElement('span');
    closeButton.textContent = '×';
    closeButton.classList.add('close-button');
    closeButton.onclick = function(event) {
        event.stopPropagation();
        clearFilter();
    };

    filterButton.classList.add('filter-button', 'show');
    filterButton.onclick = function() {
        clearFilter();
    };

    filterButton.appendChild(closeButton);
    filterButtonContainer.innerHTML = '';
    filterButtonContainer.appendChild(filterButton);

    setTimeout(() => {
        filterButton.classList.add('show'); // Добавляем класс для анимации появления
    }, 10);

    filterSearch();
}

function clearFilter() {
    const input = document.getElementById('searchInput');
    selectedSubject = '';
    input.placeholder = 'Введите имя преподавателя';

    const filterButton = document.querySelector('.filter-button');
    if (filterButton) {
        filterButton.classList.remove('show');
        filterButton.classList.add('hide'); // Добавляем класс для анимации исчезновения

        // Удаляем кнопку после завершения анимации
        setTimeout(() => {
            const filterButtonContainer = document.getElementById('filterButtonContainer');
            filterButtonContainer.innerHTML = '';
        }, 300); // Задержка совпадает с длительностью transition
    }

    filterSearch();
}
