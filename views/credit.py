import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import re
import db, credit
from views.theme import (
    CARD_BG, INPUT_BG, TEXT_PRIMARY, TEXT_MUTED, ACCENT, ACCENT_HOVER,
    SUCCESS, SUCCESS_HOVER, WARNING, WARNING_HOVER, DANGER, DANGER_HOVER,
    BORDER, CORNER_RADIUS, setup_treeview_style, section_title,
)

# ── Validation helpers ─────────────────────────────────────────────
def _valid_phone(ph):
    """Exactly 11 digits (Bangladesh mobile)."""
    return bool(re.fullmatch(r"01[3-9]\d{8}", ph))

def _valid_email(em):
    """Must end with @gmail.com (empty is allowed – optional field)."""
    return em == "" or em.lower().endswith("@gmail.com")


class CreditView(ctk.CTkFrame):
    def __init__(self, master, reload_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.reload_callback = reload_callback
        self.cart = []
        self.customers_data = []
        self.selected_customer_id = None

        section_title(self, "Credit").pack(pady=(18, 10), padx=20, anchor="w")
        tree_style = setup_treeview_style()

        # ── Input form ────────────────────────────────────────────
        form = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=CORNER_RADIUS,
                            border_width=1, border_color=BORDER)
        form.pack(fill="x", padx=20, pady=8)

        def lbl(text): return ctk.CTkLabel(form, text=text, text_color=TEXT_MUTED)
        def entry(w):  return ctk.CTkEntry(form, width=w, fg_color=INPUT_BG,
                                           border_color=BORDER, text_color=TEXT_PRIMARY)

        lbl("Customer:").pack(side="left", padx=(14, 5), pady=14)
        self.cu_e = ctk.CTkComboBox(form, width=120, command=self.on_customer_select,
                                    fg_color=INPUT_BG, border_color=BORDER,
                                    text_color=TEXT_PRIMARY, button_color=ACCENT,
                                    button_hover_color=ACCENT_HOVER)
        self.cu_e.set("")
        self.cu_e.pack(side="left", padx=5)
        self.cu_e.bind("<KeyRelease>", self.filter_customers)

        lbl("Cust ID:").pack(side="left", padx=(5, 5))
        self.cid_var = ctk.StringVar(value="")
        tk.Label(form, textvariable=self.cid_var, bg=CARD_BG,
                 fg="#8FBEFF", font=("Segoe UI", 9, "bold")).pack(side="left", padx=5)

        lbl("Phone:").pack(side="left", padx=(5, 5))
        self.ph_e = entry(110)
        self.ph_e.pack(side="left", padx=5)

        lbl("Email:").pack(side="left", padx=(5, 5))
        self.em_e = entry(130)
        self.em_e.pack(side="left", padx=5)

        lbl("Product:").pack(side="left", padx=(15, 5))
        self.cp_e = ctk.CTkComboBox(form, width=140, values=[], command=self.preview,
                                    fg_color=INPUT_BG, border_color=BORDER,
                                    text_color=TEXT_PRIMARY, button_color=ACCENT,
                                    button_hover_color=ACCENT_HOVER)
        self.cp_e.set("")
        self.cp_e.pack(side="left", padx=5)
        self.cp_e.bind("<KeyRelease>", self.preview)

        lbl("Quantity:").pack(side="left", padx=(5, 5))
        self.cq_e = entry(70)
        self.cq_e.pack(side="left", padx=5)
        self.cq_e.bind("<KeyRelease>", self.preview)

        self.cunit_hint = ctk.StringVar(value="")
        tk.Label(form, textvariable=self.cunit_hint, bg=CARD_BG,
                 fg="#8FBEFF", font=("Segoe UI", 9, "italic")).pack(side="left", padx=5)

        self.amt_var = ctk.StringVar(value="Amount: –")
        tk.Label(form, textvariable=self.amt_var, bg=CARD_BG,
                 fg="#FEC568", font=("Segoe UI", 10, "bold")).pack(side="left", padx=10)

        # ── Cart action bar ───────────────────────────────────────
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=4)

        ctk.CTkButton(bar, text="Add to Cart", fg_color=WARNING,
                      hover_color=WARNING_HOVER, text_color="black",
                      command=self.add_to_cart, width=110).pack(side="left", padx=(10, 5))

        self.cart_var = ctk.StringVar(value="Cart: 0 items (0.00 ৳)")
        tk.Label(bar, textvariable=self.cart_var, bg="#0F1A30",
                 fg=TEXT_PRIMARY, font=("Segoe UI", 10)).pack(side="left", padx=10)

        ctk.CTkButton(bar, text="Checkout Credit", fg_color=SUCCESS,
                      hover_color=SUCCESS_HOVER, text_color="white",
                      command=self.checkout_cart, width=130).pack(side="left", padx=5)
        ctk.CTkButton(bar, text="Clear Cart", fg_color="#1A2A47",
                      hover_color="#223861", text_color="white",
                      command=self.clear_cart, width=100,
                      border_width=1, border_color=BORDER).pack(side="left", padx=5)
        ctk.CTkButton(bar, text="Clear Fields", fg_color="#1A2A47",
                      hover_color="#223861", text_color="white",
                      command=self.clear_inputs, width=110,
                      border_width=1, border_color=BORDER).pack(side="left", padx=5)
        ctk.CTkButton(bar, text="Mark Paid", fg_color=DANGER,
                      hover_color=DANGER_HOVER, text_color="white",
                      command=self.c_paid, width=110).pack(side="right", padx=10)

        # ── Treeview ──────────────────────────────────────────────
        cols    = ["ID", "Customer", "Phone", "Email", "Product", "Qty (unit)", "Amount ৳", "Timestamp"]
        widths  = [40, 120, 0, 0, 120, 80, 80, 130]
        disp    = [1, 2, 5, 6, 7, 8]

        tf = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=CORNER_RADIUS,
                          border_width=1, border_color=BORDER)
        tf.pack(fill="both", expand=True, padx=20, pady=(5, 12))

        self.ctree = ttk.Treeview(tf, columns=list(range(1, len(cols)+1)),
                                   displaycolumns=disp, show="headings",
                                   height=10, style=tree_style)
        for i, (col, w) in enumerate(zip(cols, widths), 1):
            self.ctree.heading(i, text=col)
            self.ctree.column(i, width=w, anchor="center")

        sb = ttk.Scrollbar(tf, orient="vertical", command=self.ctree.yview)
        self.ctree.configure(yscrollcommand=sb.set)
        self.ctree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.ctree.bind("<<TreeviewSelect>>", self.on_csel)

        self.refresh()

    # ── Helpers ───────────────────────────────────────────────────
    def tval(self):
        sel = self.ctree.selection()
        return self.ctree.item(sel[0])["values"] if sel else None

    def _update_cart_label(self):
        total = sum(i["amount"] for i in self.cart)
        self.cart_var.set(f"Cart: {len(self.cart)} items ({total:.2f} ৳)")

    # ── Customer filtering / selection ────────────────────────────
    def filter_customers(self, event=None):
        val = self.cu_e.get().strip()
        if not val:
            self.cid_var.set("")
            self.selected_customer_id = None
            return
        for c in self.customers_data:
            if c[1] == val:
                self.selected_customer_id = c[0]
                self.cid_var.set(str(c[0]))
                return
        self.cid_var.set("(Auto Assign)")
        self.selected_customer_id = None

    def on_customer_select(self, choice):
        for c in self.customers_data:
            if c[1] == choice:
                self.ph_e.delete(0, "end")
                self.em_e.delete(0, "end")
                if c[2]: self.ph_e.insert(0, c[2])
                if c[3]: self.em_e.insert(0, c[3])
                self.selected_customer_id = c[0]
                self.cid_var.set(str(c[0]))
                return
        self.cid_var.set("(Auto Assign)")
        self.selected_customer_id = None

    # ── Amount preview ────────────────────────────────────────────
    def preview(self, choice=None):
        try:
            pn = str(choice) if isinstance(choice, str) else self.cp_e.get()
            p = db.find(pn.strip())
            if p:
                self.cunit_hint.set(f"({p['unit']} | ৳{p['sell_price']})")
                qty = float(self.cq_e.get()) if self.cq_e.get().strip() else 0.0
                self.amt_var.set(f"Amount: {qty * p['sell_price']:.2f} ৳")
            else:
                self.cunit_hint.set("")
                self.amt_var.set("Product not found" if self.cp_e.get().strip() else "Amount: –")
        except Exception:
            self.amt_var.set("Amount: –")

    # ── Tree row selection ────────────────────────────────────────
    def on_csel(self, event=None):
        v = self.tval()
        if not v:
            return
        self.selected_customer_id = None
        for c in self.customers_data:
            if c[1] == v[1]:
                self.selected_customer_id = c[0]
                self.cid_var.set(str(c[0]))
                break
        self.cu_e.set(v[1])
        self.ph_e.delete(0, "end")
        self.em_e.delete(0, "end")
        self.ph_e.insert(0, v[2] if v[2] != "None" else "")
        self.em_e.insert(0, v[3] if v[3] != "None" else "")
        self.cp_e.set(v[4])
        self.cq_e.delete(0, "end")
        self.cq_e.insert(0, str(v[5]).split()[0] if v[5] != "-" else "")
        self.preview()

    # ── Add to cart (validates only; NO DB write yet) ─────────────
    def add_to_cart(self):
        cu = self.cu_e.get().strip()
        ph = self.ph_e.get().strip()
        em = self.em_e.get().strip()
        pn = self.cp_e.get().strip()
        qs = self.cq_e.get().strip()

        if not all([cu, pn, qs, ph]):
            return messagebox.showwarning("Input", "Customer, Phone, Product, and Quantity are required.")

        # ── Phone: exactly 11 digits ──────────────────────────────
        if len(ph) != 11:
            return messagebox.showwarning(
                "Invalid Phone",
                f"Phone number must be exactly 11 digits.\nYou entered {len(ph)} digit(s).")
        if not _valid_phone(ph):
            return messagebox.showwarning(
                "Invalid Phone",
                "Phone must be a valid 11-digit Bangladesh number (e.g. 01XXXXXXXXX).")

        # ── Email: @gmail.com only ────────────────────────────────
        if em and not _valid_email(em):
            return messagebox.showerror(
                "Invalid Email",
                "Email address must end with @gmail.com\n(e.g. customer@gmail.com)")

        p = db.find(pn)
        if not p:
            return messagebox.showerror("Error", "Product not found.")
        try:
            qty = float(qs)
        except ValueError:
            return messagebox.showerror("Error", "Invalid quantity.")
        if p["stock"] < qty:
            return messagebox.showerror("Error", f"Insufficient stock. Only {p['stock']} left.")

        # Resolve customer id from local cache (no DB write here)
        cid = self.selected_customer_id
        if not cid:
            for c in self.customers_data:
                if c[1] == cu:
                    cid = c[0]
                    break

        self.cart.append({
            "customer_id": cid, "customer": cu, "phone": ph, "email": em,
            "product": pn, "qty": qs, "amount": qty * p["sell_price"],
        })
        self._update_cart_label()

        # Reset product fields only
        self.cp_e.set("")
        self.cq_e.delete(0, "end")
        self.amt_var.set("Amount: –")
        self.cunit_hint.set("")

    # ── Checkout: DB write + customer list update happens HERE ─────
    def checkout_cart(self):
        if not self.cart:
            return messagebox.showinfo("Empty Cart", "No items in the cart to checkout.")

        total_amount, added = 0, 0
        for item in self.cart:
            err, amt = credit.add(
                item["customer_id"], item["customer"], item["phone"],
                item["email"], item["product"], item["qty"], tree=None,
            )
            if err is None and amt is not None:
                total_amount += amt
                added += 1

        if added > 0:
            self.clear_cart()
            self.clear_inputs()
            self.after(0, self._refresh_after_checkout)
            messagebox.showinfo(
                "Checkout Complete",
                f"Successfully checked out {added} item(s).\nTotal: {total_amount:.2f} ৳")

    # ── Mark paid ─────────────────────────────────────────────────
    def c_paid(self):
        v = self.tval()
        if not v:
            return messagebox.showwarning("Select", "Select a credit row.")
        if not messagebox.askyesno("Mark Paid?", "Move credit to sales?"):
            return
        err, row = credit.pay(v[0], self.ctree)
        if err is None:
            self.clear_inputs()
            if self.reload_callback:
                self.reload_callback()
            messagebox.showinfo("Paid", f"{row['customer']} paid {row['amount']:.2f} ৳")

    # ── Cart helpers ──────────────────────────────────────────────
    def clear_cart(self):
        self.cart = []
        self._update_cart_label()

    def clear_inputs(self):
        self.cu_e.set("")
        self.ph_e.delete(0, "end")
        self.em_e.delete(0, "end")
        self.cp_e.set("")
        self.cq_e.delete(0, "end")
        self.cid_var.set("")
        self.selected_customer_id = None
        self.amt_var.set("Amount: –")
        self.cunit_hint.set("")
        sel = self.ctree.selection()
        if sel:
            self.ctree.selection_remove(*sel)

    # ── Refresh ───────────────────────────────────────────────────
    def refresh_customers(self):
        self.customers_data = credit.get_customers()
        names = list({c[1] for c in self.customers_data if c[1]})
        self.cu_e.configure(values=names)
        self.filter_customers()

    def refresh(self):
        credit.load(self.ctree)
        products = [p[0] for p in db.con().execute("SELECT name FROM products").fetchall()]
        self.cp_e.configure(values=products)
        self.refresh_customers()

    def _refresh_after_checkout(self):
        credit.load(self.ctree)
        self.refresh_customers()
        if self.reload_callback:
            self.reload_callback()
