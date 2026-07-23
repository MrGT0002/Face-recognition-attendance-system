from datetime import datetime
from core.db import get_db_connection
from core.notifications import send_attendance_email, send_absent_email


# =========================================================
# START CLASS SESSION
# =========================================================

def start_class_session(teacher_id, course_id, subject_code, subject_name):
    conn = get_db_connection()
    conn.execute("PRAGMA busy_timeout = 5000")
    cur = conn.cursor()

    now = datetime.now()
    session_date = now.strftime("%Y-%m-%d")
    session_time = now.strftime("%H:%M:%S")

    cur.execute("""
        INSERT INTO class_sessions (
            teacher_id,
            course_id,
            subject_code,
            subject_name,
            session_date,
            session_time,
            session_type,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'ongoing')
    """, (
        teacher_id,
        course_id,
        subject_code,
        subject_name,
        session_date,
        session_time,
        "lecture"
    ))

    conn.commit()
    session_id = cur.lastrowid
    conn.close()

    print(f"📘 Class session started (session_id={session_id})")
    return session_id


# =========================================================
# MARK PRESENT ATTENDANCE
# =========================================================

def mark_attendance(student_code, session_id):
    conn = get_db_connection()
    conn.execute("PRAGMA busy_timeout = 5000")
    cur = conn.cursor()

    # Get student
    cur.execute(
        "SELECT student_id FROM students WHERE student_code = ?",
        (student_code,)
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return

    student_id = row["student_id"]

    now = datetime.now()
    attendance_date = now.strftime("%Y-%m-%d")
    attendance_time = now.strftime("%H:%M:%S")

    # Prevent duplicate
    cur.execute("""
        SELECT 1 FROM attendance
        WHERE student_id = ? AND session_id = ?
    """, (student_id, session_id))

    if cur.fetchone():
        conn.close()
        return

    # Insert PRESENT
    cur.execute("""
        INSERT INTO attendance (
            student_id,
            session_id,
            attendance_date,
            attendance_time,
            attendance_status,
            verification_method
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        session_id,
        attendance_date,
        attendance_time,
        "present",
        "face_recognition"
    ))

    # Fetch email info
    cur.execute("""
        SELECT
            s.full_name   AS student_name,
            s.email       AS student_email,
            c.course_name,
            cs.subject_name,
            cs.subject_code,
            t.full_name   AS teacher_name
        FROM students s
        JOIN class_sessions cs ON cs.session_id = ?
        JOIN teachers t ON t.teacher_id = cs.teacher_id
        JOIN courses c ON c.course_id = cs.course_id
        WHERE s.student_id = ?
    """, (session_id, student_id))

    info = cur.fetchone()

    if info and info["student_email"]:
        send_attendance_email(
            to_email=info["student_email"],
            student_name=info["student_name"],
            course_name=info["course_name"],
            subject_name=info["subject_name"],
            subject_code=info["subject_code"],
            teacher_name=info["teacher_name"],
            date=attendance_date
        )

    conn.commit()
    conn.close()

    print(f"✅ Attendance marked (PRESENT) for {student_code}")


# =========================================================
# MARK ABSENT STUDENTS (NEW – SAFE ADDITION)
# =========================================================

def mark_absent_students(session_id):
    """
    Marks absent students and sends absence emails
    """
    conn = get_db_connection()
    conn.execute("PRAGMA busy_timeout = 5000")
    cur = conn.cursor()

    # Get session + subject + teacher info
    cur.execute("""
        SELECT
            cs.subject_name,
            cs.subject_code,
            t.full_name AS teacher_name
        FROM class_sessions cs
        JOIN teachers t ON t.teacher_id = cs.teacher_id
        WHERE cs.session_id = ?
    """, (session_id,))
    session_info = cur.fetchone()

    if not session_info:
        conn.close()
        return

    # All students
    cur.execute("""
        SELECT student_id, full_name, email
        FROM students
    """)
    all_students = cur.fetchall()

    # Present students
    cur.execute("""
        SELECT student_id
        FROM attendance
        WHERE session_id = ?
          AND attendance_status = 'present'
    """, (session_id,))
    present_ids = {row["student_id"] for row in cur.fetchall()}

    now = datetime.now()
    attendance_date = now.strftime("%Y-%m-%d")
    attendance_time = now.strftime("%H:%M:%S")

    for student in all_students:
        student_id = student["student_id"]

        if student_id in present_ids:
            continue

        # Prevent duplicate absent
        cur.execute("""
            SELECT 1 FROM attendance
            WHERE student_id = ? AND session_id = ?
        """, (student_id, session_id))

        if cur.fetchone():
            continue

        # Insert ABSENT
        cur.execute("""
            INSERT INTO attendance (
                student_id,
                session_id,
                attendance_date,
                attendance_time,
                attendance_status,
                verification_method
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            session_id,
            attendance_date,
            attendance_time,
            "absent",
            "manual"
        ))

        # Send absent email
        if student["email"]:
            send_absent_email(
                to_email=student["email"],
                student_name=student["full_name"],
                subject_name=session_info["subject_name"],
                subject_code=session_info["subject_code"],
                teacher_name=session_info["teacher_name"],
                date=attendance_date
            )

    conn.commit()
    conn.close()

    print("📌 Absent students marked and notified")
