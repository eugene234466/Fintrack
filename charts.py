# charts.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime, timedelta
from collections import defaultdict

def get_period_labels(period):
    today = datetime.now()
    if period == "weekly":
        labels = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime("%a"))
        return labels
    else:
        labels = []
        for i in range(5, -1, -1):
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            labels.append(datetime(year, month, 1).strftime("%b"))
        return labels

def group_by_period(transactions, period):
    grouped = defaultdict(lambda: {"income": 0, "expense": 0})
    
    if not transactions:
        return grouped
    
    if period == "weekly":
        today = datetime.now().date()
        for transaction in transactions:
            try:
                trans_date = datetime.strptime(transaction['date'], '%Y-%m-%d').date()
                days_diff = (today - trans_date).days
                if 0 <= days_diff < 7:
                    day_name = trans_date.strftime("%a")
                    if transaction.get('type') == 'income':
                        grouped[day_name]["income"] += transaction.get('amount', 0)
                    else:
                        grouped[day_name]["expense"] += transaction.get('amount', 0)
            except (KeyError, ValueError):
                continue
    else:
        today = datetime.now()
        for transaction in transactions:
            try:
                trans_date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_diff = (today.year - trans_date.year) * 12 + (today.month - trans_date.month)
                if 0 <= month_diff < 6:
                    month_name = trans_date.strftime("%b")
                    if transaction.get('type') == 'income':
                        grouped[month_name]["income"] += transaction.get('amount', 0)
                    else:
                        grouped[month_name]["expense"] += transaction.get('amount', 0)
            except (KeyError, ValueError):
                continue
    
    return grouped

def create_base64_chart(fig):
    """Convert matplotlib figure to base64 string"""
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

def generate_income_vs_expenses(transactions, period):
    try:
        labels = get_period_labels(period)
        grouped = group_by_period(transactions, period)
        
        income_totals = [grouped[l]["income"] for l in labels]
        expense_totals = [grouped[l]["expense"] for l in labels]
        
        # Check if there's any data
        if not any(income_totals) and not any(expense_totals):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No transaction data available', 
                    ha='center', va='center', fontsize=14)
            ax.set_title(f'Income vs Expenses ({period.capitalize()} View)')
            ax.axis('off')
            return create_base64_chart(fig)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bar_width = 0.35
        x_positions = range(len(labels))
        
        income_bars = ax.bar(
            [x - bar_width/2 for x in x_positions],
            income_totals,
            bar_width,
            label='Income',
            color='green',
            alpha=0.7
        )
        
        expense_bars = ax.bar(
            [x + bar_width/2 for x in x_positions],
            expense_totals,
            bar_width,
            label='Expenses',
            color='red',
            alpha=0.7
        )
        
        ax.set_xlabel(period.capitalize())
        ax.set_ylabel('Amount (₵)')
        ax.set_title(f'Income vs Expenses ({period.capitalize()} View)')
        ax.set_xticks(list(x_positions))
        ax.set_xticklabels(labels)
        ax.legend()
        
        # Add value labels on bars
        for bars in [income_bars, expense_bars]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(
                        bar.get_x() + bar.get_width()/2.,
                        height,
                        f'₵{height:,.0f}',
                        ha='center',
                        va='bottom',
                        fontsize=8
                    )
        
        plt.tight_layout()
        return create_base64_chart(fig)
    except Exception as e:
        print(f"Error in generate_income_vs_expenses: {e}")
        return None

def generate_spending_by_category(transactions, period):
    try:
        expenses = [t for t in transactions if t.get('type') == 'expense']
        
        if period == "weekly":
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            expenses = [
                t for t in expenses
                if datetime.strptime(t['date'], '%Y-%m-%d').date() >= week_ago
            ]
        else:
            today = datetime.now()
            six_months_ago = today - timedelta(days=180)
            expenses = [
                t for t in expenses
                if datetime.strptime(t['date'], '%Y-%m-%d') >= six_months_ago
            ]
        
        category_totals = defaultdict(float)
        for transaction in expenses:
            category_totals[transaction.get('category', 'Uncategorized')] += transaction.get('amount', 0)
        
        if not category_totals:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'No expense data available', 
                    ha='center', va='center', fontsize=14)
            ax.set_title(f'Spending by Category ({period.capitalize()} View)')
            ax.axis('off')
            return create_base64_chart(fig)
        
        # Limit categories to top 10 for readability
        labels = list(category_totals.keys())
        sizes = list(category_totals.values())
        
        if len(labels) > 10:
            sorted_items = sorted(zip(labels, sizes), key=lambda x: x[1], reverse=True)
            top_items = sorted_items[:9]
            other_total = sum([x[1] for x in sorted_items[9:]])
            labels = [x[0] for x in top_items] + ['Other']
            sizes = [x[1] for x in top_items] + [other_total]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.Set3.colors
        )
        
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        
        ax.set_title(f'Spending by Category ({period.capitalize()} View)')
        ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        return create_base64_chart(fig)
    except Exception as e:
        print(f"Error in generate_spending_by_category: {e}")
        return None

def generate_trend_over_time(transactions, period):
    try:
        labels = get_period_labels(period)
        grouped = group_by_period(transactions, period)
        
        net_totals = [grouped[l]["income"] - grouped[l]["expense"] for l in labels]
        
        if not any(net_totals):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No data available for trend analysis', 
                    ha='center', va='center', fontsize=14)
            ax.set_title(f'Financial Trend Over Time ({period.capitalize()} View)')
            ax.axis('off')
            return create_base64_chart(fig)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x_positions = range(len(labels))
        
        ax.plot(
            x_positions,
            net_totals,
            marker='o',
            linewidth=2,
            markersize=8,
            color='blue',
            label='Net Income'
        )
        
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
        
        # Fill areas
        for i, val in enumerate(net_totals):
            if i < len(net_totals) - 1:
                x_vals = [x_positions[i], x_positions[i+1]]
                y_vals = [net_totals[i], net_totals[i+1]]
                if all(v >= 0 for v in y_vals):
                    ax.fill_between(x_vals, y_vals, 0, color='green', alpha=0.3)
                elif all(v <= 0 for v in y_vals):
                    ax.fill_between(x_vals, y_vals, 0, color='red', alpha=0.3)
        
        ax.set_xlabel(period.capitalize())
        ax.set_ylabel('Net Amount (₵)')
        ax.set_title(f'Financial Trend Over Time ({period.capitalize()} View)')
        ax.set_xticks(list(x_positions))
        ax.set_xticklabels(labels)
        ax.legend()
        
        for i, value in enumerate(net_totals):
            ax.annotate(
                f'₵{value:,.0f}',
                (x_positions[i], value),
                textcoords="offset points",
                xytext=(0, 10 if value >= 0 else -15),
                ha='center',
                fontsize=9,
                fontweight='bold'
            )
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return create_base64_chart(fig)
    except Exception as e:
        print(f"Error in generate_trend_over_time: {e}")
        return None

def generate_all_charts(transactions, period):
    """Generate all charts and return as base64 data URLs"""
    return {
        'income_vs_expenses': generate_income_vs_expenses(transactions, period),
        'spending_by_category': generate_spending_by_category(transactions, period),
        'trend_over_time': generate_trend_over_time(transactions, period)
    }
