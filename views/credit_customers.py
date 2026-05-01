import customtkinter as ctk
from tkinter import ttk, messagebox
import re
import db
import credit
from views.theme import (
    CARD_BG, ACCENT, ACCENT_HOVER, BORDER, CORNER_RADIUS, setup_treeview_style, section_title
)

class CreditCustomersView(ctk.CTkFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_instance
        self.selected_customer_id = None
        tree_style = setup_treeview_style()
        
        # Title
        section_title(self, "Credit Customers").pack(pady=(18, 10), padx=20, anchor="w")
        
        # Tools Frame for interactions
        tools_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=CORNER_RADIUS, border_width=1, border_color=BORDER)
        tools_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(tools_frame, text="Name").pack(side="left", padx=(12, 5), pady=8)
        self.name_e = ctk.CTkEntry(tools_frame, width=160)
        self.name_e.pack(side="left", padx=5, pady=8)

        ctk.CTkLabel(tools_frame, text="Phone").pack(side="left", padx=(8, 5), pady=8)
        self.phone_e = ctk.CTkEntry(tools_frame, width=120)
        self.phone_e.pack(side="left", padx=5, pady=8)

        ctk.CTkLabel(tools_frame, text="Email").pack(side="left", padx=(8, 5), pady=8)
        self.email_e = ctk.CTkEntry(tools_frame, width=180)
        self.email_e.pack(side="left", padx=5, pady=8)

        ctk.CTkButton(
            tools_frame, text="Update", width=100, fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.update_customer
        ).pack(side="right", padx=5, pady=5)

        ctk.CTkButton(
            tools_frame, text="Clear", width=100, fg_color="#1A2A47", hover_color="#223861",
            command=self.clear_selection, border_width=1, border_color=BORDER
        ).pack(side="right", padx=5, pady=5)

        ctk.CTkButton(
            tools_frame, text="Mark as Paid", width=150, fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=self.pay_all_for_customer
        ).pack(side="right", padx=5, pady=5)
                      
        # Treeview mapping
        cols = ["Cust ID", "Customer", "Phone", "Email", "Total Due ৳", "Latest Date"]
        widths = [80, 200, 150, 200, 150, 150]
        
        # Treeview Frame
        tree_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=CORNER_RADIUS, border_width=1, border_color=BORDER)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15, style=tree_style)
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
            
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_customer_select)
        
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        with db.con() as c:
            for r in c.execute('''
                SELECT cr.customer_id, cust.name, cust.phone, cust.email, SUM(cr.amount) as total_due, MAX(cr.timestamp) as latest_date
                FROM credit cr 
                JOIN customers cust ON cr.customer_id = cust.id 
                GROUP BY cr.customer_id
                ORDER BY total_due DESC'''):
                self.tree.insert("", "end", values=(r[0], r[1], r[2] or "-", r[3] or "-", f"{r[4]:.2f}", r[5]))
        items = self.tree.get_children()
        if not items:
            self.clear_form()
            return

        if self.selected_customer_id is not None:
            selected = None
            for item_id in items:
                vals = self.tree.item(item_id, "values")
                if vals and str(vals[0]) == str(self.selected_customer_id):
                    selected = item_id
                    break
            if selected:
                self.tree.selection_set(selected)
                self.tree.focus(selected)
                self.on_customer_select()

    def selected_values(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0], "values")

    def clear_form(self):
        self.name_e.delete(0, "end")
        self.phone_e.delete(0, "end")
        self.email_e.delete(0, "end")
        self.selected_customer_id = None

    def clear_selection(self):
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(*sel)
        self.clear_form()

    def on_customer_select(self, event=None):
        item = self.selected_values()
        if not item:
            return
        self.selected_customer_id = str(item[0])
        self.clear_form()
        self.selected_customer_id = str(item[0])
        self.name_e.insert(0, item[1] if item[1] != "-" else "")
        self.phone_e.insert(0, item[2] if item[2] != "-" else "")
        self.email_e.insert(0, item[3] if item[3] != "-" else "")

    def update_customer(self):
        if not self.selected_customer_id:
            return messagebox.showwarning("Warning", "Select a customer to update.")

        name = self.name_e.get().strip()
        phone = self.phone_e.get().strip()
        email = self.email_e.get().strip()

        if not name:
            return messagebox.showwarning("Input", "Customer name is required.")
        if phone:
            if len(phone) != 11:
                return messagebox.showwarning(
                    "Invalid Phone",
                    f"Phone number must be exactly 11 digits.\nYou entered {len(phone)} digit(s).")
            if not re.fullmatch(r"01[3-9]\d{8}", phone):
                return messagebox.showwarning(
                    "Invalid Phone",
                    "Phone must be a valid 11-digit Bangladesh number (e.g. 01XXXXXXXXX).")
        if email and not email.lower().endswith("@gmail.com"):
            return messagebox.showerror(
                "Invalid Email",
                "Email address must end with @gmail.com\n(e.g. customer@gmail.com)")

        err = credit.update_customer(self.selected_customer_id, name, phone, email)
        if err:
            return messagebox.showerror("Error", err)

        self.refresh()
        if hasattr(self.app, "frames") and "Credit" in self.app.frames:
            self.app.frames["Credit"].refresh_customers()
        messagebox.showinfo("Success", "Customer updated successfully.")
                 
    def pay_all_for_customer(self):
        item = self.selected_values()
        if not item:
            return messagebox.showwarning("Warning", "Select a customer to settle.")

        customer_id = item[0]
        customer_name = item[1]
        
        if not messagebox.askyesno("Confirm", f"Mark all credit items as paid for '{customer_name}'?"):
            return
            
        with db.con() as c:
            # Move all to sales
            c.execute("""
                INSERT INTO sales (product, quantity, total, timestamp)
                SELECT product, quantity, amount, CURRENT_TIMESTAMP
                FROM credit WHERE customer_id=?
            """, (customer_id,))
            
            # Delete from credit
            c.execute("DELETE FROM credit WHERE customer_id=?", (customer_id,))
            
        messagebox.showinfo("Success", f"All credit for {customer_name} has been marked as paid!")
        self.refresh()
