import db
from tkinter import messagebox

UNITS = ["pcs","kg","g","L","mL","box","dozen","pack"]

def load(tree):
    tree.delete(*tree.get_children())
    with db.con() as c:
        for r in c.execute("SELECT id, name, barcode, unit, buy_price, sell_price, stock, min_stock FROM products"):
            tree.insert("","end", values=r)

def search(q, tree):
    tree.delete(*tree.get_children())
    with db.con() as c:
        for r in c.execute("SELECT id, name, barcode, unit, buy_price, sell_price, stock, min_stock FROM products WHERE name LIKE ? OR barcode LIKE ?", (f"%{q}%", f"%{q}%")):
            tree.insert("","end", values=r)

def add(name, barcode, unit, buy, sell, stock, min_stock, tree):
    try:
        with db.con() as c:
            c.execute("INSERT INTO products(name, barcode, unit, buy_price, sell_price, stock, min_stock) VALUES(?,?,?,?,?,?,?)",
                      (name, barcode, unit, float(buy), float(sell), float(stock), float(min_stock)))
        load(tree)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update(pid, name, barcode, unit, buy, sell, stock, min_stock, tree):
    try:
        with db.con() as c:
            c.execute("UPDATE products SET name=?, barcode=?, unit=?, buy_price=?, sell_price=?, stock=?, min_stock=? WHERE id=?",
                      (name, barcode, unit, float(buy), float(sell), float(stock), float(min_stock), pid))
        load(tree)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete(pid, tree):
    with db.con() as c:
        c.execute("DELETE FROM products WHERE id=?", (pid,))
    load(tree)
