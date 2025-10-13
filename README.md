# 🧠 KanMind – Team Collaboration & Task Management API

A **Django REST Framework** based backend for managing boards, tasks, and comments.  
Users can create boards, assign members, manage tasks, and collaborate using comments.  
This project provides a **fully functional REST API** ready to connect to a frontend (e.g. Angular, React, or Vue).

---

## 🚀 Features
- 🔐 User authentication via token (login/register)
- 🧑‍🤝‍🧑 Boards with members and ownership
- ✅ Tasks assigned to users and reviewers
- 💬 Comments for each task
- 🧩 Role-based permissions (owners, members)
- ⚙️ REST API endpoints for easy integration

---

## 🧰 Requirements

Before starting, make sure you have:

| Requirement | Description |
|--------------|-------------|
| **Python ≥ 3.10** | Required to run Django |
| **pip** | Python’s package manager |
| **git** | To clone this repository |
| **virtualenv** *(optional but recommended)* | To isolate project dependencies |

---

## 💻 Setup Instructions (All Operating Systems)

The following steps work on **Windows, macOS, and Linux**.

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/KanMind.git
cd KanMind
```

### 2️⃣ Create a virtual environment
#### 🪟 On Windows
```
python -m venv venv
venv\Scripts\activate
```
#### 🍎 On macOS / Linux
```
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install dependencies
```
pip install -r requirements.txt
```

### 4️⃣ Set up the database
Create all required tables:
```
python manage.py makemigrations
python manage.py migrate

```

### 5️⃣ Create a superuser (admin)
```
python manage.py createsuperuser
```
Follow the prompts to set username, email, and password.


### 6️⃣ Run the development server
```
python manage.py runserver
```
and open: 
```
http://127.0.0.1:8000/
```
---

## 🧩 Project Structure


