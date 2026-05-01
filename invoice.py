from fpdf import FPDF
from db import con
from datetime import datetime

def generate_receipt(sale_id):
    with con() as c:
        sale = c.execute("SELECT product, quantity, total, timestamp FROM sales WHERE id=?", (sale_id,)).fetchone()
    
    if not sale:
        return None
        
    product, quantity, total, timestamp = sale
    
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="RECEIPT", ln=1, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Date: {timestamp}", ln=1)
    pdf.cell(0, 10, txt=f"Sale ID: {sale_id}", ln=1)
    
    pdf.ln(5)
    
    # Items
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(70, 10, "Product", border=1)
    pdf.cell(40, 10, "Quantity", border=1, align='C')
    pdf.cell(40, 10, "Total", border=1, align='C')
    pdf.ln()
    
    pdf.set_font("Arial", size=12)
    pdf.cell(70, 10, str(product), border=1)
    pdf.cell(40, 10, str(quantity), border=1, align='C')
    pdf.cell(40, 10, f"${float(total):.2f}", border=1, align='C')
    pdf.ln(10)
    
    # Total
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(110, 10, "Amount Paid:", align='R')
    pdf.cell(40, 10, f"${float(total):.2f}", align='C')
    
    filename = f"receipt_{sale_id}.pdf"
    pdf.output(filename)
    return filename

def generate_cart_receipt(items, grand_total, filename_prefix="receipt"):
    if not items:
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt="RECEIPT", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Date: {timestamp}", ln=1)
    pdf.cell(0, 10, txt=f"Items: {len(items)}", ln=1)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Product", border=1)
    pdf.cell(35, 10, "Quantity", border=1, align="C")
    pdf.cell(35, 10, "Total", border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", size=12)
    for item in items:
        pdf.cell(80, 10, str(item["product"]), border=1)
        pdf.cell(35, 10, str(item["quantity"]), border=1, align="C")
        pdf.cell(35, 10, f"${float(item['total']):.2f}", border=1, align="C")
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(115, 10, "Amount Paid:", align="R")
    pdf.cell(35, 10, f"${float(grand_total):.2f}", align="C")

    filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
