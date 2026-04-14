from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
import requests  
import jwt, json
from .authorisation import require_auth, logout, login
from .api_requests import do_request

def login_view(request):
    if request.method == 'POST':
        result = login(request)  
        
        if result.get('error'):
            return render(request, 'authorisation/login.html', {
                'error': result['error']
            })
        
        if result.get('success'):
            return redirect(settings.MAIN)
        
        return render(request, 'authorisation/login.html', {
            'error': 'Unknown error occurred'
        })
    return render(request, 'authorisation/login.html')

@require_auth
def main(request):
    username = request.user_data.get('username')
    return render(request, 'main/forms/main/main.html', {"username": username})


@require_auth
def logout_view(request):
    logout(request)
    return redirect('login')

@require_auth
def all_users(request):
    username = request.user_data.get('username')
    response = do_request(request, "api/all-users/")
    return render(request, "main/forms/users/profile/forms/profiles.html", {"username": username, "data": response.get('data')})

@require_auth
def profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.user_data.get('username')
        response = json.loads(do_request(request, "api/profile/", method='POST', data=data))
        data = response.get('data')
        print(data)
        return render(request, "main/forms/users/profile/forms/profile.html", {"username": username})
    
@require_auth
def user_notes(request, user_id):
    username = request.user_data.get('username')
    response = do_request(request, f"api/user-notes/{user_id}")
    return render(request, "main/forms/users/profile/forms/profile.html", {"username": username, "data": response.get('data')})


@require_auth
def note(request, note_id):
    username = request.user_data.get('username')
    response = do_request(request, f"api/note/{note_id}")
    return render(request, "main/forms/users/profile/forms/profile.html", {"username": username, "data": response.get('data')})

@require_auth
def register(request):
    username = request.user_data.get('username')
    if request.method == 'POST':
        data = json.loads(request.body)
        response = do_request(request, f"api/register/", method="POST", data=data)
        return render(request, "main/forms/users/registrating.html", {"username": username, "data": response.get('data')})
    return render(request, "main/forms/users/registrating.html", {"username": username})