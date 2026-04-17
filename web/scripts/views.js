console.log("views.js inited")

async function logout() {
    const userConfirmed = confirm('Вы действительно хотите выйти?');
    if (userConfirmed) {
        await eel.logout()();
        loadPage(await eel.get_load_page()());
    }
}

async function loadPage(value, args = null) {
    let content;
    const link = document.getElementById('castom-style');
    switch(value) {
        case "login":
            content = await eel.login()();
            document.querySelector('body').innerHTML = content;
            link.href = `../static/authorisation/login.css`;
            let loginPage = new Login_page();
            loginPage.init_page();
            break;
        case "logout":
            await eel.logout()();
            loadPage(await eel.get_load_page()());
            break;
        case "send_request":
            await eel.send_request(args)();
            if (args.return_page){
                loadPage(args.return_page);
            }else if (args.action) {
                loadPage('group', args.group_id);
            }
                
            break;
        case "requests":
            [content, data] = await eel.get_requests()(); 
            document.querySelector('body').innerHTML = content;
            link.href = `../static/main/forms/requests/requests.css`;
            break;
        case "main":
            [content, data] = await eel.main(args)(); 
            console.log(data);
            document.querySelector('body').innerHTML = content;
            link.href = `../static/main/forms/users/profile/forms/profiles.css`;
            let MainPage = new Main_page();
            await eel.set_load_page('main')(); 
            break;

        case "server_note":
            link.href = `../static/main/forms/notes/note/note.css`;
            content = await eel.server_note(args)();
            document.querySelector('body').innerHTML = content;
            setTimeout(() => {
                window.updateNotePage = new UpdateNote();
            }, 100);
            break;
        case "local_note":
            link.href = `../static/main/forms/notes/note/note.css`;
            content = await eel.local_note(args)();
            document.querySelector('body').innerHTML = content;
            setTimeout(() => {
                window.updateNotePage = new UpdateNote();
            }, 100);
            break;
        case "new_note":
            link.href = `../static/main/forms/notes/note/note.css`;
            content = await eel.new_note()();
            document.querySelector('body').innerHTML = content;
            // Создаём экземпляр после загрузки HTML
            setTimeout(() => {
                if (typeof CreateNote !== 'undefined') {
                    window.createNotePage = new CreateNote();
                }
            }, 100);
            break;
        case "groups":
            [content, data] = await eel.groups()(); 
            document.querySelector('body').innerHTML = content;
            link.href = `../static/main/forms/groups/groups.css`;
            let groupsPage = new GroupsPage();
            window.groupsPage = groupsPage;
            break;
        case "group":
            [content, data] = await eel.group(args)();
            document.querySelector('body').innerHTML = content;
            link.href = `../static/main/forms/groups/group/forms/group.css`;
            break;

        default:
            console.log("nothing to show");
            document.querySelector('body').innerHTML = '<h1>Такой страницы не существует</h1>';
            break;
    }
}