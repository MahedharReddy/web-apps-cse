import os
import sqlite3
import re
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = "lab_week7b_emp_secret_key"
DB_PATH = os.path.join(BASE_DIR, "employee_records.db")

DEPARTMENTS = [
    "Software Engineering",
    "Human Resources",
    "Finance & Accounts",
    "Sales & Marketing",
    "Product Management",
    "Customer Support"
]

DESIGNATIONS = [
    "Junior Associate",
    "Software Engineer",
    "Senior Software Engineer",
    "HR Specialist",
    "Financial Analyst",
    "Team Lead",
    "Department Manager"
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            email TEXT NOT NULL,
            salary REAL NOT NULL,
            joining_date TEXT NOT NULL
        )
    """)
    # Add initial seed records if empty
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO employees (emp_id, name, department, designation, email, salary, joining_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            ("EMP1001", "David Miller", "Software Engineering", "Senior Software Engineer", "david.m@company.com", 92000.0, "2022-03-15"),
            ("EMP1002", "Elena Rostova", "Human Resources", "HR Specialist", "elena.r@company.com", 68000.0, "2023-06-01"),
            ("EMP1003", "Rajesh Kumar", "Finance & Accounts", "Financial Analyst", "rajesh.k@company.com", 74000.0, "2021-11-20")
        ])
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def employee_dashboard():
    errors = {}
    form_data = {
        "emp_id": "",
        "name": "",
        "department": "",
        "designation": "",
        "email": "",
        "salary": "",
        "joining_date": date.today().strftime("%Y-%m-%d")
    }

    if request.method == "POST":
        form_data["emp_id"] = request.form.get("emp_id", "").strip().upper()
        form_data["name"] = request.form.get("name", "").strip()
        form_data["department"] = request.form.get("department", "").strip()
        form_data["designation"] = request.form.get("designation", "").strip()
        form_data["email"] = request.form.get("email", "").strip()
        form_data["salary"] = request.form.get("salary", "").strip()
        form_data["joining_date"] = request.form.get("joining_date", "").strip()

        # Validation
        if not form_data["emp_id"]:
            errors["emp_id"] = "Employee ID is required."
        elif not re.match(r"^[A-Z0-9\-]+$", form_data["emp_id"]):
            errors["emp_id"] = "Employee ID can only contain letters, numbers, and hyphens."

        if not form_data["name"]:
            errors["name"] = "Full name is required."
        elif len(form_data["name"]) < 2:
            errors["name"] = "Name must be at least 2 characters."

        if not form_data["department"] or form_data["department"] not in DEPARTMENTS:
            errors["department"] = "Please select a valid department."

        if not form_data["designation"] or form_data["designation"] not in DESIGNATIONS:
            errors["designation"] = "Please select a valid designation."

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not form_data["email"] or not re.match(email_pattern, form_data["email"]):
            errors["email"] = "Enter a valid email address."

        try:
            salary_val = float(form_data["salary"])
            if salary_val <= 0:
                errors["salary"] = "Salary must be a positive number."
        except ValueError:
            errors["salary"] = "Please enter a valid numeric salary."

        if not form_data["joining_date"]:
            errors["joining_date"] = "Joining date is required."

        if not errors:
            conn = get_db()
            try:
                conn.execute("""
                    INSERT INTO employees (emp_id, name, department, designation, email, salary, joining_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    form_data["emp_id"],
                    form_data["name"],
                    form_data["department"],
                    form_data["designation"],
                    form_data["email"],
                    float(form_data["salary"]),
                    form_data["joining_date"]
                ))
                conn.commit()
                flash(f"Employee {form_data['name']} ({form_data['emp_id']}) registered successfully!", "success")
                conn.close()
                return redirect(url_for("employee_dashboard"))
            except sqlite3.IntegrityError:
                errors["emp_id"] = f"Employee ID '{form_data['emp_id']}' is already assigned to another employee."
                conn.close()

    # Retrieve all records from DB
    dept_filter = request.args.get("department", "").strip()
    conn = get_db()
    if dept_filter:
        employees = conn.execute(
            "SELECT * FROM employees WHERE department = ? ORDER BY id DESC", (dept_filter,)
        ).fetchall()
    else:
        employees = conn.execute("SELECT * FROM employees ORDER BY id DESC").fetchall()

    # Calculate summary metrics
    total_employees = len(employees)
    total_payroll = sum(emp["salary"] for emp in employees) if total_employees > 0 else 0
    avg_salary = (total_payroll / total_employees) if total_employees > 0 else 0
    conn.close()

    return render_template(
        "index.html",
        employees=employees,
        departments=DEPARTMENTS,
        designations=DESIGNATIONS,
        form=form_data,
        errors=errors,
        dept_filter=dept_filter,
        total_employees=total_employees,
        total_payroll=total_payroll,
        avg_salary=avg_salary
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False, port=5004)
