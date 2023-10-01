import sqlite3

DB_NAME = "app.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables():
    create_items = """CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    desc TEXT NOT NULL,
    user TEXT NOT NULL,
    price REAL,
    FOREIGN KEY (user)
        REFERENCES users (id)
    )"""
    create_users = """CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL
    )"""
    create_bids = """CREATE TABLE IF NOT EXISTS bids (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL,
    bid_owner INTEGER NOT NULL,
    bid REAL NOT NULL,
    FOREIGN KEY (item_id)
        REFERENCES items (id)
    FOREIGN KEY (bid_owner)
        REFERENCES users (id)
    )"""

    db = get_db()
    with db:
        db.execute(create_items)
        db.execute(create_users)
        db.execute(create_bids)
        db.execute('PRAGMA journal_mode=wal')