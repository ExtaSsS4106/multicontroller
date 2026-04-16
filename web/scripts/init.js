console.log("init.js inited");

window.onload = async function() {
    try {
        const page = await eel.get_load_page()();
        console.log("Загружаем страницу:", page);
        loadPage(page);
    } catch (error) {
        console.error("Ошибка загрузки:", error);
    }
};