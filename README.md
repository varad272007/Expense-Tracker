# 💸 Smart Expense Tracker

A **production-level Expense Management Web App** built using **Streamlit + Python** that helps users track, analyze, and optimize their spending with smart insights and visual analytics.

---

## 🚀 Features

### 🔐 User Management

* Secure login/signup system
* Password hashing using `bcrypt`
* Multi-user support

### 💰 Expense Tracking

* Add, edit, delete expenses
* Categories (Food, Transport, Shopping, etc.)
* Payment modes (Cash, UPI, Cards, Net Banking)
* Recurring expense tracking

### 📊 Data Visualization

* Interactive charts using `plotly`
* Category-wise spending (Pie chart)
* Monthly trends (Line graph)
* Payment mode distribution

### 📡 Smart Analytics

* End-of-month spending prediction
* Financial health score (0–100)
* Budget tracking & alerts
* Spending streak tracking
* AI-based suggestions to reduce expenses

### 🎯 Budget & Goals

* Monthly budget tracking
* Category-wise budget limits
* Savings goal monitoring

### 📂 Data Management

* Import expenses via CSV
* Backup & restore functionality
* Export reports:

  * CSV
  * Excel
  * PDF report

---

## 🛠️ Tech Stack

* **Frontend & Backend:** Streamlit
* **Data Processing:** pandas, numpy
* **Visualization:** plotly
* **Authentication:** bcrypt
* **File Handling:** JSON, CSV
* **PDF Generation:** FPDF

---

## 📦 Installation

### 1. Clone or Download the Project

```bash
git clone <your-repo-link>
cd expense-tracker
```

### 2. Install Dependencies

```bash
pip install streamlit pandas plotly numpy bcrypt fpdf openpyxl
```

---

## ▶️ Running the Application

```bash
streamlit run expense_tracker.py
```

Then open in browser:

```
http://localhost:8501
```

---

## 🔑 Default Login Credentials

* **Username:** admin
* **Password:** 1234

---

## 📁 Project Structure

```
expense-tracker/
│── expense_tracker.py
│── data/
│   ├── users.json
│   ├── expenses_<username>.csv
│   └── backups/
│── README.md
```

---

## 📸 Screens & Modules

* Login / Signup Page
* Dashboard with KPIs
* Expense Table with Filters
* Charts & Visual Analytics
* Smart Insights Panel
* Sidebar (Add Expense, Budget, Backup)

---

## 🧠 Key Concepts Used

* Data Analysis using Pandas
* Data Visualization with Plotly
* Secure Authentication (Hashing)
* Session Management (Streamlit)
* Predictive Analytics (Linear Trend)
* File Handling (CSV, JSON)

---

## ⚠️ Known Issues

* File name with spaces or brackets may cause execution issues
* Requires Python 3.8+
* Streamlit must be installed properly

---

## 📈 Future Improvements

* Cloud deployment (AWS / Streamlit Cloud)
* Mobile responsiveness
* Advanced ML-based predictions
* Multi-currency support
* Notifications system

---

## 👨‍💻 Author

**Your Name**

---

## 📜 License

This project is for educational purposes.
