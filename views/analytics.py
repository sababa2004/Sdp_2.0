import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import db
import numpy as np
from scipy.interpolate import make_interp_spline
import mplcursors

def create_sales_chart(parent):
    # Match chart style with executive dark dashboard theme
    plt.style.use("default")
    data = db.get_recent_performance()
    if not data:
        return None
        
    data.reverse() # chronological
    dates = [row[0][-5:] for row in data] # just MM-DD
    sales = [row[1] for row in data]
    credits = [row[2] for row in data]

    SALES_COLOR = '#3A7BFF'
    CREDIT_COLOR = '#F5A524'
    TEXT_COLOR = '#C9D7F6'
    BG_COLOR = '#111A2E'
    GRID_COLOR = '#223457'

    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    x = np.arange(len(dates))
    
    # Organic curves via interpolation
    if len(x) > 3:
        x_new = np.linspace(x.min(), x.max(), 300)
        spl_sales = make_interp_spline(x, sales, k=3)
        sales_smooth = spl_sales(x_new)
        
        spl_credit = make_interp_spline(x, credits, k=3)
        credit_smooth = spl_credit(x_new)
        
        line_sales, = ax.plot(x_new, sales_smooth, label='Sales', color=SALES_COLOR, linewidth=3)
        line_credit, = ax.plot(x_new, credit_smooth, label='Credit', color=CREDIT_COLOR, linewidth=3, linestyle='--')
    else:
        line_sales, = ax.plot(x, sales, label='Sales', color=SALES_COLOR, linewidth=3, marker='o')
        line_credit, = ax.plot(x, credits, label='Credit', color=CREDIT_COLOR, linewidth=3, linestyle='--', marker='o')

    # Add fill under the sales curve
    if len(x) > 3:
        ax.fill_between(x_new, sales_smooth, color=SALES_COLOR, alpha=0.18)
    else:
        ax.fill_between(x, sales, color=SALES_COLOR, alpha=0.18)

    cursor = mplcursors.cursor([line_sales, line_credit], hover=True)
    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set_text(f"{sel.target[1]:.2f} ৳")
        sel.annotation.get_bbox_patch().set_alpha(0.8)
    
    ax.set_xticks(x)
    ax.set_xticklabels(dates, rotation=45, color=TEXT_COLOR)
    ax.tick_params(colors=TEXT_COLOR, axis='y')
    ax.set_ylabel("Amount (৳)", color=TEXT_COLOR)
    ax.set_title("Recent Sales vs Credit", color=TEXT_COLOR, pad=10)
    ax.legend(facecolor=BG_COLOR, edgecolor='none', labelcolor=TEXT_COLOR)
    
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color(GRID_COLOR)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
        
    ax.grid(axis='y', color=GRID_COLOR, linestyle='--', alpha=0.7)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    return canvas
