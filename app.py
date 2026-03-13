import time
from flask import Flask, render_template, request, redirect, url_for
from models import init_db, add_transactions, get_transactions, delete_transaction, set_budget, get_budget
from charts import generate_all_charts

categories = ["Food", "Rent", "Transport", "Utilities", "Salary", "Freelance", "Entertainment", "Savings", "Other"]

app = Flask(__name__)

@app.route("/")
def index():
    period = request.args.get('period', 'weekly')
    transactions = get_transactions(period)

    total_income = 0
    total_expenses = 0
    
    for transaction in transactions:
        if transaction['type'] == 'income':
            total_income += transaction['amount']
        elif transaction['type'] == 'expense':
            total_expenses += transaction['amount']
    
    net_balance = total_income - total_expenses
    
    generate_all_charts(transactions, period)
    
    return render_template(
        'dashboard.html',
        period=period,
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=net_balance,
        cache_bust=int(time.time()),
        categories=categories
    )  
    
@app.route("/transactions", methods=["GET", "POST"])
def transactions_view():
    if request.method == "POST":
        type = request.form['type']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        note = request.form.get('note', "")
        
        add_transactions(type, amount, category, date, note)
        return redirect(url_for('transactions_view'))
    
    period = request.args.get('period', 'weekly')
    transactions = get_transactions(period)
    
    return render_template(
        'transactions.html',
        transactions=transactions,
        categories=categories,
        period=period
    ) 
    
    
@app.route("/transactions/delete/<int:id>")
def delete_transaction_view(id):
    period = request.args.get('period', 'weekly')
    delete_transaction(id)
    return redirect(url_for("transactions_view", period=period))


@app.route("/budgets", methods=["GET", "POST"])
def budgets_view():
    if request.method == "POST":
        category = request.form['category']
        monthly_limit = float(request.form['monthly_limit'])
        set_budget(category, monthly_limit)
        return redirect(url_for("budgets_view"))
        
    budgets = get_budget()
    transactions = get_transactions("monthly")
    spending = {}
    for t in transactions:
        if t['type'] == 'expense':
            spending[t['category']] = spending.get(t['category'], 0) + t['amount']

    return render_template(
        'budgets.html',
        budgets=budgets,
        categories=categories,
        spending=spending
    )
        

init_db()
if __name__ == "__main__":
    app.run(debug=True)
