from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class User(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    profile_id = fields.IntField()
    name = fields.CharField(max_length=255)
    token = fields.CharField(max_length=255, null=True)
    refresh = fields.CharField(max_length=255, null=True)
    
    class Meta:
        table = "users"
    
    def __str__(self):
        return self.name

class Notes(models.Model):
    id = fields.IntField(pk=True)
    server_id = fields.IntField(null=True)  # ID заметки на сервере
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    file_link = fields.CharField(max_length=500, null=True)
    file_name = fields.CharField(max_length=255, null=True)
    file_hash = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "notes"
    
    def __str__(self):
        return self.title

# Pydantic модели для сериализации
User_Pydantic = pydantic_model_creator(User, name="User")
Note_Pydantic = pydantic_model_creator(Notes, name="Note")


