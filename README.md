# Django Todo App — JWT Authentication & MySQL

[![Tests](https://github.com/ngohuy04022000/EntranceTest-Python/actions/workflows/tests.yml/badge.svg)](https://github.com/ngohuy04022000/EntranceTest-Python/actions/workflows/tests.yml)

A task management (to-do) web application built with **Django 4**, **Django REST Framework**, and **JWT authentication** (SimpleJWT), using **MySQL** as the database.

## Features

- User sign-up / sign-in / sign-out; all pages require login (the user list is admin-only)
- Create and delete to-do lists
- Add, update, and delete tasks (description, due date, status)
- Access token / refresh token issued via JWT (`/get-token/`, `/refresh-token/`)
- API tested with Postman (screenshots in the [`postman/`](postman) folder)

## Tech stack

| Layer      | Technology                                   |
|------------|----------------------------------------------|
| Backend    | Python, Django 4.0, Django REST Framework    |
| Auth       | JWT (djangorestframework-simplejwt)          |
| Database   | MySQL                                        |
| Frontend   | Django Templates, HTML/CSS                   |

## Project structure

```
todo_project/
├── config/                  # Django configuration (settings, urls, wsgi)
├── todo/                    # Main app: models, views, serializers, templates
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

## Running tests

```bash
cd todo_project
DB_ENGINE=sqlite python manage.py test
```

Setting `DB_ENGINE=sqlite` lets the tests run without a MySQL server. GitHub Actions runs the suite on every push against both SQLite and MySQL 8.

## Main endpoints

| Method | URL                                   | Description            |
|--------|---------------------------------------|------------------------|
| GET/POST | `/signup/`                          | Sign up                |
| GET/POST | `/signin/`                          | Sign in                |
| GET    | `/signout/`                           | Sign out               |
| GET    | `/`                                   | List of to-do lists    |
| POST   | `/list/add/`                          | Create a list          |
| POST   | `/list/<id>/item/add/`                | Add a task             |
| POST   | `/list/<id>/item/<pk>/`               | Update a task          |
| POST   | `/list/<id>/item/<pk>/delete/`        | Delete a task          |
| POST   | `/get-token/`                         | Obtain a JWT token     |
| POST   | `/refresh-token/`                     | Refresh a JWT token    |
