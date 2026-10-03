from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from todo import api, views

router = DefaultRouter()
router.register("lists", api.ToDoListViewSet, basename="api-list")
router.register("items", api.ToDoItemViewSet, basename="api-item")

urlpatterns = [
    path("signup/", views.register, name="register"),
    path(
        "signin/",
        auth_views.LoginView.as_view(
            template_name="pages/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("signout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.ListListView.as_view(), name="index"),
    path("users/", views.ListUserView.as_view(), name="index-user"),
    # CRUD patterns for ToDoLists
    path("list/add/", views.ListCreate.as_view(), name="list-add"),
    path("list/<int:list_id>/", views.ItemListView.as_view(), name="list"),
    path("list/<int:pk>/delete/", views.ListDelete.as_view(), name="list-delete"),
    # CRUD patterns for ToDoItems
    path("list/<int:list_id>/item/add/", views.ItemCreate.as_view(), name="item-add"),
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
    # REST API (JWT authentication)
    path("api/", include(router.urls)),
]
