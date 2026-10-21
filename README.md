# expense-tracker
# Expense Tracker

A personal finance management web application built with **Python, Flask, SQLite, and JavaScript**. Track income and expenses, organize transactions by category and payment method, and manage upcoming bills and receivables through a simple web interface.

## Features

- **User Authentication** — Create an account and log in securely with password hashing.
- **Income & Expense Tracking** — Add, edit, view, and delete financial transactions.
- **Transaction Categorization** — Organize transactions using categories such as Food, Rent, Transport, Salary, Shopping, and Other.
- **Payment Method Tracking** — Record payments made through cash or online methods.
- **Bill & Receivable Reminders** — Create and manage reminders with due dates and amounts.
- **Personalized Categories** — Add and manage categories for individual accounts.
- **Database Persistence** — Store user accounts and financial records using SQLite.
- **Responsive Web Interface** — Built with HTML, CSS, and JavaScript.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework and API routes |
| Flask-SQLAlchemy | Database ORM |
| SQLite | Data storage |
| HTML5 & CSS3 | User interface and styling |
| JavaScript | Frontend interactivity |
| Werkzeug | Password hashing and verification |

## Project Structure

```text
expense-tracker/
├── app.py              # Flask application and API routes
├── run.py              # Application runner
├── init_db.py          # Database initialization
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Main application interface
│   └── login.html      # Login interface
└── static/
    ├── style.css       # Application styling
    └── script.js       # Frontend logic
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- pip (Python package installer)
- Git (optional)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/yashanki1317/expense-tracker.git
cd expense-tracker
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Initialize the database**

```bash
python init_db.py
```

**5. Run the application**

```bash
python run.py
```

Open your browser and visit:

`http://127.0.0.1:5001`

Create an account to start using the application.

## Security Notes

- Passwords are hashed before being stored in the database.
- User-specific transaction, category, and reminder routes require authentication.
- Configure the Flask secret key through an environment variable before production deployment.
- Do not commit database files, credentials, environment files, or personal financial information to version control.

## Future Improvements

- Expense analytics and monthly spending summaries
- Visual charts for income and expenses
- Export transactions to CSV
- Budget planning and spending limits
- Cloud database integration and online deployment

## Author

**Yashanki Dhupia**

GitHub: [@yashanki1317](https://github.com/yashanki1317)

---

*Developed as a personal finance management project to practice Python backend development, database management, REST API design, and frontend integration.*
