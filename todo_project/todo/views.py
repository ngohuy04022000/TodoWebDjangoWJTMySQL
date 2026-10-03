from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import RegistrationForm, ToDoItemForm, ToDoListForm
from .models import ToDoItem, ToDoList


def register(request):
    if request.user.is_authenticated:
        return redirect("index")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("index")
    return render(request, "pages/register.html", {"form": form})


class ListUserView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "todo/index_user.html"
    ordering = ["username"]

    def test_func(self):
        return self.request.user.is_staff


class OwnedListMixin(LoginRequiredMixin):
    """Resolves the list from the URL, restricted to lists owned by the current user."""

    def get_todo_list(self):
        if not hasattr(self, "_todo_list"):
            self._todo_list = get_object_or_404(
                ToDoList, id=self.kwargs["list_id"], owner=self.request.user
            )
        return self._todo_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["todo_list"] = self.get_todo_list()
        return context


class ListListView(LoginRequiredMixin, ListView):
    template_name = "todo/index.html"

    def get_queryset(self):
        return ToDoList.objects.filter(owner=self.request.user)


class ListCreate(LoginRequiredMixin, CreateView):
    model = ToDoList
    form_class = ToDoListForm
    extra_context = {"title": "Thêm danh sách mới"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = ToDoList(owner=self.request.user)
        return kwargs


class ListDelete(LoginRequiredMixin, DeleteView):
    model = ToDoList
    success_url = reverse_lazy("index")

    def get_queryset(self):
        return ToDoList.objects.filter(owner=self.request.user)


class ItemListView(OwnedListMixin, ListView):
    template_name = "todo/todo_list.html"

    def get_queryset(self):
        return self.get_todo_list().items.all()


class ItemCreate(OwnedListMixin, CreateView):
    model = ToDoItem
    form_class = ToDoItemForm
    extra_context = {"title": "Thêm công việc mới"}

    def form_valid(self, form):
        form.instance.todo_list = self.get_todo_list()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])


class ItemUpdate(OwnedListMixin, UpdateView):
    model = ToDoItem
    form_class = ToDoItemForm
    extra_context = {"title": "Chỉnh sửa công việc"}

    def get_queryset(self):
        return self.get_todo_list().items.all()

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])


class ItemDelete(OwnedListMixin, DeleteView):
    model = ToDoItem

    def get_queryset(self):
        return self.get_todo_list().items.all()

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])
