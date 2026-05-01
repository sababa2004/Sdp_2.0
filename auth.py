import customtkinter as ctk
from tkinter import messagebox
import db

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_BG = "#0B1220"
CARD_BG = "#111A2E"
INPUT_BG = "#0F1A30"
TEXT_PRIMARY = "#E7EEFF"
TEXT_MUTED = "#9FB0D0"
ACCENT = "#3A7BFF"
ACCENT_HOVER = "#2F67D6"
BORDER = "#223457"

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Nizam-e-Bazaar - Login")
        self.geometry("460x390")
        self.resizable(False, False)
        self.configure(fg_color=APP_BG)
        # Prevent interaction with other windows
        self.grab_set()
        
        self.on_success = on_success

        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=18, border_width=1, border_color=BORDER)
        card.grid(row=0, column=0, padx=24, pady=28, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            card,
            text="Nizam-e-Bazaar",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Bahnschrift", size=28, weight="bold")
        )
        self.label.grid(row=0, column=0, padx=20, pady=(28, 4))
        self.subtitle = ctk.CTkLabel(
            card,
            text="Sign in to continue",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13)
        )
        self.subtitle.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.username_entry = ctk.CTkEntry(
            card,
            placeholder_text="Username",
            width=320,
            height=38,
            corner_radius=10,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT_PRIMARY
        )
        self.username_entry.grid(row=2, column=0, padx=20, pady=8)
        
        self.password_entry = ctk.CTkEntry(
            card,
            placeholder_text="Password",
            show="*",
            width=320,
            height=38,
            corner_radius=10,
            fg_color=INPUT_BG,
            border_color=BORDER,
            text_color=TEXT_PRIMARY
        )
        self.password_entry.grid(row=3, column=0, padx=20, pady=8)
        
        self.login_button = ctk.CTkButton(
            card,
            text="Login",
            command=self.login,
            width=320,
            height=40,
            corner_radius=10,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.login_button.grid(row=4, column=0, padx=20, pady=(16, 28))
        
        self.bind("<Return>", lambda e: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
            
        role = db.verify_login(username, password)
        if role:
            self.destroy()
            self.on_success(role[0])
        else:
            messagebox.showerror("Error", "Invalid credentials")
