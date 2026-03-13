import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "static", "charts")

def ensure_charts_dir():
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)


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
    if period == "weekly":
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
    else:
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


def generate_income_vs_expenses(transactions, period):
    ensure_charts_dir()
    labels = get_period_labels(period)
    grouped = group_by_period(transactions, period)
    income_totals = [grouped[l]["income"] for l in labels]
    expense_totals = [grouped[l]["expense"] for l in labels]

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    x_positions = range(len(labels))

    income_bars = ax.bar([x - bar_width/2 for x in x_positions],
                         income_totals, bar_width, label='Income', color='green', alpha=0.7)
    expense_bars = ax.bar([x + bar_width/2 for x in x_positions],
                          expense_totals, bar_width, label='Expenses', color='red', alpha=0.7)

    ax.set_xlabel(period.capitalize())
    ax.set_ylabel('Amount (₵)')
    ax.set_title(f'Income vs Expenses ({period.capitalize()} View)')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels)
    ax.legend()

    for bars in [income_bars, expense_bars]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'₵{height:,.0f}', ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'income_vs_expenses.png'), dpi=100, bbox_inches='tight')
    plt.close(fig)


def generate_spending_by_category(transactions, period):
    ensure_charts_dir()
    expenses = [t for t in transactions if t['type'] == 'expense']

    if period == "weekly":
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        expenses = [t for t in expenses
                   if datetime.strptime(t['date'], '%Y-%m-%d').date() >= week_ago]
    else:
        today = datetime.now()
        six_months_ago = today - timedelta(days=180)
        expenses = [t for t in expenses
                   if datetime.strptime(t['date'], '%Y-%m-%d') >= six_months_ago]

    category_totals = defaultdict(float)
    for transaction in expenses:
        category_totals[transaction['category']] += transaction['amount']

    if not category_totals:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'No expense data available', ha='center', va='center', fontsize=14)
        ax.set_title(f'Spending by Category ({period.capitalize()} View)')
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(CHARTS_DIR, 'spending_by_category.png'), dpi=100, bbox_inches='tight')
        plt.close(fig)
        return

    labels = list(category_totals.keys())
    sizes = list(category_totals.values())

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                       startangle=90, colors=plt.cm.Set3.colors)
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')

    ax.set_title(f'Spending by Category ({period.capitalize()} View)')
    ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'spending_by_category.png'), dpi=100, bbox_inches='tight')
    plt.close(fig)


def generate_trend_over_time(transactions, period):
    ensure_charts_dir()
    labels = get_period_labels(period)
    grouped = group_by_period(transactions, period)
    net_totals = [grouped[l]["income"] - grouped[l]["expense"] for l in labels]

    fig, ax = plt.subplots(figsize=(10, 6))
    x_positions = range(len(labels))

    ax.plot(x_positions, net_totals, marker='o', linewidth=2,
            markersize=8, color='blue', label='Net Income')
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.fill_between(x_positions, net_totals, 0,
                    where=[n > 0 for n in net_totals],
                    color='green', alpha=0.3, label='Profit')
    ax.fill_between(x_positions, net_totals, 0,
                    where=[n < 0 for n in net_totals],
                    color='red', alpha=0.3, label='Loss')

    ax.set_xlabel(period.capitalize())
    ax.set_ylabel('Net Amount (₵)')
    ax.set_title(f'Financial Trend Over Time ({period.capitalize()} View)')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels)
    ax.legend()

    for i, value in enumerate(net_totals):
        ax.annotate(f'₵{value:,.0f}',
                   (x_positions[i], value),
                   textcoords="offset points",
                   xytext=(0, 10 if value >= 0 else -15),
                   ha='center', fontsize=9, fontweight='bold')

    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, 'trend_over_time.png'), dpi=100, bbox_inches='tight')
    plt.close(fig)


def generate_all_charts(transactions, period):
    generate_income_vs_expenses(transactions, period)
    generate_spending_by_category(transactions, period)
    generate_trend_over_time(transactions, period)
