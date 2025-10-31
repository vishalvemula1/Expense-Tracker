# Expense Tracker API

A RESTful API for personal expense tracking built with FastAPI. This was my first complete backend project, where I learned to design and implement a production-ready API with authentication, authorization, and a comprehensive test suite.

## Features

- **JWT Authentication** - Token-based auth with secure password hashing (never storing plaintext passwords)
- **Category Management** - Organize expenses with custom categories, automatically creating an "Uncategorized" default for each user
- **Full CRUD Operations** - Complete expense lifecycle management with proper validation
- **Per-User Data Isolation** - Users can only access their own data, enforced at the database and API level
- **95+ Tests** - Comprehensive test coverage including edge cases, authentication, and authorization scenarios

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
- `POST /users/signup` - Create account
- `POST /users/login` - Get JWT token

### User Management
- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user details
- `DELETE /users/{user_id}` - Delete account

### Categories
- `POST /users/{user_id}/categories/` - Create category
- `GET /users/{user_id}/categories/` - List all categories
- `GET /users/{user_id}/categories/{category_id}` - Get specific category
- `PUT /users/{user_id}/categories/{category_id}` - Update category
- `DELETE /users/{user_id}/categories/{category_id}` - Delete category
- `GET /users/{user_id}/categories/{category_id}/expenses` - Get expenses by category

### Expenses
- `POST /users/{user_id}/expenses/` - Create expense
- `GET /users/{user_id}/expenses/` - List all expenses (with optional category filter)
- `GET /users/{user_id}/expenses/{expense_id}` - Get specific expense
- `PUT /users/{user_id}/expenses/{expense_id}` - Update expense
- `DELETE /users/{user_id}/expenses/{expense_id}` - Delete expense

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
I used AI to help generate many of the tests in this project, but that came with a hard lesson: **AI optimizes for passing tests, not secure code**. The AI generated 95+ tests that all passed perfectly, but it missed critical security tests like "can User A update an expense with User B's category?". 

When I caught this, I realized the tests were written to match the implementation instead of verifying requirements. I had to go back and add proper cross-user security tests, which actually exposed bugs in my code. This taught me that AI is a powerful tool for boilerplate, but you need to think critically about *what* you're testing and *why*. Failed tests that expose security issues are more valuable than passing tests that give false confidence.

I saw some of this coming which is why pretty much all of the code written for the main app files which actually runs the program were mostly handwritten since it was a learning experience but also because AI is really bad at making code secure, I'd rather use AI for boilerplate and areas that are repetitive than stuff I need to get right which is why I avoid it for the main program which is all of the app files and relegated it to testing, this gives the benefit of productivity without falling into the trap of a productivity illusion (if you use AI to generate the program's main files and security features)where you ship code faster but with technical debt which makes the amount of time saved in writing the code trivial compared to the amount of time that would need to be spent fixing the bad code which is usually not scalable, maintainable and doesn't follow DRY principles well, getting it right from the start is always better.

### 5. Python Isn't Just Syntax
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
│   └── main.py          # App entry point
├── tests/               # 95+ tests covering all endpoints
└── database.db          # SQLite database
```

## Future Improvements
- Add expense filtering by date range and amount
- Switch to PostgreSQL for production
- Containerize the project with Docker
- Deploy it on a cloud service like AWS 
