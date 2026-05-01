import db
from tkinter import messagebox

def load(tree):
    tree.delete(*tree.get_children())
    current_date = None
    with db.con() as c:
        for r in c.execute('''
            SELECT cr.id, cust.name, cust.phone, cust.email, cr.product, cr.quantity, cr.amount, cr.timestamp, cr.customer_id
            FROM credit cr 
            LEFT JOIN customers cust ON cr.customer_id = cust.id 
            ORDER BY cr.timestamp DESC, cr.id DESC'''):
            
            date_str = str(r[7]).split(" ")[0] if r[7] else "Unknown"
            if date_str != current_date:
                tree.insert("","end", values=("---", f"--- DATE: {date_str} ---", "---", "---", "---", "---", "---", "---", "---"), tags=("header",))
                current_date = date_str
                
            p = db.find(r[4])
            unit = p["unit"] if p else ""
            tree.insert("","end", values=(r[0], r[1], r[2] or "", r[3] or "", r[4], f"{r[5]} {unit}", r[6], r[7], r[8]))
    tree.tag_configure("header", background="#4a4a4a", foreground="#ffd700")

def add(customer_id, customer_name, phone, email, name_or_barcode, qty_s, tree=None):
    p = db.find(name_or_barcode)
    if not p:
        messagebox.showerror("Error","Product not found.")
        return "Product not found.", None
    try: qty = float(qty_s)
    except:
        messagebox.showerror("Error","Invalid quantity.")
        return "Invalid quantity.", None
    if p["stock"] < qty:
        messagebox.showerror("Error",f"Insufficient stock. Only {p['stock']} {p['unit']} left.")
        return "Insufficient stock.", None
    
    amount = qty * p["sell_price"]
    actual_name = p["name"]
    err = None
    with db.con() as c:
        if not customer_id:
            # Need to find or create customer
            r = c.execute("SELECT id FROM customers WHERE name=?", (customer_name,)).fetchone()
            if r:
                customer_id = r[0]
                c.execute("UPDATE customers SET phone=COALESCE(phone, ?), email=COALESCE(email, ?) WHERE id=?", (phone, email, customer_id))
            else:
                c.execute("INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)", (customer_name, phone, email))
                customer_id = c.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Get updated customer name just in case
        customer_name_db = c.execute("SELECT name FROM customers WHERE id=?", (customer_id,)).fetchone()[0]
        c.execute("INSERT INTO credit(customer_id,customer,phone,email,product,quantity,amount,timestamp) VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", (customer_id,customer_name_db,phone,email,actual_name,qty,amount))
        c.execute("UPDATE products SET stock=stock-? WHERE id=?", (qty, p["id"]))
    if tree: load(tree)
    return None, amount

def pay(cid, tree=None):
    with db.con() as c:
        r = c.execute("SELECT id,customer,phone,email,product,quantity,amount,timestamp,customer_id FROM credit WHERE id=?", (cid,)).fetchone()
        if not r: return "Not found", None
        row = dict(zip(["id","customer","phone","email","product","quantity","amount","timestamp","customer_id"], r))
        c.execute("INSERT INTO sales(product,quantity,total,timestamp) VALUES(?,?,?,CURRENT_TIMESTAMP)", (row["product"], row["quantity"], row["amount"]))
        c.execute("DELETE FROM credit WHERE id=?", (cid,))
    if tree: load(tree)
    return None, row

def get_customers():
    with db.con() as c:
        return c.execute("SELECT id, name, phone, email FROM customers").fetchall()

def update_customer(customer_id, name, phone, email):
    try:
        customer_id = int(customer_id)
    except (TypeError, ValueError):
        return "Invalid customer id."

    name = (name or "").strip()
    phone = (phone or "").strip()
    email = (email or "").strip()

    if not name:
        return "Customer name is required."

    with db.con() as c:
        exists = c.execute(
            "SELECT id FROM customers WHERE id=?",
            (customer_id,)
        ).fetchone()
        if not exists:
            return "Customer not found."

        conflict = c.execute(
            "SELECT id FROM customers WHERE name=? AND id<>?",
            (name, customer_id)
        ).fetchone()
        if conflict:
            return "Customer name already exists."

        c.execute(
            "UPDATE customers SET name=?, phone=?, email=? WHERE id=?",
            (name, phone, email, customer_id)
        )

        # Keep denormalized credit rows in sync with customers table.
        c.execute(
            "UPDATE credit SET customer=?, phone=?, email=? WHERE customer_id=?",
            (name, phone, email, customer_id)
        )
    return None
