import os
import re
from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

DEPARTMENTS = [
    "Computer Science and Engineering",
    "Information Technology",
    "Electronics and Communication",
    "Mechanical Engineering",
    "Civil Engineering",
    "Artificial Intelligence & Data Science"
]

@app.route("/", methods=["GET", "POST"])
def student_form():
    errors = {}
    form_data = {
        "student_id": "",
        "name": "",
        "department": "",
        "email": "",
        "semester": ""
    }

    if request.method == "POST":
        form_data["student_id"] = request.form.get("student_id", "").strip()
        form_data["name"] = request.form.get("name", "").strip()
        form_data["department"] = request.form.get("department", "").strip()
        form_data["email"] = request.form.get("email", "").strip()
        form_data["semester"] = request.form.get("semester", "").strip()

        # Validation logic
        if not form_data["student_id"]:
            errors["student_id"] = "Student ID / Roll Number is required."
        elif not re.match(r"^[A-Za-z0-9\-]+$", form_data["student_id"]):
            errors["student_id"] = "Student ID can only contain letters, numbers, and hyphens."

        if not form_data["name"]:
            errors["name"] = "Student name is required."
        elif len(form_data["name"]) < 2:
            errors["name"] = "Name must be at least 2 characters long."
        elif not re.match(r"^[A-Za-z\s]+$", form_data["name"]):
            errors["name"] = "Name can only contain alphabets and spaces."

        if not form_data["department"]:
            errors["department"] = "Please select a department."
        elif form_data["department"] not in DEPARTMENTS:
            errors["department"] = "Invalid department selected."

        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not form_data["email"]:
            errors["email"] = "Email address is required."
        elif not re.match(email_pattern, form_data["email"]):
            errors["email"] = "Please enter a valid email address (e.g., student@college.edu)."

        if not form_data["semester"]:
            errors["semester"] = "Please select a semester."

        # If no validation errors, show details
        if not errors:
            return render_template("result.html", student=form_data)

    return render_template("index.html", departments=DEPARTMENTS, errors=errors, form=form_data)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5001)
