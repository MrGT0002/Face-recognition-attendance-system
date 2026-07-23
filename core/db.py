"""
Database Connection Module
Handles SQLite database connections with foreign key support.
"""

import sqlite3
from pathlib import Path


def get_db_connection():
    """
    Creates and returns a SQLite database connection.
    """

    project_root = Path(__file__).parent.parent
    db_path = project_root / "database" / "attendance.db"

    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 🔥 CRITICAL FIXES HERE
    conn = sqlite3.connect(
        str(db_path),
        timeout=10,                 # wait before locking error
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    # 🔥 REQUIRED PRAGMAS
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 5000")

    return conn



def mark_attendance(student_code, session_id, status="present"):
    """
    Insert attendance record for a recognized student.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    # Convert student_code → student_id
    cursor.execute(
        "SELECT student_id FROM students WHERE student_code = ?",
        (student_code,)
    )
    row = cursor.fetchone()

    if row is None:
        conn.close()
        print(f"⚠ Student not found in DB: {student_code}")
        return False

    student_id = row["student_id"]

    cursor.execute("""
        INSERT INTO attendance (
            student_id,
            session_id,
            attendance_date,
            attendance_time,
            attendance_status
        )
        VALUES (?, ?, DATE('now'), TIME('now'), ?)
    """, (student_id, session_id, status))

    conn.commit()
    conn.close()

    print(f"✅ Attendance marked: {student_code}")
    return True


def test_connection():
    """
    Test function to verify database connection works correctly.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1")
        cursor.fetchone()

        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]

        conn.close()

        print("Database connection successful!")
        print(f"Foreign keys enabled: {fk_enabled == 1}")
        return True

    except sqlite3.Error as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
