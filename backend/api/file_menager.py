# views.py
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import notes, accesseble_notes
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
import uuid

class UploadFile(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, note_id):
        file = request.FILES.get('file')
        
        if not file or not note_id:
            return Response({"error": "No file or note_id"}, status=400)
        note = get_object_or_404(notes, id=note_id)
        
        hash_value = uuid.uuid4().hex
        while notes.objects.filter(file_hash=hash_value).exists():
            hash_value = uuid.uuid4().hex
        
        # Сохраняем файл
        file_path = default_storage.save(f'uploads/{hash_value}/{file.name}', ContentFile(file.read()))
        
        # Создаём заметку с файлом
        note.file_hash = hash_value  # Используем уникальный хэш для файла
        note.file_name = file.name
        note.file_link = file_path
        note.save()
        
        return Response({
            "status": "success",
            "note_id": note.id,
            "file_name": file.name,
            "file_path": file_path
        }, status=200)
        
class DownloadFile(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, file_hash):
        note = get_object_or_404(notes, file_hash=file_hash)
        
        if not note.file_link:
            raise Http404("File not found")
        
        # Проверка доступа

        return FileResponse(note.file_link.open(), as_attachment=True, filename=note.file_name)