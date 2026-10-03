# Django Todo App — JWT Authentication & MySQL

A task management (to-do) web application built with **Django 4**, **Django REST Framework**, and **JWT authentication** (SimpleJWT), using **MySQL** as the database.

## Features

- User sign-up / sign-in / sign-out
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
TodoWebDjangoWJTMySQL/
├── TodoWebDjangoWJTMySQL/   # Django configuration (settings, urls, wsgi)
├── todo/                    # Main app: models, views, serializers, templates
├── manage.py
└── requirements.txt
postman/                     # API test screenshots
```

## Running locally

1. Install dependencies:
   ```bash
   cd TodoWebDjangoWJTMySQL
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
3. Initialize the database and start the server:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```
4. Open: http://127.0.0.1:8000/signin/

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
