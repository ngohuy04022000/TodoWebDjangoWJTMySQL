from telnetlib import AUTHENTICATION
from django.urls import path
from todo import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("signup/", views.Register, name="register"),
    path("signin/", auth_views.LoginView.as_view(template_name="pages/login.html",next_page='index'), name="login"),
    path("signout/", auth_views.LogoutView.as_view(next_page='login'),name='logout'),
    path("", views.ListListView.as_view(), name="index"),
    path("user", views.ListUserView.as_view(), name="index-user"),
    path("list/<int:list_id>/", views.ItemListView.as_view(), name="list"),
    # CRUD patterns for ToDoLists
    path("list/add/", views.ListCreate.as_view(), name="list-add"),
    path(
        "list/<int:pk>/delete/", views.ListDelete.as_view(), name="list-delete"
    ),
    # CRUD patterns for ToDoItems
    path(
        "list/<int:list_id>/item/add/",
        views.ItemCreate.as_view(),
        name="item-add",
    ),
    path(
        "list/<int:list_id>/item/<int:pk>/",
        views.ItemUpdate.as_view(),
        name="item-update",
    ),
    path(
        "list/<int:list_id>/item/<int:pk>/delete/",
        views.ItemDelete.as_view(),
        name="item-delete",
    ),
]