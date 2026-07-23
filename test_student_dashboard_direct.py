import tkinter as tk
from student.student_dashboard import StudentDashboard

# Test creating student dashboard directly
try:
    root = tk.Tk()
    student_info = {
        'user_id': 8,
        'full_name': 'Test Student'
    }
    
    print("Creating StudentDashboard...")
    dashboard = StudentDashboard(root, student_info)
    print("StudentDashboard created successfully")
    
    # Test show_attendance method
    print("Testing show_attendance...")
    dashboard.show_attendance()
    print("show_attendance completed successfully")
    
    root.destroy()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
