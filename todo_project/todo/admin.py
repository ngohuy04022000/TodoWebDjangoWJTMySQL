from django.contrib import admin

from todo.models import ToDoItem, ToDoList


@admin.register(ToDoList)
class ToDoListAdmin(admin.ModelAdmin):
    list_display = ("title", "owner")
    list_filter = ("owner",)
    search_fields = ("title",)


@admin.register(ToDoItem)
class ToDoItemAdmin(admin.ModelAdmin):
    list_display = ("task", "todo_list", "due_date", "status")
    list_filter = ("status",)
    search_fields = ("task", "description")
