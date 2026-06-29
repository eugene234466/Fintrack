# charts.py (Simplified version)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
from collections import defaultdict

def create_base64_chart(fig):
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        buf.close()
        return img_base64
    except Exception as e:
        print(f"Error creating base64 chart: {e}")
        plt.close(fig)
        return None

def generate_all_charts(transactions, period):
    print(f"Generating charts for {period} with {len(transactions)} transactions")
    
    # Simple income vs expenses
    income = sum(t['amount'] for t in transactions if t.get('type') == 'income')
    expense = sum(t['amount'] for t in transactions if t.get('type') == 'expense')
    
    # Create a simple bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    categories = ['Income', 'Expenses']
    values = [income, expense]
    colors = ['green', 'red']
    
    bars = ax.bar(categories, values, color=colors, alpha=0.7)
    ax.set_title(f'Income vs Expenses ({period.capitalize()})')
    ax.set_ylabel('Amount (₵)')
    
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'₵{height:,.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    chart1 = create_base64_chart(fig)
    
    # Simple pie chart for categories
    category_totals = defaultdict(float)
    for t in transactions:
        if t.get('type') == 'expense':
            category_totals[t.get('category', 'Other')] += t.get('amount', 0)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    if category_totals:
        labels = list(category_totals.keys())
        sizes = list(category_totals.values())
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title(f'Spending by Category ({period.capitalize()})')
    else:
        ax.text(0.5, 0.5, 'No expense data', ha='center', va='center')
        ax.axis('off')
    
    plt.tight_layout()
    chart2 = create_base64_chart(fig)
    
    # Simple trend line
    fig, ax = plt.subplots(figsize=(10, 6))
    if transactions:
        # Group by date
        daily_totals = defaultdict(float)
        for t in transactions:
            date = t.get('date', '')
            if date:
                daily_totals[date] += t.get('amount', 0) if t.get('type') == 'income' else -t.get('amount', 0)
        
        if daily_totals:
            dates = sorted(daily_totals.keys())
            values = [daily_totals[d] for d in dates]
            ax.plot(dates, values, marker='o', linewidth=2)
            ax.set_title(f'Net Balance Trend ({period.capitalize()})')
            ax.set_xlabel('Date')
            ax.set_ylabel('Net Amount (₵)')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No trend data', ha='center', va='center')
            ax.axis('off')
    else:
        ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
        ax.axis('off')
    
    plt.tight_layout()
    chart3 = create_base64_chart(fig)
    
    return {
        'income_vs_expenses': chart1,
        'spending_by_category': chart2,
        'trend_over_time': chart3
    }
