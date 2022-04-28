from rest_framework import serializers
from .models import Todo

class LoginSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=256)
    username = serializers.CharField(max_length=128)
    password = serializers.CharField(write_only=True,
                                     required=True,
                                     style={
                                         'input_type': 'password',
                                         'placeholder': 'password'
                                     })

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = [  "Id",
                    "Task",
                    "Description",
                    "UserId" , 
                    "CompletionDate",
                    "Status",
                    "CreationDate",
                    "Modificationdate"]