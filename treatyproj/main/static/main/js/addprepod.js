document.addEventListener('DOMContentLoaded', () => {
    const openModalBtn = document.getElementById('openModalBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const overlay = document.getElementById('overlay');
    const modal = document.getElementById('modal');
    const form = modal.querySelector('form');

    if (openModalBtn) {
        openModalBtn.addEventListener('click', () => {
            overlay.style.display = 'block';
            modal.style.display = 'block';

            setTimeout(() => {
                overlay.classList.add('show');
                modal.classList.add('show');
            }, 10);
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            closeModal();
        });
    }

    overlay.addEventListener('click', () => {
        closeModal();
    });

    function closeModal() {
        overlay.classList.remove('show');
        modal.classList.remove('show');

        setTimeout(() => {
            modal.style.display = 'none';
            overlay.style.display = 'none';
        }, 500);
    }


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
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            closeModal(); //
            alert(data.message);

        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
    });


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
