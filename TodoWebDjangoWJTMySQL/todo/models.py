from django.utils import timezone

from django.db import models
from django.urls import reverse

def date_time(x):
    return timezone.now() + timezone.timedelta(days=x)

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
    id = models.IntegerField
    task = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    user_id = models.IntegerField
    completion_date = models.DateTimeField(default=date_time(7))
    status = models.BooleanField(auto_created=True)
    created_date = models.DateTimeField(default=date_time(0))
    due_date = models.DateTimeField(default=date_time(7))
    todo_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse(
            "item-update", args=[str(self.todo_list.id), str(self.id)]
        )

    def __str__(self):
        return f"{self.title}: due {self.due_date}"

    class Meta:
        ordering = ["due_date"]