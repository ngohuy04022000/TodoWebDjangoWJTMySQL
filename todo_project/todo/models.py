from django.utils import timezone

from django.db import models
from django.urls import reverse

def date_time(x):
    return timezone.now() + timezone.timedelta(days=x)

def default_due_date():
    return date_time(7)

class UserList(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    email = models.CharField(max_length=40)

class ToDoList(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def get_absolute_url(self):
        return reverse("list", args=[self.id])

    def __str__(self):
        return self.title

class ToDoItem(models.Model):
# "Id",
# "Task",
# "Description",
# "UserId" , 
# "CompletionDate",
# "Status",
# "CreationDate",
# "Modificationdate"
    id = models.CharField(primary_key=True, max_length=5)
    task = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(default=default_due_date)
    status = models.BooleanField(auto_created=True)
    created_date = models.DateTimeField(default=timezone.now)
    modification_date = models.DateTimeField(default=timezone.now)
    todo_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse(
            "item-update", args=[str(self.todo_list.id), str(self.id)]
        )

    def __str__(self):
        return f"{self.task}: due {self.due_date}"

    class Meta:
        ordering = ["due_date"]