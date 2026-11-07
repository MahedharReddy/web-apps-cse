import os
import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = "lab_week7b_secret_key"
DB_PATH = os.path.join(BASE_DIR, "student_records.db")

DEPARTMENTS = [
    "Computer Science and Engineering",
    "Information Technology",
    "Electronics & Communication",
    "Mechanical Engineering",
    "Civil Engineering",
    "Data Science & AI"
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL,
            gpa REAL NOT NULL
        )
    """)
    # Add initial seed data if table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO students (roll_no, name, department, email, gpa)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("2024CS01", "Alice Johnson", "Computer Science and Engineering", "alice.j@college.edu", 9.2),
            ("2024IT15", "Bob Martinez", "Information Technology", "bob.m@college.edu", 8.6),
            ("2024EC07", "Catherine Lee", "Electronics & Communication", "catherine.l@college.edu", 8.9)
        ])
    conn.commit()
    conn.close()

# ----------------- READ (List & Search) -----------------
@app.route("/")
def index():
    search_query = request.args.get("search", "").strip()
    conn = get_db()
    if search_query:
        query = """
            SELECT * FROM students 
            WHERE roll_no LIKE ? OR name LIKE ? OR department LIKE ?
            ORDER BY id DESC
        """
        wildcard = f"%{search_query}%"
        students = conn.execute(query, (wildcard, wildcard, wildcard)).fetchall()
    else:
        students = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", students=students, search=search_query)

# ----------------- CREATE (Add Student) -----------------
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip().upper()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        gpa = request.form.get("gpa", "").strip()

        # Validation
        if not (roll_no and name and department and email and gpa):
            flash("All fields are required!", "danger")
            return render_template("add_student.html", departments=DEPARTMENTS, form=request.form)

        try:
            gpa_val = float(gpa)
            if not (0.0 <= gpa_val <= 10.0):
                flash("GPA must be between 0.0 and 10.0", "danger")
                return render_template("add_student.html", departments=DEPARTMENTS, form=request.form)
        except ValueError:
            flash("GPA must be a valid number.", "danger")
            return render_template("add_student.html", departments=DEPARTMENTS, form=request.form)

        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO students (roll_no, name, department, email, gpa)
                VALUES (?, ?, ?, ?, ?)
            """, (roll_no, name, department, email, gpa_val))
            conn.commit()
            flash(f"Student '{name}' added successfully!", "success")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            flash(f"Error: Roll Number '{roll_no}' already exists in the database.", "danger")
        finally:
            conn.close()

    return render_template("add_student.html", departments=DEPARTMENTS, form={})

# ----------------- UPDATE (Edit Student) -----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    if not student:
        flash("Student record not found.", "warning")
        conn.close()
        return redirect(url_for("index"))

    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip().upper()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        email = request.form.get("email", "").strip()
        gpa = request.form.get("gpa", "").strip()

        if not (roll_no and name and department and email and gpa):
            flash("All fields are required!", "danger")
            return render_template("edit_student.html", student=student, departments=DEPARTMENTS)

        try:
            gpa_val = float(gpa)
            if not (0.0 <= gpa_val <= 10.0):
                flash("GPA must be between 0.0 and 10.0", "danger")
                return render_template("edit_student.html", student=student, departments=DEPARTMENTS)
        except ValueError:
            flash("GPA must be a valid number.", "danger")
            return render_template("edit_student.html", student=student, departments=DEPARTMENTS)

        try:
            conn.execute("""
                UPDATE students
                SET roll_no = ?, name = ?, department = ?, email = ?, gpa = ?
                WHERE id = ?
            """, (roll_no, name, department, email, gpa_val, id))
            conn.commit()
            flash(f"Record for '{name}' updated successfully!", "success")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            flash(f"Error: Roll Number '{roll_no}' belongs to another student.", "danger")
        finally:
            conn.close()

    conn.close()
    return render_template("edit_student.html", student=student, departments=DEPARTMENTS)

# ----------------- DELETE (Remove Student) -----------------
@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Student record deleted successfully.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, use_reloader=False, port=5003)
