from django.contrib import admin
from todo.models import ToDoItem, ToDoList, UserList

admin.site.register(ToDoItem)
admin.site.register(ToDoList)
admin.site.register(UserList)