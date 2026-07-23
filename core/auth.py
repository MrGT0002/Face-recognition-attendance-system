"""
Authentication Module
Handles password hashing and user authentication for Admin, Teacher, and Student.
"""

import hashlib
from core.db import get_db_connection


def hash_password(password):
    """
    Hash a password using SHA-256 algorithm.
    """
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


def verify_login(user_type, identifier, password):
    """
    Verify user login credentials for Admin, Teacher, or Student.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ---------------- ADMIN ----------------
        if user_type.lower() == "admin":
            if not password:
                return None

            provided_password_hash = hash_password(password)

            cursor.execute("""
                SELECT admin_id, username, full_name, email, is_active
                FROM admins
                WHERE username = ? AND password_hash = ? AND is_active = 1
            """, (identifier, provided_password_hash))

            result = cursor.fetchone()

            if result:
                conn.close()
                return {
                    'user_type': 'admin',
                    'user_id': result['admin_id'],
                    'username': result['username'],
                    'full_name': result['full_name'],
                    'email': result['email']
                }

        # ---------------- TEACHER ----------------
        elif user_type.lower() == "teacher":
            cursor.execute("""
                SELECT teacher_id, employee_id, full_name, email, department, is_active
                FROM teachers
                WHERE employee_id = ? AND is_active = 1
            """, (identifier,))

            result = cursor.fetchone()

            if result:
                conn.close()
                return {
                    'user_type': 'teacher',
                    'user_id': result['teacher_id'],
                    'employee_id': result['employee_id'],
                    'full_name': result['full_name'],
                    'email': result['email'],
                    'department': result['department']
                }

        # ---------------- STUDENT ----------------
        elif user_type.lower() == "student":
            cursor.execute("""
                SELECT student_id, student_code, full_name, email, is_active
                FROM students
                WHERE student_code = ? AND is_active = 1
            """, (identifier,))

            result = cursor.fetchone()

            if result:
                conn.close()
                return {
    'user_type': 'student',
    'user_id': result['student_id'],
    'student_code': result['student_code'],
    'full_name': result['full_name'],
    'email': result['email']
}


        else:
            conn.close()
            return None

        conn.close()
        return None

    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def update_last_login(user_type, user_id):
    """
    Update the last login timestamp for an admin user.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if user_type.lower() == "admin":
            cursor.execute("""
                UPDATE admins
                SET last_login = CURRENT_TIMESTAMP
                WHERE admin_id = ?
            """, (user_id,))
            conn.commit()

        conn.close()
        return True

    except Exception as e:
        print(f"Error updating last login: {e}")
        return False


if __name__ == "__main__":
    test_password = "testpassword123"
    hashed = hash_password(test_password)
    print(f"Original password: {test_password}")
    print(f"Hashed password: {hashed}")
