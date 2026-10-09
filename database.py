import os
import sqlite3


def db_path():
    # على Render يجب أن يشير DB_PATH إلى القرص الدائم، مثل /var/data/shop.db
    return os.getenv("DB_PATH", "shop.db")


def get_connection():
    path = db_path()
    folder = os.path.dirname(path)

    if folder:
        os.makedirs(folder, exist_ok=True)

    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_database():
    connection = get_connection()

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price INTEGER NOT NULL CHECK (price >= 0),
            cost INTEGER NOT NULL DEFAULT 0,
            stock REAL NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER REFERENCES customers(id),
            total_amount INTEGER NOT NULL,
            paid_amount INTEGER NOT NULL,
            debt_amount INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL REFERENCES sales(id),
            product_id INTEGER REFERENCES products(id),
            product_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_price INTEGER NOT NULL,
            unit_cost INTEGER NOT NULL DEFAULT 0,
            line_total INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER REFERENCES customers(id),
            amount INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity_change REAL NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
        CREATE INDEX IF NOT EXISTS idx_sales_created ON sales(created_at);
        CREATE INDEX IF NOT EXISTS idx_payments_customer ON payments(customer_id);
        CREATE INDEX IF NOT EXISTS idx_items_sale ON sale_items(sale_id);
        """
    )

    connection.commit()
    connection.close()
