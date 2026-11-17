"""Local, safe library-login demonstration using Python's standard library."""

import hashlib
import hmac
import logging
import os
import re
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).with_name("secure_demo.db")
USERNAME = re.compile(r"^[A-Za-z0-9_]{3,30}$")
LOG = logging.getLogger("secure_demo")


def hash_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210_000)
    return salt, digest


def initialize_database() -> None:
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, salt BLOB NOT NULL, password_hash BLOB NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS books (title TEXT NOT NULL)")
        if connection.execute("SELECT 1 FROM users WHERE username = ?", ("demo_user",)).fetchone() is None:
            salt, password_hash = hash_password("SafeDemoPassword!42")
            connection.execute("INSERT INTO users VALUES (?, ?, ?)", ("demo_user", salt, password_hash))
            connection.executemany("INSERT INTO books VALUES (?)", [("Secure Coding Basics",), ("Python Fundamentals",)])


def authenticate(username: str, password: str) -> bool:
    if not USERNAME.fullmatch(username) or not 12 <= len(password) <= 128:
        LOG.warning("Rejected malformed login input")
        return False
    with sqlite3.connect(DATABASE) as connection:
        row = connection.execute("SELECT salt, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if row is None:
        LOG.warning("Failed login for unknown account")
        return False
    valid = hmac.compare_digest(hash_password(password, row[0])[1], row[1])
    LOG.info("Login %s", "accepted" if valid else "rejected")
    return valid


def search_books(term: str) -> list[str]:
    if not 1 <= len(term) <= 60 or not re.fullmatch(r"[A-Za-z0-9 ]+", term):
        raise ValueError("Search terms may contain only letters, numbers, and spaces.")
    with sqlite3.connect(DATABASE) as connection:
        rows = connection.execute("SELECT title FROM books WHERE title LIKE ?", (f"%{term}%",)).fetchall()
    return [row[0] for row in rows]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    initialize_database()
    print("Valid login:", authenticate("demo_user", "SafeDemoPassword!42"))
    print("Book search:", search_books("Coding"))
    try:
        search_books("' OR 1=1 --")
    except ValueError as error:
        print("Unsafe input rejected:", error)
