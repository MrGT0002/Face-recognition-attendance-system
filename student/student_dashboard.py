"""
Student Dashboard Module
Tkinter GUI for students to view their attendance records.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import defaultdict
from core.db import get_db_connection
from core.auth import verify_login
from ui_theme import Colors, Fonts, Spacing, configure_styles, create_modern_layout, create_sidebar_button, create_content_card, GreenButton


class LoginWindow:
    """
    Student Login Window
    Handles student authentication before accessing dashboard.
    """
    
    def __init__(self, root):
        """
        Initialize login window.
        
        Args:
            root (tk.Tk): Root Tkinter window
        """
        self.root = root
        self.root.title("Student Login - Face Recognition Attendance System")
        self.root.geometry("420x220")
        self.root.resizable(False, False)

        configure_styles(self.root)
        self.root.configure(bg=Colors.BG_MAIN)
        
        # Store student info after successful login
        self.student_info = None
        
        # Create login form
        self.create_login_form()
        
        # Center window on screen
        self.center_window()
    
    def center_window(self):
        """Center the login window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_login_form(self):
        """Create login form with student code and password fields."""
        # Title label
        title_label = ttk.Label(
            self.root,
            text="Student Login",
            font=Fonts.HEADING_SMALL
        )
        title_label.pack(pady=(Spacing.LG, Spacing.XS))

        subtitle = ttk.Label(
            self.root,
            text="Secure access to your attendance records",
            font=Fonts.BODY_MEDIUM,
            foreground=Colors.TEXT_SECONDARY,
        )
        subtitle.pack(pady=(0, Spacing.MD))
        
        # Form frame
        form_frame = ttk.Frame(self.root, padding=Spacing.LG)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Student Code field
        ttk.Label(form_frame, text="Student Code *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.student_code_entry = ttk.Entry(form_frame, width=30)
        self.student_code_entry.grid(row=0, column=1, pady=5, padx=10)
        self.student_code_entry.focus()
        
        # Password field
        ttk.Label(form_frame, text="Password *:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Login button
        login_btn = ttk.Button(
            form_frame,
            text="Login",
            style="Primary.TButton",
            command=self.login
        )
        login_btn.grid(row=2, column=1, pady=15, sticky=tk.E)
    
    def login(self):
        """
        Verify student credentials and open dashboard on success.
        Uses core/auth.py for authentication.
        """
        # Get login credentials
        student_code = self.student_code_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Validate input
        if not student_code or not password:
            messagebox.showerror("Error", "Please enter both Student Code and Password")
            return
        
        # Verify login using authentication module
        # Note: For students, password check might be simplified based on your schema
        student_info = verify_login("student", student_code, password)
        
        if student_info:
            # Store student info and close login window
            self.student_info = student_info
            self.root.quit()  # Exit login loop
        else:
            messagebox.showerror("Error", "Invalid Student Code or Password")


class StudentDashboard:
    """
    Main Student Dashboard Window
    Displays student's attendance records with subject-wise and date-wise views.
    """
    
    def __init__(self, root, student_info):
        """
        Initialize student dashboard.
        
        Args:
            root (tk.Tk): Root Tkinter window
            student_info (dict): Student information from login
        """
        self.root = root
        self.root.title("Student Dashboard - Face Recognition Attendance System")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        self.student_info = student_info
        self.student_id = student_info['user_id']

        configure_styles(self.root)
        self.root.configure(bg=Colors.BG_MAIN)

        # Create modern layout structure
        self.layout = create_modern_layout(self.root)
        
        # Update title to show student name
        self.layout['title_label'].config(text=f"Student Dashboard - {student_info['full_name']}")
        
        # Store navigation buttons
        self.nav_buttons = {}
        
        # Create sidebar navigation
        self.create_sidebar_navigation()
        
        # Container for content cards
        self.content_container = tk.Frame(self.layout['content_area'], bg=Colors.BG_MAIN)
        self.content_container.pack(fill=tk.BOTH, expand=True)

        # Show initial dashboard
        self.show_dashboard()
        
        # Load attendance data
        self.load_attendance()

    def create_sidebar_navigation(self):
        """Create the sidebar navigation buttons."""
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("My Attendance", self.show_attendance),
            ("Reports", self.show_reports),
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
        """Get the command function for a navigation label."""
        commands = {
            "Dashboard": self.show_dashboard,
            "My Attendance": self.show_attendance,
            "Reports": self.show_reports,
        }
        return commands.get(label, self.show_dashboard)

    # ---------------- UI METHODS ----------------

    def show_dashboard(self):
        """Show the student dashboard with overview information."""
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Student Dashboard",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text=f"Welcome back, {self.student_info['full_name']}",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Info text
        info_text = tk.Label(
            content,
            text="Use the sidebar to view your attendance records and reports.\n\n"
                 "Track your academic attendance and monitor your progress\n"
                 "across different subjects and time periods.",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
            justify="center"
        )
        info_text.pack(expand=True)

    def show_attendance(self):
        """Show attendance records."""
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="My Attendance",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="View your attendance history and statistics",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Notebook for attendance views
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_summary_tab()
        self.create_datewise_tab()
        self.create_subjectwise_tab()
        
        # Load attendance data after tabs are created
        self.load_attendance()

    def show_reports(self):
        """Show reports section."""
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Reports",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Generate and download attendance reports",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Info text
        info_text = tk.Label(
            content,
            text="Detailed attendance reports and analytics will be available here.\n\n"
                 "You can export your attendance data for academic records\n"
                 "and track your attendance patterns over time.",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
            justify="center"
        )
        info_text.pack(expand=True)

    # ---------------- ATTENDANCE METHODS ----------------

    def create_summary_tab(self):
        """
        Create tab showing overall attendance summary and statistics.
        Displays total attendance count and overall percentage.
        """
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="Summary")
        stats_frame = ttk.LabelFrame(summary_frame, text="Statistics", padding=Spacing.LG)
        stats_frame.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.X)
        
        # Summary labels (will be updated when data loads)
        self.total_sessions_label = ttk.Label(
            stats_frame,
            text="Total Sessions Attended: 0",
            font=Fonts.BODY_MEDIUM
        )
        self.total_sessions_label.pack(pady=5)
        
        self.present_count_label = ttk.Label(
            stats_frame,
            text="Present: 0",
            font=Fonts.BODY_MEDIUM
        )
        self.present_count_label.pack(pady=5)
        
        self.late_count_label = ttk.Label(
            stats_frame,
            text="Late: 0",
            font=Fonts.BODY_MEDIUM
        )
        self.late_count_label.pack(pady=5)

        self.absent_count_label = ttk.Label(
            stats_frame,
            text="Absent: 0",
            font=Fonts.BODY_MEDIUM,
            foreground="red"
        )
        self.absent_count_label.pack(pady=5)
        
        self.overall_percentage_label = ttk.Label(
            stats_frame,
            text="Overall Attendance: 0%",
            font=Fonts.HEADING_SMALL,
            foreground="blue"
        )
        self.overall_percentage_label.pack(pady=10)
        
        # Subject-wise percentage frame
        subject_percent_frame = ttk.LabelFrame(summary_frame, text="Subject-wise Attendance", padding=Spacing.LG)
        subject_percent_frame.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.BOTH, expand=True)
        
        # Treeview for subject-wise percentages
        columns = ("Subject", "Course Code", "Sessions Attended", "Present", "Late", "Percentage")
        self.subject_percent_tree = ttk.Treeview(subject_percent_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings
        for col in columns:
            self.subject_percent_tree.heading(col, text=col)
            self.subject_percent_tree.column(col, width=150, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(subject_percent_frame, orient=tk.VERTICAL, command=self.subject_percent_tree.yview)
        self.subject_percent_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.subject_percent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Zebra striping tags
        self.subject_percent_tree.tag_configure("odd", background=Colors.CARD_BG)
        self.subject_percent_tree.tag_configure("even", background=Colors.CARD_SECONDARY)
    
    def create_datewise_tab(self):
        """
        Create tab showing attendance records grouped by date.
        Displays all attendance entries organized by date.
        """
        datewise_frame = ttk.Frame(self.notebook)
        self.notebook.add(datewise_frame, text="Date-wise Attendance")
        
        # Title label
        title_label = ttk.Label(
            datewise_frame,
            text="Attendance by Date",
            font=Fonts.HEADING_SMALL
        )
        title_label.pack(pady=Spacing.MD)
        
        # Display frame with scrollbar
        display_frame = ttk.Frame(datewise_frame)
        display_frame.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.BOTH, expand=True)
        
        # Treeview for date-wise attendance
        columns = ("Date", "Time", "Subject", "Course Code", "Session Type", "Status", "Location")
        self.datewise_tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=20)
        
        # Configure column headings
        for col in columns:
            self.datewise_tree.heading(col, text=col)
            self.datewise_tree.column(col, width=140, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.datewise_tree.yview)
        self.datewise_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.datewise_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.datewise_tree.tag_configure("odd", background=Colors.CARD_BG)
        self.datewise_tree.tag_configure("even", background=Colors.CARD_SECONDARY)
    
    def create_subjectwise_tab(self):
        """
        Create tab showing attendance records grouped by subject/course.
        Displays all attendance entries organized by subject.
        """
        subjectwise_frame = ttk.Frame(self.notebook)
        self.notebook.add(subjectwise_frame, text="Subject-wise Attendance")
        
        # Title label
        title_label = ttk.Label(
            subjectwise_frame,
            text="Attendance by Subject",
            font=Fonts.HEADING_SMALL
        )
        title_label.pack(pady=Spacing.MD)
        
        # Display frame with scrollbar
        display_frame = ttk.Frame(subjectwise_frame)
        display_frame.pack(padx=Spacing.LG, pady=Spacing.MD, fill=tk.BOTH, expand=True)
        
        # Treeview for subject-wise attendance
        columns = ("Subject", "Course Code", "Date", "Time", "Session Type", "Status", "Location")
        self.subjectwise_tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=20)
        
        # Configure column headings
        for col in columns:
            self.subjectwise_tree.heading(col, text=col)
            self.subjectwise_tree.column(col, width=140, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.subjectwise_tree.yview)
        self.subjectwise_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.subjectwise_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.subjectwise_tree.tag_configure("odd", background=Colors.CARD_BG)
        self.subjectwise_tree.tag_configure("even", background=Colors.CARD_SECONDARY)
    
    def load_attendance(self):
        """
        Load attendance records for the logged-in student.
        Fetches data from database and restricts access to only this student.
        Updates all tabs with attendance information.
        """
        try:
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query attendance records for this student only
            # JOIN with class_sessions to get session information
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
            """, (self.student_id,))
            
            records = cursor.fetchall()
            conn.close()
            
            # Process and display attendance data
            self.display_attendance_summary(records)
            self.display_datewise_attendance(records)
            self.display_subjectwise_attendance(records)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance: {str(e)}")
    
    def display_attendance_summary(self, records):
        """
        Calculate and display attendance summary statistics.
        
        Args:
            records (list): List of attendance records from database
        """
        # Clear existing data
        for item in self.subject_percent_tree.get_children():
            self.subject_percent_tree.delete(item)
        
        if not records:
            # No attendance records
            self.total_sessions_label.config(text="Total Sessions Attended: 0")
            self.present_count_label.config(text="Present: 0")
            self.late_count_label.config(text="Late: 0")
            self.absent_count_label.config(text="Absent: 0")
            self.overall_percentage_label.config(text="Overall Attendance: 0%")
            return
        
        # Calculate overall statistics
        total_sessions = len(records)
        present_count = sum(1 for r in records if r['attendance_status'] == 'present')
        late_count = sum(1 for r in records if r['attendance_status'] == 'late')
        absent_count = sum(1 for r in records if r['attendance_status'] == 'absent')
        
        # Calculate overall percentage (present / total)
        overall_percentage = (present_count / total_sessions * 100) if total_sessions > 0 else 0
        
        # Update summary labels
        self.total_sessions_label.config(text=f"Total Sessions Attended: {total_sessions}")
        self.present_count_label.config(text=f"Present: {present_count}")
        self.late_count_label.config(text=f"Late: {late_count}")
        self.absent_count_label.config(text=f"Absent: {absent_count}")
        self.overall_percentage_label.config(
            text=f"Overall Attendance: {overall_percentage:.2f}%"
        )
        
        # Calculate subject-wise statistics
        # Group records by subject
        subject_stats = defaultdict(lambda: {'total': 0, 'present': 0, 'late': 0, 'absent':0, 'course_code': ''})
        
        for record in records:
            subject_name = record['subject_name']
            course_code = record['course_code']
            
            subject_stats[subject_name]['total'] += 1
            subject_stats[subject_name]['course_code'] = course_code
            
            if record['attendance_status'] == 'present':
                subject_stats[subject_name]['present'] += 1
            elif record['attendance_status'] == 'late':
                subject_stats[subject_name]['late'] += 1
            elif record['attendance_status'] == 'absent':
                subject_stats[subject_name]['absent'] += 1    
        
        # Display subject-wise percentages in treeview
        for index, (subject_name, stats) in enumerate(sorted(subject_stats.items())):
            percentage = (stats['present'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            tag = "even" if index % 2 == 0 else "odd"
            self.subject_percent_tree.insert(
                "",
                "end",
                values=(
                    subject_name,
                    stats['course_code'],
                    stats['total'],
                    stats['present'],
                    stats['late'],
                    f"{percentage:.2f}%",
                ),
                tags=(tag,),
            )
    
    def display_datewise_attendance(self, records):
        """
        Display attendance records grouped by date.
        
        Args:
            records (list): List of attendance records from database
        """
        # Clear existing data
        for item in self.datewise_tree.get_children():
            self.datewise_tree.delete(item)
        
        # Display all records sorted by date (already sorted in query)
        for index, record in enumerate(records):
            # Extract values from Row object using dictionary-style access
            attendance_date = record['attendance_date']
            attendance_time = record['attendance_time']
            attendance_status = record['attendance_status']
            subject_code = record['subject_code']
            subject_name = record['subject_name']
            session_type = record['session_type']
            location = record['location'] if record['location'] else "N/A"
            
            tag = "even" if index % 2 == 0 else "odd"
            self.datewise_tree.insert(
                "",
                "end",
                values=(
                    attendance_date,
                    attendance_time,
                    subject_name,
                    subject_code,
                    session_type,
                    attendance_status,
                    location,
                ),
                tags=(tag,),
            )
        
        if len(records) == 0:
            self.datewise_tree.insert("", "end", values=("No attendance records", "", "", "", "", "", ""))
    
    def display_subjectwise_attendance(self, records):
        """
        Display attendance records grouped by subject.
        
        Args:
            records (list): List of attendance records from database
        """
        # Clear existing data
        for item in self.subjectwise_tree.get_children():
            self.subjectwise_tree.delete(item)
        
        # Sort records by subject name, then by date
        sorted_records = sorted(
            records,
            key=lambda r: (r['subject_name'], r['attendance_date'], r['attendance_time'])
        )
        
        # Display records grouped by subject
        for index, record in enumerate(sorted_records):
            # Extract values from Row object using dictionary-style access
            attendance_date = record['attendance_date']
            attendance_time = record['attendance_time']
            attendance_status = record['attendance_status']
            subject_code = record['subject_code']
            subject_name = record['subject_name']
            session_type = record['session_type']
            location = record['location'] if record['location'] else "N/A"
            
            tag = "even" if index % 2 == 0 else "odd"
            self.subjectwise_tree.insert(
                "",
                "end",
                values=(
                    subject_name,
                    subject_code,
                    attendance_date,
                    attendance_time,
                    session_type,
                    attendance_status,
                    location,
                ),
                tags=(tag,),
            )
        
        if len(records) == 0:
            self.subjectwise_tree.insert("", "end", values=("No attendance records", "", "", "", "", "", ""))
    
    def logout(self):
        """Logout and return to login screen."""
        response = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if response:
            self.root.quit()


def main():
    """
    Main function to run the Student Dashboard application.
    Handles login and dashboard window management.
    """
    # Create root window for login
    login_root = tk.Tk()
    login_app = LoginWindow(login_root)
    login_root.mainloop()
    
    # Check if login was successful
    if login_app.student_info:
        # Close login window
        login_root.destroy()
        
        # Create root window for dashboard
        dashboard_root = tk.Tk()
        dashboard_app = StudentDashboard(dashboard_root, login_app.student_info)
        dashboard_root.mainloop()
    else:
        # Login was cancelled or failed
        login_root.destroy()


if __name__ == "__main__":
    main()
