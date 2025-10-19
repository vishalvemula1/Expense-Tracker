"""
Script to populate the database with 20 diverse test expenses
using the direct database functions from expenses_db.py
"""

from datetime import date, timedelta
from sqlmodel import Session
from expenses_db import engine, Expense, create_db_and_tables


def populate_expenses():
    """Populate database with 20 diverse test expenses covering different cases"""
    
    # Create tables first
    create_db_and_tables()
    
    # List of diverse test expenses
    test_expenses = [
        # Food & Groceries
        {"name": "Grocery Shopping", "amount": 45.50, "category": "Food", "description": "Weekly groceries"},
        {"name": "Restaurant Dinner", "amount": 68.99, "category": "Food", "description": "Dinner at Italian restaurant"},
        {"name": "Coffee", "amount": 5.25, "category": "Food", "description": "Morning coffee"},
        
        # Transportation
        {"name": "Gas Fill Up", "amount": 52.00, "category": "Transportation", "description": "Fuel for car"},
        {"name": "Taxi Ride", "amount": 15.75, "category": "Transportation", "description": "Ride to airport"},
        {"name": "Public Transport Pass", "amount": 80.00, "category": "Transportation", "description": "Monthly metro pass"},
        
        # Utilities & Bills
        {"name": "Electric Bill", "amount": 125.50, "category": "Utilities", "description": "Monthly electricity"},
        {"name": "Internet Bill", "amount": 59.99, "category": "Utilities", "description": "Monthly internet service"},
        {"name": "Water Bill", "amount": 35.00, "category": "Utilities", "description": "Monthly water"},
        
        # Entertainment
        {"name": "Movie Tickets", "amount": 25.00, "category": "Entertainment", "description": "Two cinema tickets"},
        {"name": "Streaming Subscription", "amount": 12.99, "category": "Entertainment", "description": "Netflix monthly"},
        {"name": "Concert Tickets", "amount": 150.00, "category": "Entertainment", "description": "Music festival entry"},
        
        # Health & Fitness
        {"name": "Gym Membership", "amount": 45.00, "category": "Health", "description": "Monthly gym fee"},
        {"name": "Pharmacy", "amount": 23.45, "category": "Health", "description": "Medications and vitamins"},
        {"name": "Doctor Visit", "amount": 100.00, "category": "Health", "description": "Dental checkup"},
        
        # Shopping & Clothing
        {"name": "New Shirt", "amount": 39.99, "category": "Shopping", "description": "Casual shirt"},
        {"name": "Shoes", "amount": 89.50, "category": "Shopping", "description": "Running shoes"},
        
        # Zero amount edge case
        {"name": "Reimbursement Recorded", "amount": 0.00, "category": "Other", "description": "Tracking only"},
        
        # Large expense
        {"name": "Flight Ticket", "amount": 450.00, "category": "Travel", "description": "Round trip flight"},
        
        # Small amount
        {"name": "Snack", "amount": 2.50, "category": "Food", "description": "Vending machine snack"},
    ]
    
    # Add expenses to database
    with Session(engine) as session:
        for i, expense_data in enumerate(test_expenses):
            # Create expense with date spread across recent days
            days_ago = i % 10  # Spread across last 10 days
            expense_date = date.today() - timedelta(days=days_ago)
            
            expense = Expense(
                name=expense_data["name"],
                amount=expense_data["amount"],
                category=expense_data["category"],
                description=expense_data["description"],
                date_of_entry=expense_date
            )
            session.add(expense)
        
        # Commit all expenses at once
        session.commit()
        print(f"✅ Successfully added {len(test_expenses)} test expenses to the database!")


if __name__ == "__main__":
    populate_expenses()
