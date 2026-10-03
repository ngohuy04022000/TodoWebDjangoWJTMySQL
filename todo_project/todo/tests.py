from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import ToDoItem, ToDoList
from .serializers import TodoSerializer

PASSWORD = "S3cure-pass!"


def make_user(username, **extra):
    return User.objects.create_user(username=username, password=PASSWORD, **extra)


class ModelTests(TestCase):
    def setUp(self):
        self.owner = make_user("alice")
        self.todo_list = ToDoList.objects.create(owner=self.owner, title="Work")

    def test_list_str_and_absolute_url(self):
        self.assertEqual(str(self.todo_list), "Work")
        self.assertEqual(
            self.todo_list.get_absolute_url(),
            reverse("list", args=[self.todo_list.id]),
        )

    def test_item_defaults(self):
        before = timezone.now()
        item = ToDoItem.objects.create(task="Write tests", todo_list=self.todo_list)
        self.assertFalse(item.status)
        self.assertEqual(item.description, "")
        self.assertGreaterEqual(item.created_date, before)
        due_in = item.due_date - item.created_date
        self.assertAlmostEqual(due_in.total_seconds(), 7 * 24 * 3600, delta=5)

    def test_item_ids_are_generated(self):
        first = ToDoItem.objects.create(task="One", todo_list=self.todo_list)
        second = ToDoItem.objects.create(task="Two", todo_list=self.todo_list)
        self.assertEqual(second.id, first.id + 1)

    def test_modification_date_updates_on_save(self):
        item = ToDoItem.objects.create(task="Write tests", todo_list=self.todo_list)
        previous = item.modification_date
        item.task = "Write more tests"
        item.save()
        self.assertGreater(item.modification_date, previous)

    def test_item_str(self):
        item = ToDoItem.objects.create(task="Write tests", todo_list=self.todo_list)
        self.assertTrue(str(item).startswith("Write tests: due "))

    def test_same_title_allowed_for_different_owners(self):
        ToDoList.objects.create(owner=make_user("bob"), title="Work")
        self.assertEqual(ToDoList.objects.filter(title="Work").count(), 2)

    def test_serializer_fields(self):
        item = ToDoItem.objects.create(
            task="Write tests", status=True, todo_list=self.todo_list
        )
        data = TodoSerializer(item).data
        self.assertEqual(data["task"], "Write tests")
        self.assertTrue(data["status"])
        self.assertEqual(data["todo_list"], self.todo_list.id)


class AuthViewTests(TestCase):
    def signup(self, **overrides):
        data = {
            "username": "alice",
            "email": "alice@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        data.update(overrides)
        return self.client.post(reverse("register"), data)

    def test_signup_creates_user_and_logs_in(self):
        response = self.signup()
        self.assertRedirects(response, reverse("index"))
        user = User.objects.get(username="alice")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    def test_signup_rejects_mismatched_passwords(self):
        response = self.signup(password2="other-pass!")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="alice").exists())

    def test_signup_rejects_weak_password(self):
        response = self.signup(password1="1", password2="1")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="alice").exists())

    def test_signup_rejects_duplicate_username(self):
        make_user("Alice")
        response = self.signup()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username__iexact="alice").count(), 1)

    def test_signup_rejects_duplicate_email(self):
        make_user("bob", email="alice@example.com")
        response = self.signup()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="alice").exists())

    def test_signin_redirects_to_next(self):
        make_user("alice")
        add_url = reverse("list-add")
        response = self.client.post(
            reverse("login"),
            {"username": "alice", "password": PASSWORD, "next": add_url},
        )
        self.assertRedirects(response, add_url)

    def test_signin_without_next_goes_to_index(self):
        make_user("alice")
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": PASSWORD, "next": ""}
        )
        self.assertRedirects(response, reverse("index"))

    def test_signout_requires_post(self):
        make_user("alice")
        self.client.login(username="alice", password=PASSWORD)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class JWTTests(TestCase):
    def setUp(self):
        make_user("alice")

    def test_obtain_and_refresh_token(self):
        response = self.client.post(
            "/get-token/", {"username": "alice", "password": PASSWORD}
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
        self.alice = make_user("alice")
        self.bob = make_user("bob")
        self.alice_list = ToDoList.objects.create(owner=self.alice, title="Alice private")
        self.alice_item = ToDoItem.objects.create(task="Secret", todo_list=self.alice_list)

    def test_anonymous_user_is_redirected_to_signin(self):
        urls = [
            reverse("index"),
            reverse("index-user"),
            reverse("list", args=[self.alice_list.id]),
            reverse("list-add"),
            reverse("list-delete", args=[self.alice_list.id]),
            reverse("item-add", args=[self.alice_list.id]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_user_page_is_staff_only(self):
        self.client.login(username="bob", password=PASSWORD)
        self.assertEqual(self.client.get(reverse("index-user")).status_code, 403)

        make_user("admin", is_staff=True)
        self.client.login(username="admin", password=PASSWORD)
        self.assertContains(self.client.get(reverse("index-user")), "alice")

    def test_other_users_lists_are_hidden_and_protected(self):
        self.client.login(username="bob", password=PASSWORD)
        list_id = self.alice_list.id
        item_id = self.alice_item.id

        self.assertNotContains(self.client.get(reverse("index")), "Alice private")
        self.assertEqual(self.client.get(reverse("list", args=[list_id])).status_code, 404)
        self.assertEqual(
            self.client.post(reverse("list-delete", args=[list_id])).status_code, 404
        )
        self.assertEqual(
            self.client.post(
                reverse("item-add", args=[list_id]), {"task": "Injected"}
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse("item-update", args=[list_id, item_id]), {"task": "Hacked"}
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(reverse("item-delete", args=[list_id, item_id])).status_code,
            404,
        )

        self.alice_item.refresh_from_db()
        self.assertEqual(self.alice_item.task, "Secret")
        self.assertTrue(ToDoList.objects.filter(id=list_id).exists())
        self.assertFalse(ToDoItem.objects.filter(task="Injected").exists())

    def test_item_url_must_match_its_list(self):
        self.client.login(username="alice", password=PASSWORD)
        other_list = ToDoList.objects.create(owner=self.alice, title="Other")
        response = self.client.get(
            reverse("item-update", args=[other_list.id, self.alice_item.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_missing_list_returns_404(self):
        self.client.login(username="alice", password=PASSWORD)
        self.assertEqual(self.client.get(reverse("list", args=[999])).status_code, 404)


class TodoCrudTests(TestCase):
    def setUp(self):
        self.user = make_user("alice")
        self.todo_list = ToDoList.objects.create(owner=self.user, title="Work")
        self.client.login(username="alice", password=PASSWORD)

    def test_index_lists_own_todo_lists(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, "Work")

    def test_create_and_delete_list(self):
        response = self.client.post(reverse("list-add"), {"title": "Home"})
        home = ToDoList.objects.get(title="Home")
        self.assertEqual(home.owner, self.user)
        self.assertRedirects(response, reverse("list", args=[home.id]))

        response = self.client.post(reverse("list-delete", args=[home.id]))
        self.assertRedirects(response, reverse("index"))
        self.assertFalse(ToDoList.objects.filter(title="Home").exists())

    def test_duplicate_list_title_shows_form_error(self):
        response = self.client.post(reverse("list-add"), {"title": "work"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(ToDoList.objects.filter(owner=self.user).count(), 1)

    def test_invalid_item_form_shows_errors(self):
        response = self.client.post(
            reverse("item-add", args=[self.todo_list.id]), {"task": ""}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("task", response.context["form"].errors)

    def test_create_update_delete_item(self):
        list_url = reverse("list", args=[self.todo_list.id])
        due = (timezone.now() + timezone.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")

        response = self.client.post(
            reverse("item-add", args=[self.todo_list.id]),
            {"task": "Write tests", "description": "Cover the CRUD views", "due_date": due},
        )
        self.assertRedirects(response, list_url)
        item = ToDoItem.objects.get(task="Write tests")
        self.assertEqual(item.todo_list, self.todo_list)
        self.assertFalse(item.status)
        self.assertContains(self.client.get(list_url), "Write tests")

        response = self.client.post(
            reverse("item-update", args=[self.todo_list.id, item.id]),
            {"task": "Write more tests", "description": "", "status": "on", "due_date": due},
        )
        self.assertRedirects(response, list_url)
        item.refresh_from_db()
        self.assertEqual(item.task, "Write more tests")
        self.assertTrue(item.status)

        response = self.client.get(reverse("item-delete", args=[self.todo_list.id, item.id]))
        self.assertContains(response, "Write more tests")
        response = self.client.post(reverse("item-delete", args=[self.todo_list.id, item.id]))
        self.assertRedirects(response, list_url)
        self.assertFalse(ToDoItem.objects.filter(id=item.id).exists())

    def test_list_view_only_shows_its_own_items(self):
        other = ToDoList.objects.create(owner=self.user, title="Home")
        ToDoItem.objects.create(task="Work task", todo_list=self.todo_list)
        ToDoItem.objects.create(task="Home task", todo_list=other)

        response = self.client.get(reverse("list", args=[self.todo_list.id]))
        self.assertContains(response, "Work task")
        self.assertNotContains(response, "Home task")


class APITests(TestCase):
    def setUp(self):
        self.alice = make_user("alice")
        self.bob = make_user("bob")
        self.client = APIClient()
        token = self.client.post(
            "/get-token/", {"username": "alice", "password": PASSWORD}, format="json"
        ).json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_requires_authentication(self):
        anonymous = APIClient()
        self.assertEqual(anonymous.get("/api/lists/").status_code, 401)
        self.assertEqual(anonymous.get("/api/items/").status_code, 401)

    def test_session_login_does_not_authenticate_api(self):
        browser = APIClient()
        browser.login(username="alice", password=PASSWORD)
        self.assertEqual(browser.get("/api/lists/").status_code, 401)

    def test_list_crud(self):
        response = self.client.post("/api/lists/", {"title": "Work"}, format="json")
        self.assertEqual(response.status_code, 201)
        list_id = response.json()["id"]
        self.assertEqual(ToDoList.objects.get(id=list_id).owner, self.alice)

        response = self.client.post("/api/lists/", {"title": "work"}, format="json")
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(f"/api/lists/{list_id}/", {"title": "Job"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Job")

        self.assertEqual(self.client.delete(f"/api/lists/{list_id}/").status_code, 204)
        self.assertFalse(ToDoList.objects.filter(id=list_id).exists())

    def test_item_crud_and_filters(self):
        work = ToDoList.objects.create(owner=self.alice, title="Work")
        home = ToDoList.objects.create(owner=self.alice, title="Home")

        response = self.client.post(
            "/api/items/", {"todo_list": work.id, "task": "Write report"}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        item_id = response.json()["id"]
        self.client.post("/api/items/", {"todo_list": home.id, "task": "Cook"}, format="json")

        response = self.client.get(f"/api/items/?list={work.id}")
        self.assertEqual([i["task"] for i in response.json()["results"]], ["Write report"])

        response = self.client.patch(f"/api/items/{item_id}/", {"status": True}, format="json")
        self.assertTrue(response.json()["status"])
        response = self.client.get("/api/items/?status=true")
        self.assertEqual([i["id"] for i in response.json()["results"]], [item_id])

        self.assertEqual(self.client.delete(f"/api/items/{item_id}/").status_code, 204)

    def test_cannot_access_or_use_other_users_lists(self):
        bob_list = ToDoList.objects.create(owner=self.bob, title="Bob private")
        bob_item = ToDoItem.objects.create(task="Bob task", todo_list=bob_list)

        response = self.client.get("/api/lists/")
        self.assertEqual(response.json()["count"], 0)
        self.assertEqual(self.client.get(f"/api/lists/{bob_list.id}/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/items/{bob_item.id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/lists/{bob_list.id}/").status_code, 404)

        response = self.client.post(
            "/api/items/", {"todo_list": bob_list.id, "task": "Injected"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ToDoItem.objects.filter(task="Injected").exists())
