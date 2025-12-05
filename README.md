# **Expense Tracker API**

A containerized RESTful backend built with **FastAPI**, **SQLModel**, and **Docker**. Clean architecture, proper test pyramid (118 tests), and security by design.

```bash
docker run -dp 8000:8000 vishalvemula1/expense-tracker
```

API available at `http://localhost:8000`

---

## **Highlights**

* **Fully Containerized**—Zero-config deployment with Docker
* **118 Tests**—85 unit + 33 integration, proper test pyramid
* **JWT Authentication**—Token-based auth with secure password hashing
* **Multi-User Isolation**—Ownership validated at service layer; cross-user exploits impossible by design
* **`/me` Endpoint Design**—Eliminates user-parameter vulnerabilities entirely
* **Default Category Provisioning**—Auto-generated, write-protected "Uncategorized" per user

## **Tech Stack**

* FastAPI
* SQLModel (SQLAlchemy + Pydantic)
* Docker
* SQLite (dev) / PostgreSQL-ready
* JWT for auth
* Pytest

## **Architecture Overview**

* **Routers**: Split by domain (users, categories, expenses, auth)
* **Service Layer**: Centralized business logic with ownership validation and cross-service coordination
* **Dependency Injection**: Authentication and DB session management
* **Models**: SQLModel schemas with validators, composite constraints, and foreign keys
* **DB Layer**: Transaction helpers with structured exception mapping

## **Key Design Decisions**

### **Security Through Architecture: The /me Endpoint Design**

Early on, the `/users/{id}/expenses` pattern required every endpoint to compare the `user_id` in the URL with the `sub` in the JWT. Even with careful checks, the design made it possible for a developer to forget a comparison or validate inconsistently.

Switching to `/me/expenses` removed the parameter entirely. No `user_id` in the URL means no chance of manipulation, no forgotten comparisons, and no test cases for states that can't exist. One architectural change erased a whole category of bugs.

### **Service Layer Pattern for Business Logic Isolation**

Moving business logic into service classes solved several architectural problems:

* **Ownership validation**: Each service method verifies ownership internally. `ExpenseService._get_expense()` checks if the expense belongs to the authenticated user, eliminating the possibility of endpoints forgetting this check.
* **Cross-service coordination**: `ExpenseService` can instantiate `CategoryService` to validate category ownership when creating expenses, establishing clear dependencies without circular imports.
* **Transaction consistency**: The `db_transaction` context manager traps integrity errors and routes them to consistent HTTP responses. Every write path behaves the same without repeating error-handling code.

---

## **API Overview**

### **Authentication**

* POST /auth/signup
* POST /auth/login

### **User**

* GET /me
* PUT /me
* DELETE /me

### **Categories**

* POST /me/categories/
* GET /me/categories/
* GET /me/categories/{category_id}
* PUT /me/categories/{category_id}
* DELETE /me/categories/{category_id}
* GET /me/categories/{category_id}/expenses

### **Expenses**

* POST /me/expenses/
* GET /me/expenses/
* GET /me/expenses/{expense_id}
* PUT /me/expenses/{expense_id}
* DELETE /me/expenses/{expense_id}

## **Project Structure**

```
expense_tracker/
├── app/
│   ├── models/          # SQLModel schemas with validation
│   ├── routers/         # FastAPI route handlers
│   ├── services/        # Business logic layer
│   ├── auth.py          # JWT authentication
│   ├── dependencies.py  # Dependency injection
│   ├── exceptions.py    # Error handling
│   └── main.py          # App entry point
├── tests/
│   ├── unit/
│   │   ├── services/    # Service layer tests
│   │   ├── validation/  # Pydantic & DB constraint tests
│   │   └── security/    # Multi-tenancy tests
│   ├── integration/     # End-to-end HTTP tests
│   └── conftest.py      # Shared fixtures
├── Dockerfile
└── database.db
```

## **Running Tests**

```bash
# Docker
docker run vishalvemula1/expense-tracker pytest -q

# Local
pytest                          # All tests
pytest tests/unit/              # Unit only
pytest tests/integration/       # Integration only
pytest --cov=app                # With coverage
```

<summary><strong>Local Development Setup</strong></summary>

```bash
git clone https://github.com/vishalvemula1/expense-tracker.git
cd expense-tracker
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```bash
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Run:

```bash
uvicorn app.main:app --reload
```


## **Future Improvements**
* PostgreSQL migration 
* Cloud deployment
