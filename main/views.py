from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import requests  
import jwt, json
from .authorisation import require_auth, logout, login
from .api_requests import do_request
from django.template.loader import render_to_string

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
    response = do_request(request, "api/statistics/")
    return render(request, 'main/forms/main/main.html', {"username": username, "statistics": response.get('data')})


@require_auth
def logout_view(request):
    logout(request)
    return redirect('login')

@require_auth
def all_notes(request):
    username = request.user_data.get('username')
    response = do_request(request, "api/all-notes/")
    return render(request, "main/forms/notes/all_notes.html", {"username": username, "data": response.get('data')})

@require_auth
def all_users(request):
    username = request.user_data.get('username')
    response = do_request(request, "api/all-users/")
    return render(request, "main/forms/users/profile/forms/profiles.html", {"username": username, "data": response.get('data')})

@require_auth
def groups(request):
    if request.method == 'GET':
        username = request.user_data.get('username')
        response = do_request(request, "api/groups/")
        return render(request, "main/forms/groups/groups.html", {"username": username, "data": response.get('data')})
    

@require_auth
def group(request, group_id):
    if request.method == 'GET':
        username = request.user_data.get('username')
        response = do_request(request, f"api/group-info/{group_id}/")
        print(response)
        return render(request, "main/forms/groups/group/forms/group.html", {"username": username, "data": response.get('data')})
    if request.method == 'POST':
        username = request.user_data.get('username')
        data = json.loads(request.body)
        response = do_request(request, f"api/group-info/{group_id}/", method='POST', data=data)
        print(response)
        return render(request, "main/forms/groups/group/forms/group.html", {"username": username, "data": response.get('data')})


@require_auth
def group_adding_users(request, group_id):
    if request.method == 'GET':
        username = request.user_data.get('username')
        response = do_request(request, f"api/group-info-for-adding/{group_id}")
        print(response)
        return render(request, "main/forms/groups/group/forms/group_adding_users.html", {"username": username, "data": response.get('data')})
    if request.method == 'POST':
        username = request.user_data.get('username')
        data = json.loads(request.body)
        response = do_request(request, f"api/group-info/{group_id}", method='POST', data=data)
        print(response)
        return render(request, "main/forms/groups/group/forms/group_adding_users.html", {"username": username, "data": response.get('data')})

@require_auth
def create_group(request):
    if request.method == 'GET':
        username = request.user_data.get('username')
        response = do_request(request, "api/create-group/")
        print(response.get('data'))
        return render(request, "main/forms/groups/create_new_groupe.html", {"username": username, "data": response.get('data')})
    if request.method == 'POST':
        username = request.user_data.get('username')
        data = json.loads(request.body)
        response = do_request(request, "api/create-group/", method='POST', data=data)
        return render(request, "main/forms/groups/create_new_groupe.html", {"username": username, "data": response.get('data')})


@require_auth
def profile_content(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.user_data.get('username')
        response = json.loads(do_request(request, "api/profile-content/", method='POST', data=data))
        data = response.get('data')
        print(data)
        return render(request, "main/forms/users/profile/forms/profile.html", {"username": username})

@require_auth
def adding(request, prof_id):
    if request.method == 'GET':
        username = request.user_data.get('username')
        response = do_request(request, f"api/adding/{prof_id}/")
        data = response.get('data')
        print(data)
        return render(request, "main/forms/users/profile/adding_in_groups.html", {"username": username, "data": response.get('data'), "prof_id": response.get('prof_id')})  
    if request.method == 'POST':
        username = request.user_data.get('username')
        data = json.loads(request.body)
        response = do_request(request, f"api/adding/{prof_id}/", method='POST', data=data)
        print(response)
        return JsonResponse({"data": response.get('data')})
        
@require_auth
def user_notes(request, user_id):
    if request.method == 'GET':
        username = request.user_data.get('username')
        response = do_request(request, f"api/user-notes/{user_id}")
        print(response)
        return render(request, "main/forms/users/profile/forms/profile.html", {"username": username, "data": response.get('data'), "user_id": response.get('user_id')})
    if request.method == 'POST':
        username = request.user_data.get('username')

        data = json.loads(request.body)
        response = do_request(request, f"api/profile-content/", method='POST', data=data)
        file = data.get('type')
        # Возвращаем только HTML блока
        html = render_to_string(f'main/forms/users/profile/forms/profile/{file}.html', {"username": username, "data": response.get('data'), "prof_id": response.get('prof_id')})
        
        return HttpResponse(html)  # Возвращаем только HTML, не JSON

@require_auth
def note(request, note_id):
    username = request.user_data.get('username')
    response = do_request(request, f"api/note/{note_id}")
    return render(request, "main/forms/notes/note/note.html", {"username": username, "data": response.get('data'), "download_url": response.get('download_url')})

@require_auth
def register(request):
    username = request.user_data.get('username')
    if request.method == 'POST':
        data = json.loads(request.body)
        response = do_request(request, f"api/register/", method="POST", data=data)
        return render(request, "main/forms/users/registrating.html", {"username": username, "data": response.get('data')})
    return render(request, "main/forms/users/registrating.html", {"username": username})

@require_auth
def requests(request):
    if request.method == 'GET':
        username = request.user_data.get('username')
        response = do_request(request, "api/requests/")
        return render(request, "main/forms/requests/requests.html", {"username": username, "data": response.get('data')})
    if request.method == 'POST':
        username = request.user_data.get('username')
        data = json.loads(request.body)
        print(data)
        response = do_request(request, "api/requests/", method="POST", data=data)
        return render(request, "main/forms/requests/requests.html", {"username": username, "data": response.get('data')})