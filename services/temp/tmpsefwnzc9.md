# Mini Project Management System

## Full‑Stack Assignment Documentation

---

## Overview

This project is a **multi‑tenant project management system** built using modern full‑stack technologies. It supports organizations, projects, tasks, and task comments with complete CRUD functionality and strict data isolation per organization.

---

## Features

### Backend (Django + GraphQL)

- Organization‑based **multi‑tenant architecture**
- GraphQL **queries and mutations** for:
  - Listing projects
  - Listing tasks by project
  - Creating projects
  - Creating tasks
  - Updating task status
  - Adding comments to tasks
- Clean **Django ORM models** with proper relationships
- Project‑level **statistics**:
  - Total task count
  - Completed task count

### Frontend (React + TypeScript)

- Organization‑based **project dashboard**
- Task listing per project
- Mark tasks as completed
- Add comments to tasks
- **Apollo Client** integration with:
  - Caching
  - Query and mutation handling
  - Loading and error states
- Responsive UI built using **TailwindCSS**

---

## Tech Stack

### Backend

- Django 4.x
- Graphene GraphQL
- PostgreSQL

### Frontend

- React 18+
- TypeScript
- TailwindCSS
- Apollo Client

---

## Project Structure

```text
backend/
  core/
    models.py
    mutations.py
    schema.py
    types.py
  assignment_backend/
  manage.py

frontend/
  src/
    components/
    graphql/
    pages/
    App.tsx
  package.json
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

---

## Backend Setup (Django + PostgreSQL)

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv
```

#### Activate Environment

- **Windows**
  ```bash
  venv\Scripts\activate
  ```
- **macOS / Linux**
  ```bash
  source venv/bin/activate
  ```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing:

```bash
pip freeze > requirements.txt
```

---

### 4. Configure PostgreSQL

#### Create Database

```sql
CREATE DATABASE project_management;
```

#### Update `settings.py`

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "project_management",
        "USER": "postgres",
        "PASSWORD": "<your-password>",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

---

### 5. Run Migrations

```bash
python manage.py migrate
```

---

### 6. Start Backend Server

```bash
python manage.py runserver
```

#### GraphQL Endpoint

```
http://127.0.0.1:8000/graphql/
```

---

## Frontend Setup (React + TypeScript)

### 7. Install Dependencies

```bash
cd frontend
npm install
```

---

### 8. Start Frontend Server

```bash
npm run dev
```

#### Frontend URL

```
http://localhost:5173
```

---

## GraphQL API Overview

### Queries

- `projectsByOrganization`
- `tasksByProject`
- `taskComments`

### Mutations

- `createProject`
- `createTask`
- `updateTaskStatus`
- `addTaskComment`

---

## Demonstration

A demo video is included that showcases:

- Creating projects
- Listing tasks
- Updating task status
- Adding task comments
- Multi‑tenant organization separation

---

## Technical Notes

### Design Decisions

- GraphQL chosen for **flexible frontend data requirements**
- Organization slug used for **tenant isolation**
- Apollo Client cache improves performance and UX
- Clean separation of **backend and frontend concerns**

---

## Future Improvements

- Authentication using JWT
- Drag‑and‑drop task board
- Real‑time comments using WebSockets
- Docker Compose setup
- CI/CD pipeline and automated testing

---

## Author

**Vedant Kulkarni**

Full Stack Developer

