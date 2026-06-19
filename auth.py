"""
auth.py — User authentication: registration, login, password hashing.
Uses hashlib SHA-256 with random salt for secure password storage.
"""

import hashlib
import os
import sqlite3
from database import get_connection


def hash_password(password, salt=None):
    """Hash a password with SHA-256 + salt. Returns (hash, salt)."""
    if salt is None:
        salt = os.urandom(32).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt


def register_user(username, email, password):
    """
    Register a new user. Returns (success: bool, message: str).
    Validates all inputs before inserting.
    """
    if not username or not email or not password:
        return False, "All fields are required."
    username = username.strip()
    email = email.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if "@" not in email or "." not in email:
        return False, "Invalid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = get_connection()
    try:
        password_hash, salt = hash_password(password)
        conn.execute(
            "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, salt),
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e).lower():
            return False, "Username already exists."
        elif "email" in str(e).lower():
            return False, "Email already registered."
        return False, "Registration failed."
    finally:
        conn.close()


def login_user(username, password):
    """
    Authenticate a user. Returns (user_dict or None, message: str).
    """
    if not username or not password:
        return None, "Please enter both username and password."

    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username.strip(),)
    ).fetchone()
    conn.close()

    if user is None:
        return None, "Username not found."

    hashed, _ = hash_password(password, user["salt"])
    if hashed != user["password_hash"]:
        return None, "Incorrect password."

    return dict(user), "Login successful!"
