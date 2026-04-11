from django.contrib import admin
from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Наши эндпоинты
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    
    path('api/getUsers/', AllUsers.as_view(), name='allusers'),
    path('api/getNotes/', AllNotes.as_view(), name='allnotes'),
    path('api/getUserNotes/', UserNotes.as_view(), name='usernotes'),
    
    path('api/note/<int:note_id>', Note.as_view(), name='note'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
