import matplotlib # non-interactive backend, required for Flask
matplotlib.use('Agg')
import matplotlib.pyplot as plt


import os
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "static", "charts")

# -- SETUP --
def ensure_charts_dir():
    """Ensure the charts directory exists"""
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)


# -- HELPER FUNCTIONS --
def get_period_labels(period):
    """Get labels for the given period"""
    today = datetime.now()
    
    if period == "weekly":
        # Get last 7 days as day names
        labels = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime("%a"))  # Mon, Tue, etc.
        return labels
    else:  # monthly
        # Get last 6 months as month names
        labels = []
        for i in range(5, -1, -1):
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            labels.append(datetime(year, month, 1).strftime("%b"))  # Jan, Feb, etc.
        return labels


def group_by_period(transactions, period):
    """Group transactions by day or month"""
    grouped = defaultdict(lambda: {"income": 0, "expense": 0})
    
    if period == "weekly":
        # Group by day for last 7 days
        today = datetime.now().date()
        for transaction in transactions:
            trans_date = datetime.strptime(transaction['date'], '%Y-%m-%d').date()
            days_diff = (today - trans_date).days
            if 0 <= days_diff < 7:
                day_name = trans_date.strftime("%a")
                if transaction['type'] == 'income':
                    grouped[day_name]["income"] += transaction['amount']
                else:
                    grouped[day_name]["expense"] += transaction['amount']
    else:  # monthly
        # Group by month for last 6 months
        today = datetime.now()
        for transaction in transactions:
            trans_date = datetime.strptime(transaction['date'], '%Y-%m-%d')
            month_diff = (today.year - trans_date.year) * 12 + (today.month - trans_date.month)
            if 0 <= month_diff < 6:
                month_name = trans_date.strftime("%b")
                if transaction['type'] == 'income':
                    grouped[month_name]["income"] += transaction['amount']
                else:
                    grouped[month_name]["expense"] += transaction['amount']
    
    return grouped


# -- CHART 1: Income vs Expenses --
def generate_income_vs_expenses(transactions, period):
    """Generate bar chart comparing income and expenses over time"""
    ensure_charts_dir()
    
    # Get labels based on period
    labels = get_period_labels(period)
    
    # Group transactions by period
    grouped = group_by_period(transactions, period)
    
    # Prepare data for chart
    income_totals = []
    expense_totals = []
    
    for label in labels:
        income_totals.append(grouped[label]["income"])
        expense_totals.append(grouped[label]["expense"])
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set bar width and positions
    bar_width = 0.35
    x_positions = range(len(labels))
    
    # Plot bars
    income_bars = ax.bar([x - bar_width/2 for x in x_positions], 
                         income_totals, bar_width, 
                         label='Income', color='green', alpha=0.7)
    expense_bars = ax.bar([x + bar_width/2 for x in x_positions], 
                          expense_totals, bar_width, 
                          label='Expenses', color='red', alpha=0.7)
    
    # Add labels and formatting
    ax.set_xlabel(period.capitalize())
    ax.set_ylabel('Amount ($)')
    ax.set_title(f'Income vs Expenses ({period.capitalize()} View)')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Add value labels on bars
    for bars in [income_bars, expense_bars]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}', ha='center', va='bottom', fontsize=8)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'income_vs_expenses.png'), 
                dpi=100, bbox_inches='tight')
    plt.close(fig)


# -- CHART 2: Spending by Category --
def generate_spending_by_category(transactions, period):
    """Generate pie chart showing spending by category"""
    ensure_charts_dir()
    
    # Filter to only expenses
    expenses = [t for t in transactions if t['type'] == 'expense']
    
    # Filter by period if needed
    if period == "weekly":
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        expenses = [t for t in expenses 
                   if datetime.strptime(t['date'], '%Y-%m-%d').date() >= week_ago]
    else:  # monthly
        today = datetime.now()
        six_months_ago = today - timedelta(days=180)
        expenses = [t for t in expenses 
                   if datetime.strptime(t['date'], '%Y-%m-%d') >= six_months_ago]
    
    # Group by category
    category_totals = defaultdict(float)
    for transaction in expenses:
        category_totals[transaction['category']] += transaction['amount']
    
    # Check if we have data
    if not category_totals:
        # Create a blank placeholder chart
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'No expense data available', 
                ha='center', va='center', fontsize=14)
        ax.set_title(f'Spending by Category ({period.capitalize()} View)')
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, 'spending_by_category.png'), 
                    dpi=100, bbox_inches='tight')
        plt.close(fig)
        return
    
    # Prepare data for pie chart
    labels = list(category_totals.keys())
    sizes = list(category_totals.values())
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot pie chart
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                       startangle=90, colors=plt.cm.Set3.colors)
    
    # Format percentage text
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
    
    # Add title
    ax.set_title(f'Spending by Category ({period.capitalize()} View)')
    
    # Add legend for categories with small percentages
    ax.legend(wedges, labels, title="Categories", 
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'spending_by_category.png'), 
                dpi=100, bbox_inches='tight')
    plt.close(fig)


# -- CHART 3: Trend Over Time --
def generate_trend_over_time(transactions, period):
    """Generate line chart showing net income trend over time"""
    ensure_charts_dir()
    
    # Get labels based on period
    labels = get_period_labels(period)
    
    # Group transactions by period
    grouped = group_by_period(transactions, period)
    
    # Calculate net totals (income - expenses)
    net_totals = []
    for label in labels:
        net = grouped[label]["income"] - grouped[label]["expense"]
        net_totals.append(net)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot line chart
    x_positions = range(len(labels))
    ax.plot(x_positions, net_totals, marker='o', linewidth=2, 
            markersize=8, color='blue', label='Net Income')
    
    # Add horizontal line at y=0
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    
    # Fill positive and negative areas
    ax.fill_between(x_positions, net_totals, 0, 
                    where=[n > 0 for n in net_totals], 
                    color='green', alpha=0.3, label='Profit')
    ax.fill_between(x_positions, net_totals, 0, 
                    where=[n < 0 for n in net_totals], 
                    color='red', alpha=0.3, label='Loss')
    
    # Add labels and formatting
    ax.set_xlabel(period.capitalize())
    ax.set_ylabel('Net Amount ($)')
    ax.set_title(f'Financial Trend Over Time ({period.capitalize()} View)')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Add value labels on points
    for i, value in enumerate(net_totals):
        ax.annotate(f'${value:,.0f}', 
                   (x_positions[i], value),
                   textcoords="offset points",
                   xytext=(0, 10 if value >= 0 else -15),
                   ha='center',
                   fontsize=9,
                   fontweight='bold')
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'trend_over_time.png'), 
                dpi=100, bbox_inches='tight')
    plt.close(fig)


# -- GENERATE ALL CHARTS --
def generate_all_charts(transactions, period):
    """Generate all three charts for the given period"""
    generate_income_vs_expenses(transactions, period)
    generate_spending_by_category(transactions, period)
    generate_trend_over_time(transactions, period)