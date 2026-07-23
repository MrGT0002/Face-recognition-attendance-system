from core.db import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

print("\n--- TEACHERS ---")
cur.execute("SELECT teacher_id, employee_id, full_name FROM teachers")
for row in cur.fetchall():
    print(dict(row))

print("\n--- COURSES ---")
cur.execute("SELECT course_id, course_code, course_name FROM courses")
for row in cur.fetchall():
    print(dict(row))

conn.close()
