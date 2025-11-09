# Expense Tracker API

A RESTful API for personal expense tracking built with FastAPI. My first complete backend project, where I learned that building secure, maintainable APIs requires architectural thinking—the kind that comes from understanding trade-offs.


## Insight

The main takeaway wasn’t just technical — it was learning to think in terms of failure surfaces, maintainability, and human readability instead of lines of code. I realized why frameworks like FastAPI emphasize dependency injection and how those design decisions scale beyond one project.

## Features

- **JWT Authentication** - Token-based auth with secure password hashing (never storing plaintext passwords)
- **Category Management** - Organize expenses with custom categories, automatically creating an "Uncategorized" default for each user
- **Full CRUD Operations** - Complete expense lifecycle management with proper validation
- **Secure-by-Design Architecture** - Token-based `/me` endpoints that make cross-user exploits architecturally impossible
- **85+ Tests** - Comprehensive test coverage focusing on real security scenarios and edge cases

## Tech Stack

- **FastAPI** - Modern, fast web framework with automatic API documentation
- **SQLModel** - Type-safe ORM combining SQLAlchemy and Pydantic
- **SQLite** - Lightweight database for development
- **JWT** - Secure token-based authentication
- **Pytest** - Testing framework with async support

## Quick Start

```bash
# Clone and setup
git clone https://github.com/vishalvemula1/expense-tracker.git
cd expense-tracker
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r app/requirements.txt

# Configure environment (create .env file)
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Run the API
uvicorn app.main:app --reload

# Run tests
pytest
```

The API will be available at `http://127.0.0.1:8000` with interactive docs at `/docs`.

## API Overview

### Authentication
- `POST /auth/signup` - Create account
- `POST /auth/login` - Get JWT token

### User Management
- `GET /me` - Get your profile
- `PUT /me` - Update your details
- `DELETE /me` - Delete your account

### Categories
- `POST /me/categories/` - Create category
- `GET /me/categories/` - List your categories
- `GET /me/categories/{category_id}` - Get specific category
- `PUT /me/categories/{category_id}` - Update category
- `DELETE /me/categories/{category_id}` - Delete category
- `GET /me/categories/{category_id}/expenses` - Get expenses by category

### Expenses
- `POST /me/expenses/` - Create expense
- `GET /me/expenses/` - List your expenses (with optional category filter)
- `GET /me/expenses/{expense_id}` - Get specific expense
- `PUT /me/expenses/{expense_id}` - Update expense
- `DELETE /me/expenses/{expense_id}` - Delete expense

## What I Learned

Building this project from scratch taught me more than any tutorial could. Here are the biggest challenges I faced:

### 1. Designing the Category System
The hardest part wasn't writing the code—it was figuring out *what* to write. I knew I wanted expenses to have categories, but then I realized: what if a user creates an expense before making any categories? Should it fail? Should category be optional?

I decided every expense *needs* a category, so I implemented an auto-generated "Uncategorized" default for each user. But then came another problem: how do I prevent users from editing or deleting this special category? I ended up adding an `is_default` flag and protection logic in the update/delete endpoints.

This taught me that API design is as much about anticipating user behavior as it is about writing clean code.

### 2. Database Constraints and Multi-User Design
Initially, I made category names globally unique—meaning if one user created a "Food" category, nobody else could. Rookie mistake. I learned about composite unique constraints (`UniqueConstraint('name', 'user_id')`) to make names unique *per user* instead.

This pattern repeated throughout the project: thinking through edge cases like "what if two users try to do the same thing?" shaped how I designed the entire database schema.

### 3. Where Does Logic Go?
Early on, I tried putting password hashing inside the SQLModel class. It seemed logical, since it would enforce hashing upon creation so I wouldn't have to worry about missing anything within endpoints, it felt like something that could just be abstracted away from the main logic for "cleaner code" but I was wrong. I learned the hard way that **models define data structure**, while **business logic belongs in endpoints or service layers** and trying to hash it in the model was definitely not clean and felt out of place.

When I hit circular import issues between `dependencies.py` and `auth.py`, I had to refactor everything. I created a separate `services.py` file to centralize business logic, which made the codebase way more maintainable. This taught me that good architecture isn't about clever tricks—it's about clear separation of concerns.

### 4. Learning to Use (and Critique) AI-Generated Code
I used AI to help generate many of the tests in this project, but that came with a hard lesson: **AI optimizes for passing tests, not secure code**. The AI generated dozens of tests that all passed perfectly, but it missed critical security tests like "can User A update an expense with User B's category?".

When I caught this, I realized the tests were written to match the implementation instead of verifying requirements. I had to go back and add proper cross-user security tests, which actually exposed real bugs in my authorization logic. This taught me that AI is a powerful tool for boilerplate, but you need to think critically about *what* you're testing and *why*. Failed tests that expose security issues are infinitely more valuable than passing tests that give false confidence.

This is why I hand-wrote all the core application code (`app/` directory)—not as a learning exercise, but because AI-generated business logic would have compromised quality. AI scaffolds repetitive patterns well, but it produces code that *works* without being secure, scalable, or maintainable. By keeping AI limited to testing boilerplate while implementing the architecture myself, I gained deep understanding of FastAPI's dependency injection, SQLModel relationships, and JWT token validation—but more importantly, I was able to focus on clean abstractions, proper separation of concerns, and DRY principles. These are architectural decisions that AI-generated code struggles to replicate, and they are what ensure the project is both high-quality and maintainable.

### 5. The Best Security Bug is the One That Can't Happen
After fixing those authorization bugs, I stepped back and realized something uncomfortable: **I was writing increasingly complex tests to validate an inherently flawed design.**

My original API structure was `/users/{user_id}/expenses/`. Every endpoint required extracting `user_id` from the URL, validating it against the JWT token, and ensuring they matched. I had tests for every permutation: "What if User A tries to access User B's data? What if the token is valid but the user_id is wrong?" The tests caught bugs, but the architecture *invited* them.

Then it hit me: why am I passing `user_id` in the URL when I already have it in the authenticated token? The design was fundamentally wrong. I refactored the entire API to use `/me` endpoints—`/me`, `/me/expenses/`, `/me/categories/`—where the user is *only* identified by their JWT token. No more URL parameters to exploit.

This single architectural decision:
- **Made cross-user exploits literally impossible**—there's no `user_id` parameter to manipulate
- **Simplified dependencies drastically**—no more passing and verifying `user_id` everywhere
- **Cut 10 redundant tests**—scenarios that could no longer exist didn't need testing

This is the kind of architectural thinking AI can't do. It would've generated working code for `/users/{user_id}/` endpoints with all the validation logic, passing all its tests, never questioning whether the design itself was flawed. I learned that **architecture is security**—the best defense isn't rigorous testing, it's designing systems where entire vulnerability classes can't exist. Preventing bugs at the design level beats detecting them at the test level every single time.

### 6. Python Isn't Just Syntax
I went in knowing Python basics but came out understanding `TypeVar` for generic functions, Pydantic validators with factory patterns, and FastAPI's dependency injection system. Reading the FastAPI and SQLModel docs deeply (not just skimming) made a huge difference. I learned that understanding *why* a framework makes certain design choices helps you use it properly.

---

## Project Structure
```
expense_tracker/
├── app/
│   ├── models/          # SQLModel schemas (User, Expense, Category)
│   ├── routers/         # API endpoints by resource
│   ├── auth.py          # JWT authentication logic
│   ├── services.py      # Business logic layer
│   ├── dependencies.py  # FastAPI dependency injection
│   ├── exceptions.py    # Custom exception handlers
│   └── main.py          # App entry point
├── tests/               # 85+ tests covering security and edge cases
└── database.db          # SQLite database
```

## Future Improvements
- Add expense filtering by date range and amount
- Switch to PostgreSQL for production
- Containerize the project with Docker
- Deploy it on a cloud service like AWS 
