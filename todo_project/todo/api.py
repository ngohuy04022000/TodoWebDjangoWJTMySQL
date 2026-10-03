from rest_framework import permissions, viewsets

from .models import ToDoItem, ToDoList
from .serializers import ToDoListSerializer, TodoSerializer


class ToDoListViewSet(viewsets.ModelViewSet):
    """CRUD for the authenticated user's to-do lists."""

    serializer_class = ToDoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ToDoList.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ToDoItemViewSet(viewsets.ModelViewSet):
    """CRUD for items in the authenticated user's lists.

    Filter by list with ``?list=<id>`` and by completion with ``?status=true|false``.
    """

    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = ToDoItem.objects.filter(todo_list__owner=self.request.user)
        list_id = self.request.query_params.get("list")
        if list_id is not None and list_id.isdigit():
            queryset = queryset.filter(todo_list_id=list_id)
        status = self.request.query_params.get("status")
        if status in ("true", "false"):
            queryset = queryset.filter(status=status == "true")
        return queryset
