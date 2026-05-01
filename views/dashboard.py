import customtkinter as ctk
from tkinter import messagebox
from fpdf import FPDF
from datetime import datetime
import db
import os
from views.analytics import create_sales_chart
from views.theme import (
    CARD_BG, TEXT_PRIMARY, TEXT_MUTED, ACCENT, ACCENT_HOVER, SUCCESS, WARNING,
    BORDER, CORNER_RADIUS, FONT, DISPLAY_FONT
)

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Dashboard Title & Report Button Container
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="ew")
        self.title_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.title_frame, text="Sales Overview", 
            font=ctk.CTkFont(family=DISPLAY_FONT, size=32, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.report_btn = ctk.CTkButton(
            self.title_frame, text="Print Report",
            font=ctk.CTkFont(family=FONT, size=14, weight="bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="white",
            corner_radius=CORNER_RADIUS,
            command=self.open_report_dialog
        )
        self.report_btn.grid(row=0, column=1, sticky="e")
        
        # Cards Frame
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        card_kwargs = {"fg_color": CARD_BG, "corner_radius": CORNER_RADIUS, "border_width": 1, "border_color": BORDER}
        
        # Profit Card
        self.profit_frame = ctk.CTkFrame(self.cards_frame, **card_kwargs)
        self.profit_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.profit_label = ctk.CTkLabel(
            self.profit_frame, text="Profit\n0.00 ৳", 
            font=ctk.CTkFont(family=FONT, size=22, weight="bold"), 
            text_color=SUCCESS
        )
        self.profit_label.pack(pady=30, padx=20)
        
        # Sales Card
        self.sales_frame = ctk.CTkFrame(self.cards_frame, **card_kwargs)
        self.sales_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.sales_label = ctk.CTkLabel(
            self.sales_frame, text="Sales\n0.00 ৳", 
            font=ctk.CTkFont(family=FONT, size=22, weight="bold"), 
            text_color=TEXT_PRIMARY
        )
        self.sales_label.pack(pady=30, padx=20)
        
        # Credit Card
        self.credit_frame = ctk.CTkFrame(self.cards_frame, **card_kwargs)
        self.credit_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.credit_label = ctk.CTkLabel(
            self.credit_frame, text="Credit Due\n0.00 ৳", 
            font=ctk.CTkFont(family=FONT, size=22, weight="bold"), 
            text_color=WARNING
        )
        self.credit_label.pack(pady=30, padx=20)
        
        # Bottom Frame for Analytics and Low Stock
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.bottom_frame.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Low Stock Alerts
        self.low_stock_frame = ctk.CTkFrame(self.bottom_frame, **card_kwargs)
        self.low_stock_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(self.low_stock_frame, text="Stock Status", font=ctk.CTkFont(family=FONT, size=18, weight="bold"), text_color=TEXT_MUTED).pack(pady=(15, 5))
        self.stock_list_frame = ctk.CTkScrollableFrame(self.low_stock_frame, fg_color="transparent")
        self.stock_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Analytics Chart
        self.chart_frame = ctk.CTkFrame(self.bottom_frame, **card_kwargs)
        self.chart_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(self.chart_frame, text="Sales Trend", font=ctk.CTkFont(family=FONT, size=18, weight="bold"), text_color=TEXT_MUTED).pack(pady=(15, 5))
        self.chart_canvas = None

    def refresh(self):
        profit, total_sales, credit_due = db.totals()
        self.profit_label.configure(text=f"Profit\n{profit:.2f} ৳")
        self.sales_label.configure(text=f"Sales\n{total_sales:.2f} ৳")
        self.credit_label.configure(text=f"Credit Due\n{credit_due:.2f} ৳")
        
        # Update Low Stock
        for widget in self.stock_list_frame.winfo_children():
            widget.destroy()
        
        low_stocks = db.get_low_stock()
        if not low_stocks:
            ctk.CTkLabel(self.stock_list_frame, text="All products are well stocked.", font=ctk.CTkFont(family=FONT, size=14), text_color=SUCCESS).pack(pady=20)
        else:
            for name, stock, min_stock in low_stocks:
                ctk.CTkLabel(self.stock_list_frame, text=f"• {name}: {stock} left (Min: {min_stock})", font=ctk.CTkFont(family=FONT, size=14), text_color=WARNING).pack(anchor="w", pady=4, padx=10)
                
        # Update Chart
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        
        self.chart_canvas = create_sales_chart(self.chart_frame)
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def open_report_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sales Report")
        dialog.geometry("300x250")
        dialog.configure(fg_color="#0F1A30")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Generate Sales Report", text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Default dates to today
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        ctk.CTkLabel(dialog, text="Start Date (YYYY-MM-DD):", text_color=TEXT_MUTED).pack(pady=(10, 0))
        start_entry = ctk.CTkEntry(dialog, fg_color="#0C162B", border_color=BORDER, text_color=TEXT_PRIMARY)
        start_entry.insert(0, today_str)
        start_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="End Date (YYYY-MM-DD):", text_color=TEXT_MUTED).pack()
        end_entry = ctk.CTkEntry(dialog, fg_color="#0C162B", border_color=BORDER, text_color=TEXT_PRIMARY)
        end_entry.insert(0, today_str)
        end_entry.pack(pady=5)
        
        def generate():
            s_date = start_entry.get()
            e_date = end_entry.get()
            # Append time to cover whole day if same
            s_datetime = s_date + " 00:00:00"
            e_datetime = e_date + " 23:59:59"
            
            with db.con() as c:
                sales = c.execute("SELECT product, quantity, total, timestamp FROM sales WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp", (s_datetime, e_datetime)).fetchall()
                
            if not sales:
                messagebox.showinfo("No Data", "No sales found for the selected dates.")
                return
                
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, txt="SALES REPORT", ln=1, align='C')
            
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, txt=f"Period: {s_date} to {e_date}", ln=1)
            pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(80, 10, "Product", border=1)
            pdf.cell(30, 10, "Quantity", border=1, align='C')
            pdf.cell(30, 10, "Total", border=1, align='C')
            pdf.cell(50, 10, "Date", border=1, align='C')
            pdf.ln()
            
            pdf.set_font("Arial", size=11)
            total_sum = 0
            for product, qty, total, ts in sales:
                total_sum += float(total)
                pdf.cell(80, 10, str(product)[:30], border=1)
                pdf.cell(30, 10, f"{qty:.2f}", border=1, align='C')
                pdf.cell(30, 10, f"{total:.2f}", border=1, align='R')
                pdf.cell(50, 10, str(ts)[:16], border=1, align='C')
                pdf.ln()
                
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(110, 10, "Total Sales:", align='R')
            pdf.cell(30, 10, f"{total_sum:.2f}", align='R')
            pdf.ln(5)
            
            filename = f"sales_report_{s_date}_{e_date}.pdf"
            pdf.output(filename)
            messagebox.showinfo("Success", f"Report saved as '{filename}'")
            dialog.destroy()
            
            try:
                os.startfile(filename)
            except Exception:
                pass

        ctk.CTkButton(dialog, text="Generate PDF", fg_color=ACCENT, hover_color=ACCENT_HOVER, command=generate).pack(pady=15)

