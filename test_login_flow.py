import tkinter as tk
from student.student_dashboard import LoginWindow

# Test the complete student login flow
try:
    print("Testing student login flow...")
    root = tk.Tk()
    login_app = LoginWindow(root)
    print("LoginWindow created successfully")
    
    # Start the login loop
    root.mainloop()
    print("Login loop completed")
    
except Exception as e:
    print(f"Error in login flow: {e}")
    import traceback
    traceback.print_exc()
