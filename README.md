# 🧠 KanMind Backend

This is the backend API for **KanMind**, a lightweight Kanban-style task management system.  
The project was created for training purposes in **Django** and **Django REST Framework**.

The API allows users to create boards, manage tasks, assign roles, and collaborate via comments – all with secure token-based authentication.

---

## 🚀 Features

- ✅ Token-based user authentication (login/registration)
- ✅ Create & manage boards (title, members, ownership)
- ✅ Task creation with assignee/reviewer roles
- ✅ Task status & priority management (`todo`, `review`, `done`, ...)
- ✅ Comment system per task
- ✅ Role-based filtering: see only your assigned/review tasks
- ✅ Clean RESTful endpoints (JSON)
- ✅ CORS support for frontend connection

---

## 🛠️ Tech Stack

- **Python** 3.10+
- **Django** 4.x
- **Django REST Framework**
- **SQLite** for development (switchable to PostgreSQL)
- **TokenAuthentication** via `rest_framework.authtoken`
- CORS enabled for frontend integration

---

## 📦 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/enes/kanmind-backend.git
cd kanmind-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Start development server

```bash
python manage.py runserver
```

---

## 🔐 Authentication

All protected endpoints require token-based authentication.

### 1. Register

`POST /api/registration/`  
```json
{
  "fullname": "Max Mustermann",
  "email": "max@example.com",
  "password": "strongPass123!",
  "repeated_password": "strongPass123!"
}
```

### 2. Login

`POST /api/login/`  
Returns:
```json
{
  "token": "abc123...",
  "user_id": 1,
  "fullname": "Max Mustermann",
  "email": "max@example.com"
}
```

### 3. Use Token

Include this in every authenticated request:
```
Authorization: Token abc123...
```

---

## 📬 Main API Endpoints

### Boards

| Method | URL | Description |
|--------|-----|-------------|
| GET    | `/api/boards/`           | List all boards (owned or member) |
| POST   | `/api/boards/`           | Create a new board |
| GET    | `/api/boards/<id>/`      | Get board details |
| PATCH  | `/api/boards/<id>/`      | Update board title or members |
| DELETE | `/api/boards/<id>/`      | Delete board (only owner) |

### Tasks

| Method | URL | Description |
|--------|-----|-------------|
| POST   | `/api/tasks/`            | Create new task |
| GET    | `/api/tasks/assigned-to-me/` | List tasks assigned to you |
| GET    | `/api/tasks/reviewing/`      | List tasks you're reviewing |
| PATCH  | `/api/tasks/<id>/`       | Update task |
| DELETE | `/api/tasks/<id>/`       | Delete task (creator or board owner) |

### Comments

| Method | URL | Description |
|--------|-----|-------------|
| GET    | `/api/tasks/<task_id>/comments/` | List all comments on a task |
| POST   | `/api/tasks/<task_id>/comments/` | Add new comment |
| DELETE | `/api/tasks/<task_id>/comments/<comment_id>/` | Delete comment (only author) |

---

## 🧪 Testing

- Test suite was verified using Postman
- Test coverage: **95%+**, with full coverage of all business-critical endpoints
- Auth and permission handling fully verified
- Error handling for:
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
  - 400 Bad Request

---

## 🧾 Notes

- ⚠️ The database file (`db.sqlite3`) is **excluded from version control**
- This is a **backend-only project** – no frontend included
- `CORS_ALLOWED_ORIGINS` includes `http://127.0.0.1:5500` for local frontend testing

---

## 📁 Folder Structure

```
kanmind-backend/
│
├── auth_app/           # Custom user model and authentication logic
├── kanban_app/         # Core app for boards, tasks, and comments
├── core/               # Project settings
├── manage.py
├── requirements.txt
└── README.md
```

---

## 👤 Author

**Enes Tester**  
📧 enes@example.com  
🔗 [GitHub: enes](https://github.com/enes)

---

## 📌 License

This project is intended for educational purposes only. Not for production use.
