"""
Teacher Dashboard Module
Handles class sessions and face-recognition attendance.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import sqlite3

from core.db import get_db_connection
from core.attendance import start_class_session, mark_attendance
from core.recognizer import recognize_students
from core.attendance import mark_absent_students
from core.exporter import export_session_attendance_to_excel
from ui_theme import Colors, Fonts, Spacing, configure_styles, create_card_frame, create_modern_layout, create_sidebar_button, create_content_card, GreenButton



class TeacherDashboard:
    def __init__(self, root, teacher_info):
        self.root = root
        self.root.title("Teacher Dashboard")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)

        self.teacher_info = teacher_info
        self.active_session_id = None

        configure_styles(self.root)
        self.root.configure(bg=Colors.BG_MAIN)

        # Create modern layout structure
        self.layout = create_modern_layout(self.root)
        
        # Update title to show teacher name
        self.layout['title_label'].config(text=f"Teacher Dashboard - {teacher_info['full_name']}")
        
        # Store navigation buttons
        self.nav_buttons = {}
        
        # Create sidebar navigation
        self.create_sidebar_navigation()
        
        # Container for content cards
        self.content_container = tk.Frame(self.layout['content_area'], bg=Colors.BG_MAIN)
        self.content_container.pack(fill=tk.BOTH, expand=True)

        # Show initial dashboard
        self.show_dashboard()

    def create_sidebar_navigation(self):
        """Create sidebar navigation buttons."""
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Start Session", self.show_start_session),
            ("Start Attendance (Face Recognition)", self.start_attendance),
            ("End Session & Export Excel", self.end_session),
            ("Refresh Data", self.refresh_data),
            ("Logout", self.logout),
        ]

        for idx, (label, command) in enumerate(nav_items):
            is_active = (label == "Dashboard")  # Dashboard is initially active
            btn = create_sidebar_button(
                self.layout['sidebar'],
                text=label,
                command=lambda c=command, name=label: self.on_nav_click(name, c),
                is_active=is_active
            )
            btn.pack(fill=tk.X, padx=Spacing.SM, pady=(Spacing.SM if idx == 0 else Spacing.XS))
            self.nav_buttons[label] = btn

    def clear_content(self):
        """Clear all content from the content container."""
        for child in self.content_container.winfo_children():
            child.destroy()

    def on_nav_click(self, name, callback):
        """Handle navigation button clicks."""
        # Update button styles
        for label, btn in self.nav_buttons.items():
            # Recreate button with new active state
            btn.destroy()
            is_active = (label == name)
            new_btn = create_sidebar_button(
                self.layout['sidebar'],
                text=label,
                command=lambda c=self.get_command_for_label(label), name=label: self.on_nav_click(name, c),
                is_active=is_active
            )
            new_btn.pack(fill=tk.X, padx=Spacing.SM, pady=(Spacing.SM if label == "Dashboard" else Spacing.XS))
            self.nav_buttons[label] = new_btn
        
        # Clear content and show new page
        self.clear_content()
        callback()

    def get_command_for_label(self, label):
        """Get command function for a navigation label."""
        commands = {
            "Dashboard": self.show_dashboard,
            "Start Session": self.show_start_session,
            "Start Attendance (Face Recognition)": self.start_attendance,
            "End Session & Export Excel": self.end_session,
            "Refresh Data": self.refresh_data,
            "Logout": self.logout,
        }
        return commands.get(label, self.show_dashboard)

    # ---------------- UI METHODS ----------------

    def show_dashboard(self):
        """Show the teacher dashboard with overview information."""
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Teacher Dashboard",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text=f"Welcome back, {self.teacher_info['full_name']}",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Info text
        info_text = tk.Label(
            content,
            text="Use the sidebar to start a class session or view attendance records.\n\n"
                 "Face recognition attendance helps you efficiently track student presence\n"
                 "and maintain accurate academic records.",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
            justify="center"
        )
        info_text.pack(expand=True)

    def show_start_session(self):
        """Show the start session form."""
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Start Class Session",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Begin face recognition attendance for your class",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Form
        form = tk.Frame(content, bg=Colors.CARD_BG)
        form.pack(fill=tk.X)
        
        tk.Label(
            form,
            text="Class Session Details",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_SMALL,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, Spacing.LG))

        tk.Label(form, text="Subject Code *", background=Colors.CARD_BG, font=Fonts.LABEL).grid(row=1, column=0, sticky="w", pady=Spacing.SM, padx=(0, Spacing.MD))
        self.subject_code_entry = ttk.Entry(form, width=40, font=Fonts.INPUT)
        self.subject_code_entry.grid(row=1, column=1, pady=Spacing.SM, sticky="w")

        tk.Label(form, text="Subject Name *", background=Colors.CARD_BG, font=Fonts.LABEL).grid(row=2, column=0, sticky="w", pady=Spacing.SM, padx=(0, Spacing.MD))
        self.subject_name_entry = ttk.Entry(form, width=40, font=Fonts.INPUT)
        self.subject_name_entry.grid(row=2, column=1, pady=Spacing.SM, sticky="w")

        tk.Label(form, text="Class Duration (minutes) *", background=Colors.CARD_BG, font=Fonts.LABEL).grid(row=3, column=0, sticky="w", pady=Spacing.SM, padx=(0, Spacing.MD))
        self.duration_entry = ttk.Entry(form, width=40, font=Fonts.INPUT)
        self.duration_entry.grid(row=3, column=1, pady=Spacing.SM, sticky="w")
        self.duration_entry.insert(0, "60")

        # Buttons
        button_frame = tk.Frame(form, bg=Colors.CARD_BG)
        button_frame.grid(row=4, column=0, columnspan=2, pady=Spacing.XL)
        
        start_btn = GreenButton(button_frame, text="Start Session", command=self.start_session)
        start_btn.pack(side=tk.LEFT, padx=(0, Spacing.MD))
        
        # Status display
        self.session_status_label = tk.Label(
            content,
            text="",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM
        )
        self.session_status_label.pack(pady=Spacing.LG)

    def show_view_attendance(self):
        """Show attendance view."""
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="View Attendance",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Review and export attendance records",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Info text
        info_text = tk.Label(
            content,
            text="Attendance records will appear here after you complete class sessions.\n\n"
                 "You can export attendance data to Excel for record-keeping.",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
            justify="center"
        )
        info_text.pack(expand=True)

    # ---------------- SESSION METHODS ----------------

    def start_session(self):
        subject_code = self.subject_code_entry.get().strip()
        subject_name = self.subject_name_entry.get().strip()

        if not subject_code or not subject_name:
            messagebox.showerror(
                "Error",
                "Subject Code and Subject Name are required"
            )
            return

        try:
            teacher_id = self.teacher_info["user_id"]

            # TEMP / DEFAULT course_id (must exist in DB)
            course_id = 2

            self.active_session_id = start_class_session(
                teacher_id,
                course_id,
                subject_code,
                subject_name
            )

            # Note: attendance_btn is created in show_view_attendance, not here
            # self.attendance_btn.config(state=tk.NORMAL)
            # self.end_session_btn.config(state=tk.NORMAL)

            messagebox.showinfo(
                "Session Started",
                f"Session started for {subject_name}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def end_session(self):
        if not self.active_session_id:
            messagebox.showwarning("Warning", "No active session to end")
            return

        try:
            mark_absent_students(self.active_session_id)
            file_name = export_session_attendance_to_excel(
                self.active_session_id
            )

            messagebox.showinfo(
                "Session Ended",
                f"Attendance exported successfully!\n\nFile created:\n{file_name}"
            )

            # Reset UI + session
            self.active_session_id = None
            self.attendance_btn.config(state=tk.DISABLED)
            self.end_session_btn.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ---------------- ATTENDANCE ----------------

    def start_attendance(self):
        if not self.active_session_id:
            messagebox.showwarning("Warning", "Start session first")
            return

        threading.Thread(
            target=self.run_attendance,
            daemon=True
        ).start()

    def run_attendance(self):
        try:
            recognized_students = recognize_students(10)

            marked = 0

            for student_code in recognized_students:
                try:
                    mark_attendance(student_code, self.active_session_id)
                    marked += 1
                except sqlite3.IntegrityError:
                    print(f"⚠️ Skipped duplicate: {student_code}")

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Attendance Done",
                    f"Marked attendance for {marked} students"
                )
            )

        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Attendance Error",
                    str(e)
                )
            )

    def refresh_data(self):
        """Refresh dashboard data."""
        try:
            # Clear and reload dashboard
            self.clear_content()
            self.show_dashboard()
            messagebox.showinfo("Data Refreshed", "Dashboard data has been refreshed!")
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh data: {str(e)}")

    def logout(self):
        """Logout from teacher dashboard."""
        try:
            if self.active_session_id:
                # End active session before logout
                self.end_session()
            
            # Close current window and return to login
            self.root.destroy()
            
            # Import and show login screen
            import main
            main.show_login_screen()
            
        except Exception as e:
            messagebox.showerror("Logout Error", f"Failed to logout: {str(e)}")
