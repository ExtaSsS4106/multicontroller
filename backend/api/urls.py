from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from .views import (
    RegisterView, ProfileView, LogoutView,
    AllUsers, AllNotes, Groups, GroupInfo, CreateGroup,
    UserNotes, Note, Statistics, ProfileContent, Requests, CreateNote, Adding_to_groups, for_addingGroupInfo
)

urlpatterns = [

    path('api/register/', RegisterView.as_view(), name='register'),
    
    path('api/profile/', ProfileView.as_view(), name='profile'),
    
    path('api/logout/', LogoutView.as_view(), name='logout'),
    
    path('api/all-users/', AllUsers.as_view(), name='all-users'),
    
    path('api/user-notes/<int:user_id>/', UserNotes.as_view(), name='user-notes'),

    path('api/all-notes/', AllNotes.as_view(), name='all-notes'),
    
    path('api/note/<int:note_id>/', Note.as_view(), name='note-detail'),
    
    path('api/groups/', Groups.as_view(), name='groups'),
    
    path('api/group-info/<int:group_id>/', GroupInfo.as_view(), name='group-info'),
    path('api/group-info-for-adding/<int:group_id>/', for_addingGroupInfo.as_view(), name='group-info-for-adding'),
    
    path('api/create-group/', CreateGroup.as_view(), name='create-group'),

    path('api/statistics/', Statistics.as_view(), name='statistics'),

    path('api/profile-content/', ProfileContent.as_view(), name='profile-content'),
    
    path('api/create-note/', CreateNote.as_view(), name='create-note'),

    path('api/requests/', Requests.as_view(), name='requests'),
    
    path('api/adding/<int:prof_id>/', Adding_to_groups.as_view(), name='adding'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
