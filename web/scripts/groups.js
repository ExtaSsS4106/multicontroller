class GroupsPage {
    constructor() {
        console.log("GroupsPage constructor");
        this.init();
    }
    
    // Поиск групп
    searchGroups() {
        const query = document.getElementById('query')?.value.toLowerCase().trim() || '';
        const cards = document.querySelectorAll('.card');
        
        if (!query) {
            cards.forEach(card => card.style.display = 'flex');
            return;
        }
        
        cards.forEach(card => {
            const name = card.querySelector('.c-text h2')?.innerText.toLowerCase() || '';
            card.style.display = name.includes(query) ? 'flex' : 'none';
        });
    }
    
    init() {
        const input = document.getElementById('query');
        if (input) {
            input.addEventListener('input', () => this.searchGroups());
            console.log("Groups search initialized");
        }
    }
}