function filterSearch() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const results = document.getElementById('resultsContainer');
    const items = results.getElementsByClassName('containerPrepods');

    for (let i = 0; i < items.length; i++) {
        const title = items[i].getElementsByClassName('FIO')[0].textContent.toLowerCase();
        const subject = items[i].getElementsByClassName('subject')[0].textContent.toLowerCase();
        const description = items[i].getElementsByClassName('desc')[0].textContent.toLowerCase();

        if (title.includes(filter) || subject.includes(filter) || description.includes(filter)) {
            items[i].style.display = "";
        } else {
            items[i].style.display = "none";
        }
    }
}
