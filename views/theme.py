import customtkinter as ctk
from tkinter import ttk

APP_BG = "#0B1220"
PANEL_BG = "#0F1A30"
CARD_BG = "#111A2E"
INPUT_BG = "#0C162B"
TEXT_PRIMARY = "#E7EEFF"
TEXT_MUTED = "#9FB0D0"
ACCENT = "#3A7BFF"
ACCENT_HOVER = "#2F67D6"
SUCCESS = "#24B47E"
SUCCESS_HOVER = "#1D9569"
WARNING = "#F5A524"
WARNING_HOVER = "#D9921E"
DANGER = "#EF5A5A"
DANGER_HOVER = "#D54A4A"
BORDER = "#223457"
CORNER_RADIUS = 14
FONT = "Segoe UI"
DISPLAY_FONT = "Bahnschrift"
TREE_STYLE = "Executive.Treeview"


def section_title(parent, text):
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(family=DISPLAY_FONT, size=30, weight="bold"),
        text_color=TEXT_PRIMARY
    )


def setup_treeview_style():
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        TREE_STYLE,
        background="#0F1D37",
        foreground=TEXT_PRIMARY,
        rowheight=30,
        fieldbackground="#0F1D37",
        borderwidth=0,
        font=(FONT, 10),
    )
    style.configure(
        f"{TREE_STYLE}.Heading",
        background=CARD_BG,
        foreground=TEXT_MUTED,
        font=(FONT, 10, "bold"),
        borderwidth=0,
    )
    style.map(TREE_STYLE, background=[("selected", ACCENT)])
    return TREE_STYLE
