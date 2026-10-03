# Django Todo App — JWT Authentication & MySQL

[![Tests](https://github.com/ngohuy04022000/django-todo-jwt-api/actions/workflows/tests.yml/badge.svg)](https://github.com/ngohuy04022000/django-todo-jwt-api/actions/workflows/tests.yml)

A task management (to-do) application built with **Django 5.2 LTS**, offering both a server-rendered web UI and a **REST API** secured with **JWT authentication** (SimpleJWT), backed by **MySQL**.

## Features

- User sign-up (with Django password validation), sign-in and sign-out
- Every user has their own private to-do lists; other users' data is never visible (404)
- Create and delete lists; add, update, complete and delete tasks (description, due date, status)
- REST API for lists and tasks under `/api/`, authenticated with JWT access/refresh tokens
- Admin-only member list; Django admin for lists and tasks
- Automated tests (web views, access control, API) run in GitHub Actions on SQLite and MySQL 8
- UI screenshots in the [`postman/`](postman) folder

## Tech stack

| Layer      | Technology                                   |
|------------|----------------------------------------------|
| Backend    | Python 3.10+, Django 5.2, Django REST Framework |
| Auth       | JWT (djangorestframework-simplejwt)          |
| Database   | MySQL                                        |
| Frontend   | Django Templates, HTML/CSS                   |

## Project structure

```
todo_project/
├── config/                  # Django configuration (settings, urls, wsgi)
├── todo/                    # Main app: models, views, forms, REST API, templates, tests
├── manage.py
└── requirements.txt
postman/                     # API test screenshots
```

## Running locally

1. Install dependencies:
   ```bash
   cd todo_project
   pip install -r requirements.txt
   ```
2. Create a MySQL database (e.g. `todo_app`), then set the connection environment variables:
   ```bash
   export DB_NAME=todo_app
   export DB_USER=root
   export DB_PASSWORD=your_password
   export DB_HOST=127.0.0.1
   export DB_PORT=3306
   ```
   Optional variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`True`/`False`), `DJANGO_ALLOWED_HOSTS` (comma-separated).
3. Initialize the database and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
4. Open: http://127.0.0.1:8000/signin/

To use the admin pages (`/admin/` and the member list at `/users/`), create an admin account with `python manage.py createsuperuser`.

> Upgrading an existing database: `migrate` assigns lists created before per-user ownership to the oldest superuser (or the oldest user), and converts task IDs to auto-increment numbers.

## Running tests

```bash
cd todo_project
DB_ENGINE=sqlite python manage.py test
```

Setting `DB_ENGINE=sqlite` lets the tests run without a MySQL server. GitHub Actions runs the suite on every push against both SQLite and MySQL 8.

## Web pages

| URL                                 | Description                      |
|-------------------------------------|----------------------------------|
| `/signup/`                          | Sign up                          |
| `/signin/`                          | Sign in                          |
| `/signout/` (POST)                  | Sign out                         |
| `/`                                 | Your to-do lists                 |
| `/list/add/`                        | Create a list                    |
| `/list/<id>/`                       | Tasks in a list                  |
| `/list/<id>/delete/`                | Delete a list                    |
| `/list/<id>/item/add/`              | Add a task                       |
| `/list/<id>/item/<item_id>/`        | Edit a task                      |
| `/list/<id>/item/<item_id>/delete/` | Delete a task                    |
| `/users/`                           | Member list (staff only)         |

## REST API

Obtain a token, then send it as `Authorization: Bearer <access>`:

```bash
curl -X POST http://127.0.0.1:8000/get-token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "alice", "password": "your_password"}'
# -> {"refresh": "...", "access": "..."}

curl http://127.0.0.1:8000/api/lists/ -H "Authorization: Bearer <access>"
```

| Method                  | URL                   | Description                                         |
|-------------------------|-----------------------|-----------------------------------------------------|
| POST                    | `/get-token/`         | Obtain access + refresh tokens                      |
| POST                    | `/refresh-token/`     | Get a new access token from a refresh token         |
| GET, POST               | `/api/lists/`         | List / create your to-do lists                      |
| GET, PUT, PATCH, DELETE | `/api/lists/<id>/`    | Read / update / delete a list                       |
| GET, POST               | `/api/items/`         | List / create tasks (filters: `?list=<id>`, `?status=true\|false`) |
| GET, PUT, PATCH, DELETE | `/api/items/<id>/`    | Read / update / delete a task                       |

Access tokens are valid for 15 minutes and refresh tokens for 1 day. List responses are paginated (20 per page).
