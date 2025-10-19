# 💰 Expense Tracker CRUD

> **📚 Learning Project** - A FastAPI & SQLModel practice application exploring REST API design and database operations

> **Note:** This is a simple educational project built to learn FastAPI, SQLModel, and best practices for API development. It's not intended for production use.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-Latest-purple?style=flat-square&logo=sqlalchemy)](https://sqlmodel.tiangolo.com/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Resources](#-resources)

---

## ✨ Features

This project demonstrates core REST API concepts:

- 🚀 **FastAPI Basics** - Building modern web APIs with Python
- 📊 **CRUD Operations** - Create, Read, Update, Delete fundamentals
- 🗄️ **SQLite & ORM** - Database operations with SQLModel
- 📖 **Auto Documentation** - Swagger UI for API exploration
- � **Type Hints & Validation** - Pydantic integration with FastAPI
- 🏗️ **Project Organization** - Clean code structure and routing

## 🎓 Learning Goals

This project was built to practice and understand:

✅ FastAPI fundamentals and request/response handling  
✅ SQLModel ORM and database operations  
✅ REST API design principles (CRUD operations)  
✅ Pydantic models for data validation  
✅ Project structure and code organization  
✅ Git workflows and version control best practices  

---

## ⚠️ Important Notes

- **Educational Only** - Built for learning purposes
- **No Production Use** - Lacks security, error handling, and scalability features
- **Simple Database** - Uses SQLite; not suitable for concurrent access
- **Basic Validation** - Real projects need comprehensive input validation and error handling
- **No Authentication** - All endpoints are publicly accessible

---

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Modern web framework for building APIs |
| **SQLModel** | SQL database ORM combining SQLAlchemy + Pydantic |
| **SQLite** | Lightweight, self-contained database |
| **Uvicorn** | ASGI server for running the application |
| **Python 3.9+** | Programming language |

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/vishalvemula1/Expense-Tracker-CRUD.git
cd Expense-Tracker-CRUD
```

2. **Create virtual environment**
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r app/requirements.txt
```

4. **Run the application**
```bash
fastapi dev app/expenses_db.py
```

The API will be available at: **http://localhost:8000**

---

## 🚀 Usage

### Interactive API Documentation

Visit **http://localhost:8000/docs** to access the interactive Swagger UI where you can:
- 📖 View all available endpoints
- 🧪 Test API requests directly
- 📤 See request/response examples
- 🔍 Explore request parameters

### Example: Add an Expense

```bash
curl -X POST "http://localhost:8000/expenses/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grocery Shopping",
    "amount": 45.50,
    "category": "Food",
    "description": "Weekly groceries"
  }'
```

### Example: Get All Expenses

```bash
curl -X GET "http://localhost:8000/expenses/?limit=10&offset=0"
```

---

## 📡 API Endpoints

### Expense Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/expenses/` | Create a new expense |
| `GET` | `/expenses/` | Get all expenses (with pagination) |
| `GET` | `/expenses/{expense_id}` | Get a specific expense |
| `PUT` | `/expenses/{expense_id}` | Update an expense |
| `DELETE` | `/expenses/{expense_id}` | Delete an expense |

### Query Parameters

**GET `/expenses/`**
- `limit` (int, default=100): Maximum number of expenses to return
- `offset` (int, default=0): Number of expenses to skip (for pagination)
- `category` (string, optional): Filter by expense category
- `min_amount` (number, optional): Filter expenses >= this amount
- `max_amount` (number, optional): Filter expenses <= this amount

---

## 📁 Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── expenses_db.py          # Database setup & CRUD operations
├── database.py             # Database configuration
├── requirements.txt        # Python dependencies
├── routers/
│   ├── __init__.py
│   └── expenses.py         # Expense route handlers
└── __pycache__/           # Python cache files
```

---

## 🔧 Development

### Running the Development Server

```bash
fastapi dev app/expenses_db.py
```

The server will automatically reload on file changes thanks to FastAPI's development mode.

### Project Structure

- **Models**: Defined in `expenses_db.py` using SQLModel
- **Routes**: Organized in `routers/expenses.py`
- **Database**: SQLite database stored locally as `database.db`

### Adding a New Endpoint

1. Create a new route in `routers/expenses.py`
2. Use FastAPI decorators (`@app.get`, `@app.post`, etc.)
3. Add proper type hints and docstrings
4. Test in Swagger UI at `/docs`

---

## 📚 Resources

### Learning Materials
- **[Git & File Operations Guide](./GIT_FILE_OPERATIONS_GUIDE.md)** - Complete reference for safe file operations and Git best practices
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Official FastAPI docs
- **[SQLModel Documentation](https://sqlmodel.tiangolo.com/)** - SQL database ORM guide
- **[Pydantic Documentation](https://docs.pydantic.dev/)** - Data validation library

### Useful Commands

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1       # Windows
source .venv/bin/activate        # macOS/Linux

# Install dependencies
pip install -r app/requirements.txt

# Run the server
fastapi dev app/expenses_db.py

# Access API docs
# Open http://localhost:8000/docs in your browser
```

---

## 📝 Git Best Practices

This project includes a comprehensive guide for safe file operations with Git:
- ✅ When to use `git mv` vs OS commands
- ✅ How to avoid file lock issues
- ✅ Proper workflow for renaming/moving/deleting files
- ✅ Emergency procedures for common mistakes

See **[GIT_FILE_OPERATIONS_GUIDE.md](./GIT_FILE_OPERATIONS_GUIDE.md)** for detailed information.

---

## 🤝 Contributing

This is a personal learning project, so contributions aren't expected. However, feel free to:
- Fork it for your own learning
- Modify it as you like
- Use it as a reference for your own projects

---

## 📄 License

This project is unlicensed and shared for educational purposes only.

---

## 👤 Author

**Vishal Vemula**
- GitHub: [@vishalvemula1](https://github.com/vishalvemula1)

---

## 🎯 Future Learning Areas

If you're extending this project, consider exploring:

- [ ] Add user authentication (JWT tokens)
- [ ] Implement expense categories management
- [ ] Add database migrations (Alembic)
- [ ] Create unit and integration tests
- [ ] Add input validation and error handling
- [ ] Implement logging and monitoring
- [ ] Add API rate limiting
- [ ] Deploy to cloud platform (Heroku, AWS, etc.)

---

**📚 This is a learning project built to explore FastAPI and SQLModel.**
