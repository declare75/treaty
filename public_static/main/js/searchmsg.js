function filterSearch() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const chatBox = document.getElementById('chat-box');
    const messages = chatBox.getElementsByClassName('message');

    for (let i = 0; i < messages.length; i++) {
        const username = messages[i].getElementsByClassName('username2')[0].textContent.toLowerCase();
        const messageContent = messages[i].getElementsByClassName('message-content')[0].textContent.toLowerCase();

        // Если имя пользователя или текст сообщения содержит искомое слово, показываем сообщение
        if (username.includes(filter) || messageContent.includes(filter)) {
            messages[i].style.display = "";
        } else {
            messages[i].style.display = "none";
        }
    }
}
