import tkinter as tk
from core.db import get_db_connection
from core.auth import verify_login

print("=" * 50)
print("COMPREHENSIVE STUDENT DASHBOARD TEST")
print("=" * 50)

# Test 1: Direct authentication
print("\n1. Testing direct authentication...")
try:
    student_info = verify_login("student", "241721", "password123")  # Use actual student data
    print(f"Authentication result: {student_info}")
    if student_info:
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
except Exception as e:
    print(f"❌ Authentication error: {e}")

# Test 2: Database connection and query
print("\n2. Testing database connection...")
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ?", (8,))  # Student ID 8 has records
    count = cursor.fetchone()[0]
    print(f"Student 8 attendance records: {count}")
    
    if count > 0:
        cursor.execute("""
            SELECT 
                a.attendance_id,
                a.attendance_date,
                a.attendance_time,
                a.attendance_status,
                cs.subject_code,
                cs.subject_name,
                cs.session_type,
                cs.location
            FROM attendance a
            INNER JOIN class_sessions cs ON a.session_id = cs.session_id
            WHERE a.student_id = ?
            ORDER BY a.attendance_date DESC, a.attendance_time DESC
            LIMIT 5
        """, (8,))
        
        records = cursor.fetchall()
        print(f"Query result: {len(records)} records")
        for i, record in enumerate(records):
            print(f"  Record {i+1}: {dict(record)}")
    
    conn.close()
    print("✅ Database test completed")
    
except Exception as e:
    print(f"❌ Database error: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Testing StudentDashboard creation...")
try:
    root = tk.Tk()
    student_info = {'user_id': 8, 'full_name': 'Test Student'}
    from student.student_dashboard import StudentDashboard
    dashboard = StudentDashboard(root, student_info)
    print("✅ StudentDashboard created")
    
    # Test show_attendance
    print("4. Testing show_attendance...")
    dashboard.show_attendance()
    print("✅ show_attendance completed")
    
    root.destroy()
    
except Exception as e:
    print(f"❌ Dashboard error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("TEST COMPLETED")
print("=" * 50)
