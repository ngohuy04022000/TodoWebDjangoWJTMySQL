from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import ToDoItem, ToDoList
from .serializers import TodoSerializer


class ModelTests(TestCase):
    def setUp(self):
        self.todo_list = ToDoList.objects.create(title="Work")

    def test_list_str_and_absolute_url(self):
        self.assertEqual(str(self.todo_list), "Work")
        self.assertEqual(
            self.todo_list.get_absolute_url(),
            reverse("list", args=[self.todo_list.id]),
        )

    def test_item_default_dates_are_computed_at_creation(self):
        before = timezone.now()
        item = ToDoItem.objects.create(
            id="1", task="Write tests", status=False, todo_list=self.todo_list
        )
        self.assertGreaterEqual(item.created_date, before)
        due_in = item.due_date - item.created_date
        self.assertAlmostEqual(due_in.total_seconds(), 7 * 24 * 3600, delta=5)

    def test_item_str(self):
        item = ToDoItem.objects.create(
            id="1", task="Write tests", status=False, todo_list=self.todo_list
        )
        self.assertTrue(str(item).startswith("Write tests: due "))

    def test_serializer_fields(self):
        item = ToDoItem.objects.create(
            id="1", task="Write tests", status=True, todo_list=self.todo_list
        )
        data = TodoSerializer(item).data
        self.assertEqual(data["task"], "Write tests")
        self.assertTrue(data["status"])
        self.assertEqual(data["todo_list"], self.todo_list.id)


class AuthViewTests(TestCase):
    def test_signup_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "password1": "S3cure-pass",
                "password2": "S3cure-pass",
            },
        )
        self.assertRedirects(response, "/")
        user = User.objects.get(username="alice")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "password1": "S3cure-pass",
                "password2": "other-pass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="alice").exists())

    def test_signup_rejects_duplicate_username(self):
        User.objects.create_user(username="alice", password="S3cure-pass")
        response = self.client.post(
            reverse("register"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "password1": "S3cure-pass",
                "password2": "S3cure-pass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="alice").count(), 1)

    def test_signin(self):
        User.objects.create_user(username="alice", password="S3cure-pass")
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": "S3cure-pass"}
        )
        self.assertRedirects(response, reverse("index"))


class JWTTests(TestCase):
    def setUp(self):
        User.objects.create_user(username="alice", password="S3cure-pass")

    def test_obtain_and_refresh_token(self):
        response = self.client.post(
            "/get-token/", {"username": "alice", "password": "S3cure-pass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

        response = self.client.post(
            "/refresh-token/", {"refresh": response.json()["refresh"]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_invalid_credentials_rejected(self):
        response = self.client.post(
            "/get-token/", {"username": "alice", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 401)


class AccessControlTests(TestCase):
    def setUp(self):
        self.todo_list = ToDoList.objects.create(title="Work")

    def test_anonymous_user_is_redirected_to_signin(self):
        urls = [
            reverse("index"),
            reverse("index-user"),
            reverse("list", args=[self.todo_list.id]),
            reverse("list-add"),
            reverse("list-delete", args=[self.todo_list.id]),
            reverse("item-add", args=[self.todo_list.id]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_anonymous_user_cannot_create_list(self):
        self.client.post(reverse("list-add"), {"title": "Home"})
        self.assertFalse(ToDoList.objects.filter(title="Home").exists())

    def test_user_page_is_staff_only(self):
        User.objects.create_user(username="alice", password="S3cure-pass")
        self.client.login(username="alice", password="S3cure-pass")
        self.assertEqual(self.client.get(reverse("index-user")).status_code, 403)

        User.objects.create_user(username="admin", password="S3cure-pass", is_staff=True)
        self.client.login(username="admin", password="S3cure-pass")
        response = self.client.get(reverse("index-user"))
        self.assertEqual(response.status_code, 200)


class TodoCrudTests(TestCase):
    def setUp(self):
        self.todo_list = ToDoList.objects.create(title="Work")
        User.objects.create_user(username="alice", password="S3cure-pass")
        self.client.login(username="alice", password="S3cure-pass")

    def test_index_lists_todo_lists(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Work")

    def test_create_and_delete_list(self):
        response = self.client.post(reverse("list-add"), {"title": "Home"})
        home = ToDoList.objects.get(title="Home")
        self.assertRedirects(response, reverse("list", args=[home.id]))

        response = self.client.post(reverse("list-delete", args=[home.id]))
        self.assertRedirects(response, reverse("index"))
        self.assertFalse(ToDoList.objects.filter(title="Home").exists())

    def test_create_update_delete_item(self):
        list_url = reverse("list", args=[self.todo_list.id])
        due = (timezone.now() + timezone.timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        response = self.client.post(
            reverse("item-add", args=[self.todo_list.id]),
            {
                "todo_list": self.todo_list.id,
                "id": "1",
                "task": "Write tests",
                "description": "Cover the CRUD views",
                "created_date": now,
                "due_date": due,
            },
        )
        self.assertRedirects(response, list_url)
        item = ToDoItem.objects.get(id="1")
        self.assertEqual(item.task, "Write tests")
        self.assertFalse(item.status)
        self.assertContains(self.client.get(list_url), "Write tests")

        response = self.client.post(
            reverse("item-update", args=[self.todo_list.id, 1]),
            {
                "todo_list": self.todo_list.id,
                "id": "1",
                "task": "Write more tests",
                "description": "",
                "modification_date": now,
                "status": "on",
                "due_date": due,
            },
        )
        self.assertRedirects(response, list_url)
        item.refresh_from_db()
        self.assertEqual(item.task, "Write more tests")
        self.assertTrue(item.status)

        response = self.client.post(
            reverse("item-delete", args=[self.todo_list.id, 1])
        )
        self.assertRedirects(response, list_url)
        self.assertFalse(ToDoItem.objects.filter(id="1").exists())

    def test_list_view_only_shows_its_own_items(self):
        other = ToDoList.objects.create(title="Home")
        ToDoItem.objects.create(id="1", task="Work task", status=False, todo_list=self.todo_list)
        ToDoItem.objects.create(id="2", task="Home task", status=False, todo_list=other)

        response = self.client.get(reverse("list", args=[self.todo_list.id]))
        self.assertContains(response, "Work task")
        self.assertNotContains(response, "Home task")
