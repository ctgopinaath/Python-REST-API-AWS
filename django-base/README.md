# Django Project from Scratch

Step-by-step guide to create a Django project with a homepage (index.html) and REST APIs.

---

## Prerequisites

```bash
pip install django djangorestframework
```

---

## Step 1 — Create the Project

```bash
django-admin startproject myproject
cd myproject
```

This creates:
```
myproject/
├── manage.py
└── myproject/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

---

## Step 2 — Create an App

```bash
python3 manage.py startapp myapp
```

This creates:
```
myapp/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
└── views.py
```

---

## Step 3 — Register the App

In `myproject/settings.py`, add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'myapp',
]
```

---

## Step 4 — Create Templates Folder (for HTML)

```bash
mkdir -p myapp/templates/myapp
```

Create `myapp/templates/myapp/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Home</title>
</head>
<body>
    <h1>Welcome to Django</h1>
    <p>API available at /api/products/</p>
</body>
</html>
```

Tell Django where to find templates — in `myproject/settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,   # This auto-discovers templates inside each app
        ...
    },
]
```

---

## Step 5 — Create Views

In `myapp/views.py`:

```python
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# HTML homepage
def index(request):
    return render(request, 'myapp/index.html')

# JSON API
@api_view(['GET'])
def get_products(request):
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99},
        {"id": 2, "name": "Mouse", "price": 29.99},
    ]
    return Response({"products": products})
```

---

## Step 6 — Wire Up URLs

Create `myapp/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),               # Homepage -> index.html
    path('api/products/', views.get_products),  # JSON API
]
```

Include in `myproject/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('', include('myapp.urls')),
]
```

---

## Step 7 — Run Migrations & Start Server

```bash
python3 manage.py migrate
python3 manage.py runserver
```

---

## Step 8 — Test

| URL | What you see |
|-----|-------------|
| `http://127.0.0.1:8000/` | index.html homepage |
| `http://127.0.0.1:8000/api/products/` | JSON response |

---

## Full Folder Structure

```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── myapp/
    ├── views.py
    ├── urls.py
    └── templates/
        └── myapp/
            └── index.html
```
