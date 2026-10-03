from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


def default_due_date():
    return timezone.now() + timezone.timedelta(days=7)


class ToDoList(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="todo_lists",
    )
    title = models.CharField(max_length=100)

    class Meta:
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "title"], name="unique_list_title_per_owner"
            ),
        ]

    def get_absolute_url(self):
        return reverse("list", args=[self.id])

    def __str__(self):
        return self.title


class ToDoItem(models.Model):
    todo_list = models.ForeignKey(
        ToDoList, on_delete=models.CASCADE, related_name="items"
    )
    task = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    due_date = models.DateTimeField(default=default_due_date)
    status = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date"]

    def get_absolute_url(self):
        return reverse("item-update", args=[self.todo_list_id, self.id])

    def __str__(self):
        return f"{self.task}: due {self.due_date}"
