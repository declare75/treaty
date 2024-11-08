document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const warningIcon = document.querySelector('.warning-icon');
    const form = document.querySelector('form');



    document.querySelector('.upload-image-container').addEventListener('click', function() {
        fileInput.click();
        warningIcon.style.display = 'none';
    });


    fileInput.addEventListener('change', function() {
        const fileName = this.files[0] ? this.files[0].name : '';


        if (!fileName) {
            warningIcon.style.display = 'inline';
        } else {
            warningIcon.style.display = 'none';
        }
    });


    form.addEventListener('submit', function(e) {
        const fileName = fileInput.files[0] ? fileInput.files[0].name : '';


        if (!fileName) {
            e.preventDefault();
            warningIcon.style.display = 'inline';
            alert("Пожалуйста, загрузите аватар.");
        } else {
            warningIcon.style.display = 'none';
        }
    });
});
