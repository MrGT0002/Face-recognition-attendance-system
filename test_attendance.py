from core.recognizer import recognize_students
from core.attendance import mark_attendance

# 🔒 HARD-CODE ACTIVE SESSION
SESSION_ID = 1   # 👈 CHANGE if your session_id is different

print("📷 Starting camera for attendance...")
recognized_students = recognize_students(duration_seconds=10)

print("✅ Recognized students:", recognized_students)

for student_code in recognized_students:
    mark_attendance(student_code, SESSION_ID)
