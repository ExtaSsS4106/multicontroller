from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('all_users/', views.all_users, name='all_users'),
    path('all_notes/', views.all_notes, name='all_notes'),
    path('profile_content/', views.profile_content, name='profile_content'),
    path('user-notes/<int:user_id>/', views.user_notes, name='user_notes'),
    path('note/<int:note_id>/', views.note, name='note-detail'),
    path('register/', views.register, name='register'),
    path('adding/<int:prof_id>/', views.adding, name='adding'),
    path('groups/', views.groups, name='groups'),
    path('group/<int:group_id>/', views.group, name='group'),
    path('group_adding_users/<int:group_id>/', views.group_adding_users, name='group_adding_users'),
    path('create_group/', views.create_group, name='create_group'),
    path('requests/', views.requests, name='requests'),

]
