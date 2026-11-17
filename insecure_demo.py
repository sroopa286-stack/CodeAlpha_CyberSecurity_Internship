"""INTENTIONALLY INSECURE TRAINING EXAMPLE. Do not deploy or reuse this code."""

import sqlite3

DATABASE = "library.db"


def login(username, password):
    """Problems: SQL injection, plaintext password comparison, detailed errors."""
    connection = sqlite3.connect(DATABASE)
    query = f"SELECT username FROM users WHERE username = '{username}' AND password = '{password}'"
    user = connection.execute(query).fetchone()
    if user:
        print(f"Welcome {username}")
    else:
        print(f"No account found for {username}; password was {password}")
    connection.close()


def find_book(term):
    """Problem: user input is concatenated into SQL."""
    connection = sqlite3.connect(DATABASE)
    query = f"SELECT title FROM books WHERE title LIKE '%{term}%'"
    return connection.execute(query).fetchall()


if __name__ == "__main__":
    print("Review only. This intentionally insecure sample must not be run against real data.")
