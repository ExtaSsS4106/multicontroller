from functools import wraps
from django.shortcuts import redirect, render
from django.conf import settings
import requests
import jwt, json
from django.http import JsonResponse


def require_auth(view_func):
    """Декоратор для проверки авторизации через API бэкенда"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.session.get('access_token')
        
        if not access_token:
            return redirect(settings.LOGIN)
        
        try:
            response = requests.get(
                f'{settings.BACKEND_API_URL}/api/profile/',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                request.user_data = response.json()
                return view_func(request, *args, **kwargs)
            else:
                refresh_token = request.session.get('refresh_token')
                if refresh_token:
                    refresh_response = requests.post(
                        f'{settings.BACKEND_API_URL}/api/token/refresh/',
                        json={'refresh': refresh_token}
                    )
                    if refresh_response.status_code == 200:
                        new_access = refresh_response.json()['access']
                        request.session['access_token'] = new_access
                        
                        response = requests.get(
                            f'{settings.BACKEND_API_URL}/api/profile/',
                            headers={'Authorization': f'Bearer {new_access}'}
                        )
                        if response.status_code == 200:
                            request.user_data = response.json()
                            return view_func(request, *args, **kwargs)
                
                request.session.flush()
                return redirect(settings.LOGIN)
                
        except requests.RequestException:
            return response(request,{
                'error': 'Backend server is unavailable'
            }, status=503)
    
    return wrapper

def logout(request):
    access_token = request.session.get('access_token')
    
    if access_token:
        try:
            requests.post(
                f'{settings.BACKEND_API_URL}/api/logout/',
                headers={'Authorization': f'Bearer {access_token}'}
            )
        except:
            pass  
    
    request.session.flush()
    
    
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    # Проверка наличия полей
    if not username or not password:
        return {"error": "Username and password are required"}
    
    try:
        response = requests.post(
            f'{settings.BACKEND_API_URL}/api/login/',  
            json={'username': username, 'password': password},
            timeout=5
        )
        data = response.json()
        access_token = data.get('access')
               # Проверка is_superuser
        try:
            amisuperuser_response = requests.get(
                f'{settings.BACKEND_API_URL}/api/amisuperuser/',
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=5
            )
            
            if amisuperuser_response.status_code == 200:
                amisuperuser = amisuperuser_response.json()
                if not amisuperuser.get('status_admin', False):
                    # Не админ - разлогиниваем
                    logout(request)
                    return {"error": "You don't have admin privileges"}
        except:
            return {"error": "Cannot verify admin status"}
        if response.status_code == 200:
            data = response.json()
            
            request.session['access_token'] = data['access']
            request.session['refresh_token'] = data['refresh']
            
            decoded = jwt.decode(
                data['access'], 
                options={"verify_signature": False}
            )
            request.session['user_id'] = decoded.get('user_id')
            
            return {"success": True}
        else:
            return {"error": "Invalid username or password"}
            
    except requests.ConnectionError:
        return {"error": "Cannot connect to authentication server"}
    except requests.Timeout:
        return {"error": "Connection timeout. Please try again"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}