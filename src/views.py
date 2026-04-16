import eel
import os, requests, json
from .settings import *
from .render import render

class Views:


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
    def main():
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
                f'{HOST}/api/profile-content/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=5
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                profile_data = response.json()
                print("Profile data received:", profile_data)
                return render("main/forms/users/profile/forms/profile.html", {'data': profile_data})
            else:
                print(f"Error: {response.status_code}")
                Views.set_load_page('login')
                return render("authorisation/login.html", {"error": "Authentication failed"})
                
        except FileNotFoundError:
            print("USER_DATA file not found")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": "Please login first"})
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": "Invalid user data"})
        except requests.ConnectionError:
            print("Connection error to backend")
            return render("authorisation/login.html", {"error": "Cannot connect to server"})
        except Exception as e:
            print(f"Unexpected error: {e}")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": str(e)})
    
    @eel.expose
    def note(note_id):
        try:
            with open(USER_DATA, 'r', encoding='utf-8') as file:
                user_data = json.load(file)
            
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
                return render("main/forms/notes/note/note.html", {'data': note_data})
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
            Views.set_load_page('login')
            print(f"Error in note: {e}")
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
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": "Please login first"})
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": "Invalid user data"})
        except requests.ConnectionError:
            print("Connection error to backend")
            return render("authorisation/login.html", {"error": "Cannot connect to server"})
        except Exception as e:
            print(f"Unexpected error: {e}")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": str(e)})
    
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
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": "Invalid user data"})
        except requests.ConnectionError:
            print("Connection error to backend")
            return render("authorisation/login.html", {"error": "Cannot connect to server"})
        except Exception as e:
            print(f"Unexpected error: {e}")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": str(e)})
    
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
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": "Invalid user data"})
        except requests.ConnectionError:
            print("Connection error to backend")
            return render("authorisation/login.html", {"error": "Cannot connect to server"})
        except Exception as e:
            print(f"Unexpected error: {e}")
            Views.set_load_page('login')
            return render("authorisation/login.html", {"error": str(e)})
        
        
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
            
    
    
    
    
    
  