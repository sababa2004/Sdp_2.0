import sqlite3, os
from datetime import datetime

DB = "shop.db"

def con(): return sqlite3.connect(DB)

def init():
    with con() as c:
        # Core tables
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE, password TEXT, role TEXT);
            
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, barcode TEXT, unit TEXT,
            buy_price REAL, sell_price REAL, stock REAL, min_stock REAL DEFAULT 5);
            
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT, quantity REAL, total REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
            
        CREATE TABLE IF NOT EXISTS credit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT, product TEXT, quantity REAL, amount REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, phone TEXT, email TEXT);
        """)
        
        # Migrations for existing database
        try: c.execute("ALTER TABLE products ADD COLUMN barcode TEXT")
        except sqlite3.OperationalError: pass
        
        try: c.execute("ALTER TABLE products ADD COLUMN min_stock REAL DEFAULT 5")
        except sqlite3.OperationalError: pass

        try: 
            c.execute("ALTER TABLE sales ADD COLUMN timestamp DATETIME")
            c.execute("UPDATE sales SET timestamp = CURRENT_TIMESTAMP WHERE timestamp IS NULL")
        except sqlite3.OperationalError: pass
        
        try: 
            c.execute("ALTER TABLE credit ADD COLUMN timestamp DATETIME")
            c.execute("UPDATE credit SET timestamp = CURRENT_TIMESTAMP WHERE timestamp IS NULL")
        except sqlite3.OperationalError: pass
        
        try: c.execute("ALTER TABLE credit ADD COLUMN phone TEXT")
        except sqlite3.OperationalError: pass
        
        try: c.execute("ALTER TABLE credit ADD COLUMN email TEXT")
        except sqlite3.OperationalError: pass

        c.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, phone TEXT, email TEXT
        );
        """)
        
        try: 
            c.execute("ALTER TABLE credit ADD COLUMN customer_id INTEGER")
            
            # Migrate unique names from credit table to customers table
            # Insert distinct customers
            c.execute("INSERT OR IGNORE INTO customers (name, phone, email) SELECT DISTINCT customer, phone, email FROM credit WHERE customer IS NOT NULL")
            # Update customer_id in credit table
            c.execute("UPDATE credit SET customer_id = (SELECT id FROM customers WHERE customers.name = credit.customer) WHERE customer_id IS NULL")
        except sqlite3.OperationalError: pass

        # Create default admin user if none exists
        if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin', 'Admin')")
            
def find(name_or_barcode):
    with con() as c:
        r = c.execute("SELECT id, name, barcode, unit, buy_price, sell_price, stock, min_stock FROM products WHERE name=? COLLATE NOCASE OR barcode=?", (name_or_barcode, name_or_barcode)).fetchone()
        return dict(zip(["id","name","barcode","unit","buy_price","sell_price","stock","min_stock"], r)) if r else None

def verify_login(username, password):
    with con() as c:
        return c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password)).fetchone()

def totals():
    with con() as c:
        sales = c.execute("SELECT SUM(total) FROM sales").fetchone()[0] or 0
        credit = c.execute("SELECT SUM(amount) FROM credit").fetchone()[0] or 0
        profit = c.execute("""
            SELECT SUM((p.sell_price-p.buy_price)*s.quantity)
            FROM sales s JOIN products p ON p.name=s.product COLLATE NOCASE
        """).fetchone()[0] or 0
        return profit, sales, credit

def get_low_stock():
    with con() as c:
        return c.execute("SELECT name, stock, min_stock FROM products WHERE stock <= min_stock").fetchall()

def get_recent_sales():
    with con() as c:
        return c.execute("SELECT strftime('%Y-%m-%d', timestamp) as date, SUM(total) FROM sales GROUP BY date ORDER BY date DESC LIMIT 7").fetchall()

def get_recent_performance():
    with con() as c:
        return c.execute("""
            SELECT date, SUM(sales), SUM(credit) FROM (
               SELECT strftime('%Y-%m-%d', timestamp) as date, total as sales, 0 as credit FROM sales
               UNION ALL
               SELECT strftime('%Y-%m-%d', timestamp) as date, 0 as sales, amount as credit FROM credit
            ) WHERE date IS NOT NULL
            GROUP BY date ORDER BY date DESC LIMIT 7
        """).fetchall()

