import uuid

import eel
import os, requests, json
from .settings import *
from .render import render
import base64
from .db.models import *
from .db.db import with_db
import asyncio

class Views:

    def get_user_data():
        with open(USER_DATA, 'r', encoding='utf-8') as file:
            data = json.load(file)
        response =  requests.get(
                f'{HOST}/api/profile-info/',
                headers={'Authorization': f'Bearer {data.get('access')}'}
            )
        
        @with_db
        async def update_local_profile(id):
            """Обновление локального профиля данными с сервера"""
            user = await User.get(id=id)  
            user.name = response.json().get('username')
            user.user_id = response.json().get('user_id')
            user.profile_id = response.json().get('profile_id')
            await user.save()

    @eel.expose
    def logout():
        with open(USER_DATA, 'r', encoding='utf-8') as file:
            data = json.load(file)
        with open(CONF_PATH, 'r', encoding='utf-8') as file:
            page = json.load(file)
        requests.post(
                f'{HOST}/api/logout/',
                headers={'Authorization': f'Bearer {data.get('refresh')}'}
            )
        page['load_page'] = 'login'
        with open(CONF_PATH, 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=4, ensure_ascii=False)
        with open(USER_DATA, 'w', encoding='utf-8') as f:
            json.dump('', f, indent=4, ensure_ascii=False)
        
    @eel.expose
    def login(username=None, password=None):
        if username and password:
            print(f"Попытка входа: {username}")
            try:
                response = requests.post(
                    f'{HOST}/api/login/',  
                    json={'username': username, 'password': password},
                    timeout=5
                )
                print(f"Статус ответа: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    # Сохраняем данные пользователя
                    with open(USER_DATA, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    Views.set_load_page('main')
                    
                    # Возвращаем JSON для успешного входа
                    return {
                        'status': '200',
                        'success': True,
                        'user': data.get('user'),
                        'token': data.get('access')
                    }
                else:
                    # Возвращаем JSON с ошибкой
                    return {
                        'status': str(response.status_code),
                        'success': False,
                        'error': f'Ошибка сервера: {response.status_code}'
                    }
            except requests.ConnectionError:
                return {
                    'status': 'error',
                    'success': False,
                    'error': 'Нет соединения с сервером'
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'success': False,
                    'error': str(e)
                }
        else:
            # Возвращаем HTML страницу логина
            return render("authorisation/login.html")
        
        
    
    
    @eel.expose
    def main(args):
        try:
            type = args.get('type') if args else None
            if not type:
                type = 'server' # Значение по умолчанию, если type не передан
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print("User data loaded:", data)
            
            access_token = data.get('access')
            if not access_token:
                print("No access token found")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Session expired"})
            if type == 'server':
                response = requests.get(
                    f'{HOST}/api/profile-content/',
                    headers={'Authorization': f'Bearer {access_token}'},
                    timeout=5
                )
                print(f"Response status: {response.status_code}")
                if response.status_code == 200:
                    profile_data = response.json()
                    print("Profile data received:", profile_data)
                    return render("main/forms/users/profile/forms/profile.html", {'data': profile_data, "type": "server"})
                else:
                    print(f"Error: {response.status_code}")
                    Views.set_load_page('login')
                    return render("authorisation/login.html", {"error": "Authentication failed"})
                
            elif type == 'local':
                @with_db
                async def init():
                    try:
                        notes = await Notes.all()
                        data = []
                        for n in notes:
                            data.append({
                                "id": n.id,
                                "title": n.title,
                                "description": n.description,
                                "file_link": n.file_link,
                                "file_name": n.file_name,
                                "file_hash": n.file_hash,
                                "server_id": n.server_id,
                                "created_at": n.created_at.isoformat(),
                                "updated_at": n.updated_at.isoformat()
                            })
                        
                        return data
                    except Exception as e:
                        print(f"Error fetching local profile: {e}")
                        return []
                
                data = asyncio.run(init())
                print("Profile data received:", data)
                return render("main/forms/users/profile/forms/profile.html", {
                    'data': data, 
                    "type": "local"
                })
                
                
        except requests.ConnectionError:
            print("USER_DATA file not found")
            Views.main({'type': 'local'})
        except requests.ConnectionError:
            Views.main({'type': 'local'})
        
    
    @eel.expose
    def server_note(note_id):
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                user_data = json.load(file)
    
            @with_db
            async def inner():
                try:
                    note = await Notes.get(server_id=note_id)
                except Exception as e:
                    print(f"Error occurred while fetching note: {e}")
                    note = None
                return note.id if note else None
            
            note =  asyncio.run(inner())
            print("note_id: ", note_id)
            print("local_note: ", note)
            access_token = user_data.get('access')
            if not access_token:
                Views.set_load_page('login')
                return {"error": "No access token", "status": "error"}
            
            response = requests.get(
                f'{HOST}/api/note/{note_id}/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=5
            )
            
            print(f"Note API response status: {response.status_code}")
            
            if response.status_code == 200:
                note_data = response.json()
                print(note_data)
                # Используем ключ 'data' вместо 'note'
                return render("main/forms/notes/note/note.html", {'data': note_data, "local_note_id": note, "type": "server"})
            else:
                Views.set_load_page('login')
                error_msg = response.json().get('error', 'Note not found')
                return render("main/forms/notes/note/note.html", {'error': error_msg})
                
        except FileNotFoundError:
            Views.set_load_page('login')
            return render("main/forms/notes/note/note.html", {'error': 'Please login first'})
        except requests.ConnectionError:
            return render("main/forms/notes/note/note.html", {'error': 'Cannot connect to server'})
        except Exception as e:
            print(f"Error in note: {e}")
            return render("main/forms/notes/note/note.html", {'error': str(e)})
    
    @eel.expose
    def local_note(note_id):
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                user_data = json.load(file)
    
            @with_db
            async def inner():
                try:
                    note = await Notes.get(id=note_id)
                    data = {
                                "id": note.id,
                                "title": note.title,
                                "description": note.description,
                                "file_link": note.file_link,
                                "file_name": note.file_name,
                                "file_hash": note.file_hash,
                                "server_id": note.server_id,
                                "created_at": note.created_at.isoformat(),
                                "updated_at": note.updated_at.isoformat()
                            }
                except Exception as e:
                    print(f"Error occurred while fetching local note: {e}")
                    data = None
                return data
            
            data =  asyncio.run(inner())
            if not data:
                return render("main/forms/notes/note/note.html", {'error': 'Note not found'})
            
            return render("main/forms/notes/note/note.html", {'data': data, "type": "local", "local_note_id": note_id})
                
        except FileNotFoundError:
            Views.set_load_page('login')
            return render("main/forms/notes/note/note.html", {'error': 'Please login first'})
        except Exception as e:
            print(f"Error in local_note: {e}")
            return render("main/forms/notes/note/note.html", {'error': str(e)})
    
    @eel.expose
    def new_note():
        return render("main/forms/notes/note/new_note.html")

   
    
    @eel.expose
    def create_note(title, description):
        """Создание новой заметки"""
        try:
            # Получаем токен
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                user_data = json.load(file)
            
            access_token = user_data.get('access')
            if not access_token:
                return {"status": "error", "error": "No access token"}
            
            # Отправляем запрос на бэкенд
            response = requests.post(
                f'{HOST}/api/create-note/',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'title': title,
                    'description': description
                },
                timeout=5
            )
            
            print(f"Create note response status: {response.status_code}")
            
            if response.status_code == 200:
                note_data = response.json()
                return {
                    "status": "success",
                    "message": note_data.get('message', 'Note created'),
                    "note": note_data.get('note')
                }
            else:
                error_msg = response.json().get('details', 'Failed to create note')
                return {"status": "error", "error": error_msg}
                
        except FileNotFoundError:
            return {"status": "error", "error": "Please login first"}
        except requests.ConnectionError:
            return {"status": "error", "error": "Cannot connect to server"}
        except Exception as e:
            print(f"Error in create_note: {e}")
            return {"status": "error", "error": str(e)}
        
    
    @with_db
    async def create_or_update_local_note_wrapper(args):
        """Создание или обновление заметки без отправки на бэкенд"""
        title = args.get('title')
        description = args.get('description')
        note_id = args.get('note_id')
        server_id = args.get('server_id')
        print("Note ID: ", note_id)
        if note_id is not None and note_id != '':
            note = await Notes.get(id=note_id)
            note.title = title
            note.description = description
            note.server_id = server_id
            await note.save()
        else:
            try:
                notes = await Notes.all()
            except:
                notes = []
            file_hash = uuid.uuid4().hex  # Генерируем уникальный hash для файла  
            while any(n.file_hash == file_hash for n in notes):
                file_hash = uuid.uuid4().hex          
            note = await Notes.create(title=title, description=description, file_hash=file_hash, server_id=server_id)
            
        return {
            "status": "success",
            "message": "Note saved locally",
            "note": {
                "id": note.id,
                "title": note.title,
                "description": note.description,
                "file_link": None,
                "file_name": None,
                "file_hash": note.file_hash
            }
        }
    @eel.expose
    def create_or_update_local_note(args):
        return asyncio.run(Views.create_or_update_local_note_wrapper(args))
    
    @eel.expose
    def delete_note(note_id, type):
        """Удаление заметки"""
        
        try:
            if type == 'server':
                with open(USER_DATA, 'r', encoding='utf-8') as file:
                    user_data = json.load(file)
                
                access_token = user_data.get('access')
                if not access_token:
                    return {"status": "error", "error": "No access token"}
                
                response = requests.delete(
                    f'{HOST}/api/note/{note_id}/',
                    headers={'Authorization': f'Bearer {access_token}'},
                    timeout=5
                )
                
                print(f"Delete note response status: {response.status_code}")
                
                if response.status_code == 200:
                    return {"status": "success", "message": "Note deleted"}
                else:
                    error_msg = response.json().get('error', 'Failed to delete note')
                    return {"status": "error", "error": error_msg}
            elif type == 'local':
                @with_db
                async def delete_local_note():
                    try:
                        note = await Notes.get(id=note_id)
                        if note.file_hash and note.file_name:
                            file_path = os.path.join('media', note.file_hash ,f'{note.file_name}')
                            folder_path = os.path.join('media', note.file_hash)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            if os.path.exists(folder_path) and not os.listdir(folder_path):
                                os.rmdir(folder_path)
                        await note.delete()
                        return {"status": "success", "message": "Note deleted locally"}
                    except Exception as e:
                        print(f"Error deleting local note: {e}")
                        return {"status": "error", "error": str(e)}
                
                return asyncio.run(delete_local_note())
        except FileNotFoundError:
            return {"status": "error", "error": "Please login first"}
        except requests.ConnectionError:
            return {"status": "error", "error": "Cannot connect to server"}
        except Exception as e:
            print(f"Error in delete_note: {e}")
            return {"status": "error", "error": str(e)}
        
    @eel.expose
    def update_note(title, description, noteId):
        """Обновление существующей заметки"""
        try:
            # Получаем токен
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                user_data = json.load(file)
            
            access_token = user_data.get('access')
            if not access_token:
                return {"status": "error", "error": "No access token"}
            
            # Отправляем запрос на бэкенд
            response = requests.post(
                f'{HOST}/api/note/{noteId}/',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'title': title,
                    'description': description
                },
                timeout=5
            )
            
            print(f"Update note response status: {response.status_code}")
            
            if response.status_code == 200:
                note_data = response.json()
                return {
                    "status": "success",
                    "message": note_data.get('message', 'Note updated'),
                    "note": note_data.get('note')
                }
            else:
                error_msg = response.json().get('details', 'Failed to update note')
                return {"status": "error", "error": error_msg}
                
        except FileNotFoundError:
            return {"status": "error", "error": "Please login first"}
        except requests.ConnectionError:
            return {"status": "error", "error": "Cannot connect to server"}
        except Exception as e:
            print(f"Error in update_note: {e}")
            return {"status": "error", "error": str(e)}
        
    @eel.expose
    def upload_file(file_name, file_data_base64, note_id):
        """Загрузка файла к заметке"""
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            access_token = user_data.get('access')
            if not access_token:
                return {"status": "error", "error": "No access token"}
            
            # Декодируем base64 в байты
            file_bytes = base64.b64decode(file_data_base64)
            
            # Отправляем на бэкенд
            files = {'file': (file_name, file_bytes)}
            
            response = requests.post(
                f'{HOST}/api/upload-file/{note_id}/',
                headers={'Authorization': f'Bearer {access_token}'},
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = response.json().get('error', 'Upload failed')
                return {"status": "error", "error": error_msg}
                
        except FileNotFoundError:
            return {"status": "error", "error": "Please login first"}
        except requests.ConnectionError:
            return {"status": "error", "error": "Cannot connect to server"}
        except Exception as e:
            print(f"Error in upload_file: {e}")
            return {"status": "error", "error": str(e)}
    @with_db
    async def local_save_file_wrapper(file_name, file_data_base64, note_id):
        """Локальное сохранение файла к заметке"""
        try:
            print(f"Saving file locally: {file_name} for note ID: {note_id}")
            note = await Notes.get(id=note_id)
            print(f"Note found: {note.title} with current file: {note.file_name}")
            # Декодируем base64 в байты
            file_bytes = base64.b64decode(file_data_base64)
            old_file = os.path.join('media', note.file_hash ,f'{note.file_name}') if note.file_hash and note.file_name else None
            if old_file and os.path.exists(old_file):
                os.remove(old_file)
            # Сохраняем файл локально
            local_path = os.path.join('media', note.file_hash ,f'{file_name}')
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(file_bytes)
            
            note.file_name = file_name
            note.file_link = local_path
            await note.save()
            return {"status": "success", "message": "File saved locally", "file_path": local_path}
                
        except Exception as e:
            print(f"Error in local_save_file: {e}")
            return {"status": "error", "error": str(e)}
    @eel.expose
    def local_save_file(file_name, file_data_base64, note_id):
        return asyncio.run(Views.local_save_file_wrapper(file_name, file_data_base64, note_id))
    @eel.expose
    def download_note_file(note_id):
        """Скачивание файла заметки"""
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            access_token = user_data.get('access')
            if not access_token:
                return {"status": "error", "error": "No access token"}
            
            response = requests.get(
                f'{HOST}/api/download-file/{note_id}/',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "file_data": base64.b64encode(response.content).decode('utf-8'),
                    "file_name": response.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"')
                }
            else:
                return {"status": "error", "error": "File not found"}
                
        except Exception as e:
            print(f"Error in download_note_file: {e}")
            return {"status": "error", "error": str(e)}    
    @eel.expose
    def groups():
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print("User data loaded:", data)
            
            access_token = data.get('access')
            if not access_token:
                print("No access token found")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Session expired"})
            
            response = requests.get(
                f'{HOST}/api/groups/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=5
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                groups = response.json()
                print("Groups data received:", groups)
                return render("main/forms/groups/groups.html", {'data': groups})
            else:
                print(f"Error: {response.status_code}")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Authentication failed"})
                
        except FileNotFoundError:
            print("USER_DATA file not found")
            return render("main/forms/groups/groups.html")
        
    
    @eel.expose
    def group(group_id):
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print("User data loaded:", data)
            
            access_token = data.get('access')
            if not access_token:
                print("No access token found")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Session expired"})
            
            response = requests.get(
                f'{HOST}/api/group-info/{group_id}/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=5
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                group_data = response.json()
                print("Group data received:", group_data)
                return render("main/forms/groups/group/forms/group.html", {'data': group_data})
            else:
                print(f"Error: {response.status_code}")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Authentication failed"})
                
        except FileNotFoundError:
            print("USER_DATA file not found")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": "Please login first"})
        
    
    @eel.expose
    def send_request(args):
        action = args.get('action')
        print(args)
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print("User data loaded:", data)
            
            access_token = data.get('access')
            if not access_token:
                print("No access token found")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Session expired"})
            

            if action == 'pending':
                note_id = args.get('note_id')
                request_id = args.get('request_id')
                print(f"Sending request: action={action}, note_id={note_id}")
                response = requests.post(
                f'{HOST}/api/requests/',
                headers={'Authorization': f'Bearer {access_token}'},
                json={'action': action, 'note_id': note_id, 'request_id': request_id},
                timeout=5)
            elif action == 'cancel':
                request_id = args.get('request_id')
                response = requests.post(
                f'{HOST}/api/requests/',
                headers={'Authorization': f'Bearer {access_token}'},
                json={'action': action, 'request_id': request_id},
                timeout=5)
        except:
            print("Error sending request")
    @eel.expose
    def get_requests():
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print("User data loaded:", data)
            
            access_token = data.get('access')
            if not access_token:
                print("No access token found")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Session expired"})
            
            response = requests.get(
                f'{HOST}/api/requests/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=5
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                requests_data = response.json()
                print("Requests data received:", requests_data)
                return render("main/forms/requests/requests.html", {'data': requests_data})
            else:
                print(f"Error: {response.status_code}")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Authentication failed"})
                
        except FileNotFoundError:
            print("USER_DATA file not found")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": "Please login first"})
        
        
        
    @eel.expose
    def get_load_page():
        try:
            with open(CONF_PATH, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"Current load page: {data['load_page']}")
            return data['load_page']
        except Exception as e:
            print(f"[ERROR]: {e}")
            return 'login'  # Возвращаем значение по умолчанию при ошибке
            
            
    @eel.expose
    def set_load_page(value='login'):
        try:
            with open(CONF_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                    
                # Изменяем
                data['load_page'] = value
                    
            # Записываем
            with open(CONF_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                    
            return True
        except Exception as e:
            print(f"[ERROR]: {e}")
            
    
    
    
    
    
  