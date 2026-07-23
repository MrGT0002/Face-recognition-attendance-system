import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv()  # 👈 loads .env automatically

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
  # Gmail App Password (16 chars)

def send_attendance_email(to_email,
    student_name,
    course_name,
    subject_name,
    subject_code,
    teacher_name,
    date):
    # Safety check
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("⚠️ Email credentials not set. Skipping email.")
        return

    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = "Attendance Marked Successfully"

        msg.set_content(f"""
Hello {student_name},

Your attendance has been marked successfully.

📘 Course        : {course_name}
📕 Subject       : {subject_name}
🔢 Subject Code  : {subject_code}
👨‍🏫 Faculty      : {teacher_name}
📅 Date          : {date}
✅ Status        : Present

Regards,
Face Recognition Attendance System
""")


        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"📧 Email sent to {to_email}")

    except Exception as e:
        print(f"⚠️ Email failed: {e}")




def send_absent_email(
    to_email,
    student_name,
    subject_name,
    subject_code,
    teacher_name,
    date
):
    # Safety check
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("⚠️ Email credentials not set. Skipping absent email.")
        return

    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = "Attendance Status: Absent"

        msg.set_content(f"""
Hello {student_name},

You were marked ABSENT for the following class session:

📕 Subject       : {subject_name}
🔢 Subject Code  : {subject_code}
👨‍🏫 Faculty      : {teacher_name}
📅 Date          : {date}
❌ Status        : Absent

If you believe this is a mistake, please contact your faculty.

Regards,
Face Recognition Attendance System
""")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"📧 Absent email sent to {to_email}")

    except Exception as e:
        print(f"⚠️ Absent email failed: {e}")
