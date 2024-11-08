document.addEventListener('DOMContentLoaded', () => {
    const openEditModalBtns = document.querySelectorAll('.edit-btn');
    const closeEditModalBtn = document.getElementById('closeEditModalBtn');
    const overlay = document.getElementById('overlay');
    const editModal = document.getElementById('editModal');
    const editForm = editModal.querySelector('form');


    openEditModalBtns.forEach(button => {
        button.addEventListener('click', () => {

            const id = button.getAttribute('data-id');
            const title = button.getAttribute('data-title');
            const subject = button.getAttribute('data-subject');
            const description = button.getAttribute('data-description');
            const age = button.getAttribute('data-age');
            const rating = button.getAttribute('data-rating');
            const contactLink = button.getAttribute('data-contact-link');


            document.getElementById('editId').value = id;
            document.getElementById('editTitle').value = title;
            document.getElementById('editSubject').value = subject;
            document.getElementById('editDescription').value = description;
            document.getElementById('editAge').value = age;
            document.getElementById('editRating').value = rating;
            document.getElementById('editContactLink').value = contactLink;


            overlay.style.display = 'block';
            editModal.style.display = 'block';

            setTimeout(() => {
                overlay.classList.add('show');
                editModal.classList.add('show');
            }, 10);
        });
    });


    if (closeEditModalBtn) {
        closeEditModalBtn.addEventListener('click', () => {
            closeEditModal();
        });
    }

    overlay.addEventListener('click', () => {
        closeEditModal();
    });

    function closeEditModal() {
        overlay.classList.remove('show');
        editModal.classList.remove('show');

        setTimeout(() => {
            editModal.style.display = 'none';
            overlay.style.display = 'none';
        }, 500);
    }


    editForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const formData = new FormData(editForm);

        fetch('/edit-prepod/', {
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
            closeEditModal();
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
