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
import json
from django.urls import reverse
import os
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
class AmIsuperUser(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.is_superuser:
            status = True
        else:
            status = False
        return Response({"status_admin": status})
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

class ProfileInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        profile = get_object_or_404(profiles, user__id=user_id)
        response = {
            "user_id": profile.user.id,
            "profile_id": profile.id,
            "username": profile.user.username,
            "email": profile.user.email,
            "date_joined": profile.user.date_joined,
        }
        return Response(response)

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
        profiles_ = profiles.objects.all().order_by('-id')
        response = []
        for p in profiles_:
            response.append({
                                "profile_id": p.id,
                                "username": p.user.username,
                                "user_id": p.user.id,
                            })
        return Response(response)
    
    def post(self, request):
        data = json.loads(request.body)
        query = data.get('query')
        
        if query:
            profiles_ = profiles.objects.filter(user__username__icontains=query).order_by('-id')
        else:
            return Response({"error": "Not found"}, status=404)
        response = []
        for p in profiles_:
            response.append({
                                "profile_id": p.id,
                                "username": p.user.username,
                                "user_id": p.user.id,
                            })
        return Response(response)
    
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
                    status_val = req.status 
                else:
                    status_val = None  
                response.append({
                    "id": note.id,
                    "title": note.title,
                    "file_link": str(note.file_link) if note.file_link else None,
                    "file_name": note.file_name,
                    "user_id": note.profile.user.id,
                    "access": access,
                    "status": status_val,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at.strftime("%d.%m.%Y %H:%M"),
                })
            return Response({"data": response})
        else: 
            for note in Allnotes:
                response.append({
                    "id": note.id,
                    "title": note.title,
                    "file_link": str(note.file_link) if note.file_link else None,
                    "file_name": note.file_name,
                    "user_id": note.profile.user.id,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at.strftime("%d.%m.%Y %H:%M"),
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
                    status_val = req.status 
                else:
                    status_val = None  
                response.append({
                    "id": note.id,
                    "title": note.title,
                    "file_link": str(note.file_link) if note.file_link else None,
                    "file_name": note.file_name,
                    "user_id": note.profile.user.id,
                    "access": access,
                    "status": status_val,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at.strftime("%d.%m.%Y %H:%M"),
                })
            return Response({"data": response})
        else: 
            for note in Allnotes:
                response.append({
                    "id": note.id,
                    "title": note.title,
                    "file_link": str(note.file_link) if note.file_link else None,
                    "file_name": note.file_name,
                    "user_id": note.profile.user.id,
                    "created_at": note.created_at,
                    "updated_at": note.updated_at.strftime("%d.%m.%Y %H:%M"),
                })
            return Response({"data": response})

class Groups(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        response = []
        if not request.user.is_superuser:
            # Получаем ID групп, в которых состоит пользователь
            group_ids = prof_group.objects.filter(
                profile__user=request.user
            ).values_list('group_id', flat=True)

            # Получаем сами группы
            groups_ = groups.objects.filter(id__in=group_ids).order_by("-id")
            for group in groups_:
                response.append({
                    "id": group.id,
                    "name": group.name,
                    "created_at": group.created_at,
                    "updated_at": group.updated_at,
                })
            return Response({"data": response})
        else: 
            groups_ = groups.objects.filter().order_by("-id")
            for group in groups_:
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
            Allgroups = prof_group.objects.filter(group__name__icontains=query, profile__user=request.user).order_by("-id")
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
            Allgroups = prof_group.objects.filter(group__name__icontains=query).order_by("-id")
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
    
class for_addingGroupInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, group_id):
        group = get_object_or_404(groups, id=group_id)
        pg = prof_group.objects.filter(group=group).order_by("-id")
        ng = note_group.objects.filter(group=group).order_by("-id")
        profile_ids = pg.values_list('profile_id', flat=True)  
        profiles_ = profiles.objects.exclude(id__in=profile_ids).order_by("-id")
        response=[]
        if not request.user.is_superuser:
            profile = profiles.objects.get(user=request.user)
            if pg.filter(profile=profile).exists():
                users = []
                notes = []
                for item in profiles_:
                    if item.profile.user.is_superuser:
                        continue
                    users.append({
                        "user_id": item.user.id,
                        "prof_id": item.id,
                        "name": item.user.username,
                    })
                for item in ng:
                    notes.append({
                        "id": item.note.id,
                        "title": item.note.title,
                        "file_name": item.note.file_name,
                        "updated_at": item.note.updated_at.strftime("%d.%m.%Y %H:%M"),
                    })
                response= {
                    "users":users,
                    "notes":notes,
                    "group_title":group.name,
                    "group_id":group.id,
                }
                return Response({"data": response}, status=200)
            else:
                return Response({"error": "no permision"}, status=403)
        else:
            users = []
            notes = []
            for item in profiles_:
                if item.user.is_superuser:
                    continue
                users.append({
                    "user_id": item.user.id,
                    "prof_id": item.id,
                    "name": item.user.username,
                })
            for item in ng:
                notes.append({
                    "id": item.note.id,
                    "title": item.note.title,
                    "file_name": item.note.file_name,
                    "updated_at": item.note.updated_at.strftime("%d.%m.%Y %H:%M"),
                })
            response= {
                    "users":users,
                    "notes":notes,
                    "group_title":group.name,
                    "group_id":group.id,
                }
            return Response({"data": response}, status=200)
class GroupInfo(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, group_id):
        group = get_object_or_404(groups, id=group_id)
        pg = prof_group.objects.filter(group=group).order_by("-id")
        ng = note_group.objects.filter(group=group).order_by("-id")
        if not request.user.is_superuser:
            profile = profiles.objects.get(user=request.user)
            if pg.filter(profile=profile).exists():
                users = []
                notes = []
                accessible_note_ids = accesseble_notes.objects.filter(
                    profile=profile
                ).values_list('note_id', flat=True)
                for item in pg:
                    if item.profile.user.is_superuser:
                        continue
                    users.append({
                        "user_id": item.profile.user.id,
                        "prof_id": item.profile.id,
                        "name": item.profile.user.username,
                    })
                for item in ng:
                    request_obj = requests.objects.filter(note=item.note, profile=profile).first()
                    notes.append({
                        "id": item.note.id,
                        "title": item.note.title,
                        "file_name": item.note.file_name,
                        "is_accessible": item.note.id in accessible_note_ids,
                        "request_id": request_obj.id if request_obj else -1,
                        "status_request": request_obj.status if request_obj else "no_request",
                        "updated_at": item.note.updated_at.strftime("%d.%m.%Y %H:%M"),
                    })
                response= {
                    "users":users,
                    "notes":notes,
                    "group_title":group.name,
                    "group_id":group.id,

                }
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
                    "updated_at": item.note.updated_at.strftime("%d.%m.%Y %H:%M"),
                })
            response= {
                    "users":users,
                    "notes":notes,
                    "group_title":group.name,
                    "group_id":group.id,
                }
            return Response({"data": response}, status=200)
        
    def post(self, request, group_id):
        data = json.loads(request.body)
        notes_query = data.get('notes_query', '')
        users_query = data.get('users_query', '')

        action = data.get('action', '')
        group = groups.objects.get(id=group_id)

        if action == "search":
            if notes_query != '':
                ng = note_group.objects.filter(group__id=group_id, note__title__icontains=notes_query).order_by("-id")
            else:
                ng = note_group.objects.filter(group__id=group_id).order_by("-id")

            if users_query !='':
                pg = prof_group.objects.filter(group__id=group_id, profile__user__username__icontains=users_query).order_by("-id")
            else:
                pg = prof_group.objects.filter(group__id=group_id).order_by("-id")
            notes_ = []
            users= []
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
            response = {
                "notes":notes_,
                "users": users,
                "notes_query": notes_query,
                "users_query": users_query
            }
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
                if item.user.is_superuser:
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

            profiles_in_group = profiles.objects.filter(
                id__in=pg
            ).order_by("-id")
            users = []
            for item in profiles_in_group:
                if item.user.is_superuser:
                    continue
                users.append({
                    "user_id": item.user.id,
                    "prof_id": item.id,
                    "name": item.user.username,
                })
            return Response({"users": users}, status=200)
        elif action == "add_user":
            user_id = data.get("user_id")
            profile = profiles.objects.get(user__id=user_id)
            notes_ = notes.objects.filter(profile=profile)
            for note in notes_:
                ng, __ = note_group.objects.get_or_create(
                    group=group,
                    note=note
                )
            pg, __ = prof_group.objects.get_or_create(
                group=group,
                profile=profile
            )
            return Response({"status": "added"}, status=200)

        elif action == "remove_user":
            user_id = data.get("user_id")
            
            try:
                # Получаем профиль пользователя
                profile = profiles.objects.get(user__id=user_id)
                
                # Удаляем все связи note_group для этого пользователя в группе
                notes_ = notes.objects.filter(profile=profile)
                note_group.objects.filter(
                    group=group,
                    note__in=notes_
                ).delete()
                
                # Удаляем связь prof_group
                deleted_count, _ = prof_group.objects.filter(
                    group=group,
                    profile=profile
                ).delete()
                
                if deleted_count == 0:
                    return Response({"error": "User not in this group"}, status=404)
                
                return Response({"status": "deleted"}, status=200)
                
            except profiles.DoesNotExist:
                return Response({"error": "Profile not found"}, status=404)
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        #TODO

class CreateGroup(APIView):
    permission_classes = (permissions.IsAdminUser,)
    def get(self, request):
        profiles_ = profiles.objects.all().order_by("-id")
        response = []
        for profile in profiles_:
            if profile.user.is_superuser:
                continue
            response.append({
                "user_id": profile.user.id,
                "prof_id": profile.id,
                "name": profile.user.username,
            })

        
        return Response({"data": response}, status=200)
    def post(self, request):
        data = json.loads(request.body)
        name = data.get('name')
        users_id = data.get('users_id')
        group = groups.objects.create(
            name = name
        )
        for user_id in users_id:
            prof = profiles.objects.get(user__id = user_id)
            if prof.user.is_superuser:
                continue
            prof_group.objects.create(
                profile=prof,
                group=group
            )
            users_notes = notes.objects.filter(profile=prof)
            for note in users_notes:
                note_group.objects.create(
                    note=note,
                    group=group
                )
        return Response({"group_id": group.id}, status=200)
        
class UserNotes(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, user_id):

        
        Allnotes = notes.objects.filter(profile__user__id=user_id).order_by("-id")
        prof = profiles.objects.get(user__id=user_id)
        response = []
        for note in Allnotes:
            response.append({
                "id": note.id,
                "username": note.profile.user.username,
                "title": note.title,
                "file_name": note.file_name,
                "user_id": note.profile.user.id,
                "created_at": note.created_at.strftime("%d.%m.%Y %H:%M"),
                "updated_at": note.updated_at.strftime("%d.%m.%Y %H:%M"),
            })
        return Response({"data": response, "prof_id": prof.id})
    
    def post(self, request, user_id):
        data = json.loads(request.body)
        query = data.get('query')  
        profile = get_object_or_404(profiles, user__id=user_id)
        if query:
            Allnotes = notes.objects.filter(profile=profile, title__icontains=query).order_by("-id")
        else:
            Allnotes = notes.objects.filter(profile=profile).order_by("-id")

        response = []
        for note in Allnotes:
            response.append({
                "id": note.id,
                "username": note.profile.user.username,
                "title": note.title,
                "file_name": note.file_name,
                "user_id": note.profile.user.id,
                "created_at": note.created_at.strftime("%d.%m.%Y %H:%M"),
                "updated_at": note.updated_at.strftime("%d.%m.%Y %H:%M"),
            })
        return Response({"data": response, "username": profile.user.username,})

class Note(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, note_id):
        profile = profiles.objects.get(user=request.user)
        note = get_object_or_404(notes,id=note_id)
        download_url = None
        if note.file_link:
            relative_url = reverse('download-file', args=[note.file_hash])
            download_url = request.build_absolute_uri(relative_url)
        if profile.user.is_superuser:
            return Response({
                    
                    "id": note.id,
                    "title": note.title,
                    "file_link": str(note.file_link) if note.file_link else None,
                    "file_name": note.file_name,
                    "user_id": note.profile.user.id,
                    "description": note.description,
                    "username": note.profile.user.username,
                    "created_at": note.created_at.strftime("%d.%m.%Y %H:%M"),
                    "updated_at": note.updated_at.strftime("%d.%m.%Y %H:%M"),
                    "download_url": download_url
            })
        else:
            an = accesseble_notes.objects.filter(note=note,profile=profile)
            if an.exists():
                return Response({
                        
                        "id": note.id,
                        "title": note.title,
                        "file_link": str(note.file_link) if note.file_link else None,
                        "file_name": note.file_name,
                        "user_id": note.profile.user.id,
                        "description": note.description,
                        "username": note.profile.user.username,
                        "created_at": note.created_at.strftime("%d.%m.%Y %H:%M"),
                        "updated_at": note.updated_at.strftime("%d.%m.%Y %H:%M"),
                        "download_url": download_url
                })
            else:
                return Response({
                    "error": "no permission"  
                }, status=status.HTTP_403_FORBIDDEN) 
    
    def post(self, request, note_id):
        profile = profiles.objects.get(user=request.user)
        if profile.user.is_superuser:
            return Response({"error": "to edit notes can only users"})
        
        try:
            note= notes.objects.get(id=note_id)
        except notes.DoesNotExist:
            return Response({"error": "Note not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if note.profile != profile:
            an = accesseble_notes.objects.filter(note=note, profile=profile)
            if not an.exists():
                return Response({
                    "error": "no permission"
                }, status=status.HTTP_403_FORBIDDEN)
                
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        
        if title:
            note.title = title
        if description:
            note.description = description
        note.save()
        
        statistics.objects.create(
            profile=profile,
            action='update'
        )
        return Response({
            "message": "Note updated",
            "note": {
                "id": note.id,
                "title": note.title,
                "description": note.description,
                "updated_at": note.updated_at
            }
        }, status=status.HTTP_200_OK)
        


    def delete(self, request, note_id):
        profile = profiles.objects.get(user=request.user)
        
        try:
            note = notes.objects.get(id=note_id)
        except notes.DoesNotExist:
            return Response({"error": "Note not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # ✅ Правильная проверка прав
        has_permission = False
        
        if request.user.is_superuser:
            has_permission = True
        elif note.profile == profile:
            has_permission = True
        else:
            # Проверяем доступ через accesseble_notes
            an = accesseble_notes.objects.filter(note=note, profile=profile)
            if an.exists():
                has_permission = True
        
        if not has_permission:
            return Response({
                "error": "no permission"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Удаляем файл если есть
        if note.file_link:
            try:
                file_path = note.file_link.path
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        
        # Удаляем папку с хэшем если есть
        if note.file_hash:
            file_hash_path = os.path.join('media', 'uploads', note.file_hash)
            if os.path.exists(file_hash_path):
                import shutil
                shutil.rmtree(file_hash_path)
        
        note.delete()
        
        statistics.objects.create(
            profile=profile,
            action='delete',
        )
        
        return Response({
            "message": "Note deleted successfully"
        }, status=status.HTTP_200_OK)  # 200 вместо 204
    
class CreateNote(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        if request.user.is_superuser:
            return Response({"error": "no permision"}, status=status.HTTP_403_FORBIDDEN)
        try:
            data = json.loads(request.body)
        except:
            return Response({"details": "missed json body"})

        title = data.get('title')
        description = data.get('description')
        if not data and not title and not description:
            return Response({"details": "missed params: data, title, description"})
        profile = profiles.objects.get(user=request.user)
        note = notes.objects.create(
            profile=profile,
            description=description,
            title=title
        )
        accesseble_notes.objects.create(
            profile=profile,
            note=note
        )
        statistics.objects.create(
            profile=profile,
            action='create',
        )
        return Response({
            "message": "Note added",
            "note": {
                "id": note.id,
                "title": note.title,
                "description": note.description,
                "updated_at": note.updated_at
            }
        }, status=status.HTTP_200_OK)
        
class Statistics(APIView):
    permission_classes = (permissions.IsAdminUser,)

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
        
        # Исправленный top_5_users
        top_5_users = statistics.objects.values(
            'profile__user__username',
            'profile__user__id'
        ).annotate(
            total_requests=Count('id')
        ).order_by('-total_requests')[:5]
        
        # Преобразуем в нужный формат
        top_5_users_list = []
        for user in top_5_users:
            top_5_users_list.append({
                'username': user['profile__user__username'],
                'user_id': user['profile__user__id'],
                'total_requests': user['total_requests']
            })
        
        return Response({
            "requests_by_last_7_days": requests_7_d,
            "top_5_users": top_5_users_list
        })


class ProfileContent(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):

        user = request.user
        profile_ = profiles.objects.get(user=user)
        if user.is_superuser:
                return Response({"error": "user reqired"}, status=403)

        usr_notes = notes.objects.filter(profile__user=user).order_by("-id")
        response = []
        for item in usr_notes:
            response.append({
                "id": item.id,
                "title": item.title,
                "file_link":  str(item.file_link) if item.file_link else None,
                "file_name": item.file_name,
                "user_id": item.profile.user.id,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            })
            
        return Response({"data": response})
    
    def post(self, request):

        data = json.loads(request.body)
        type = data.get('type')
        try:
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
        except:
            user = request.user
            
        if user.is_superuser:
            return Response({"error": "user reqired"}, status=403)
        
        if type == "profile":
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            profile_ = profiles.objects.get(user=user)
            if user.is_superuser:
                    return Response({"error": "user reqired"}, status=403)

            usr_notes = notes.objects.filter(profile__user=user).order_by("-id")
            response = []
            for item in usr_notes:
                response.append({
                    "id": item.id,
                    "title": item.title,
                    "file_link":  str(item.file_link) if item.file_link else None,
                    "file_name": item.file_name,
                    "user_id": item.profile.user.id,
                    "created_at": item.created_at.strftime("%d.%m.%Y %H:%M"),
                    "updated_at": item.updated_at.strftime("%d.%m.%Y %H:%M"),
                })
                
            return Response({"data": response})
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
                    "file_link":  str(item.file_link) if item.file_link else None,
                    "file_name": item.file_name,
                    "user_id": item.profile.user.id,
                    "created_at": item.created_at.strftime("%d.%m.%Y %H:%M"),
                    "updated_at": item.updated_at.strftime("%d.%m.%Y %H:%M"),
                })
                
            return Response({"data": response})
        
        if type == "groups":
            data = json.loads(request.body)
            query = data.get('query', '')  
            
            pg = prof_group.objects.filter(profile__user=user)
            
            if query:
                pg = pg.filter(group__name__icontains=query)
            response = []
            for item in pg:
                response.append({
                    "id": item.group.id,
                    "name": item.group.name,
                    "created_at": item.group.created_at.strftime("%d.%m.%Y %H:%M"),
                    "updated_at": item.group.updated_at.strftime("%d.%m.%Y %H:%M"),
                })
                
            return Response({"data": response})
        

        
        # доделать запрос локальных

        if type == "local":
            pass
            #TODO
           
class Adding_to_groups(APIView):
    def get(self, request, prof_id):
        prof = get_object_or_404(profiles, id=prof_id)
        if not request.user.is_superuser:
            return Response({"error": "only admins"}, status=403)
        
        all_groups = groups.objects.all()
        
        user_group_ids = prof_group.objects.filter(
            profile=prof
        ).values_list('group', flat=True)
        
        user_group_ids_set = set(user_group_ids)
        
        response = []
        for group in all_groups:
            response.append({
                "id": group.id,
                "name": group.name,
                "in_group": group.id in user_group_ids_set,  
                "created_at": group.created_at,
                "updated_at": group.updated_at,
            })
        return Response({"data": response, "prof_id": prof.id, "username": prof.user.username,})
    
    def post(self, request, prof_id): 
        
        profile = get_object_or_404(profiles, id=prof_id)
        if profile.user.is_superuser:
            return Response({"error": "admin cant be in groups"}, status=403)
        data = json.loads(request.body)
        type = data.get('type')
        if type == "add_to_groups":
            if not request.user.is_superuser:
                return Response({"error": "only admins"}, status=403)
            
            data = json.loads(request.body)
            group_id = data.get('group_id')
            
            # Получаем объекты
            group = groups.objects.get(id=group_id)
            
            # Создаем связь
            prof_group_obj, created = prof_group.objects.get_or_create(
                group=group,
                profile=profile
            )
            
            if created:
                return Response({"status": "added"})
            else:
                return Response({"status": "already_exists"}, status=status.HTTP_200_OK)
        
        if type == "delete_from_groups":
            if not request.user.is_superuser:
                return Response({"error": "only admins"}, status=403)
            
            data = json.loads(request.body)
            group_id = data.get('group_id')
            if not group_id:
                return Response({"error": "group_id required"}, status=403)
            # Получаем объекты
            group = groups.objects.get(id=group_id)
            
            # Создаем связь
            user_groups = prof_group.objects.filter(
                group=group,
                profile=profile
            )
            if not user_groups.exists():
                return Response({"error": "not exists"})
            user_groups.delete()
            return Response({"status": "deleted"})   
        
    
class Requests(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        response = []
        if request.user.is_superuser:
            all_req_list = requests.objects.all().order_by("-id")
            for req_item in all_req_list:
                if req_item.status == 'rejected' or req_item.status == 'approved':
                    continue
                response.append({
                    "id": req_item.id,
                    "user_id": req_item.profile.user.id,
                    "username": req_item.profile.user.username,
                    "note_id": req_item.note.id,
                    "note_title": req_item.note.title,
                    "created_at": req_item.created_at.strftime("%d.%m.%Y %H:%M"),
                    "updated_at": req_item.updated_at.strftime("%d.%m.%Y %H:%M"),
                    "status": req_item.status
                })
        else:
            profile = profiles.objects.get(user=request.user)
            all_req_list = requests.objects.filter(profile=profile).order_by("-id")
            for req_item in all_req_list:
                if req_item.status == 'rejected' or req_item.status == 'approved':
                    continue
                response.append({
                    "id": req_item.id,
                    "user_id": req_item.profile.user.id,
                    "username": req_item.profile.user.username,
                    "note_id": req_item.note.id,
                    "note_title": req_item.note.title,
                    "created_at": req_item.created_at.strftime("%d.%m.%Y %H:%M"),
                    "updated_at": req_item.updated_at.strftime("%d.%m.%Y %H:%M"),
                    "status": req_item.status
                })
        return Response({"data": response}, status=200)
    def post(self, request):
        data = json.loads(request.body)
        action = data.get('action')
        
        profile = profiles.objects.get(user=request.user)
        details = []
        print(data)
        if action == "pending" and not request.user.is_superuser:
            note_id = data.get('note_id')
            request_id = data.get('request_id')
            note = get_object_or_404(notes, id=note_id)
            an = accesseble_notes.objects.filter(profile=profile, note=note)
            
            if an.exists():
                return Response({"details": "you already have access for this note"})
            
            profile_obj = profiles.objects.get(user=request.user)
            if request_id != -1:
                existing_request = requests.objects.get(
                    id=request_id,
                )
                if existing_request.status == "pending":
                    details.append({"error": "Request already exists"})
                else:
                    # Если запрос есть, но статус не pending (например rejected)
                    # Можно обновить или создать новый
                    req = requests.objects.update(
                        profile=profile_obj,
                        note=note,
                        status="pending"
                    )
                    req = requests.objects.get(id=request_id)
                    details.append({"request_id": req.id})
            else:
                # Запроса нет - создаём новый
                req = requests.objects.create(
                    profile=profile_obj,
                    note=note,
                    status="pending"
                )
                details.append({"request_id": req.id})
                
        elif action == "approved" and request.user.is_superuser:
            request_id = data.get('request_id')
            note_id = data.get('note_id')
            note = get_object_or_404(notes, id=note_id)
            profile = profiles.objects.get(user__id=data.get('user_id'))
            an, created = accesseble_notes.objects.get_or_create(
                profile=profile,
                note=note
            )

            requests.objects.filter(id=request_id).update(status='approved')
        elif action=="cancel":
            request_id = data.get('request_id')
            requests.objects.filter(id=request_id).update(status='rejected')
        return Response({"status": action, "details": details}, status=200)