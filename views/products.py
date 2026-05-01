import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import product
from views.theme import (
    PANEL_BG, CARD_BG, INPUT_BG, TEXT_PRIMARY, TEXT_MUTED, ACCENT, ACCENT_HOVER,
    SUCCESS, SUCCESS_HOVER, DANGER, DANGER_HOVER, BORDER, CORNER_RADIUS,
    setup_treeview_style, section_title
)

class ProductsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.title_label = section_title(self, "Inventory")
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nw")
        
        self._setup_table_style()
        
    def _setup_table_style(self):
        tree_style = setup_treeview_style()
        
        # Form
        self.form_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=CORNER_RADIUS, border_width=1, border_color=BORDER)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Row 1
        ctk.CTkLabel(self.form_frame, text="Name", text_color=TEXT_MUTED).grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.nm_e = ctk.CTkEntry(self.form_frame, width=180, fg_color=INPUT_BG, border_color=BORDER, text_color=TEXT_PRIMARY)
        self.nm_e.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Barcode", text_color=TEXT_MUTED).grid(row=0, column=2, padx=10, pady=8, sticky="e")
        self.bc_e = ctk.CTkEntry(self.form_frame, width=120, fg_color=INPUT_BG, border_color=BORDER, text_color=TEXT_PRIMARY)
        self.bc_e.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Unit", text_color=TEXT_MUTED).grid(row=0, column=4, padx=10, pady=8, sticky="e")
        self.unit_var = ctk.StringVar(value="pcs")
        self.unit_cb = ctk.CTkOptionMenu(
            self.form_frame, variable=self.unit_var, 
            values=product.UNITS, width=90, fg_color=ACCENT, button_color=ACCENT, button_hover_color=ACCENT_HOVER
        )
        self.unit_cb.grid(row=0, column=5, padx=10, pady=5, sticky="w")
        
        # Row 2
        ctk.CTkLabel(self.form_frame, text="Buy ৳", text_color=TEXT_MUTED).grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.by_e = ctk.CTkEntry(self.form_frame, width=100, fg_color=INPUT_BG, border_color=BORDER, text_color=TEXT_PRIMARY)
        self.by_e.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Sell ৳", text_color=TEXT_MUTED).grid(row=1, column=2, padx=10, pady=8, sticky="e")
        self.sl_e = ctk.CTkEntry(self.form_frame, width=100, fg_color=INPUT_BG, border_color=BORDER, text_color=TEXT_PRIMARY)
        self.sl_e.grid(row=1, column=3, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Stock", text_color=TEXT_MUTED).grid(row=1, column=4, padx=10, pady=8, sticky="e")
        self.st_e = ctk.CTkEntry(self.form_frame, width=80, fg_color=INPUT_BG, border_color=BORDER, text_color=TEXT_PRIMARY)
        self.st_e.grid(row=1, column=5, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(self.form_frame, text="Min Stock", text_color=TEXT_MUTED).grid(row=1, column=6, padx=10, pady=8, sticky="e")
        self.ms_e = ctk.CTkEntry(self.form_frame, width=80, fg_color=INPUT_BG, border_color=BORDER, text_color=TEXT_PRIMARY)
        self.ms_e.grid(row=1, column=7, padx=10, pady=5, sticky="w")
        
        # Buttons
        self.btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.btn_frame.grid(row=0, column=8, rowspan=2, padx=20, pady=5)
        
        self.btn_add = ctk.CTkButton(
            self.btn_frame, text="Add", fg_color=SUCCESS, 
            hover_color=SUCCESS_HOVER, width=92, command=self.p_add
        )
        self.btn_add.pack(pady=2)
        
        self.btn_update = ctk.CTkButton(
            self.btn_frame, text="Update", fg_color=ACCENT, 
            hover_color=ACCENT_HOVER, width=92, command=self.p_update
        )
        self.btn_update.pack(pady=2)
        
        self.btn_del = ctk.CTkButton(
            self.btn_frame, text="Delete", fg_color=DANGER, 
            hover_color=DANGER_HOVER, width=92, command=self.p_del
        )
        self.btn_del.pack(pady=2)

        self.btn_clear_form = ctk.CTkButton(
            self.btn_frame, text="Clear", fg_color=PANEL_BG,
            hover_color="#162543", width=92, command=self.clear_form_selection,
            border_width=1, border_color=BORDER
        )
        self.btn_clear_form.pack(pady=2)

        # Search Bar
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.search_entry = ctk.CTkEntry(
            self.search_frame, width=300, 
            placeholder_text="Search by Name or Barcode...",
            fg_color=INPUT_BG, border_color=BORDER, text_color=TEXT_PRIMARY
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        self.search_btn = ctk.CTkButton(
            self.search_frame, text="Search", fg_color=ACCENT, 
            hover_color=ACCENT_HOVER, width=110, command=self.do_search
        )
        self.search_btn.pack(side="left", padx=5)
        
        self.clear_btn = ctk.CTkButton(
            self.search_frame, text="Clear", fg_color=PANEL_BG, 
            hover_color="#162543", width=110, command=self.clear_search, border_width=1, border_color=BORDER
        )
        self.clear_btn.pack(side="left", padx=5)

        # Treeview Configuration
        self.tree_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=CORNER_RADIUS, border_width=1, border_color=BORDER)
        self.tree_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.tree_scroll = ctk.CTkScrollbar(self.tree_frame)
        self.tree_scroll.pack(side="right", fill="y")
        
        cols = ["ID", "Name", "Barcode", "Unit", "Buy ৳", "Sell ৳", "Stock", "Min Stock"]
        widths = [50, 180, 100, 60, 80, 80, 80, 80]
        
        self.ptree = ttk.Treeview(
            self.tree_frame, columns=cols, show="headings", 
            yscrollcommand=self.tree_scroll.set, height=15, style=tree_style
        )
        
        for col, width in zip(cols, widths):
            self.ptree.heading(col, text=col)
            self.ptree.column(col, width=width, anchor="center")
            
        self.ptree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_scroll.configure(command=self.ptree.yview)
        
        self.ptree.bind("<<TreeviewSelect>>", self.on_psel)

    def refresh(self):
        product.load(self.ptree)

    def get_selected(self):
        selected = self.ptree.selection()
        if not selected:
            return None
        return self.ptree.item(selected[0])["values"]

    def clr(self):
        for e in (self.nm_e, self.bc_e, self.by_e, self.sl_e, self.st_e, self.ms_e):
            e.delete(0, tk.END)
        self.unit_var.set("pcs")

    def clear_form_selection(self):
        self.clr()
        selected = self.ptree.selection()
        if selected:
            self.ptree.selection_remove(*selected)

    def trigger_global_refresh(self):
        if hasattr(self.controller, "refresh_views"):
            self.controller.refresh_views()
        else:
            self.refresh()

    def on_psel(self, event=None):
        v = self.get_selected()
        if not v:
            return
        self.clr()
        # [0]=ID, [1]=Name, [2]=Barcode, [3]=Unit, [4]=Buy, [5]=Sell, [6]=Stock, [7]=Min Stock
        self.nm_e.insert(0, str(v[1]) if v[1] is not None else "")
        self.bc_e.insert(0, str(v[2]) if v[2] is not None else "")
        self.unit_var.set(str(v[3]) if v[3] is not None else "pcs")
        self.by_e.insert(0, str(v[4]) if v[4] is not None else "")
        self.sl_e.insert(0, str(v[5]) if v[5] is not None else "")
        self.st_e.insert(0, str(v[6]) if v[6] is not None else "")
        self.ms_e.insert(0, str(v[7]) if v[7] is not None else "")

    def p_add(self):
        n = self.nm_e.get().strip()
        if not n:
            return messagebox.showwarning("Input", "Name required.")
        product.add(
            n, 
            self.bc_e.get().strip(), 
            self.unit_var.get(), 
            self.by_e.get() or 0, 
            self.sl_e.get() or 0, 
            self.st_e.get() or 0, 
            self.ms_e.get() or 0, 
            self.ptree
        )
        self.clr()
        self.trigger_global_refresh()

    def p_update(self):
        v = self.get_selected()
        if not v:
            return messagebox.showwarning("Select", "Select a product.")
        product.update(
            v[0], 
            self.nm_e.get().strip(), 
            self.bc_e.get().strip(), 
            self.unit_var.get(), 
            self.by_e.get() or 0, 
            self.sl_e.get() or 0, 
            self.st_e.get() or 0, 
            self.ms_e.get() or 0, 
            self.ptree
        )
        self.clr()
        self.trigger_global_refresh()

    def p_del(self):
        v = self.get_selected()
        if not v:
            return messagebox.showwarning("Select", "Select a product.")
        if messagebox.askyesno("Delete", "Delete this product?"):
            product.delete(v[0], self.ptree)
            self.clr()
            self.trigger_global_refresh()

    def do_search(self):
        q = self.search_entry.get().strip()
        if q:
            product.search(q, self.ptree)
        else:
            self.refresh()

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh()
