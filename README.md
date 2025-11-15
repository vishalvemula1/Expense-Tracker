# **Expense Tracker API**

A RESTful multi-user backend built with FastAPI and SQLModel. The focus is straightforward: clean structure, predictable behavior, and security that comes from architectural choices rather than patches.

This is a small but intentionally designed service that handles real multi-user rules, ownership, and validation without relying on framework magic or scaffolding.

## **Highlights**

* Multi-user architecture with ownership validated through service layer
* /me endpoint design removes user-parameter edge cases entirely
* Clear domain rules: composite uniqueness, default-category protection, and proper schema constraints
* Transaction-scoped DB operations with structured integrity handling
* Comprehensive test suite covering security paths and edge cases

## **Features**

* **JWT Authentication**—Token-based auth with secure password hashing
* **Multi-User Isolation**—Each user has their own categories and expenses; cross-user exploits impossible by design
* **Default Category Provisioning**—Auto-generated, write-protected "Uncategorized" per user
* **Full CRUD for Expenses & Categories**—With proper validation and ownership checks
* **85+ Tests**—Security-focused, cross-user, edge cases, and core logic

## **Architecture Overview**

* **Routers**: Split by domain (users, categories, expenses, auth)
* **Service Layer**: Centralized business logic with ownership validation and cross-service coordination
* **Dependency Injection**: Authentication and DB session management
* **Models**: SQLModel schemas with validators, composite constraints, and foreign keys
* **DB Layer**: Transaction helpers with structured exception mapping

## **Tech Stack**

* FastAPI
* SQLModel (SQLAlchemy + Pydantic)
* SQLite for dev
* JWT for auth
* Pytest + pytest-asyncio

## **Quick Start**

```bash
git clone https://github.com/vishalvemula1/expense-tracker.git
cd expense-tracker
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r app/requirements.txt
```

Create a `.env` file in the root directory:

```bash
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Run and test:

```bash
uvicorn app.main:app --reload
pytest
```

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

## **Key Design Decisions**

### **1. Security Through Architecture: The /me Endpoint Design**

A concrete example: early on, the /users/{id}/expenses pattern required every endpoint to compare the user_id in the URL with the sub in the JWT. Even with careful checks, the design made it possible for a developer to forget one comparison or validate it inconsistently. It also forced tests to cover every permutation of mismatched IDs.

Switching to /me/expenses removed the parameter entirely. No user_id in the URL means no chance of someone manipulating it, no forgotten comparisons, and no test cases for a state that can no longer exist. One architectural change erased a whole category of bugs.

### **2. Service Layer Pattern for Business Logic Isolation**

Moving business logic into service classes (AuthService, UserService, ExpenseService, CategoryService) solved several architectural problems:

* **Ownership validation**: Each service method verifies ownership internally before any operation. ExpenseService._get_expense() checks if the expense belongs to the authenticated user, eliminating the possibility of endpoints forgetting this check.
* **Cross-service coordination**: ExpenseService can instantiate CategoryService to validate category ownership when creating expenses, establishing clear dependencies without circular imports.
* **Transaction consistency**: The db_transaction context manager traps integrity errors (like duplicate category names per user via composite uniqueness) and routes them to consistent HTTP responses. Every write path behaves the same without repeating error-handling code.
* **Standardized method naming**: All services follow create/get/update/delete/list conventions, making the codebase predictable and maintainable.

These weren't abstractions for neatness—they eliminated repetitive code and prevented subtle inconsistencies.

### **3. Deliberate AI Use: Core Logic vs. Test Boilerplate**

For example, when relying on AI-generated tests early on, none of them explored cross-user scenarios. A test like "Can User A update an expense belonging to User B?" simply didn't exist. Writing that test manually exposed real authorization gaps that AI had no intuition to look for. This was eventually a problem that was phased out due to the /me refactor making these kind of cross-user attacks impossible by design but that wasn't always the case.

This is why the core application logic in the app/ directory was handwritten. While AI can scaffold a "working" endpoint, it struggles to weave in the project's specific architectural needs, like integrating the correct ownership checks in service methods or the db_transaction helper for consistent error handling. These are the exact vulnerabilities that AI-generated *application code* would have likely introduced.

AI was therefore intentionally limited to tests/, where it could accelerate boilerplate, but kept out of app/, where its inability to grasp architectural intent would have compromised quality and security.

## **Project Structure**

```
expense_tracker/
├── app/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── auth.py
│   ├── dependencies.py
│   ├── exceptions.py
│   └── main.py
├── tests/
└── database.db
```

## **Future Improvements**

* Date-range filtering
* PostgreSQL support
* Dockerization
* Cloud deployment
