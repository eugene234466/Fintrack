# FinTrack 💸

A personal finance tracker built with Flask and SQLite. Log income and expenses, visualise spending patterns with Matplotlib, and track monthly budget goals — all in a clean dark interface that works on desktop and mobile.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-embedded-003B57?style=flat-square)
![PWA](https://img.shields.io/badge/PWA-ready-00e676?style=flat-square)

---

## Features

- **Transaction tracking** — log income and expenses with category, date, and notes
- **Weekly / Monthly views** — toggle between the last 7 days or last 6 months
- **3 auto-generated charts** — Income vs Expenses, Spending by Category (pie), Trend Over Time (line)
- **Budget goals** — set monthly limits per category with colour-coded progress bars
- **PWA ready** — installable on mobile, works offline, bottom nav on small screens
- **Dark UI** — clean terminal-inspired design with Syne + DM Mono fonts

---

## Screenshots

> Add screenshots here once deployed.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite via `sqlite3` |
| Charts | Matplotlib (PNG served statically) |
| Frontend | Jinja2 templates, vanilla CSS |
| Deployment | Render (gunicorn) |

---

## Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/fintrack.git
cd fintrack

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open your browser at `http://127.0.0.1:5000`

---

## Project Structure

```
fintrack/
├── app.py                  # Flask routes
├── models.py               # SQLite schema and queries
├── charts.py               # Matplotlib chart generation
├── requirements.txt
├── render.yaml             # Render deployment config
├── templates/
│   ├── base.html           # Shared layout, nav, PWA setup
│   ├── dashboard.html      # Summary stats + charts
│   ├── transactions.html   # Add/view/delete transactions
│   └── budgets.html        # Set and track budget goals
└── static/
    ├── manifest.json       # PWA manifest
    ├── sw.js               # Service worker
    ├── icons/              # PWA icons
    └── charts/             # Auto-generated chart images
```

---

## Deployment (Render)

1. Push to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your repo — Render auto-detects `render.yaml`
4. Click **Deploy**

> **Note:** Render's free tier uses an ephemeral filesystem. The SQLite database and chart images reset on each redeploy. For persistent storage, migrate to Render's free PostgreSQL add-on.

---

## Categories

Built-in: `Food` `Rent` `Transport` `Utilities` `Salary` `Freelance` `Entertainment` `Savings` `Other`

To add custom categories, edit the `categories` list in `app.py` and restart the server.

---

## Known Limitations

- Single-user only (no authentication)
- SQLite not persistent on Render free tier
- Charts regenerate on every dashboard load (no caching)

---

## License

This project is proprietary software. All rights reserved.
Unauthorized copying, distribution, or modification is strictly prohibited.
```

And create a `LICENSE` file in your project root:
```
Copyright (c) 2025. All rights reserved.

This software and its source code are proprietary and confidential.
No part of this software may be copied, modified, distributed, or used
in any form without prior written permission from the owner.

Unauthorized use, reproduction, or distribution of this software,
in whole or in part, is strictly prohibited and may result in
severe civil and criminal penalties.
