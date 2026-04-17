from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.
class profiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=45)
    
    
class notes(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, null=False)
    description = models.CharField(max_length=255, null=False)
    file_link = models.FileField(upload_to='files/', null=True)
    file_name = models.CharField(max_length=255, null=True)
    file_hash = models.CharField(max_length=255, null=True)
    profile = models.ForeignKey(profiles, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class groups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
       
class requests(models.Model):
    id = models.AutoField(primary_key=True)
    TYPE_CHOICES = [('pending', 'Pending'),('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    profile = models.ForeignKey(profiles, on_delete=models.CASCADE)
    note = models.ForeignKey(notes, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   
    status = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
class statistics(models.Model):
    id = models.AutoField(primary_key=True)
    TYPE_CHOICES = [('create', 'Create'), ('delete', 'Delete'), ('update', 'Update')]
    profile = models.ForeignKey(profiles, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class prof_group(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(profiles, on_delete=models.CASCADE)
    group = models.ForeignKey(groups, on_delete=models.CASCADE)

class accesseble_notes(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(profiles, on_delete=models.CASCADE)
    note = models.ForeignKey(notes, on_delete=models.CASCADE)
    
class group_an(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(groups, on_delete=models.CASCADE)
    accesseble_notes = models.ForeignKey(accesseble_notes, on_delete=models.CASCADE)

class note_group(models.Model):
    id = models.AutoField(primary_key=True)
    note = models.ForeignKey(notes, on_delete=models.CASCADE)
    group = models.ForeignKey(groups, on_delete=models.CASCADE)