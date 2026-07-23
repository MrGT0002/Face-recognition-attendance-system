"""
Main Entry Point for Face Recognition Attendance System
Provides unified login interface for Admin, Teacher, and Student users.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
from ui_theme import Colors, Fonts, Spacing, configure_styles, RoundedInput, GreenButton


# --------------------------------------------------
# AUTHENTICATION LOGIC
# --------------------------------------------------
def verify_login(user_type, identifier, password):
    conn = sqlite3.connect("database/attendance.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if user_type == "admin":
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("""
            SELECT admin_id, username, full_name
            FROM admins
            WHERE username = ?
              AND password_hash = ?
              AND is_active = 1
        """, (identifier, password_hash))

    elif user_type == "teacher":
        # Teacher login WITHOUT password
        cursor.execute("""
            SELECT teacher_id, employee_id, full_name
            FROM teachers
            WHERE employee_id = ?
              AND is_active = 1
        """, (identifier,))

    elif user_type == "student":
        cursor.execute("""
            SELECT student_id, student_code, full_name
            FROM students
            WHERE student_code = ?
              AND is_active = 1
        """, (identifier,))
    else:
        conn.close()
        return None

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "user_id": row[0],
            "identifier": row[1],
            "full_name": row[2]
        }
    return None


# --------------------------------------------------
# LOGIN WINDOW
# --------------------------------------------------
class MainLoginWindow:
    """
    Login Window for Admin / Teacher / Student
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System - Login")
        self.root.geometry("520x580")
        self.root.resizable(False, False)

        self.user_info = None
        self.user_type = None

        # Apply modern theme
        configure_styles(self.root)
        self.root.configure(bg=Colors.BG_MAIN)

        self.create_ui()

    def create_ui(self):
        # ================= HEADER / TOP BAR =================
        header = tk.Frame(self.root, bg=Colors.ACCENT_PRIMARY, height=72)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Face Recognition Attendance",
            bg=Colors.ACCENT_PRIMARY,
            fg=Colors.TEXT_LIGHT,
            font=Fonts.HEADING_LARGE
        )
        title.pack(pady=(Spacing.MD, 0))

        subtitle = tk.Label(
            header,
            text="Secure access to the academic attendance dashboard",
            bg=Colors.ACCENT_PRIMARY,
            fg=Colors.ACCENT_BG,
            font=Fonts.BODY_MEDIUM
        )
        subtitle.pack()

        # ================= MAIN AREA =================
        main = tk.Frame(self.root, bg=Colors.BG_MAIN)
        main.pack(expand=True, fill=tk.BOTH, padx=Spacing.XL, pady=Spacing.XL)

        # ================= LOGIN CARD =================
        card_outer = tk.Frame(main, bg=Colors.BORDER_LIGHT, highlightthickness=0)
        card_outer.pack(expand=True, fill=tk.BOTH)

        card = tk.Frame(card_outer, bg=Colors.CARD_BG, highlightthickness=0)
        card.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(padx=Spacing.XL, pady=Spacing.XL, fill=tk.BOTH, expand=True)

        # Title
        tk.Label(
            content,
            text="Sign In",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        ).pack(pady=(0, Spacing.XL))

        # User Type
        tk.Label(
            content,
            text="User Type",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.LABEL
        ).pack(anchor="w", pady=(0, Spacing.XS))
        
        self.user_type_var = tk.StringVar(value="Student")
        user_type_combo = ttk.Combobox(
            content,
            textvariable=self.user_type_var,
            values=["Admin", "Teacher", "Student"],
            state="readonly",
            width=35,
            font=Fonts.INPUT
        )
        user_type_combo.pack(pady=(0, Spacing.LG))
        # Keyboard navigation: ENTER moves focus to identifier
        user_type_combo.bind("<Return>", lambda e: self.identifier_input.focus_set())

        # Identifier
        tk.Label(
            content,
            text="Identifier",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.LABEL
        ).pack(anchor="w", pady=(0, Spacing.XS))
        
        self.identifier_input = RoundedInput(content, width=35)
        self.identifier_input.pack(pady=(0, Spacing.LG))
        self.identifier_input.focus_set()
        # ENTER from identifier moves to password
        self.identifier_input.entry.bind("<Return>", lambda e: self.password_input.focus_set())

        # Password
        tk.Label(
            content,
            text="Password",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.LABEL
        ).pack(anchor="w", pady=(0, Spacing.XS))
        
        self.password_input = RoundedInput(content, width=35)
        self.password_input.pack(pady=(0, Spacing.XL))
        # Configure password entry to show dots
        self.password_input.entry.config(show="•")
        self.password_input.entry.bind('<Return>', lambda e: self.login())

        # Login Button
        login_btn = GreenButton(
            content,
            text="LOGIN",
            command=self.login
        )
        login_btn.pack(fill=tk.X, pady=(0, Spacing.SM))

        # Footer text
        tk.Label(
            content,
            text="Please select your role and enter credentials",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_SMALL
        ).pack(pady=(Spacing.LG, 0))

    def login(self):
        user_type = self.user_type_var.get().lower()
        identifier = self.identifier_input.get().strip()
        password = self.password_input.get().strip()

        if not identifier:
            messagebox.showerror("Error", "Identifier is required")
            return

        # Teacher ignores password
        if user_type == "teacher":
            user_info = verify_login(user_type, identifier, None)
        else:
            if not password:
                messagebox.showerror("Error", "Password is required")
                return
            user_info = verify_login(user_type, identifier, password)

        if user_info:
            self.user_info = user_info
            self.user_type = user_type
            self.root.quit()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")


# --------------------------------------------------
# DASHBOARD ROUTING
# --------------------------------------------------
def redirect_to_dashboard(user_type, user_info):
    if user_type == "admin":
        from admin.admin_dashboard import AdminDashboard
        root = tk.Tk()
        AdminDashboard(root, admin_id=user_info["user_id"])  # ✅ FIX
        root.mainloop()

    elif user_type == "teacher":
        from teacher.teacher_dashboard import TeacherDashboard
        root = tk.Tk()
        TeacherDashboard(root, user_info)
        root.mainloop()

    elif user_type == "student":
        from student.student_dashboard import StudentDashboard
        root = tk.Tk()
        StudentDashboard(root, user_info)
        root.mainloop()


# --------------------------------------------------
# MAIN ENTRY POINT
# --------------------------------------------------
def main():
    login_root = tk.Tk()
    login_app = MainLoginWindow(login_root)
    login_root.mainloop()

    if login_app.user_info and login_app.user_type:
        redirect_to_dashboard(login_app.user_type, login_app.user_info)
    else:
        print("Application closed.")


if __name__ == "__main__":
    main()
