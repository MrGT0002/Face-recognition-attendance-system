import pandas as pd
from core.db import get_db_connection


def export_session_attendance_to_excel(session_id):
    conn = get_db_connection()

    query = """
    SELECT
        cs.session_id,
        cs.subject_code,
        cs.subject_name,
        cs.session_date,
        cs.session_time,
        t.employee_id AS teacher_id,
        t.full_name AS teacher_name,
        s.student_code,
        s.full_name AS student_name,
        a.attendance_status,
        a.attendance_time
    FROM attendance a
    JOIN students s ON s.student_id = a.student_id
    JOIN class_sessions cs ON cs.session_id = a.session_id
    JOIN teachers t ON t.teacher_id = cs.teacher_id
    WHERE cs.session_id = ?
    ORDER BY s.student_code
    """

    df = pd.read_sql_query(query, conn, params=(session_id,))
    conn.close()

    if df.empty:
        raise ValueError("No attendance data found for this session")

    filename = f"attendance_session_{session_id}.xlsx"
    df.to_excel(filename, index=False)

    return filename
