document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById("container");
    const registerBtn = document.getElementById('register');
    const loginBtn = document.getElementById('login');
    const overlay = document.getElementById('overlay2');
    const btn = document.getElementById("logregOpenBtn");
    const span = document.getElementsByClassName("close")[0];

    if (registerBtn && loginBtn) {
        registerBtn.addEventListener('click', () => {
            container.classList.add("active");
        });

        loginBtn.addEventListener('click', () => {
            container.classList.remove("active");
        });
    }

    if (btn && span) {
        btn.onclick = function() {
            overlay.style.display = "block";
            modal.style.display = "block";
            setTimeout(() => {
                overlay.style.opacity = "1";
                modal.style.opacity = "1";
                overlay.style.visibility = "visible";
                modal.style.visibility = "visible";
            }, 10);
        }

        span.onclick = function() {
            overlay.style.opacity = "0";
            modal.style.opacity = "0";
            setTimeout(() => {
                overlay.style.visibility = "hidden";
                modal.style.visibility = "hidden";
                overlay.style.display = "none";
                modal.style.display = "none";
            }, 500);
        }

        window.onclick = function(event) {
            if (event.target == overlay) {
                overlay.style.opacity = "0";
                modal.style.opacity = "0";
                setTimeout(() => {
                    overlay.style.visibility = "hidden";
                    modal.style.visibility = "hidden";
                    overlay.style.display = "none";
                    modal.style.display = "none";
                }, 500);
            }
        }
    }


    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ email: email, password: password })
            }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Вход выполнен успешно');
                    window.location.href = '/';
                } else {
                    alert('Ошибка входа: ' + data.message);
                }
            }).catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке данных.');
            });
        });
    }


    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            event.preventDefault();

        const regLastName = document.getElementById('regLastName').value;
        const regFirstName = document.getElementById('regFirstName').value;
        const regMiddleName = document.getElementById('regMiddleName').value;
        const regEmail = document.getElementById('regEmail').value;
        const regPassword = document.getElementById('regPassword').value;


            fetch('/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    email: regEmail,
                    password: regPassword,
                    last_name: regLastName,
                    first_name: regFirstName,
                    middle_name: regMiddleName
                })
            }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Регистрация выполнена успешно');

                    window.location.href = data.redirect_url;
                } else {
                    alert('Ошибка регистрации: ' + data.message);
                }
            }).catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке данных.');
            });
        });
    }


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
