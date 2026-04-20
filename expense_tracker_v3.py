"""
╔══════════════════════════════════════════════════════╗
║       SMART EXPENSE TRACKER - Production Level       ║
║       Built with Streamlit + Python                  ║
╚══════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import bcrypt
import json
import os
import io
import shutil
from datetime import date, datetime, timedelta
from fpdf import FPDF

# ─────────────────────────────────────────────────────
#  PAGE CONFIG (must be first Streamlit call)
# ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────
#  PATHS & CONSTANTS
# ─────────────────────────────────────────────────────
BASE_DIR    = "data"
USERS_FILE  = os.path.join(BASE_DIR, "users.json")
BACKUP_DIR  = os.path.join(BASE_DIR, "backups")
CATEGORIES  = ['Food', 'Transport', 'Shopping', 'Bills',
               'Entertainment', 'Health', 'Education', 'Other']
PAY_MODES   = ['Cash', 'UPI', 'Credit Card', 'Debit Card', 'Net Banking']

os.makedirs(BASE_DIR,   exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────
#  THEME CSS
# ─────────────────────────────────────────────────────
def apply_theme():
    # Single clean dark theme
    bg        = "#0a0e1a"
    card_bg   = "#1a1f35"
    border    = "#2a2f4a"
    text      = "#e0e0f0"
    muted     = "#8888aa"
    accent    = "#7c6af7"
    accent2   = "#06b6d4"
    success   = "#22c55e"
    warning   = "#f59e0b"
    danger    = "#ef4444"
    sidebar   = "#0d1225"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }}
    .stApp {{ background-color: {bg}; }}
    section[data-testid="stSidebar"] > div {{
        background-color: {sidebar};
        border-right: 1px solid {border};
    }}
    .metric-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(124,106,247,0.15);
    }}
    .metric-value {{
        font-size: 1.9rem;
        font-weight: 800;
        color: {accent};
        line-height: 1.1;
    }}
    .metric-label {{
        font-size: 0.8rem;
        color: {muted};
        margin-top: 5px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    .section-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {text};
        margin: 28px 0 14px 0;
        border-left: 4px solid {accent};
        padding-left: 12px;
        border-radius: 0 4px 4px 0;
    }}
    .insight-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 14px 18px;
        margin: 8px 0;
        font-size: 0.88rem;
        color: {text};
        transition: border-color 0.2s;
    }}
    .insight-card:hover {{ border-color: {accent}; }}
    .health-score {{
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
    }}
    .streak-badge {{
        background: linear-gradient(135deg, {accent}, {accent2});
        color: white;
        border-radius: 999px;
        padding: 6px 18px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
    }}
    .budget-bar-bg {{
        background: {border};
        border-radius: 999px;
        height: 10px;
        margin: 8px 0 4px 0;
        overflow: hidden;
    }}
    .budget-bar-fill {{
        border-radius: 999px;
        height: 10px;
        transition: width 0.6s ease;
    }}
    .stButton > button {{
        border-radius: 10px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px);
    }}
    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
    }}
    .login-card {{
        background: {card_bg};
        border: 1px solid {border};
        border-radius: 20px;
        padding: 40px 36px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
#  USER MANAGEMENT (with bcrypt hashing)
# ─────────────────────────────────────────────────────
def load_users() -> dict:
    """Load users from JSON file."""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_users(users: dict):
    """Save users dict to JSON file."""
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        st.error(f"Could not save users: {e}")

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False

def ensure_default_user():
    """Create default admin user if none exist."""
    users = load_users()
    if not users:
        users["admin"] = {
            "password": hash_password("1234"),
            "created": str(date.today()),
            "budget": 5000.0,
            "savings_goal": 1000.0,
            "cat_budgets": {c: 0.0 for c in CATEGORIES}
        }
        save_users(users)

# ─────────────────────────────────────────────────────
#  EXPENSE DATA MANAGEMENT
# ─────────────────────────────────────────────────────
def get_csv_path(username: str) -> str:
    return os.path.join(BASE_DIR, f"expenses_{username}.csv")

def load_expenses(username: str) -> pd.DataFrame:
    """Load expenses safely with date parsing."""
    path = get_csv_path(username)
    cols = ['Date', 'Category', 'Amount', 'Description', 'Payment Mode', 'Recurring']
    try:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
            for c in cols:
                if c not in df.columns:
                    df[c] = "" if c != 'Amount' else 0.0
            df['Recurring'] = df['Recurring'].fillna(False).astype(bool)
            return df.reset_index(drop=True)
    except Exception as e:
        st.warning(f"Data load issue: {e}")
    return pd.DataFrame(columns=cols)

def save_expenses(username: str, df: pd.DataFrame):
    """Save expenses to CSV safely."""
    try:
        df.to_csv(get_csv_path(username), index=False)
    except Exception as e:
        st.error(f"Could not save: {e}")

def add_recurring_expenses(username: str):
    """Auto-add recurring expenses if not already added this month."""
    df = st.session_state.expenses
    if df.empty:
        return
    recurring = df[df['Recurring'] == True].copy()
    if recurring.empty:
        return
    today = pd.Timestamp(date.today())
    current_month = today.month
    current_year  = today.year
    this_month_df = df[
        (pd.to_datetime(df['Date']).dt.month == current_month) &
        (pd.to_datetime(df['Date']).dt.year  == current_year)
    ]
    for _, row in recurring.iterrows():
        already = this_month_df[
            (this_month_df['Category']    == row['Category']) &
            (this_month_df['Description'] == row['Description'] + " (Auto)") &
            (this_month_df['Amount']      == row['Amount'])
        ]
        if already.empty:
            new_row = pd.DataFrame([[
                str(today.date()), row['Category'], row['Amount'],
                row['Description'] + " (Auto)", row['Payment Mode'], False
            ]], columns=df.columns)
            st.session_state.expenses = pd.concat(
                [st.session_state.expenses, new_row], ignore_index=True)
    save_expenses(username, st.session_state.expenses)

# ─────────────────────────────────────────────────────
#  AI / SMART ANALYTICS
# ─────────────────────────────────────────────────────
def spending_prediction(df: pd.DataFrame, budget: float) -> dict:
    """Predict end-of-month spending using linear trend."""
    result = {"predicted": 0, "warning": False, "days_left": 0, "daily_avg": 0}
    if df.empty:
        return result
    try:
        today     = pd.Timestamp(date.today())
        month_df  = df[
            (df['Date'].dt.month == today.month) &
            (df['Date'].dt.year  == today.year)
        ].copy()
        if month_df.empty:
            return result
        daily     = month_df.groupby(month_df['Date'].dt.date)['Amount'].sum()
        days_in   = today.days_in_month
        day_num   = today.day
        days_left = days_in - day_num
        avg_daily = daily.mean() if len(daily) > 0 else 0
        predicted = float(month_df['Amount'].sum()) + avg_daily * days_left
        result = {
            "predicted":  round(predicted, 2),
            "warning":    predicted > budget,
            "days_left":  days_left,
            "daily_avg":  round(avg_daily, 2)
        }
    except Exception:
        pass
    return result

def top_categories_to_cut(df: pd.DataFrame, budget: float) -> list:
    """Suggest top 3 categories to reduce."""
    if df.empty:
        return []
    try:
        cat_sum = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        total   = cat_sum.sum()
        if total == 0:
            return []
        suggestions = []
        for cat, amt in cat_sum.head(3).items():
            pct = round(amt / total * 100, 1)
            suggestions.append({"category": cat, "amount": amt, "pct": pct})
        return suggestions
    except Exception:
        return []

def financial_health_score(df: pd.DataFrame, budget: float, savings_goal: float) -> dict:
    """Calculate a 0–100 financial health score."""
    score = 100
    reasons = []
    try:
        if df.empty:
            return {"score": 75, "grade": "B", "reasons": ["Not enough data yet"]}
        total = df['Amount'].sum()
        if budget > 0:
            ratio = total / budget
            if ratio > 1.0:
                score -= 40
                reasons.append("Over budget this period")
            elif ratio > 0.8:
                score -= 20
                reasons.append("Spending above 80% of budget")
            elif ratio < 0.5:
                score += 5
                reasons.append("Excellent budget control")
        # Diversity penalty (spending in only 1 category)
        num_cats = df['Category'].nunique()
        if num_cats < 2:
            score -= 5
        # Savings check (simple: budget - spending vs goal)
        saved = max(budget - total, 0)
        if savings_goal > 0 and saved >= savings_goal:
            score += 10
            reasons.append("Savings goal achieved!")
        elif savings_goal > 0 and saved < savings_goal * 0.5:
            score -= 15
            reasons.append("Behind on savings goal")
        score = max(0, min(100, score))
        grade = "A+" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 55 else "D"
        color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
    except Exception:
        score, grade, color, reasons = 50, "C", "#f59e0b", ["Calculation error"]
    return {"score": score, "grade": grade, "color": color, "reasons": reasons}

def spending_streak(df: pd.DataFrame, budget: float) -> int:
    """Count consecutive days without overspending daily average."""
    if df.empty or budget <= 0:
        return 0
    try:
        daily_limit = budget / 30
        daily = df.groupby(df['Date'].dt.date)['Amount'].sum().sort_index(ascending=False)
        streak = 0
        for amt in daily:
            if amt <= daily_limit:
                streak += 1
            else:
                break
        return streak
    except Exception:
        return 0

def daily_notifications(df: pd.DataFrame) -> list:
    """Generate smart notification messages."""
    msgs = []
    if df.empty:
        return msgs
    try:
        today     = pd.Timestamp(date.today())
        yesterday = today - timedelta(days=1)
        today_amt = df[df['Date'].dt.date == today.date()]['Amount'].sum()
        yest_amt  = df[df['Date'].dt.date == yesterday.date()]['Amount'].sum()
        if today_amt > yest_amt and yest_amt > 0:
            msgs.append(("⚠️", f"You spent ₹{today_amt:,.0f} today vs ₹{yest_amt:,.0f} yesterday"))
        elif today_amt < yest_amt and yest_amt > 0:
            msgs.append(("✅", f"Great! Spent less today (₹{today_amt:,.0f}) than yesterday (₹{yest_amt:,.0f})"))
        week_ago  = today - timedelta(days=7)
        week_df   = df[df['Date'] >= week_ago]
        if not week_df.empty:
            best_day = week_df.groupby(week_df['Date'].dt.date)['Amount'].sum().idxmin()
            msgs.append(("🏆", f"Best spending day this week: {best_day}"))
    except Exception:
        pass
    return msgs

# ─────────────────────────────────────────────────────
#  PDF EXPORT
# ─────────────────────────────────────────────────────
def generate_pdf(df: pd.DataFrame, username: str, budget: float, health: dict) -> bytes:
    """Generate a summary PDF report."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(60, 40, 180)
        pdf.cell(0, 12, "Smart Expense Tracker - Report", ln=True, align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(80, 80, 100)
        pdf.cell(0, 8, f"User: {username}   |   Generated: {date.today()}", ln=True, align="C")
        pdf.ln(6)

        # Summary
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 30, 50)
        pdf.cell(0, 10, "Summary", ln=True)
        pdf.set_font("Helvetica", "", 11)
        total = df['Amount'].sum() if not df.empty else 0
        pdf.cell(0, 8, f"Total Expenses: Rs {total:,.2f}", ln=True)
        pdf.cell(0, 8, f"Monthly Budget: Rs {budget:,.2f}", ln=True)
        pdf.cell(0, 8, f"Transactions:   {len(df)}", ln=True)
        pdf.cell(0, 8, f"Financial Health Score: {health.get('score', 'N/A')}/100 ({health.get('grade', 'N/A')})", ln=True)
        pdf.ln(4)

        if not df.empty:
            # Category breakdown
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 10, "Category Breakdown", ln=True)
            pdf.set_font("Helvetica", "", 10)
            cat_sum = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
            for cat, amt in cat_sum.items():
                pdf.cell(0, 7, f"  {cat}: Rs {amt:,.2f}", ln=True)
            pdf.ln(4)

            # Recent transactions (up to 15)
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 10, "Recent Transactions", ln=True)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(30, 7, "Date", border=1)
            pdf.cell(35, 7, "Category", border=1)
            pdf.cell(28, 7, "Amount", border=1)
            pdf.cell(0,  7, "Description", border=1, ln=True)
            pdf.set_font("Helvetica", "", 9)
            for _, row in df.tail(15).iterrows():
                pdf.cell(30, 6, str(row['Date'])[:10], border=1)
                pdf.cell(35, 6, str(row['Category']),  border=1)
                pdf.cell(28, 6, f"Rs {float(row['Amount']):,.0f}", border=1)
                desc = str(row['Description'])[:35]
                pdf.cell(0,  6, desc, border=1, ln=True)

        return bytes(pdf.output())
    except Exception as e:
        st.error(f"PDF error: {e}")
        return b""

# ─────────────────────────────────────────────────────
#  CHARTS
# ─────────────────────────────────────────────────────
def chart_colors():
    return ['#7c6af7','#06b6d4','#22c55e','#f59e0b','#ef4444','#a855f7','#ec4899','#14b8a6']

def transparent_layout(fig, title=""):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans", color="#ccd0ee"),
        title=dict(text=title, font=dict(size=15, weight=700)),
        margin=dict(t=45, b=20, l=10, r=10),
        legend=dict(bgcolor='rgba(0,0,0,0)', borderwidth=0)
    )
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.06)', showline=False)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.06)', showline=False)
    return fig

def render_charts(df: pd.DataFrame):
    """Render all charts section."""
    if df.empty:
        st.info("Add some expenses to see charts!")
        return

    st.markdown("<div class='section-title'>📊 Visual Analysis</div>", unsafe_allow_html=True)

    # Row 1: Pie + Bar
    c1, c2 = st.columns(2)
    with c1:
        cat_data = df.groupby('Category')['Amount'].sum().reset_index()
        fig = px.pie(cat_data, values='Amount', names='Category',
                     color_discrete_sequence=chart_colors(), hole=0.42)
        fig = transparent_layout(fig, "Spending by Category")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(cat_data, x='Category', y='Amount',
                     color='Category', color_discrete_sequence=chart_colors())
        fig = transparent_layout(fig, "Category Bar Chart")
        st.plotly_chart(fig, use_container_width=True)

    # Row 2: Monthly Trend Line
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    monthly = df.groupby('Month')['Amount'].sum().reset_index()
    if len(monthly) >= 1:
        fig = px.line(monthly, x='Month', y='Amount', markers=True,
                      color_discrete_sequence=['#7c6af7'],
                      line_shape='spline')
        fig.update_traces(line_width=3, marker_size=8)
        fig = transparent_layout(fig, "📈 Monthly Spending Trend")
        st.plotly_chart(fig, use_container_width=True)

    # Payment Mode chart
    if 'Payment Mode' in df.columns:
        pay_data = df.groupby('Payment Mode')['Amount'].sum().reset_index()
        if not pay_data.empty:
            fig = px.bar(pay_data, x='Payment Mode', y='Amount',
                         color='Amount', color_continuous_scale='purples')
            fig = transparent_layout(fig, "💳 Spending by Payment Mode")
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────
#  LOGIN / SIGNUP PAGE
# ─────────────────────────────────────────────────────
def render_login():
    apply_theme()
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔐 Login", "✨ Sign Up"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="li_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="li_pass", placeholder="Enter password")
            if st.button("Login →", use_container_width=True, key="login_btn"):
                users = load_users()
                if username in users and verify_password(password, users[username]["password"]):
                    st.session_state.logged_in    = True
                    st.session_state.current_user = username
                    st.session_state.user_data    = users[username]
                    st.rerun()
                else:
                    st.error("❌ Wrong username or password!")
            st.caption("Default: admin / 1234")

        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            new_user = st.text_input("Choose Username", key="su_user")
            new_pass = st.text_input("Choose Password", type="password", key="su_pass")
            new_pass2 = st.text_input("Confirm Password", type="password", key="su_pass2")
            if st.button("Create Account →", use_container_width=True, key="signup_btn"):
                if not new_user or not new_pass:
                    st.error("Username and password required!")
                elif new_pass != new_pass2:
                    st.error("Passwords don't match!")
                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters!")
                else:
                    users = load_users()
                    if new_user in users:
                        st.error("Username already exists!")
                    else:
                        users[new_user] = {
                            "password":    hash_password(new_pass),
                            "created":     str(date.today()),
                            "budget":      5000.0,
                            "savings_goal": 1000.0,
                            "cat_budgets": {c: 0.0 for c in CATEGORIES}
                        }
                        save_users(users)
                        st.success("✅ Account created! Please login.")

# ─────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────
def render_sidebar():
    username  = st.session_state.current_user
    user_data = st.session_state.user_data
    df        = st.session_state.expenses

    with st.sidebar:
        # Header
        st.markdown(f"### 👋 {username}")
        st.markdown("---")

        # Budget & Savings
        st.markdown("### 🎯 Budget & Goals")
        budget = st.number_input("Monthly Budget (₹)", min_value=100.0,
                                  value=float(user_data.get("budget", 5000)),
                                  step=100.0, key="budget_input")
        savings_goal = st.number_input("Savings Goal (₹)", min_value=0.0,
                                        value=float(user_data.get("savings_goal", 1000)),
                                        step=100.0, key="savings_input")

        # Category budgets
        with st.expander("📂 Category Budgets"):
            cat_budgets = user_data.get("cat_budgets", {c: 0.0 for c in CATEGORIES})
            new_cat_budgets = {}
            for cat in CATEGORIES:
                new_cat_budgets[cat] = st.number_input(
                    f"{cat} (₹)", min_value=0.0,
                    value=float(cat_budgets.get(cat, 0.0)),
                    step=50.0, key=f"catb_{cat}")

        if st.button("💾 Save Settings", use_container_width=True):
            users = load_users()
            users[username]["budget"]       = budget
            users[username]["savings_goal"] = savings_goal
            users[username]["cat_budgets"]  = new_cat_budgets
            save_users(users)
            st.session_state.user_data = users[username]
            st.success("Saved!")

        # Budget progress bar
        total_spent = df['Amount'].sum() if not df.empty else 0
        pct = min(total_spent / budget * 100, 100) if budget > 0 else 0
        color = "#ef4444" if pct > 80 else "#f59e0b" if pct > 50 else "#22c55e"
        st.markdown(f"""
        <div class='budget-bar-bg'>
          <div class='budget-bar-fill' style='width:{pct:.1f}%;background:{color};'></div>
        </div>
        <small style='color:#8888aa;'>₹{total_spent:,.0f} / ₹{budget:,.0f} spent</small>
        """, unsafe_allow_html=True)

        # Savings goal bar
        saved = max(budget - total_spent, 0)
        spct  = min(saved / savings_goal * 100, 100) if savings_goal > 0 else 0
        st.markdown(f"""
        <div class='budget-bar-bg'>
          <div class='budget-bar-fill' style='width:{spct:.1f}%;background:#7c6af7;'></div>
        </div>
        <small style='color:#8888aa;'>Savings: ₹{saved:,.0f} / ₹{savings_goal:,.0f}</small>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Add / Edit Expense Form
        if st.session_state.get("edit_index") is not None:
            idx = st.session_state.edit_index
            # Use original_index stored at edit time
            orig_idx = st.session_state.get("edit_orig_index", idx)
            row = st.session_state.expenses.loc[orig_idx]
            st.markdown("### ✏️ Edit Expense")
            try:
                d_val = pd.to_datetime(row['Date']).date()
            except Exception:
                d_val = date.today()
            e_date = st.date_input("Date", value=d_val, key="e_date")
            e_cat  = st.selectbox("Category", CATEGORIES,
                        index=CATEGORIES.index(row['Category']) if row['Category'] in CATEGORIES else 0,
                        key="e_cat")
            e_amt  = st.number_input("Amount (₹)", min_value=0.0,
                        value=float(row['Amount']), step=10.0, key="e_amt")
            e_desc = st.text_input("Description", value=str(row['Description']), key="e_desc")
            e_pay  = st.selectbox("Payment Mode", PAY_MODES,
                        index=PAY_MODES.index(row['Payment Mode'])
                        if 'Payment Mode' in row and row['Payment Mode'] in PAY_MODES else 0,
                        key="e_pay")
            e_rec  = st.checkbox("Recurring Monthly", value=bool(row.get('Recurring', False)), key="e_rec")
            ca, cb = st.columns(2)
            with ca:
                if st.button("💾 Save", use_container_width=True):
                    st.session_state.expenses.at[orig_idx, 'Date']         = str(e_date)
                    st.session_state.expenses.at[orig_idx, 'Category']     = e_cat
                    st.session_state.expenses.at[orig_idx, 'Amount']       = e_amt
                    st.session_state.expenses.at[orig_idx, 'Description']  = e_desc
                    st.session_state.expenses.at[orig_idx, 'Payment Mode'] = e_pay
                    st.session_state.expenses.at[orig_idx, 'Recurring']    = e_rec
                    st.session_state.edit_index = None
                    save_expenses(username, st.session_state.expenses)
                    st.success("Updated!")
                    st.rerun()
            with cb:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.edit_index = None
                    st.rerun()
        else:
            st.markdown("### ➕ Add Expense")
            a_date = st.date_input("Date", value=date.today(), key="a_date")
            a_cat  = st.selectbox("Category", CATEGORIES, key="a_cat")
            a_amt  = st.number_input("Amount (₹)", min_value=0.0, step=10.0, key="a_amt")
            a_desc = st.text_input("Description", placeholder="e.g. lunch", key="a_desc")
            a_pay  = st.selectbox("Payment Mode", PAY_MODES, key="a_pay")
            a_rec  = st.checkbox("Recurring Monthly", key="a_rec")
            if st.button("➕ Add Expense", use_container_width=True, key="add_btn"):
                if a_amt > 0 and a_desc.strip():
                    new_row = pd.DataFrame([[
                        str(a_date), a_cat, a_amt, a_desc.strip(), a_pay, a_rec
                    ]], columns=st.session_state.expenses.columns)
                    st.session_state.expenses = pd.concat(
                        [st.session_state.expenses, new_row], ignore_index=True)
                    save_expenses(username, st.session_state.expenses)
                    st.success("✅ Added!")
                    st.rerun()
                else:
                    st.warning("Fill in Amount and Description!")

        st.markdown("---")

        # Import CSV
        st.markdown("### 📥 Import CSV")
        uploaded = st.file_uploader("Upload CSV", type=["csv"], key="csv_upload")
        if uploaded and st.button("Import", use_container_width=True):
            try:
                imp = pd.read_csv(uploaded)
                imp['Date'] = pd.to_datetime(imp['Date'], errors='coerce')
                imp = imp.dropna(subset=['Date'])
                for c in st.session_state.expenses.columns:
                    if c not in imp.columns:
                        imp[c] = ""
                st.session_state.expenses = pd.concat(
                    [st.session_state.expenses, imp[st.session_state.expenses.columns]],
                    ignore_index=True)
                save_expenses(username, st.session_state.expenses)
                st.success(f"Imported {len(imp)} rows!")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

        st.markdown("---")

        # Backup & Restore
        with st.expander("🗄 Backup & Restore"):
            if st.button("📦 Create Backup"):
                try:
                    src = get_csv_path(username)
                    if os.path.exists(src):
                        dst = os.path.join(BACKUP_DIR,
                              f"expenses_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                        shutil.copy(src, dst)
                        st.success("Backup created!")
                    else:
                        st.info("No data to backup.")
                except Exception as e:
                    st.error(f"Backup failed: {e}")

            backups = sorted([f for f in os.listdir(BACKUP_DIR)
                              if f.startswith(f"expenses_{username}_")], reverse=True)
            if backups:
                sel = st.selectbox("Restore from:", backups)
                if st.button("♻️ Restore"):
                    try:
                        src = os.path.join(BACKUP_DIR, sel)
                        shutil.copy(src, get_csv_path(username))
                        st.session_state.expenses = load_expenses(username)
                        st.success("Restored!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Restore failed: {e}")

        st.markdown("---")

        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logout_confirm = True
        if st.session_state.get("logout_confirm"):
            st.warning("Sure you want to logout?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes", use_container_width=True):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            with c2:
                if st.button("No", use_container_width=True):
                    st.session_state.logout_confirm = False
                    st.rerun()

    return float(budget), float(savings_goal), new_cat_budgets

# ─────────────────────────────────────────────────────
#  MAIN DASHBOARD
# ─────────────────────────────────────────────────────
def render_dashboard(budget, savings_goal, cat_budgets):
    username = st.session_state.current_user
    df_full  = st.session_state.expenses.copy()
    if not df_full.empty:
        df_full['Date'] = pd.to_datetime(df_full['Date'], errors='coerce')
        df_full = df_full.dropna(subset=['Date'])

    # ── Header ──
    st.markdown("# 💸 Smart Expense Tracker")
    st.markdown("*Track · Analyse · Save Smarter with Data-Driven Insights*")

    # ── Notifications ──
    notifs = daily_notifications(df_full)
    for icon, msg in notifs:
        if icon == "⚠️":
            st.warning(f"{icon} {msg}")
        else:
            st.success(f"{icon} {msg}")

    st.markdown("---")

    # ── Date Filters ──
    st.markdown("<div class='section-title'>🗓 Date Filter</div>", unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filter_type = st.selectbox("Filter by", ["All Time", "This Month",
                                                   "This Year", "Custom Range"])
    df = df_full.copy()
    today = pd.Timestamp(date.today())
    with fc2:
        if filter_type == "Custom Range":
            start_date = st.date_input("From", value=date.today().replace(day=1))
        elif filter_type == "This Month":
            start_date = today.replace(day=1).date()
            st.info(f"From {start_date}")
        elif filter_type == "This Year":
            start_date = today.replace(month=1, day=1).date()
            st.info(f"From {start_date}")
        else:
            start_date = None
    with fc3:
        if filter_type == "Custom Range":
            end_date = st.date_input("To", value=date.today())
        elif filter_type in ["This Month", "This Year"]:
            end_date = today.date()
            st.info(f"To {end_date}")
        else:
            end_date = None

    if start_date and end_date and not df.empty:
        df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    elif filter_type == "This Month" and not df.empty:
        df = df[(df['Date'].dt.month == today.month) & (df['Date'].dt.year == today.year)]
    elif filter_type == "This Year" and not df.empty:
        df = df[df['Date'].dt.year == today.year]

    # ── Dashboard Section ──
    st.markdown("<div class='section-title'>📊 Dashboard</div>", unsafe_allow_html=True)

    # ── KPI Metrics ──
    total    = df['Amount'].sum()    if not df.empty else 0
    avg_e    = df['Amount'].mean()   if not df.empty else 0
    highest  = df['Amount'].max()    if not df.empty else 0
    tx_count = len(df)
    remaining = max(budget - total, 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    def metric_html(val, label):
        return f"""<div class='metric-card'>
            <div class='metric-value'>{val}</div>
            <div class='metric-label'>{label}</div></div>"""

    c1.markdown(metric_html(f"₹{total:,.0f}",     "💰 Total Spent"),     unsafe_allow_html=True)
    c2.markdown(metric_html(f"₹{avg_e:,.0f}",     "📊 Avg per Entry"),   unsafe_allow_html=True)
    c3.markdown(metric_html(f"₹{highest:,.0f}",   "🔺 Highest"),         unsafe_allow_html=True)
    c4.markdown(metric_html(f"{tx_count}",         "🧾 Transactions"),    unsafe_allow_html=True)
    c5.markdown(metric_html(f"₹{remaining:,.0f}", "💚 Remaining"),       unsafe_allow_html=True)

    # ── Predictive Analytics ──
    st.markdown("<div class='section-title'>📡 Predictive Analytics & Insights</div>", unsafe_allow_html=True)
    pred   = spending_prediction(df_full, budget)
    health = financial_health_score(df_full, budget, savings_goal)
    streak = spending_streak(df_full, budget)
    top3   = top_categories_to_cut(df, budget)

    ai1, ai2, ai3 = st.columns(3)

    with ai1:
        st.markdown("<div class='insight-card'>", unsafe_allow_html=True)
        st.markdown("**📈 End-of-Month Forecast**")
        if pred["predicted"] > 0:
            col = "🔴" if pred["warning"] else "🟢"
            st.markdown(f"{col} Predicted spend: **₹{pred['predicted']:,.0f}**")
            st.markdown(f"Daily average: ₹{pred['daily_avg']:,.0f} | Days left: {pred['days_left']}")
            if pred["warning"]:
                st.error("⚠️ Likely to exceed budget this month!")
            else:
                st.success("✅ On track to stay within budget!")
        else:
            st.info("Add more data for predictions.")
        st.markdown("</div>", unsafe_allow_html=True)

    with ai2:
        score_color = health.get('color', '#22c55e')
        grade = health.get('grade', 'B')
        score = health.get('score', 75)
        st.markdown(f"""<div class='insight-card' style='text-align:center;'>
            <div style='font-size:13px;color:#8888aa;font-weight:600;'>FINANCIAL HEALTH</div>
            <div class='health-score' style='color:{score_color};'>{score}</div>
            <div style='font-size:1.2rem;font-weight:700;color:{score_color};'>Grade: {grade}</div>
        </div>""", unsafe_allow_html=True)
        for r in health.get("reasons", []):
            st.caption(f"• {r}")

    with ai3:
        st.markdown("<div class='insight-card'>", unsafe_allow_html=True)
        st.markdown("**🔥 Streak & Suggestions**")
        st.markdown(f"<span class='streak-badge'>🔥 {streak} day streak</span>",
                    unsafe_allow_html=True)
        st.markdown("<br>**Top 3 to reduce:**", unsafe_allow_html=True)
        for s in top3:
            st.markdown(f"• **{s['category']}** — ₹{s['amount']:,.0f} ({s['pct']}%)")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Category Budget Warnings ──
    if not df.empty:
        cat_spent = df.groupby('Category')['Amount'].sum()
        warnings  = []
        for cat, limit in cat_budgets.items():
            if limit > 0 and cat in cat_spent:
                spent = cat_spent[cat]
                pct   = spent / limit * 100
                if pct > 80:
                    warnings.append((cat, spent, limit, pct))
        if warnings:
            st.markdown("<div class='section-title'>🚨 Category Budget Alerts</div>",
                        unsafe_allow_html=True)
            for cat, spent, limit, pct in warnings:
                color = "#ef4444" if pct >= 100 else "#f59e0b"
                st.markdown(f"""<div class='insight-card' style='border-color:{color};'>
                    {'🔴' if pct >= 100 else '🟡'} <b>{cat}</b>:
                    ₹{spent:,.0f} / ₹{limit:,.0f} ({pct:.0f}% used)
                </div>""", unsafe_allow_html=True)

    # ── Search & Filter Table ──
    st.markdown("<div class='section-title'>🔍 Search & Filter Expenses</div>",
                unsafe_allow_html=True)
    sf1, sf2, sf3 = st.columns(3)
    with sf1:
        cats_avail = ['All'] + sorted(df['Category'].unique().tolist()) if not df.empty else ['All']
        sel_cat = st.selectbox("Category", cats_avail, key="filter_cat")
    with sf2:
        pays_avail = ['All'] + PAY_MODES
        sel_pay = st.selectbox("Payment Mode", pays_avail, key="filter_pay")
    with sf3:
        search = st.text_input("🔎 Search Description", placeholder="type to search...", key="search")

    filtered = df.copy()
    if sel_cat != 'All':
        filtered = filtered[filtered['Category'] == sel_cat]
    if sel_pay != 'All' and 'Payment Mode' in filtered.columns:
        filtered = filtered[filtered['Payment Mode'] == sel_pay]
    if search:
        filtered = filtered[filtered['Description'].str.contains(search, case=False, na=False)]

    # ── Expense Table ──
    st.markdown("<div class='section-title'>📋 All Expenses</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.info("No expenses found. Try a different filter or add expenses from the sidebar.")
    else:
        hdr = st.columns([1.4, 1.4, 1, 2.2, 1.4, 0.7, 0.7])
        for col_w, label in zip(hdr, ["Date","Category","Amount","Description","Payment","Edit","Del"]):
            col_w.markdown(f"**{label}**")
        st.markdown("---")

        # Use actual index from main df to avoid mismatch
        for display_pos, (orig_idx, row) in enumerate(filtered.iterrows()):
            cols = st.columns([1.4, 1.4, 1, 2.2, 1.4, 0.7, 0.7])
            try:
                cols[0].write(str(row['Date'])[:10])
                cols[1].write(str(row['Category']))
                cols[2].write(f"₹{float(row['Amount']):,.0f}")
                cols[3].write(str(row['Description'])[:40])
                cols[4].write(str(row.get('Payment Mode', '')))
            except Exception:
                pass
            if cols[5].button("✏️", key=f"edit_{orig_idx}_{display_pos}"):
                st.session_state.edit_index      = orig_idx
                st.session_state.edit_orig_index = orig_idx
                st.rerun()
            if cols[6].button("🗑️", key=f"del_{orig_idx}_{display_pos}"):
                st.session_state.expenses = st.session_state.expenses.drop(
                    index=orig_idx).reset_index(drop=True)
                save_expenses(username, st.session_state.expenses)
                st.rerun()

    # ── Charts ──
    render_charts(df)

    # ── Smart Insights ──
    if not df.empty:
        st.markdown("<div class='section-title'>🧠 Data-Driven Insights</div>", unsafe_allow_html=True)
        try:
            max_cat     = df.groupby('Category')['Amount'].sum().idxmax()
            max_amt     = df.groupby('Category')['Amount'].sum().max()
            min_cat     = df.groupby('Category')['Amount'].sum().idxmin()
            top_expense = df.loc[df['Amount'].idxmax()]
        except Exception:
            max_cat, max_amt, min_cat, top_expense = "N/A", 0, "N/A", None

        ii1, ii2 = st.columns(2)
        with ii1:
            st.markdown(f"<div class='insight-card'>🔥 <b>Highest Category:</b> {max_cat} (₹{max_amt:,.0f})</div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='insight-card'>💡 <b>Lowest Category:</b> {min_cat}</div>",
                        unsafe_allow_html=True)
            if top_expense is not None:
                try:
                    st.markdown(f"""<div class='insight-card'>🧾 <b>Biggest Expense:</b>
                        {top_expense['Description']} — ₹{float(top_expense['Amount']):,.0f}</div>""",
                                unsafe_allow_html=True)
                except Exception:
                    pass
        with ii2:
            saved = max(budget - total, 0)
            if saved >= savings_goal and savings_goal > 0:
                st.success(f"🎯 Savings goal achieved! Saved ₹{saved:,.0f}")
            else:
                needed = max(savings_goal - saved, 0)
                st.info(f"🎯 Need ₹{needed:,.0f} more to hit savings goal")
            if total > budget:
                st.error(f"⚠️ Over budget by ₹{total - budget:,.0f}!")
            elif total > budget * 0.8:
                st.warning("📢 Over 80% of budget used!")
            else:
                st.success("✅ Spending under control!")

    # ── Export Section ──
    st.markdown("<div class='section-title'>📤 Insights & Export</div>", unsafe_allow_html=True)
    ex1, ex2, ex3 = st.columns(3)

    with ex1:
        if not df_full.empty:
            csv_bytes = df_full.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", data=csv_bytes,
                               file_name=f"expenses_{username}.csv",
                               mime="text/csv", use_container_width=True)

    with ex2:
        if not df_full.empty:
            try:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                    df_full.to_excel(writer, index=False, sheet_name="Expenses")
                    df_full.groupby('Category')['Amount'].sum().reset_index().to_excel(
                        writer, index=False, sheet_name="Summary")
                buf.seek(0)
                st.download_button("📊 Download Excel", data=buf.getvalue(),
                                   file_name=f"expenses_{username}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)
            except Exception as e:
                st.error(f"Excel export error: {e}")

    with ex3:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            health_local = financial_health_score(df_full, budget, savings_goal)
            pdf_bytes    = generate_pdf(df_full, username, budget, health_local)
            if pdf_bytes:
                st.download_button("⬇️ Download PDF", data=pdf_bytes,
                                   file_name=f"report_{username}_{date.today()}.pdf",
                                   mime="application/pdf", use_container_width=True)

    st.markdown("---")
    st.caption("💸 Smart Expense Tracker v2.0 | Built with Python & Streamlit | Powered by Predictive Analytics")

# ─────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────────────
def main():
    ensure_default_user()

    # Init session state
    if 'logged_in'     not in st.session_state: st.session_state.logged_in     = False
    if 'current_user'  not in st.session_state: st.session_state.current_user  = ""
    if 'user_data'     not in st.session_state: st.session_state.user_data     = {}
    if 'edit_index'    not in st.session_state: st.session_state.edit_index    = None
    if 'logout_confirm' not in st.session_state: st.session_state.logout_confirm = False

    apply_theme()

    if not st.session_state.logged_in:
        render_login()
        return

    # Load expenses on first login
    if 'expenses' not in st.session_state:
        st.session_state.expenses = load_expenses(st.session_state.current_user)
        add_recurring_expenses(st.session_state.current_user)

    budget, savings_goal, cat_budgets = render_sidebar()
    render_dashboard(budget, savings_goal, cat_budgets)

if __name__ == "__main__":
    main()
