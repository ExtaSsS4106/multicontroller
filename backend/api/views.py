from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q

# Регистрация пользователя
class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/
    Content-Type: application/json

    {
        "username": "john",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    queryset = User.objects.all()
    permission_classes = (permissions.IsAdminUser,) 
    serializer_class = RegisterSerializer

# Получение профиля текущего пользователя
class ProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Логаут (добавляем refresh-токен в чёрный список)
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  # требует 'rest_framework_simplejwt.token_blacklist' в INSTALLED_APPS
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class AllUsers(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        users = User.objects.all()
        serialeizer = UserSerializer(users, many=True)
        return Response(serialeizer.data)
    
    def post(self, request):
        data = json.loads(request.body)
        query = data.get('query')
        
        if query:
            users = User.objects.filter(username__search=query)
        else:
            return Response({"error": "Not found"}, status=404)
        serialeizer = UserSerializer(users, many=True)
        return Response(serialeizer.data)
    
class AllNotes(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        Allnotes = notes.objects.all().order_by("-id")
        response = []
        if not request.user.is_superuser:
            accessible_note_ids = accesseble_notes.objects.filter(
                profile__user=request.user
            ).values_list('note', flat=True)
            requests_ = requests.objects.filter(profile__user=request.user)
            for note in Allnotes:
                access = note.id in accessible_note_ids
                req = [r for r in requests_ if r.note == note]
                if req:
                    req = req[0]
                    status = req.status 
                else:
                    status = None  
                response.append({
                    "id": note.id,
                    "title": note.title,
                    "file_link": note.file_link,
                    "file_name": note.file_name,
                    "profile": note.profile,
                    "access": access,
                    "status": status,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at,
                })
            return Response({"data": response})
        else: 
            for note in Allnotes:
                response.append({
                    "id": note.id,
                    "title": note.title,
                    "file_link": note.file_link,
                    "file_name": note.file_name,
                    "profile": note.profile,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at,
                })
            return Response({"data": response})
        
    def post(self, request):
        data = json.loads(request.body)
        query = data.get('query')
        Allnotes = notes.objects.filter(title__icontains=query).order_by("-id")
        response=[]
        if not request.user.is_superuser:
            accessible_note_ids = accesseble_notes.objects.filter(
                profile__user=request.user
            ).values_list('note', flat=True)
            requests_ = requests.objects.filter(profile__user=request.user)
            for note in Allnotes:
                access = note.id in accessible_note_ids
                req = [r for r in requests_ if r.note == note]
                if req:
                    req = req[0]
                    status = req.status 
                else:
                    status = None  
                response.append({
                    "id": note.id,
                    "title": note.title,
                    "file_link": note.file_link,
                    "file_name": note.file_name,
                    "profile": note.profile,
                    "access": access,
                    "status": status,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at,
                })
            return Response({"data": response})
        else: 
            for note in Allnotes:
                response.append({
                    "id": note.id,
                    "title": note.title,
                    "file_link": note.file_link,
                    "file_name": note.file_name,
                    "profile": note.profile,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at,
                })
            return Response({"data": response})

class AllGroups(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        response = []
        if not request.user.is_superuser:
            Allgroups = prof_group.objects.filter(profile__user=request.user).order_by("-id")
            for pg in Allgroups:
                group = pg.group
                response.append({
                    "id": group.id,
                    "name": group.name,
                    "created_at": group.created_at,
                    "updated_at": group.updated_at,
                })
            return Response({"data": response})
        else: 
            Allgroups = prof_group.objects.filter().order_by("-id")
            for pg in Allgroups:
                group = pg.group
                response.append({
                    "id": group.id,
                    "name": group.name,
                    "created_at": group.created_at,
                    "updated_at": group.updated_at,
                })
            return Response({"data": response})


    def post(self, request):
        data = json.loads(request.body)
        query = data.get('query')
        response=[]
        if not request.user.is_superuser:
            Allgroups = prof_group.objects.filter(name__icontains=query, profile__user=request.user).order_by("-id")
            for pg in Allgroups:
                group = pg.group
                response.append({
                    "id": group.id,
                    "name": group.name,
                    "created_at": group.created_at,
                    "updated_at": group.updated_at,
                })
            return Response({"data": response})
        else: 
            Allgroups = prof_group.objects.filter(name__icontains=query).order_by("-id")
            for pg in Allgroups:
                group = pg.group
                response.append({
                    "id": group.id,
                    "name": group.name,
                    "created_at": group.created_at,
                    "updated_at": group.updated_at,
                })
            return Response({"data": response})
        
    def delete(self, request):
        if not request.user.is_superuser:
            return Response({"error": "no permision accsess"}, status=403)
        data = json.loads(request.body)
        group_id = data.get('group_id')
        group = get_object_or_404(groups, id=group_id)
        group.delete()
        return Response({"status": "group deleted"}, status=200)

class GroupInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, group_id):
        pg = prof_group.objects.filter(group__id=group_id).order_by("-id")
        ng = note_group.objects.filter(group__id=group_id).order_by("-id")
        response=[]
        if not request.user.is_superuser:
            profile = profiles.objects.get(user=request.user)
            if pg.profile == profile:
                users = []
                notes = []
                for item in pg:
                    if item.profile.user.is_superuser:
                        continue
                    users.append({
                        "user_id": item.profile.user.id,
                        "prof_id": item.profile.id,
                        "name": item.profile.user.username,
                    })
                for item in ng:
                    notes.append({
                        "id": item.note.id,
                        "title": item.note.title,
                        "file_name": item.note.file_name,
                        "updated_at": item.note.updated_at
                    })
                response.append({
                    "user":users,
                    "notes":notes
                })
                return Response({"data": response}, status=200)
            else:
                return Response({"error": "no permision"}, status=403)
        else:
            users = []
            notes = []
            for item in pg:
                if item.profile.user.is_superuser:
                    continue
                users.append({
                    "user_id": item.profile.user.id,
                    "prof_id": item.profile.id,
                    "name": item.profile.user.username,
                })
            for item in ng:
                notes.append({
                    "id": item.note.id,
                    "title": item.note.title,
                    "file_name": item.note.file_name,
                    "updated_at": item.note.updated_at
                })
            response.append({
                "user":users,
                "notes":notes
            })
            return Response({"data": response}, status=200)
        
    def post(self, request, group_id):
        data = json.loads(request.body)
        query = data.get('query', '')
        action = data.get('action', '')
        if action == "search":
            ng = note_group.objects.filter(group__id=group_id, note__title__icontains=query).order_by("-id")

            response=[]
            notes = []
            for item in ng:
                notes.append({
                    "id": item.note.id,
                    "title": item.note.title,
                    "file_name": item.note.file_name,
                    "updated_at": item.note.updated_at
                })
            response.append({
                "notes":notes
            })
            return Response({"data": response}, status=200)
        elif action == "select_add_user":
            pg = prof_group.objects.filter(
                group__id=group_id
            ).values_list('profile', flat=True)

            profiles_not_in_group = profiles.objects.exclude(
                id__in=pg
            ).order_by("-id")
            users = []
            for item in profiles_not_in_group:
                if item.profile.user.is_superuser:
                    continue
                users.append({
                    "user_id": item.user.id,
                    "prof_id": item.id,
                    "name": item.user.username,
                })
            return Response({"users": users}, status=200)

        elif action == "select_user_in_group":
            pg = prof_group.objects.filter(
                group__id=group_id
            ).values_list('profile', flat=True)

            profiles_not_in_group = profiles.objects.filter(
                id__in=pg
            ).order_by("-id")
            users = []
            for item in profiles_not_in_group:
                if item.profile.user.is_superuser:
                    continue
                users.append({
                    "user_id": item.user.id,
                    "prof_id": item.id,
                    "name": item.user.username,
                })
            return Response({"users": users}, status=200)
        elif action == "add_user":
            user_id = data.get("user_id")
            pg = prof_group.objects.get_or_create(
                group__id=group_id,
                profile__user__id=user_id
            )
            # нужно потом запросить данные на тех кто есть в группе и тех кого нет
            
            #TODO
            
            
            
        elif action == "remove_user":
            user_id = data.get("user_id")
            pg = prof_group.objects.get(
                group__id=group_id,
                profile__user__id=user_id
            )
            
            #TODO

class Create(APIView):
    pass

class UserNotes(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, user_id):

        
        Allnotes = notes.objects.filter(profile__user__id=user_id).order_by("-id")

        response = []
        for note in Allnotes:
            response.append({
                "id": note.id,
                "title": note.title,
                "file_link": note.file_link,
                "file_name": note.file_name,
                "profile": note.profile,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            })
        return Response({"data": response})
    
    def post(self, request, user_id):
        data = json.loads(request.body)
        query = data.get('query')  
        
        if query:
            Allnotes = notes.objects.filter(profile__user__id=user_id, title__icontains=query).order_by("-id")
        else:
            Allnotes = notes.objects.filter(profile__user__id=user_id).order_by("-id")

        response = []
        for note in Allnotes:
            response.append({
                "id": note.id,
                "title": note.title,
                "file_link": note.file_link,
                "file_name": note.file_name,
                "profile": note.profile,
                "created_at": note.created_at,
                "updated_at": note.updated_at,
            })
        return Response({"data": response})

class Note(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, note_id):
        profile = profiles.objects.get(user=request.user)
        note = get_object_or_404(notes,id=note_id)
        if profile.user.is_superuser:
            return Response({
                "data": {
                    "id": note.id,
                    "title": note.title,
                    "file_link": note.file_link,
                    "file_name": note.file_name,
                    "profile": note.profile,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at,
                    }
            })
        else:
            an = accesseble_notes.objects.filter(note=note,profile=profile)
            if an.exists():
                return Response({
                    "data": {
                        "id": note.id,
                        "title": note.title,
                        "file_link": note.file_link,
                        "file_name": note.file_name,
                        "profile": note.profile,
                        "created_at": note.created_at,
                        "updated_at": note.updated_at,
                        }
                })
            else:
                return Response({
                    "error": "no permision"
                })
    
    def post(self, request, note_id):
        profile = profiles.objects.get(user=request.user)
        if profile.user.is_superuser:
            return Response({"error": "to edit notes can onli users"})
        
        try:
            note = notes.objects.get(id=note_id)
        except notes.DoesNotExist:
            return Response({"error": "Note not found"}, status=404)
        
        if note.profile != profile:
            an = accesseble_notes.objects.filter(note=note, profile=profile)
            if not an.exists():
                return Response({
                    "error": "no permision"
                })
                
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        
        if title:
            note.title = title
        if description:
            note.description = description
        note.save()
        
        return Response({
            "message": "Note updated",
            "note": {
                "id": note.id,
                "title": note.title,
                "description": note.description,
                "updated_at": note.updated_at
            }
        }, status=204)
        


    def delete(self, request, note_id):
        profile = profiles.objects.get(user=request.user)
        if profile.user.is_superuser:
            return Response({"error": "to edit notes can onli users"}, status=403)
        
        try:
            note = notes.objects.get(id=note_id)
        except notes.DoesNotExist:
            return Response({"error": "Note not found"}, status=404)
        
        if note.profile != profile:
            an = accesseble_notes.objects.filter(note=note, profile=profile)
            if not an.exists():
                return Response({
                    "error": "no permision"
                })
        
        note.delete()
        return Response({
            "message": "Note deleted successfully"
        }, status=204)
    
class Statistics(APIView):
    permission_classes = (permissions.IsAdminUser,)
    """
    {
        "requests_by_last_7_days": [
            {"day": 5, "month": 4, "year": 2026, "count": 32},
            {"day": 6, "month": 4, "year": 2026, "count": 28},
            {"day": 7, "month": 4, "year": 2026, "count": 45},
            {"day": 8, "month": 4, "year": 2026, "count": 38},
            {"day": 9, "month": 4, "year": 2026, "count": 41},
            {"day": 10, "month": 4, "year": 2026, "count": 35},
            {"day": 11, "month": 4, "year": 2026, "count": 26}
        ],
        "top_5_users": [
            {"username": "john_doe", "prof_id": 5, "total_requests": 87},
            {"username": "anna_smith", "prof_id": 12, "total_requests": 54},
            {"username": "mike_johnson", "prof_id": 8, "total_requests": 43},
            {"username": "lisa_williams", "prof_id": 3, "total_requests": 38},
            {"username": "tom_brown", "prof_id": 15, "total_requests": 29}
        ]
    }
    """
    def get(self, request):
        last_7_days = timezone.now() - timedelta(days=7)
        requests_by_day = statistics.objects.filter(
            created_at__gte=last_7_days
        ).extra(
            {'day': "DATE(created_at)"}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        requests_7_d = []
        
        for item in requests_by_day:
            date_obj = item['day']  
            
            year = date_obj.year    
            month = date_obj.month    
            day = date_obj.day  
            
            requests_7_d.append({
                "day": day,
                "month": month,
                "year": year,
                "count": item['count']
                
            })     
            
        top_5_users = statistics.objects.values(
            username = 'prof_id__user__username',  
            prof_id = 'prof_id__id'               
        ).annotate(
            total_requests=Count('id')
        ).order_by('-total_requests')[:5]
        return Response({
            "requests_by_last_7_days": requests_7_d,
            "top_5_users": list(top_5_users)
        })


class ProfileContent(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        try:
            user = request.GET.get('user')
        except:
            user = request.user
        
        if user.is_superuser:
            return Response({"error": "notes can have only user"}, status=404)
        
        usr_notes = notes.objects.filter(profile__user=user).order_by("-id")
        response = []
        for item in usr_notes:
            response.append({
                "id": item.id,
                "title": item.title,
                "file_link": item.file_link,
                "file_name": item.file_name,
                "profile": item.profile,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            })
            
        return Response({"data": response})
    
    def post(self, request):
        if not request.user.is_superuser:
            return Response({"error": "only admins"}, status=403)
        data = json.loads(request.body)
        type = data.get('type')
        try:
            user = request.GET.get('user')
        except:
            return Response({"error": "missing user"}, status=404)
        if type == "server":
            data = json.loads(request.body)
            query = data.get('query', '')  
            
            if query:
                usr_notes = notes.objects.filter(profile__user=user, title__icontains=query).order_by("-id")
            else:
                usr_notes = notes.objects.filter(profile__user=user).order_by("-id")

            response = []
            for item in usr_notes:
                response.append({
                    "id": item.id,
                    "title": item.title,
                    "file_link": item.file_link,
                    "file_name": item.file_name,
                    "profile": item.profile,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                })
                
            return Response({"data": response})
        
        if type == "groups":
            data = json.loads(request.body)
            query = data.get('query', '')  
            
            pg = prof_group.objects.filter(profile__user=user)
            
            if query:
                pg = user_groups.filter(group__name__icontains=query)
            response = []
            for item in pg:
                response.append({
                    "id": item.group.id,
                    "name": item.group.name,
                    "created_at": item.group.created_at,
                    "updated_at": item.group.updated_at,
                })
                
            return Response({"data": response})
        
        if type == "adding_to_groups":
            all_groups = groups.objects.all()
            
            user_group_ids = prof_group.objects.filter(
                profile__user=user
            ).values_list('group', flat=True)
            
            user_group_ids_set = set(user_group_ids)
            
            response = []
            for group in all_groups:
                response.append({
                    "id": group.id,
                    "name": group.name,
                    "in_groupe": group.id in user_group_ids_set,
                    "created_at": group.created_at,
                    "updated_at": group.updated_at,
                })
            return Response({"data": response})
        
        if type == "add_to_groups":
            data = json.loads(request.body)
            group_id = data.get('group_id')
            
            # Получаем объекты
            group = groups.objects.get(id=group_id)
            profile = profiles.objects.get(user=user)
            
            # Создаем связь
            user_groups = prof_group.objects.create(
                group=group,
                profile=profile
            )
            return Response({"status": "added"})
        
        if type == "delete_from_groups":
            data = json.loads(request.body)
            group_id = data.get('group_id')
            
            # Получаем объекты
            group = groups.objects.get(id=group_id)
            profile = profiles.objects.get(user=user)
            
            # Создаем связь
            user_groups = prof_group.objects.filter(
                group=group,
                profile=profile
            )
            if not user_groups.exists():
                return Response({"error": "not exists"})

            user_groups.delete()
            return Response({"status": "deleted"})
        
        # доделать запрос локальных

        

