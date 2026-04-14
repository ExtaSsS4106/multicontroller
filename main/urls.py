from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('all_users/', views.all_users, name='all_users'),
    path('profile/', views.profile, name='profile'),
    path('user-notes/<int:user_id>/', views.user_notes, name='user_notes'),
    path('note/<int:note_id>/', views.note, name='note-detail'),
    path('register/', views.register, name='register'),

]
