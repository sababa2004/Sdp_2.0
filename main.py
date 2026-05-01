import customtkinter as ctk
import sys
import db
import auth
from views.dashboard import DashboardView
from views.products import ProductsView
from views.sales import SalesView
from views.credit import CreditView
from views.credit_customers import CreditCustomersView

ctk.set_appearance_mode("Dark")

# ── Theme constants ────────────────────────────────────────────────
APP_BG        = "#0B1220"
SIDEBAR_BG    = "#111A2E"
MAIN_BG       = "#0F1A30"
TEXT_PRIMARY  = "#E7EEFF"
TEXT_MUTED    = "#9FB0D0"
ACCENT        = "#3A7BFF"
ACCENT_HOVER  = "#2F67D6"
BTN_HOVER     = "#1A2A47"
BORDER        = "#223457"
CORNER_RADIUS = 16
FONT          = "Segoe UI"
FONT_DISPLAY  = "Bahnschrift"

NAV_ITEMS = [
    ("📊 Dashboard",  "Dashboard"),
    ("📦 Inventory",  "Products"),
    ("💳 Sales",      "Sales"),
    ("📝 Credit",     "Credit"),
    ("👥 Customers",  "CreditCustomers"),
]


class App(ctk.CTk):
    def __init__(self, user_role="Admin"):
        super().__init__()
        self.user_role = user_role
        self.title(f"Super Shop Management System – {user_role}")
        self.geometry("1100x800")
        self.configure(fg_color=APP_BG)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._build_sidebar()
        self._build_main_area()
        self.current_frame = None
        self.frames = {}

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=250, corner_radius=0,
                          fg_color=SIDEBAR_BG, border_width=1, border_color=BORDER)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_rowconfigure(len(NAV_ITEMS) + 2, weight=1)

        ctk.CTkLabel(sb, text="POS Console",
                     font=ctk.CTkFont(family=FONT_DISPLAY, size=30, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=0, column=0, padx=24, pady=(30, 4), sticky="w")
        ctk.CTkLabel(sb, text=f"Signed in as {self.user_role}",
                     font=ctk.CTkFont(family=FONT, size=12),
                     text_color=TEXT_MUTED).grid(row=1, column=0, padx=24, pady=(0, 22), sticky="w")

        btn_cfg = dict(font=ctk.CTkFont(family=FONT, size=14, weight="bold"),
                       text_color=TEXT_PRIMARY, fg_color="transparent",
                       hover_color=BTN_HOVER, corner_radius=CORNER_RADIUS,
                       anchor="w", height=42)
        self.nav_buttons = {}
        for idx, (label, key) in enumerate(NAV_ITEMS, start=2):
            btn = ctk.CTkButton(sb, text=label,
                                command=lambda k=key: self.select_frame(k), **btn_cfg)
            btn.grid(row=idx, column=0, padx=18, pady=5, sticky="ew")
            self.nav_buttons[key] = btn

        ctk.CTkButton(sb, text="Logout", command=self.logout,
                      fg_color="#1D2C49", hover_color="#24385D",
                      border_width=1, border_color="#304A79",
                      text_color=TEXT_PRIMARY, corner_radius=CORNER_RADIUS,
                      height=40).grid(row=len(NAV_ITEMS) + 3, column=0,
                                      padx=18, pady=(6, 20), sticky="ew")

    def _build_main_area(self):
        self.main_content = ctk.CTkFrame(self, corner_radius=CORNER_RADIUS,
                                         fg_color=MAIN_BG, border_width=1, border_color=BORDER)
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

    def setup_frames(self):
        self.frames = {
            "Dashboard":       DashboardView(self.main_content, self),
            "Products":        ProductsView(self.main_content, self),
            "Sales":           SalesView(self.main_content, self),
            "Credit":          CreditView(self.main_content, self),
            "CreditCustomers": CreditCustomersView(self.main_content, self),
        }
        self.select_frame("Dashboard")

    def select_frame(self, name):
        if self.current_frame:
            self.current_frame.grid_forget()
        self.current_frame = self.frames[name]
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        self._highlight_nav(name)
        self.current_frame.refresh()

    def _highlight_nav(self, active):
        for key, btn in self.nav_buttons.items():
            if key == active:
                btn.configure(fg_color=ACCENT, hover_color=ACCENT_HOVER)
            else:
                btn.configure(fg_color="transparent", hover_color=BTN_HOVER)

    def refresh_views(self):
        for frame in self.frames.values():
            if hasattr(frame, "refresh"):
                frame.refresh()
        credit_view = self.frames.get("Credit")
        if credit_view and hasattr(credit_view, "refresh_customers"):
            credit_view.refresh_customers()

    def logout(self):
        self.destroy()
        start()


def on_login_success(role):
    app = App(user_role=role)
    app.setup_frames()
    app.mainloop()


def start():
    db.init()
    temp_root = ctk.CTk()
    temp_root.withdraw()

    def _launch(role):
        temp_root.destroy()
        on_login_success(role)

    win = auth.LoginDialog(temp_root, _launch)
    win.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    temp_root.mainloop()


if __name__ == "__main__":
    start()
