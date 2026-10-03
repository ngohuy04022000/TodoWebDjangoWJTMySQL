from rest_framework import serializers

from .models import ToDoItem, ToDoList


class ToDoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDoList
        fields = ["id", "title"]

    def validate_title(self, title):
        owner = self.context["request"].user
        duplicates = ToDoList.objects.filter(owner=owner, title__iexact=title)
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError("You already have a list with this title.")
        return title


class TodoSerializer(serializers.ModelSerializer):
    todo_list = serializers.PrimaryKeyRelatedField(queryset=ToDoList.objects.none())

    class Meta:
        model = ToDoItem
        fields = [
            "id",
            "todo_list",
            "task",
            "description",
            "due_date",
            "status",
            "created_date",
            "modification_date",
        ]
        read_only_fields = ["created_date", "modification_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None and request.user.is_authenticated:
            # Only allow items to be placed in the requesting user's own lists.
            self.fields["todo_list"].queryset = ToDoList.objects.filter(owner=request.user)
