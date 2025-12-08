# **Expense Tracker API**

A containerized RESTful backend built with **FastAPI**, **SQLModel**, **PostgreSQL**, and **Docker Compose**. Clean architecture, proper test pyramid (118 tests), and security by design.

## **Quick Start**

```bash
git clone https://github.com/vishalvemula1/expense-tracker.git
cd expense-tracker
cp .env.example .env
docker compose up
```

API available at `http://localhost:8000/docs`

---

## **Running Tests**

```bash
docker compose -f compose.test.yaml up --build
```


## **Highlights**

* **Fully Containerized**—Zero-config deployment with Docker Compose
* **118 Tests**—85 unit + 33 integration, proper test pyramid
* **JWT Authentication**—Token-based auth with secure password hashing
* **Multi-User Isolation**—Ownership validated at service layer; cross-user exploits impossible by design
* **`/me` Endpoint Design**—Eliminates user-parameter vulnerabilities entirely

## **Tech Stack**

* FastAPI
* SQLModel (SQLAlchemy + Pydantic)
* Docker Compose
* PostgreSQL
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
│   ├── auth.py          # JWT token creation/validation
│   ├── config.py        # Environment settings
│   ├── database.py      # PostgreSQL engine & session
│   ├── dependencies.py  # Dependency injection
│   ├── exceptions.py    # Error handling & db_transaction
│   ├── main.py          # App entry point
│   └── security.py      # Password hashing utilities
├── tests/
│   ├── unit/
│   │   ├── services/    # Service layer tests
│   │   ├── validation/  # Pydantic & DB constraint tests
│   │   └── security/    # Multi-tenancy tests
│   ├── integration/     # End-to-end HTTP tests
│   └── conftest.py      # Shared fixtures
├── compose.yaml         # App + PostgreSQL services
├── compose.test.yaml    # Test runner + test database
├── Dockerfile
└── .env.example         # Environment template
```


## **Future Improvements**
* Cloud deployment
