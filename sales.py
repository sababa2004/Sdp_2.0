import db
from tkinter import messagebox

def load(tree):
    tree.delete(*tree.get_children())
    current_date = None
    with db.con() as c:
        for r in c.execute("SELECT id,product,quantity,total,timestamp FROM sales ORDER BY timestamp DESC, id DESC"):
            date_str = str(r[4]).split(" ")[0] if r[4] else "Unknown"
            if date_str != current_date:
                tree.insert("", "end", values=("---", f"--- DATE: {date_str} ---", "---", "---", "---"), tags=("header",))
                current_date = date_str
            tree.insert("","end", values=r)
    tree.tag_configure("header", background="#4a4a4a", foreground="#ffd700")

def _validate_item(name_or_barcode, qty_s):
    p = db.find(name_or_barcode)
    if not p:
        return "Product not found.", None
    try:
        qty = float(qty_s)
    except Exception:
        return "Invalid quantity.", None
    if p["stock"] < qty:
        return f"Insufficient stock. Only {p['stock']} {p['unit']} left.", None
    return None, {
        "id": p["id"],
        "product": p["name"],
        "qty": qty,
        "total": qty * p["sell_price"],
        "remaining_stock": p["stock"] - qty,
        "min_stock": p["min_stock"],
    }

def checkout(items, tree=None):
    if not items:
        return "No items to checkout.", None

    prepared = []
    for item in items:
        err, row = _validate_item(item["product"], item["qty"])
        if err:
            return err, None
        prepared.append(row)

    sale_ids, alerts = [], []
    with db.con() as c:
        for row in prepared:
            c.execute(
                "INSERT INTO sales(product,quantity,total,timestamp) VALUES(?,?,?,CURRENT_TIMESTAMP)",
                (row["product"], row["qty"], row["total"]),
            )
            sale_ids.append(c.execute("SELECT last_insert_rowid()").fetchone()[0])
            c.execute("UPDATE products SET stock=stock-? WHERE id=?", (row["qty"], row["id"]))
            if row["remaining_stock"] <= row["min_stock"]:
                alerts.append({"product": row["product"], "stock": row["remaining_stock"]})

    if tree:
        load(tree)
    return None, {
        "sale_ids": sale_ids,
        "items": [{"product": r["product"], "quantity": r["qty"], "total": r["total"]} for r in prepared],
        "total": sum(r["total"] for r in prepared),
        "alerts": alerts,
    }

def sell(name_or_barcode, qty_s, tree):
    err, result = checkout([{"product": name_or_barcode, "qty": qty_s}], tree=tree)
    if err:
        messagebox.showerror("Error", err)
        return "error"
    if result["alerts"]:
        first = result["alerts"][0]
        return {"alert": True, "product": first["product"], "stock": first["stock"]}
    return None