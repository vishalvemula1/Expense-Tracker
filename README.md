# Expense Tracker API# Expense Tracker API



A RESTful multi-user backend built with FastAPI and SQLModel. The focus is straightforward: clean structure, predictable behavior, and security that comes from architectural choices rather than patches.A RESTful multi-user backend built with FastAPI and SQLModel. The focus is straightforward: clean structure, predictable behavior, and security that comes from architectural choices rather than patches.



This is a small but intentionally designed service that handles real multi-user rules, ownership, and validation without relying on framework magic or scaffolding.This is a small but intentionally designed service that handles real multi-user rules, ownership, and validation without relying on framework magic or scaffolding.



------



## ✨ Highlights## ✨ Highlights



- **Multi-user architecture** with ownership validated through dependencies- **Multi-user architecture** with ownership validated through dependencies

- **/me endpoint design** removes user-parameter edge cases entirely- **/me endpoint design** removes user-parameter edge cases entirely

- **Clear domain rules**: composite uniqueness, default-category protection, and proper schema constraints- **Clear domain rules**: composite uniqueness, default-category protection, and proper schema constraints

- **Transaction-scoped DB operations** with structured integrity handling- **Transaction-scoped DB operations** with structured integrity handling

- **Comprehensive test suite** covering security paths and edge cases- **Comprehensive test suite** covering security paths and edge cases



------



## 🚀 Features## 🚀 Features



- **JWT Authentication**—Token-based auth with secure password hashing- **JWT Authentication**—Token-based auth with secure password hashing

- **Multi-User Isolation**—Each user has their own categories and expenses; cross-user exploits impossible by design- **Multi-User Isolation**—Each user has their own categories and expenses; cross-user exploits impossible by design

- **Default Category Provisioning**—Auto-generated, write-protected "Uncategorized" per user- **Default Category Provisioning**—Auto-generated, write-protected "Uncategorized" per user

- **Full CRUD for Expenses & Categories**—With proper validation and ownership checks- **Full CRUD for Expenses & Categories**—With proper validation and ownership checks

- **85+ Tests**—Security-focused, cross-user, edge cases, and core logic- **85+ Tests**—Security-focused, cross-user, edge cases, and core logic



------



## 🏗️ Architecture Overview## 🏗️ Architecture Overview



- **Routers**: Split by domain (users, categories, expenses, auth)- **Routers**: Split by domain (users, categories, expenses, auth)

- **Service Layer**: Centralized business logic, avoids circular imports and keeps endpoints clean- **Service Layer**: Centralized business logic, avoids circular imports and keeps endpoints clean

- **Dependency Injection**: Security, ownership validation, DB session management- **Dependency Injection**: Security, ownership validation, DB session management

- **Models**: SQLModel schemas with validators, composite constraints, and foreign keys- **Models**: SQLModel schemas with validators, composite constraints, and foreign keys

- **DB Layer**: Transaction helpers with structured exception mapping- **DB Layer**: Transaction helpers with structured exception mapping



------



## 🛠️ Tech Stack## 🛠️ Tech Stack



- **FastAPI**- **FastAPI**

- **SQLModel** (SQLAlchemy + Pydantic)- **SQLModel** (SQLAlchemy + Pydantic)

- **SQLite** for dev- **SQLite** for dev

- **JWT** for auth- **JWT** for auth

- **Pytest** + pytest-asyncio- **Pytest** + pytest-asyncio



------



## 📦 Quick Start## 📦 Quick Start



### 1️⃣ Clone and Setup### 1️⃣ Clone and Setup



```bash```bash

git clone https://github.com/vishalvemula1/expense-tracker.gitgit clone https://github.com/vishalvemula1/expense-tracker.git

cd expense-trackercd expense-tracker

python -m venv .venvpython -m venv .venv

source .venv/bin/activate  # On Windows: .venv\Scripts\activatesource .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r app/requirements.txtpip install -r app/requirements.txt

``````



### 2️⃣ Configure Environment### 2️⃣ Configure Environment



Create a `.env` file in the root directory:Create a `.env` file in the root directory:



```bash```bash

SECRET_KEY=your_secret_key_hereSECRET_KEY=your_secret_key_here

ALGORITHM=HS256ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30ACCESS_TOKEN_EXPIRE_MINUTES=30

``````



### 3️⃣ Run and Test### 3️⃣ Run and Test



```bash```bash

# Start the server# Start the server

uvicorn app.main:app --reloaduvicorn app.main:app --reload



# Run tests# Run tests

pytestpytest

``````



------



## 📚 API Overview## 📚 API Overview



### 🔐 Authentication### 🔐 Authentication

- `POST /auth/signup`- `POST /auth/signup`

- `POST /auth/login`- `POST /auth/login`



### 👤 User### 👤 User

- `GET /me`- `GET /me`

- `PUT /me`- `PUT /me`

- `DELETE /me`- `DELETE /me`



### 📁 Categories### 📁 Categories

- `POST /me/categories/`- `POST /me/categories/`

- `GET /me/categories/`- `GET /me/categories/`

- `GET /me/categories/{category_id}`- `GET /me/categories/{category_id}`

- `PUT /me/categories/{category_id}`- `PUT /me/categories/{category_id}`

- `DELETE /me/categories/{category_id}`- `DELETE /me/categories/{category_id}`

- `GET /me/categories/{category_id}/expenses`- `GET /me/categories/{category_id}/expenses`



### 💰 Expenses### 💰 Expenses

- `POST /me/expenses/`- `POST /me/expenses/`

- `GET /me/expenses/`- `GET /me/expenses/`

- `GET /me/expenses/{expense_id}`- `GET /me/expenses/{expense_id}`

- `PUT /me/expenses/{expense_id}`- `PUT /me/expenses/{expense_id}`

- `DELETE /me/expenses/{expense_id}`- `DELETE /me/expenses/{expense_id}`



---



## 💡 Key Design Decisions## Key Design DecisionsKey Design Decisions



### 1. Security Through Architecture: The `/me` Endpoint Design



A concrete example: early on, the `/users/{id}/expenses` pattern required every endpoint to compare the `user_id` in the URL with the `sub` in the JWT. Even with careful checks, the design made it possible for a developer to forget one comparison or validate it inconsistently. It also forced tests to cover every permutation of mismatched IDs.### 1. Security Through Architecture: The /me Endpoint Design1. Security Through Architecture: The /me Endpoint Design



Switching to `/me/expenses` removed the parameter entirely. No `user_id` in the URL means no chance of someone manipulating it, no forgotten comparisons, and no test cases for a state that can no longer exist. One architectural change erased a whole category of bugs.



### 2. Intentional Abstractions for MaintainabilityA concrete example: early on, the `/users/{id}/expenses` pattern required every endpoint to compare the `user_id` in the URL with the `sub` in the JWT. Even with careful checks, the design made it possible for a developer to forget one comparison or validate it inconsistently. It also forced tests to cover every permutation of mismatched IDs.A concrete example: early on, the /users/{id}/expenses pattern required every endpoint to compare the user_id in the URL with the sub in the JWT. Even with careful checks, the design made it possible for a developer to forget one comparison or validate it inconsistently. It also forced tests to cover every permutation of mismatched IDs.



Examples that justified their existence:



- **Ownership via dependencies**: `VerifiedExpenseDep` and `VerifiedWriteCategoryDep` don't just "check a box"—they guarantee that every endpoint touching a resource verifies ownership or default-category rules automatically. There's no risk of one endpoint forgetting the logic.Switching to `/me/expenses` removed the parameter entirely. No `user_id` in the URL means no chance of someone manipulating it, no forgotten comparisons, and no test cases for a state that can no longer exist. One architectural change erased a whole category of bugs. Switching to /me/expenses removed the parameter entirely. No user_id in the URL means no chance of someone manipulating it, no forgotten comparisons, and no test cases for a state that can no longer exist. One architectural change erased a whole category of bugs.



- **DRY validation via mixin factory**: A key abstraction was the `create_string_validators` factory. Instead of repeating `field_validator` logic for whitespace and empty-string checks, this factory generates a reusable mixin. This one mixin is inherited by all 6 Create and Update models, eliminating duplicated code and ensuring validation logic is defined in exactly one place.



- **Transaction helper**: The `db_transaction` context manager trapped integrity errors (like duplicate category names per user via composite uniqueness) and routed them to consistent HTTP responses. Every write path behaved the same without repeating error-handling code.### 2. Intentional Abstractions for Maintainability2. Intentional Abstractions for Maintainability



These weren't abstractions for neatness—they eliminated repetitive code and prevented subtle inconsistencies.



### 3. Deliberate AI Use: Core Logic vs. Test BoilerplateExamples that justified their existence:Examples that justified their existence:



For example, when relying on AI-generated tests early on, none of them explored cross-user scenarios. A test like "Can User A update an expense belonging to User B?" simply didn't exist. Writing that test manually exposed real authorization gaps that AI had no intuition to look for. This was eventually a problem that was phased out due to the `/me` refactor making these kind of cross-user attacks impossible by design but that wasn't always the case.



This is why the core application logic in the [`app/`](app) directory was handwritten. While AI can scaffold a "working" endpoint, it struggles to weave in the project's specific architectural needs, like integrating the correct ownership dependency or the `db_transaction` helper for consistent error handling. These are the exact vulnerabilities that AI-generated application code would have likely introduced.- **Ownership via dependencies**: `VerifiedExpenseDep` and `VerifiedWriteCategoryDep` don't just "check a box"—they guarantee that every endpoint touching a resource verifies ownership or default-category rules automatically. There's no risk of one endpoint forgetting the logic.Ownership via dependencies: VerifiedExpenseDep and VerifiedWriteCategoryDep don’t just "check a box"—they guarantee that every endpoint touching a resource verifies ownership or default-category rules automatically. There's no risk of one endpoint forgetting the logic.



AI was therefore intentionally limited to [`tests/`](tests), where it could accelerate boilerplate, but kept out of [`app/`](app), where its inability to grasp architectural intent would have compromised quality and security.



---- **DRY validation via mixin factory**: A key abstraction was the `create_string_validators` factory. Instead of repeating `field_validator` logic for whitespace and empty-string checks, this factory generates a reusable mixin. This one mixin is inherited by all 6 Create and Update models, eliminating duplicated code and ensuring validation logic is defined in exactly one place.DRY validation via mixin factory: A key abstraction was the create_string_validators factory. Instead of repeating field_validator logic for whitespace and empty-string checks, this factory generates a reusable mixin. This one mixin is inherited by all 6 Create and Update models, eliminating duplicated code and ensuring validation logic is defined in exactly one place.



## 📂 Project Structure



```- **Transaction helper**: The `db_transaction` context manager trapped integrity errors (like duplicate category names per user via composite uniqueness) and routed them to consistent HTTP responses. Every write path behaved the same without repeating error-handling code.Transaction helper: The db_transaction context manager trapped integrity errors (like duplicate category names per user via composite uniqueness) and routed them to consistent HTTP responses. Every write path behaved the same without repeating error-handling code.

expense_tracker/

├── app/

│   ├── models/

│   ├── routers/These weren't abstractions for neatness—they eliminated repetitive code and prevented subtle inconsistencies.These weren’t abstractions for neatness—they eliminated repetitive code and prevented subtle inconsistencies.

│   ├── auth.py

│   ├── service.py

│   ├── dependencies.py

│   ├── exceptions.py### 3. Deliberate AI Use: Core Logic vs. Test Boilerplate3. Deliberate AI Use: Core Logic vs. Test Boilerplate

│   └── main.py

├── tests/

└── database.db

```For example, when relying on AI-generated tests early on, none of them explored cross-user scenarios. A test like "Can User A update an expense belonging to User B?" simply didn't exist. Writing that test manually exposed real authorization gaps that AI had no intuition to look for. This was eventually a problem that was phased out due to the `/me` refactor making these kind of cross-user attacks impossible by design but that wasn't always the case.For example, when relying on AI-generated tests early on, none of them explored cross-user scenarios. A test like “Can User A update an expense belonging to User B?” simply didn’t exist. Writing that test manually exposed real authorization gaps that AI had no intuition to look for. This was eventually a problem that was phased out due to the /me refactor making these kind of cross-user attacks impossible by design but that wasn’t always the case.



---



## 🔮 Future ImprovementsThis is why the core application logic in the [`app`](app) directory was handwritten. While AI can scaffold a "working" endpoint, it struggles to weave in the project's specific architectural needs, like integrating the correct ownership dependency or the `db_transaction` helper for consistent error handling. These are the exact vulnerabilities that AI-generated application code would have likely introduced.This is why the core application logic in the app/ directory was handwritten. While AI can scaffold a "working" endpoint, it struggles to weave in the project's specific architectural needs, like integrating the correct ownership dependency or the db_transaction helper for consistent error handling. These are the exact vulnerabilities that AI-generated application code would have likely introduced.



- Date-range filtering

- PostgreSQL support

- DockerizationAI was therefore intentionally limited to [`tests`](tests), where it could accelerate boilerplate, but kept out of [`app`](app), where its inability to grasp architectural intent would have compromised quality and security.AI was therefore intentionally limited to tests/, where it could accelerate boilerplate, but kept out of app/, where its inability to grasp architectural intent would have compromised quality and security.

- Cloud deployment



## Project StructureProject Structure



```expense_tracker/

expense_tracker/├── app/

├── app/│   ├── models/

│   ├── models/│   ├── routers/

│   ├── routers/│   ├── auth.py

│   ├── auth.py│   ├── service.py

│   ├── service.py│   ├── dependencies.py

│   ├── dependencies.py│   ├── exceptions.py

│   ├── exceptions.py│   └── main.py

│   └── main.py├── tests/

├── tests/└── database.db

└── database.db

```



## Future Improvements



- Date-range filteringFuture Improvements

- PostgreSQL support

- DockerizationDate-range filtering

- Cloud deployment

PostgreSQL support

Dockerization

Cloud deployment