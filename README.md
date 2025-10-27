# Expense Tracker API

This is a FastAPI-based API for a personal expense tracker. It allows users to manage their expenses through a secure and authenticated RESTful interface.

## Key Features

*   **User Authentication:** Secure user authentication using JWT (JSON Web Tokens). Passwords are not stored in the database, only their hashes.
*   **Expense Management:** Full CRUD (Create, Read, Update, Delete) functionality for expenses.
*   **Data Validation:** Robust data validation using Pydantic to ensure data integrity.
*   **Authorization:** Users can only access and modify their own expenses.
*   **Comprehensive Test Suite:** The application is thoroughly tested using Pytest, with a focus on unit and integration testing.

## Tech Stack

*   **Backend:** Python, FastAPI
*   **Database:** SQLModel, SQLite
*   **Authentication:** JWT, pwdlib
*   **Testing:** Pytest, Pytest-Asyncio
*   **Data Validation:** Pydantic

## Getting Started

### Prerequisites

*   Python 3.9+
*   Poetry (or pip)

### Installation and Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/expense-tracker.git
    cd expense-tracker
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    pip install -r app/requirements.txt
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the root directory and add the following variables:

    ```
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

4.  **Run the application:**

    ```bash
    uvicorn app.main:app --reload
    ```

    The API will be available at `http://127.0.0.1:8000`.

### Running the Tests

To run the tests, execute the following command in the root directory:

```bash
pytest
```

## API Endpoints

The API provides the following endpoints:

### Users

*   `POST /users/signup`: Create a new user.
*   `POST /users/login`: Log in and receive a JWT token.
*   `GET /users/{user_id}`: Get user details.
*   `PUT /users/{user_id}`: Update user details.
*   `DELETE /users/{user_id}`: Delete a user.

### Expenses

*   `POST /users/{user_id}/expenses/`: Add a new expense.
*   `GET /users/{user_id}/expenses/`: Get all expenses for a user.
*   `GET /users/{user_id}/expenses/{expense_id}`: Get a specific expense.
*   `PUT /users/{user_id}/expenses/{expense_id}`: Update an expense.
*   `DELETE /users/{user_id}/expenses/{expense_id}`: Delete an expense.

## Challenges & Key Learnings

This project was a great learning experience. Here are some of the key challenges I faced and what I learned from them:

1.  **Separation of Concerns:** I initially struggled with where to place the password hashing logic. I tried to implement it within the SQLModel class, but I soon realized that it was business logic, not data validation. I ended up moving the hashing logic to the API endpoints, which resulted in a cleaner and more maintainable codebase.

2.  **Dependency Management:** I encountered a circular import issue between my `dependencies.py` and `auth.py` files. This forced me to refactor my code and rethink my dependency injection strategy. I ended up creating a `services.py` file to house my business logic, which resolved the circular import and made my code more modular.

3.  **Advanced Python Concepts:** I had the opportunity to learn and apply some more advanced Python concepts, such as `TypeVar` for creating generic functions and using factory functions to create reusable Pydantic validators. These concepts helped me to write more concise and reusable code.

4.  **Authentication and Authorization:** I gained a deep understanding of how authentication and authorization work in a web application. I learned how to implement JWT-based authentication, how to securely store passwords, and how to restrict access to certain endpoints based on user permissions.