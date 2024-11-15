document.addEventListener('DOMContentLoaded', () => {
    // Открытие и закрытие модального окна
    const openModalBtn = document.getElementById('openModalBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const overlay = document.getElementById('overlay');
    const modal = document.getElementById('modal');
    const form = document.getElementById('prepodForm');
    const subjectSelect = document.querySelector('select[name="subject"]'); // Изменено: используем name

    // Проверяем, если элемент существует
    if (subjectSelect) {
        fetch('/catalog2/get-subjects/')
            .then(response => response.json())
            .then(data => {
                // Очистить старые опции
                subjectSelect.innerHTML = ''; // Сбросим опции перед добавлением новых
                if (data.subjects && data.subjects.length > 0) {
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.disabled = true;
                    defaultOption.selected = true;
                    defaultOption.textContent = 'Выберите предмет';
                    subjectSelect.appendChild(defaultOption);

                    data.subjects.forEach(subject => {
                        const option = document.createElement('option');
                        option.value = subject.id;
                        option.textContent = subject.name; // Изменено: выводим name
                        subjectSelect.appendChild(option);
                    });
                } else {
                    const noSubjectsOption = document.createElement('option');
                    noSubjectsOption.disabled = true;
                    noSubjectsOption.textContent = 'Нет доступных предметов';
                    subjectSelect.appendChild(noSubjectsOption);
                }
            })
            .catch(error => {
                console.error('Ошибка при загрузке предметов:', error);
            });
    } else {
        console.error('Элемент с name="subject" не найден.');
    }

    // Функция открытия модального окна
    function openModal() {
        overlay.style.display = 'block';
        modal.style.display = 'block';

        setTimeout(() => {
            overlay.classList.add('show');
            modal.classList.add('show');
        }, 10);
    }

    // Функция закрытия модального окна
    function closeModal() {
        overlay.classList.remove('show');
        modal.classList.remove('show');

        setTimeout(() => {
            modal.style.display = 'none';
            overlay.style.display = 'none';
        }, 500);
    }

    // Открытие модального окна при клике на кнопку
    if (openModalBtn) {
        openModalBtn.addEventListener('click', openModal);
    }

    // Закрытие модального окна при клике на кнопку или оверлей
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    overlay.addEventListener('click', closeModal);

    // Отправка формы через AJAX
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(form);

        fetch('/add-prepod/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                closeModal();
            }
        })
        .catch(error => {
            console.error('Ошибка при отправке:', error);
        });
    });

    // Функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
