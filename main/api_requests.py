# frontend/authorisation.py
import requests
from django.conf import settings
from django.http import JsonResponse

def do_request(request, path, method='GET', data=None):
    """Универсальная функция для запросов к бэкенду"""
    access_token = request.session.get('access_token')
    
    if not access_token:
        return {"error": "Not authenticated", "status": 401}
    
    try:
        # Формируем URL
        url = f'{settings.BACKEND_API_URL}/{path}'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Выполняем запрос
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            return {"error": f"Unsupported method: {method}", "status": 400}
        
        # Обрабатываем ответ
        if response.status_code == 200:
            return {"success": True, "data": response.json(), "status": 200}
        else:
            # Пробуем обновить токен
            refresh_token = request.session.get('refresh_token')
            if refresh_token:
                refresh_response = requests.post(
                    f'{settings.BACKEND_API_URL}/api/token/refresh/',
                    json={'refresh': refresh_token},
                    timeout=5
                )
                if refresh_response.status_code == 200:
                    new_access = refresh_response.json()['access']
                    request.session['access_token'] = new_access
                    
                    # Повторяем запрос с новым токеном
                    headers['Authorization'] = f'Bearer {new_access}'
                    if method == 'GET':
                        response = requests.get(url, headers=headers, timeout=5)
                    else:
                        response = requests.post(url, headers=headers, json=data, timeout=5)
                    
                    if response.status_code == 200:
                        return {"success": True, "data": response.json(), "status": 200}
            
            return {"error": f"Request failed: {response.status_code}", "status": response.status_code}
            
    except requests.Timeout:
        return {"error": "Connection timeout", "status": 504}
    except requests.ConnectionError:
        return {"error": "Cannot connect to backend server", "status": 503}
    except Exception as e:
        return {"error": str(e), "status": 500}