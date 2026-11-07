import os
import re
import random
from datetime import datetime, date
from flask import Flask, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

DOCTORS = [
    {"id": "doc1", "name": "Dr. Sarah Jenkins", "specialty": "Cardiology"},
    {"id": "doc2", "name": "Dr. Rajesh Sharma", "specialty": "Neurology"},
    {"id": "doc3", "name": "Dr. Emily Watson", "specialty": "Pediatrics"},
    {"id": "doc4", "name": "Dr. Alan Brooks", "specialty": "Orthopedics"},
    {"id": "doc5", "name": "Dr. Priya Patel", "specialty": "General Medicine"}
]

TIME_SLOTS = [
    "09:00 AM - 10:00 AM",
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "03:30 PM - 04:30 PM",
    "05:00 PM - 06:00 PM"
]

@app.route("/", methods=["GET", "POST"])
def appointment_booking():
    errors = {}
    form_data = {
        "patient_name": "",
        "doctor_id": "",
        "appointment_date": "",
        "time_slot": "",
        "contact_phone": "",
        "contact_email": ""
    }

    min_date = date.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        form_data["patient_name"] = request.form.get("patient_name", "").strip()
        form_data["doctor_id"] = request.form.get("doctor_id", "").strip()
        form_data["appointment_date"] = request.form.get("appointment_date", "").strip()
        form_data["time_slot"] = request.form.get("time_slot", "").strip()
        form_data["contact_phone"] = request.form.get("contact_phone", "").strip()
        form_data["contact_email"] = request.form.get("contact_email", "").strip()

        # 1. Validate Patient Name
        if not form_data["patient_name"]:
            errors["patient_name"] = "Patient name is required."
        elif len(form_data["patient_name"]) < 2:
            errors["patient_name"] = "Patient name must be at least 2 characters."
        elif not re.match(r"^[A-Za-z\s\.]+$", form_data["patient_name"]):
            errors["patient_name"] = "Patient name should only contain letters, dots, and spaces."

        # 2. Validate Doctor Selection
        selected_doctor = next((d for d in DOCTORS if d["id"] == form_data["doctor_id"]), None)
        if not form_data["doctor_id"]:
            errors["doctor_id"] = "Please select a doctor."
        elif not selected_doctor:
            errors["doctor_id"] = "Selected doctor is not recognized."

        # 3. Validate Appointment Date
        if not form_data["appointment_date"]:
            errors["appointment_date"] = "Appointment date is required."
        else:
            try:
                appt_date_obj = datetime.strptime(form_data["appointment_date"], "%Y-%m-%d").date()
                if appt_date_obj < date.today():
                    errors["appointment_date"] = "Appointment date cannot be in the past."
            except ValueError:
                errors["appointment_date"] = "Invalid date format. Use YYYY-MM-DD."

        # 4. Validate Time Slot
        if not form_data["time_slot"]:
            errors["time_slot"] = "Please select a preferred time slot."
        elif form_data["time_slot"] not in TIME_SLOTS:
            errors["time_slot"] = "Invalid time slot selected."

        # 5. Validate Phone Number (10 digits)
        phone_clean = re.sub(r"[\s\-\(\)]", "", form_data["contact_phone"])
        if not form_data["contact_phone"]:
            errors["contact_phone"] = "Contact phone number is required."
        elif not re.match(r"^[6-9]\d{9}$", phone_clean):
            errors["contact_phone"] = "Enter a valid 10-digit mobile number (e.g., 9876543210)."

        # 6. Validate Email
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not form_data["contact_email"]:
            errors["contact_email"] = "Contact email is required."
        elif not re.match(email_pattern, form_data["contact_email"]):
            errors["contact_email"] = "Enter a valid email address (e.g., patient@example.com)."

        # If valid, render confirmation
        if not errors:
            token_num = f"APT-{date.today().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            confirmation_data = {
                "token": token_num,
                "patient_name": form_data["patient_name"],
                "doctor": selected_doctor["name"],
                "specialty": selected_doctor["specialty"],
                "date": form_data["appointment_date"],
                "slot": form_data["time_slot"],
                "phone": form_data["contact_phone"],
                "email": form_data["contact_email"],
                "booked_at": datetime.now().strftime("%d-%b-%Y %I:%M %p")
            }
            return render_template("confirmation.html", appointment=confirmation_data)

    return render_template(
        "appointment.html",
        doctors=DOCTORS,
        time_slots=TIME_SLOTS,
        min_date=min_date,
        errors=errors,
        form=form_data
    )

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5002)
