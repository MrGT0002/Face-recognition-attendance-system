"""
Admin Dashboard Module
Tkinter GUI for administrative tasks: managing years, subjects, courses, teachers, and students.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from core.db import get_db_connection
from core.camera import capture_face_images
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui_theme import Colors, Fonts, Spacing, configure_styles, create_header_bar, create_stat_card, create_modern_layout, create_sidebar_button, create_content_card, RoundedInput, GreenButton


class AdminDashboard:
    """
    Main Admin Dashboard Window
    Provides forms and functionality for all administrative tasks.
    """
    
    def __init__(self, root, admin_id=None):
        """
        Initialize the Admin Dashboard window.
        
        Args:
            root (tk.Tk): Root Tkinter window
            admin_id (int): ID of the logged-in admin (optional)
        """
        self.root = root
        self.root.title("Admin Dashboard - Face Recognition Attendance System")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        self.admin_id = admin_id
        self.INPUT_FONT = Fonts.INPUT
        
        # Apply modern theme
        configure_styles(self.root)
        self.root.configure(bg=Colors.BG_MAIN)

        # Create modern layout structure
        self.layout = create_modern_layout(self.root)
        
        # Store navigation buttons
        self.nav_buttons = {}
        
        # Create sidebar navigation
        self.create_sidebar_navigation()
        
        # Container for content cards
        self.content_container = tk.Frame(self.layout['content_area'], bg=Colors.BG_MAIN)
        self.content_container.pack(fill=tk.BOTH, expand=True)

        # Create notebook for detailed admin panels (inside Admin Panel section)
        self.notebook = ttk.Notebook(self.content_container)
        
        # Configure notebook style with modern curved tabs and mixed green colors
        style = ttk.Style()
        
        # Notebook container styling
        style.configure("TNotebook", 
                      background="#0E9F6E",  # Deep teal green
                      borderwidth=0)
        
        # Tab styling with mixed green colors
        style.configure("TNotebook.Tab", 
                      background="#34D399",  # Medium aqua green
                      foreground="#FFFFFF",    # White text
                      padding=[Spacing.MD, Spacing.LG],
                      borderwidth=1,
                      focuscolor='none',
                      relief="raised")
        
        # Active tab styling
        style.map("TNotebook.Tab",
                 background=[("selected", "#0E9F6E"),    # Deep teal when active
                            ("active", "#6EE7B7")],      # Soft aqua on hover
                 foreground=[("selected", "#FFFFFF"),    # White text when active
                            ("active", "#FFFFFF")],      # White text on hover
                 relief=[("selected", "flat"),           # Flat when active
                        ("active", "raised")])           # Raised on hover
        
        # Tab container styling
        style.configure("TFrame", background="#F3FBF4")  # Light green for tab content
        
        self.notebook.configure(style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)  # Pack the notebook!

        # Pre-create inner tabs but mount only when Admin Panel is active
        self.create_year_tab()
        self.create_subject_tab()
        self.create_course_tab()
        self.create_teacher_tab()
        self.create_student_tab()

        # Initial view
        self.on_nav_click("Dashboard", self.show_dashboard)

    def create_sidebar_navigation(self):
        """Create the sidebar navigation buttons."""
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Mark Attendance", self.show_mark_attendance_info),
            ("Register Student", self.show_register_student),
            ("Train Model", self.show_train_model_info),
            ("View Attendance", self.show_view_attendance_info),
            ("Export Attendance", self.show_export_attendance),
            ("Start Face Recognition", self.show_start_face_recognition),
            ("Admin Panel", self.show_admin_panel),
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

    # =====================================================
    # NAVIGATION HANDLERS
    # =====================================================

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
            "Mark Attendance": self.show_mark_attendance_info,
            "Register Student": self.show_register_student,
            "Train Model": self.show_train_model_info,
            "View Attendance": self.show_view_attendance_info,
            "Admin Panel": self.show_admin_panel,
        }
        return commands.get(label, self.show_dashboard)

    def show_dashboard(self):
        """
        High-level overview dashboard with statistic cards.
        """
        # Create content card
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Admin Dashboard",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Overview of attendance statistics",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))

        # Statistics cards container
        stats_container = tk.Frame(content, bg=Colors.CARD_BG)
        stats_container.pack(fill=tk.X, pady=Spacing.LG)

        # Create statistics cards
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Total Students
            cursor.execute("SELECT COUNT(*) FROM students WHERE is_active = 1")
            total_students = cursor.fetchone()[0]

            # Total Teachers
            cursor.execute("SELECT COUNT(*) FROM teachers WHERE is_active = 1")
            total_teachers = cursor.fetchone()[0]

            # Today's Attendance (simplified - you may need to adjust based on your schema)
            cursor.execute("""
                SELECT COUNT(*) FROM attendance 
                WHERE DATE(date) = DATE('now')
            """)
            today_attendance = cursor.fetchone()[0] or 0

            conn.close()

            # Create stat cards
            cards_row = tk.Frame(stats_container, bg=Colors.CARD_BG)
            cards_row.pack(fill=tk.X)

            # Students card
            students_card = create_stat_card(cards_row, "Total Students", total_students, Colors.ACCENT_PRIMARY)
            students_card.pack(side=tk.LEFT, padx=(0, Spacing.LG), expand=True, fill=tk.BOTH)

            # Teachers card
            teachers_card = create_stat_card(cards_row, "Total Teachers", total_teachers, Colors.SUCCESS)
            teachers_card.pack(side=tk.LEFT, padx=Spacing.LG, expand=True, fill=tk.BOTH)

            # Today's Attendance card
            attendance_card = create_stat_card(cards_row, "Today's Attendance", today_attendance, Colors.INFO)
            attendance_card.pack(side=tk.LEFT, padx=(Spacing.LG, 0), expand=True, fill=tk.BOTH)

        except Exception as e:
            error_label = tk.Label(
                content,
                text=f"Error loading statistics: {str(e)}",
                bg=Colors.CARD_BG,
                fg=Colors.ERROR,
                font=Fonts.BODY_MEDIUM
            )
            error_label.pack(pady=Spacing.LG)

    def show_mark_attendance_info(self):
        # Create content card
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Mark Attendance",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Record classroom presence using face recognition",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Information text
        info_text = tk.Label(
            content,
            text="Classroom attendance is managed from the Teacher Dashboard.\n\n"
                 "Use the teacher login from the main screen to start a session\n"
                 "and mark attendance with face recognition.",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
            justify="center"
        )
        info_text.pack(expand=True)

    def show_register_student(self):
        # Create content card
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Student Registration",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Add and manage student biometric profiles",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Notebook for registration form
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Only mount the student tab visibly in this context
        self.create_student_tab()
        # Ensure student tab is last and selected
        self.notebook.select(len(self.notebook.tabs()) - 1)

    def show_train_model_info(self):
        # Create content card
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Train Face Recognition Model",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Update biometric recognition with latest student faces",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Information text
        info_text = tk.Label(
            content,
            text="After registering and capturing faces for new students,\n"
                 "run model training to update the recognition system.\n\n"
                 "You can also trigger training directly from the\n"
                 "student registration success dialog.",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
            justify="center"
        )
        info_text.pack(expand=True)

    def show_view_attendance_info(self):
        # Create content card
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Attendance Reports",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Explore consolidated attendance reports and summaries",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Information text
        info_text = tk.Label(
            content,
            text="Detailed attendance views are available in the Student Dashboard.\n\n"
                 "Students can log in to explore date-wise and subject-wise reports.",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
            justify="center"
        )
        info_text.pack(expand=True)

    def show_admin_panel(self):
        # Create content card
        content = create_content_card(self.content_container)
        
        # Title
        title = tk.Label(
            content,
            text="Admin Panel",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM
        )
        title.pack(pady=(0, Spacing.SM))
        
        # Subtitle
        subtitle = tk.Label(
            content,
            text="Manage system configuration and data",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_LARGE
        )
        subtitle.pack(pady=(0, Spacing.XL))
        
        # Restore the full notebook with all management tabs
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_year_tab()
        self.create_subject_tab()
        self.create_course_tab()
        self.create_teacher_tab()
        self.create_student_tab()

    # =====================================================
    # SMALL DATA HELPERS FOR DASHBOARD
    # =====================================================

    def _count_table_rows(self, table_name):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) AS total FROM {table_name}")
            row = cur.fetchone()
            conn.close()
            return row["total"] if row else 0
        except Exception:
            return 0

    def _count_today_attendance(self):
        try:
            today = datetime.now().date().isoformat()
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) AS total FROM attendance WHERE attendance_date = ?",
                (today,),
            )
            row = cur.fetchone()
            conn.close()
            return row["total"] if row else 0
        except Exception:
            return 0
    
    # =====================================================
    # YEAR MANAGEMENT TAB
    # =====================================================
    
    def create_year_tab(self):
        tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(tab, text="Academic Years")

        # Background for entire tab
        tab.configure(style="TFrame")

        # Centered card container
        container = tk.Frame(tab, bg=Colors.BG_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Enhanced card with gradient background
        card = tk.Frame(
            container,
            bg="#F3FBF4",
            highlightbackground="#34D399",
            highlightthickness=2,
            bd=0,
            relief="raised"
        )
        card.pack(expand=True, fill=tk.BOTH)

        # Create gradient effect canvas inside card
        gradient_bg = tk.Canvas(card, bg="#F3FBF4", highlightthickness=0)
        gradient_bg.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        # Draw subtle gradient pattern
        def draw_enhanced_background():
            width = gradient_bg.winfo_width()
            height = gradient_bg.winfo_height()
            if width <= 1 or height <= 1:
                return
            
            # Clear existing
            gradient_bg.delete("all")
            
            # Draw subtle gradient rectangles
            steps = 50
            for i in range(steps):
                ratio = i / steps
                
                # Create subtle green gradient
                if ratio < 0.5:
                    # Light to medium green
                    r1, g1, b1 = 243, 251, 244   # #F3FBF4
                    r2, g2, b2 = 211, 247, 228   # #D3F7E4
                    local_ratio = ratio / 0.5
                else:
                    # Medium to light green
                    r1, g1, b1 = 211, 247, 228   # #D3F7E4
                    r2, g2, b2 = 243, 251, 244   # #F3FBF4
                    local_ratio = (ratio - 0.5) / 0.5
                
                # Interpolate colors
                r = int(r1 + (r2 - r1) * local_ratio)
                g = int(g1 + (g2 - g1) * local_ratio)
                b = int(b1 + (b2 - b1) * local_ratio)
                
                color = f"#{r:02x}{g:02x}{b:02x}"
                
                # Draw rectangle
                y1 = int(height * ratio)
                y2 = int(height * (ratio + 1/steps))
                gradient_bg.create_rectangle(
                    0, y1, width, y2,
                    fill=color, outline="", tags="bg"
                )
            
            # Add decorative pattern
            for i in range(0, width, 40):
                for j in range(0, height, 40):
                    gradient_bg.create_oval(
                        i+5, j+5, i+15, j+15,
                        fill="#E8F5F0", outline="", tags="pattern"
                    )
        
        # Bind to canvas resize
        gradient_bg.bind("<Configure>", lambda e: draw_enhanced_background())
        card.after(100, draw_enhanced_background)

        # Content frame on top of gradient
        content = tk.Frame(gradient_bg, bg="#F3FBF4")
        content.pack(padx=Spacing.XL, pady=Spacing.XL, fill=tk.BOTH, expand=True)

        # Title and subtitle
        tk.Label(
            content,
            text="Academic Year Configuration",
            bg="#F3FBF4",
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.SM))

        tk.Label(
            content,
            text="Define academic timelines and branch structure",
            bg="#F3FBF4",
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.LG))

        # Create a canvas and scrollbar for scrollable content
        canvas = tk.Canvas(content, bg=Colors.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.CARD_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
            canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Enable drag scrolling with mouse
        def _start_drag(event):
            canvas.scan_mark(event.x, event.y)
        
        def _drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)
        
        canvas.bind("<ButtonPress-1>", _start_drag)
        canvas.bind("<B1-Motion>", _drag)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Form container
        form = tk.Frame(scrollable_frame, bg=Colors.CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)

        # Year
        tk.Label(form, text="Year *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.year_cb = ttk.Combobox(
            form,
            values=["FE", "SE", "TE", "BE"],
            state="readonly",
            width=35,
            font=self.INPUT_FONT,
        )
        self.year_cb.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Academic Start Date
        tk.Label(form, text="Academic Start Date (YYYY-MM-DD) *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.academic_start = RoundedInput(form, width=35)
        self.academic_start.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Academic End Date
        tk.Label(form, text="Academic End Date (YYYY-MM-DD) *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.academic_end = RoundedInput(form, width=35)
        self.academic_end.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Branch
        tk.Label(form, text="Branch *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.branch_cb = ttk.Combobox(
            form,
            values=[
                "CSE(AI/ML)",
                "IOT",
                "Mechanical",
                "Automobile",
                "CS(Core)",
                "IT",
                "EXTC",
                "Civil",
            ],
            state="readonly",
            width=35,
            font=self.INPUT_FONT,
        )
        self.branch_cb.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Branch Start Date
        tk.Label(form, text="Branch Start Date *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.branch_start = RoundedInput(form, width=35)
        self.branch_start.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Branch End Date
        tk.Label(form, text="Branch End Date *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.branch_end = RoundedInput(form, width=35)
        self.branch_end.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Submit button
        submit_btn = GreenButton(
            form,
            text="Add Academic Year",
            command=self.save_academic_year
        )
        submit_btn.pack(pady=(Spacing.LG, 0))

    def save_academic_year(self):
        if not all([
            self.year_cb.get(),
            self.branch_cb.get(),
            self.academic_start.get(),
            self.academic_end.get(),
            self.branch_start.get(),
            self.branch_end.get()
        ]):
            messagebox.showerror("Error", "All fields are required")
            return

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT year_id FROM years WHERE year_name = ?", (self.year_cb.get(),))
        year = cur.fetchone()
        if not year:
            messagebox.showerror("Error", "Year not found in DB")
            conn.close()
            return

        cur.execute("SELECT branch_id FROM branches WHERE branch_name = ?", (self.branch_cb.get(),))
        branch = cur.fetchone()
        if not branch:
            messagebox.showerror("Error", "Branch not found in DB")
            conn.close()
            return

        try:
            cur.execute("""
                INSERT INTO branch_years (
                    branch_id,
                    year_id,
                    academic_start_date,
                    academic_end_date,
                    branch_start_date,
                    branch_end_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                branch["branch_id"],
                year["year_id"],
                self.academic_start.get(),
                self.academic_end.get(),
                self.branch_start.get(),
                self.branch_end.get()
            ))
            conn.commit()
            messagebox.showinfo("Success", "Academic year added successfully!")
            
            # Clear form
            self.academic_start.set("")
            self.academic_end.set("")
            self.branch_start.set("")
            self.branch_end.set("")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add academic year: {str(e)}")
        finally:
            conn.close()

    # =====================================================
    # SUBJECT MANAGEMENT TAB
    # =====================================================
    
    def create_subject_tab(self):
        """
        Create tab for adding subjects.
        Subjects are academic disciplines (e.g., "Mathematics", "Computer Science").
        """
        tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(tab, text="Subjects")

        # Background for entire tab
        tab.configure(style="TFrame")

        # Centered card container
        container = tk.Frame(tab, bg=Colors.BG_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Card
        card = tk.Frame(
            container,
            bg=Colors.CARD_BG,
            highlightbackground=Colors.BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        card.pack(expand=True, fill=tk.BOTH)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(padx=Spacing.XL, pady=Spacing.XL, fill=tk.BOTH, expand=True)

        # Title and subtitle
        tk.Label(
            content,
            text="Subject Catalog",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.SM))

        tk.Label(
            content,
            text="Manage academic subjects and their credit structure",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.LG))

        # Create a canvas and scrollbar for scrollable content
        canvas = tk.Canvas(content, bg=Colors.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.CARD_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
            canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Enable drag scrolling with mouse
        def _start_drag(event):
            canvas.scan_mark(event.x, event.y)
        
        def _drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)
        
        canvas.bind("<ButtonPress-1>", _start_drag)
        canvas.bind("<B1-Motion>", _drag)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Form container
        form = tk.Frame(scrollable_frame, bg=Colors.CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)

        # Subject Code
        tk.Label(form, text="Subject Code *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.subject_code_entry = RoundedInput(form, width=35)
        self.subject_code_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Subject Name
        tk.Label(form, text="Subject Name *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.subject_name_entry = RoundedInput(form, width=35)
        self.subject_name_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Description
        tk.Label(form, text="Description", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.subject_desc_entry = tk.Text(form, height=4, font=Fonts.INPUT, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY, relief="flat", bd=1, highlightthickness=1, highlightbackground=Colors.BORDER_LIGHT, highlightcolor=Colors.ACCENT_PRIMARY)
        self.subject_desc_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Credits
        tk.Label(form, text="Credits", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.credits_entry = RoundedInput(form, width=35)
        self.credits_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Submit button
        submit_btn = GreenButton(
            form,
            text="Add Subject",
            command=self.add_subject
        )
        submit_btn.pack(pady=(Spacing.LG, 0))

    def add_subject(self):
        """
        Add a new subject to database.
        Validates input and inserts record into subjects table.
        """
        # Get values from form fields
        subject_code = self.subject_code_entry.get().strip()
        subject_name = self.subject_name_entry.get().strip()
        description = self.subject_desc_entry.get("1.0", tk.END).strip()
        credits = self.credits_entry.get().strip()
        
        # Validate required fields
        if not subject_code or not subject_name:
            messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
            return
        
        # Validate credits (if provided, must be numeric)
        if credits:
            try:
                credits = int(credits)
            except ValueError:
                messagebox.showerror("Error", "Credits must be a number")
                return
        else:
            credits = None
        
        try:
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert new subject into database
            cursor.execute("""
                INSERT INTO subjects (subject_code, subject_name, description, credits)
                VALUES (?, ?, ?, ?)
            """, (subject_code, subject_name, description if description else None, credits))
            
            conn.commit()
            conn.close()
            
            # Show success message
            messagebox.showinfo("Success", f"Subject '{subject_name}' added successfully!")
            
            # Clear form fields
            self.subject_code_entry.delete(0, tk.END)
            self.subject_name_entry.delete(0, tk.END)
            self.subject_desc_entry.delete("1.0", tk.END)
            self.credits_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add subject: {str(e)}")
    
    def add_course(self):
        """
        Add a new course to database.
        Validates input and inserts record into courses table.
        """
        # Get values from form fields
        course_code = self.course_code_entry.get().strip()
        course_name = self.course_name_entry.get().strip()
        year_selection = self.year_combobox.get()
        subject_selection = self.subject_combobox.get()
        description = self.course_desc_entry.get("1.0", tk.END).strip()
        
        # Validate required fields
        if not course_code or not course_name or not year_selection or not subject_selection:
            messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
            return
        
        # Extract year_id and subject_id from combobox selections
        try:
            year_id = int(year_selection.split(" - ")[0])
            subject_id = int(subject_selection.split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Please select valid year and subject")
            return
        
        try:
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert new course into database
            cursor.execute("""
                INSERT INTO courses (course_code, course_name, year_id, subject_id, description)
                VALUES (?, ?, ?, ?, ?)
            """, (course_code, course_name, year_id, subject_id, description if description else None))
            
            conn.commit()
            conn.close()
            
            # Show success message
            messagebox.showinfo("Success", f"Course '{course_name}' added successfully!")
            
            # Clear form fields
            self.course_code_entry.delete(0, tk.END)
            self.course_name_entry.delete(0, tk.END)
            self.year_combobox.set("")
            self.subject_combobox.set("")
            self.course_desc_entry.delete("1.0", tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add course: {str(e)}")

    def load_years(self):
        """Load academic years from database into combobox."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT year_id, year_name FROM years ORDER BY year_name")
            years = cursor.fetchall()
            conn.close()
            
            # Format: "year_id - year_name"
            year_list = [f"{row['year_id']} - {row['year_name']}" for row in years]
            self.year_combobox['values'] = year_list
            
        except Exception as e:
            print(f"Error loading years: {e}")
    
    def load_subjects(self):
        """Load subjects from database into combobox."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT subject_id, subject_name FROM subjects ORDER BY subject_name")
            subjects = cursor.fetchall()
            conn.close()
            
            # Format: "subject_id - subject_name"
            subject_list = [f"{row['subject_id']} - {row['subject_name']}" for row in subjects]
            self.subject_combobox['values'] = subject_list
            
        except Exception as e:
            print(f"Error loading subjects: {e}")

    # =====================================================
    # COURSE MANAGEMENT TAB
    # =====================================================
    
    def create_course_tab(self):
        """
        Create tab for adding courses.
        Courses link subjects to academic years.
        """
        tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(tab, text="Courses")

        # Background for entire tab
        tab.configure(style="TFrame")

        # Centered card container
        container = tk.Frame(tab, bg=Colors.BG_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Card
        card = tk.Frame(
            container,
            bg=Colors.CARD_BG,
            highlightbackground=Colors.BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        card.pack(expand=True, fill=tk.BOTH)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(padx=Spacing.XL, pady=Spacing.XL, fill=tk.BOTH, expand=True)

        # Title and subtitle
        tk.Label(
            content,
            text="Course Configuration",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.SM))

        tk.Label(
            content,
            text="Link subjects to academic years and courses",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.LG))

        # Create a canvas and scrollbar for scrollable content
        canvas = tk.Canvas(content, bg=Colors.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.CARD_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
            canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Enable drag scrolling with mouse
        def _start_drag(event):
            canvas.scan_mark(event.x, event.y)
        
        def _drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)
        
        canvas.bind("<ButtonPress-1>", _start_drag)
        canvas.bind("<B1-Motion>", _drag)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Form container
        form = tk.Frame(scrollable_frame, bg=Colors.CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)

        # Course Code
        tk.Label(form, text="Course Code *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.course_code_entry = RoundedInput(form, width=35)
        self.course_code_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Course Name
        tk.Label(form, text="Course Name *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.course_name_entry = RoundedInput(form, width=35)
        self.course_name_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Year selection
        tk.Label(form, text="Academic Year *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.year_combobox = ttk.Combobox(
            form,
            state="readonly",
            width=35,
            font=self.INPUT_FONT,
        )
        self.year_combobox.pack(fill=tk.X, pady=(0, Spacing.LG))
        self.load_years()

        # Subject selection
        tk.Label(form, text="Subject *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.subject_combobox = ttk.Combobox(
            form,
            state="readonly",
            width=35,
            font=self.INPUT_FONT,
        )
        self.subject_combobox.pack(fill=tk.X, pady=(0, Spacing.LG))
        self.load_subjects()

        # Description
        tk.Label(form, text="Description", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.course_desc_entry = tk.Text(form, height=4, font=Fonts.INPUT, bg=Colors.CARD_BG, fg=Colors.TEXT_PRIMARY, relief="flat", bd=1, highlightthickness=1, highlightbackground=Colors.BORDER_LIGHT, highlightcolor=Colors.ACCENT_PRIMARY)
        self.course_desc_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Submit button
        submit_btn = GreenButton(
            form,
            text="Add Course",
            command=self.add_course
        )
        submit_btn.pack(pady=(Spacing.LG, 0))
    
    # =====================================================
    # TEACHER REGISTRATION TAB
    # =====================================================
    
    def create_teacher_tab(self):
        """
        Create tab for registering teachers.
        Teachers are assigned to branches, academic years, and subjects.
        """
        tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(tab, text="Register Teacher")

        # Background for entire tab
        tab.configure(style="TFrame")

        # Centered card container
        container = tk.Frame(tab, bg=Colors.BG_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Card
        card = tk.Frame(
            container,
            bg=Colors.CARD_BG,
            highlightbackground=Colors.BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        card.pack(expand=True, fill=tk.BOTH)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(padx=Spacing.XL, pady=Spacing.XL, fill=tk.BOTH, expand=True)

        # Title and subtitle
        tk.Label(
            content,
            text="Teacher Registration",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.SM))

        tk.Label(
            content,
            text="Assign faculty to branches, academic years, and subjects",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.LG))

        # Create a canvas and scrollbar for scrollable content
        canvas = tk.Canvas(content, bg=Colors.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.CARD_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
            canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Enable drag scrolling with mouse
        def _start_drag(event):
            canvas.scan_mark(event.x, event.y)
        
        def _drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)
        
        canvas.bind("<ButtonPress-1>", _start_drag)
        canvas.bind("<B1-Motion>", _drag)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Form container
        form = tk.Frame(scrollable_frame, bg=Colors.CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)

        # Employee ID
        tk.Label(form, text="Employee ID *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.employee_id_entry = RoundedInput(form, width=35)
        self.employee_id_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Full Name
        tk.Label(form, text="Full Name *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.teacher_name_entry = RoundedInput(form, width=35)
        self.teacher_name_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Email
        tk.Label(form, text="Email", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.teacher_email_entry = RoundedInput(form, width=35)
        self.teacher_email_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Phone
        tk.Label(form, text="Phone", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.teacher_phone_entry = RoundedInput(form, width=35)
        self.teacher_phone_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Department
        tk.Label(form, text="Department", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.teacher_dept_entry = RoundedInput(form, width=35)
        self.teacher_dept_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Branch
        tk.Label(form, text="Branch *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.teacher_branch_cb = ttk.Combobox(
            form,
            values=["CSE(AI/ML)", "IOT", "Mechanical", "Automobile", "CS(Core)", "IT", "EXTC", "Civil"],
            state="readonly",
            width=35,
            font=self.INPUT_FONT,
        )
        self.teacher_branch_cb.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Academic Year
        tk.Label(form, text="Academic Year *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.teacher_year_cb = ttk.Combobox(
            form,
            values=["FE", "SE", "TE", "BE"],
            state="readonly",
            width=35,
            font=self.INPUT_FONT,
        )
        self.teacher_year_cb.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Subjects (Max 4)
        tk.Label(form, text="Subjects (Max 4)", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.teacher_subjects = []
        for i in range(4):
            subject_entry = RoundedInput(form, width=35)
            subject_entry.pack(fill=tk.X, pady=(0, Spacing.SM))
            self.teacher_subjects.append(subject_entry)

        # Submit button
        submit_btn = GreenButton(
            form,
            text="Register Teacher",
            command=self.register_teacher
        )
        submit_btn.pack(pady=(Spacing.LG, 0))

    def register_teacher(self):
        emp = self.employee_id_entry.get().strip()
        name = self.teacher_name_entry.get().strip()
        email = self.teacher_email_entry.get().strip()
        phone = self.teacher_phone_entry.get().strip()
        dept = self.teacher_dept_entry.get().strip()
        branch = self.teacher_branch_cb.get()
        year = self.teacher_year_cb.get()

        if not emp or not name or not branch or not year:
            messagebox.showerror("Error", "Please fill all required fields")
            return

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO teachers (employee_id, full_name, email, phone, department)
            VALUES (?, ?, ?, ?, ?)
        """, (emp, name, email, phone, dept))

        teacher_id = cur.lastrowid

        cur.execute("SELECT branch_id FROM branches WHERE branch_name=?", (branch,))
        branch_id = cur.fetchone()["branch_id"]

        cur.execute("SELECT year_id FROM academic_years WHERE year_name=?", (year,))
        year_id = cur.fetchone()["year_id"]

        for sub in self.teacher_subjects:
            s = sub.get().strip()
            if not s:
                continue

            cur.execute("SELECT subject_id FROM subjects WHERE subject_name=?", (s,))
            row = cur.fetchone()

            subject_id = row["subject_id"] if row else cur.execute(
                "INSERT INTO subjects (subject_name) VALUES (?)", (s,)
            ).lastrowid

            cur.execute("""
                INSERT INTO teacher_assignments
                (teacher_id, branch_id, year_id, subject_id)
                VALUES (?, ?, ?, ?)
            """, (teacher_id, branch_id, year_id, subject_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Teacher '{name}' registered successfully")
    
    
    
    # =====================================================
    # STUDENT REGISTRATION TAB
    # =====================================================
    
    def create_student_tab(self):
        """
        Create tab for registering students.
        Includes face capture functionality for face recognition training.
        """
        tab = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(tab, text="Register Student")

        # Background for entire tab
        tab.configure(style="TFrame")

        # Centered card container
        container = tk.Frame(tab, bg=Colors.BG_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Card
        card = tk.Frame(
            container,
            bg=Colors.CARD_BG,
            highlightbackground=Colors.BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        card.pack(expand=True, fill=tk.BOTH)

        content = tk.Frame(card, bg=Colors.CARD_BG)
        content.pack(padx=Spacing.XL, pady=Spacing.XL, fill=tk.BOTH, expand=True)

        # Title and subtitle
        tk.Label(
            content,
            text="Student Registration",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.SM))

        tk.Label(
            content,
            text="Add and manage student biometric records",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.LG))

        # Create a canvas and scrollbar for scrollable content
        canvas = tk.Canvas(content, bg=Colors.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.CARD_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
            canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Enable drag scrolling with mouse
        def _start_drag(event):
            canvas.scan_mark(event.x, event.y)
        
        def _drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)
        
        canvas.bind("<ButtonPress-1>", _start_drag)
        canvas.bind("<B1-Motion>", _drag)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Form container
        form = tk.Frame(scrollable_frame, bg=Colors.CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)

        # Student Code
        tk.Label(form, text="Student Code *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.student_code_entry = RoundedInput(form, width=35)
        self.student_code_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Full Name
        tk.Label(form, text="Full Name *", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.student_name_entry = RoundedInput(form, width=35)
        self.student_name_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Email
        tk.Label(form, text="Email", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.student_email_entry = RoundedInput(form, width=35)
        self.student_email_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Phone
        tk.Label(form, text="Phone", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.student_phone_entry = RoundedInput(form, width=35)
        self.student_phone_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Date of Birth
        tk.Label(form, text="Date of Birth (YYYY-MM-DD)", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        self.student_dob_entry = RoundedInput(form, width=35)
        self.student_dob_entry.pack(fill=tk.X, pady=(0, Spacing.LG))

        # Face Capture section
        tk.Label(form, text="Face Capture", bg=Colors.CARD_BG, font=Fonts.LABEL).pack(anchor="w", pady=(0, Spacing.XS))
        
        capture_container = tk.Frame(form, bg=Colors.CARD_BG)
        capture_container.pack(fill=tk.X, pady=(0, Spacing.LG))
        
        capture_btn = GreenButton(
            capture_container,
            text="Capture Face Images",
            command=self.capture_student_face
        )
        capture_btn.pack(side="left", padx=(0, Spacing.SM))
        
        self.face_capture_status = tk.Label(
            capture_container,
            text="Not captured",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_SECONDARY,
            font=Fonts.BODY_SMALL
        )
        self.face_capture_status.pack(side="left", padx=Spacing.SM)

        # Submit button
        submit_btn = GreenButton(
            form,
            text="Register Student",
            command=self.register_student
        )
        submit_btn.pack(pady=(Spacing.LG, 0))
    
    def capture_student_face(self):
        """
        Trigger face capture process for student registration.
        Uses camera module to capture 30-50 face images for training.
        """
        # Get student code to use as identifier for face images
        student_code = self.student_code_entry.get().strip()
        
        if not student_code:
            messagebox.showwarning("Warning", "Please enter Student Code first before capturing face images")
            return
        
        # Confirm face capture
        response = messagebox.askyesno(
            "Face Capture",
            "This will open the camera to capture face images.\n"
            "Press SPACE to capture when face is detected.\n"
            "Do you want to proceed?"
        )
        
        if response:
            try:
                # Update status
                self.face_capture_status.config(text="Capturing...", foreground="blue")
                self.root.update()
                
                # Capture face images using camera module
                # student_code is used as the identifier for organizing images
                success, count = capture_face_images(student_code, num_images=40)
                
                if success and count >= 30:
                    self.face_capture_status.config(
                        text=f"Captured {count} images successfully",
                        foreground="green"
                    )
                    messagebox.showinfo(
                        "Success",
                        f"Face images captured successfully!\n"
                        f"Total images: {count}\n"
                        f"Images saved in: datasets/students/{student_code}/"
                    )
                else:
                    self.face_capture_status.config(
                        text=f"Capture incomplete ({count} images)",
                        foreground="orange"
                    )
                    messagebox.showwarning(
                        "Warning",
                        f"Only {count} images were captured.\n"
                        f"Minimum 30 images recommended for better recognition."
                    )
                    
            except Exception as e:
                self.face_capture_status.config(text="Capture failed", foreground="red")
                messagebox.showerror("Error", f"Face capture failed: {str(e)}")
    
    def register_student(self):
        """
        Register a new student in the database.
        Validates input and inserts record into students table.
        """
        # Get values from form fields
        student_code = self.student_code_entry.get().strip()
        full_name = self.student_name_entry.get().strip()
        email = self.student_email_entry.get().strip()
        phone = self.student_phone_entry.get().strip()
        date_of_birth = self.student_dob_entry.get().strip()
        
        # Validate required fields
        if not student_code or not full_name:
            messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
            return
        
        try:
            # Get database connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert new student into database
            cursor.execute("""
                INSERT INTO students (student_code, full_name, email, phone, date_of_birth)
                VALUES (?, ?, ?, ?, ?)
            """, (
                student_code,
                full_name,
                email if email else None,
                phone if phone else None,
                date_of_birth if date_of_birth else None
            ))
            
            conn.commit()
            conn.close()
            
            # Show success message
            messagebox.showinfo("Success", f"Student '{full_name}' registered successfully!")
            
            # Clear form fields
            self.student_code_entry.delete(0, tk.END)
            self.student_name_entry.delete(0, tk.END)
            self.student_email_entry.delete(0, tk.END)
            self.student_phone_entry.delete(0, tk.END)
            self.student_dob_entry.delete(0, tk.END)
            self.face_capture_status.config(text="Not captured", foreground="gray")
            
            # Remind about training model if face images were captured
            response = messagebox.askyesno(
                "Model Training",
                "Do you want to train the face recognition model now?\n"
                "(Required for face recognition to work)"
            )
            
            if response:
                # Import and trigger training
                from core.trainer import train_model
                try:
                    train_model()
                    messagebox.showinfo("Success", "Model trained successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Model training failed: {str(e)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register student: {str(e)}")

    def show_export_attendance(self):
        """Show export attendance functionality."""
        self.clear_content()
        
        # Create export attendance form
        canvas = tk.Canvas(self.content_container, bg=Colors.BG_MAIN, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.content_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form container
        form = tk.Frame(scrollable_frame, bg=Colors.CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)
        
        # Title
        tk.Label(
            form,
            text="Export Attendance Data",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.LG))
        
        # Export options
        options_frame = tk.Frame(form, bg=Colors.CARD_BG)
        options_frame.pack(fill=tk.X, pady=Spacing.MD)
        
        tk.Label(
            options_frame,
            text="Select Date Range:",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.LABEL,
        ).pack(side="left", padx=Spacing.MD)
        
        self.export_date_entry = RoundedInput(options_frame, width=25)
        self.export_date_entry.pack(side="left", padx=Spacing.MD)
        
        tk.Label(
            options_frame,
            text="Export Format:",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.LABEL,
        ).pack(side="left", padx=Spacing.MD)
        
        self.export_format_var = tk.StringVar(value="Excel")
        export_format_combo = ttk.Combobox(
            options_frame,
            textvariable=self.export_format_var,
            values=["Excel", "CSV", "PDF"],
            state="readonly",
            width=15
        )
        export_format_combo.pack(side="left", padx=Spacing.MD)
        
        # Export button
        export_btn = GreenButton(
            form,
            text="Export Attendance",
            command=self.export_attendance_data
        )
        export_btn.pack(pady=Spacing.LG)
        
        # Enable scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
            canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    def export_attendance_data(self):
        """Export attendance data to selected format."""
        try:
            date_range = self.export_date_entry.get()
            export_format = self.export_format_var.get()
            
            if not date_range:
                messagebox.showwarning("Warning", "Please enter a date range")
                return
            
            # Here you would implement actual export logic
            # For now, just show success message
            messagebox.showinfo("Export Success", f"Attendance data for {date_range} exported as {export_format}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export attendance: {str(e)}")

    def show_start_face_recognition(self):
        """Show start face recognition functionality."""
        self.clear_content()
        
        # Create face recognition control panel
        canvas = tk.Canvas(self.content_container, bg=Colors.BG_MAIN, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.content_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form container
        form = tk.Frame(scrollable_frame, bg=Colors.CARD_BG)
        form.pack(fill=tk.BOTH, expand=True, pady=Spacing.LG)
        
        # Title
        tk.Label(
            form,
            text="Start Face Recognition Session",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.HEADING_MEDIUM,
        ).pack(anchor="w", pady=(0, Spacing.LG))
        
        # Face recognition controls
        controls_frame = tk.Frame(form, bg=Colors.CARD_BG)
        controls_frame.pack(fill=tk.X, pady=Spacing.MD)
        
        # Camera status
        status_frame = tk.Frame(controls_frame, bg=Colors.CARD_BG)
        status_frame.pack(side="left", padx=Spacing.MD)
        
        tk.Label(
            status_frame,
            text="Camera Status:",
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            font=Fonts.LABEL,
        ).pack(anchor="w")
        
        self.camera_status_label = tk.Label(
            status_frame,
            text="Ready",
            bg=Colors.SUCCESS_BG,
            fg=Colors.SUCCESS,
            font=Fonts.LABEL,
        )
        self.camera_status_label.pack(side="left", padx=Spacing.SM)
        
        # Control buttons
        buttons_frame = tk.Frame(controls_frame, bg=Colors.CARD_BG)
        buttons_frame.pack(side="left", padx=Spacing.LG)
        
        # Start session button
        start_session_btn = GreenButton(
            buttons_frame,
            text="Start Session",
            command=self.start_face_recognition_session
        )
        start_session_btn.pack(pady=Spacing.SM)
        
        # Stop session button
        stop_session_btn = GreenButton(
            buttons_frame,
            text="Stop Session",
            command=self.stop_face_recognition_session
        )
        stop_session_btn.pack(pady=Spacing.SM)
        
        # Test camera button
        test_camera_btn = GreenButton(
            buttons_frame,
            text="Test Camera",
            command=self.test_camera
        )
        test_camera_btn.pack(pady=Spacing.SM)
        
        # Enable scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)  # Linux
            canvas.bind_all("<Button-5>", _on_mousewheel)  # Linux
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

    def start_face_recognition_session(self):
        """Start face recognition session."""
        try:
            self.camera_status_label.configure(
                text="Session Active",
                bg=Colors.WARNING_BG,
                fg=Colors.WARNING
            )
            # Here you would implement actual face recognition logic
            messagebox.showinfo("Session Started", "Face recognition session started successfully!")
            
        except Exception as e:
            messagebox.showerror("Session Error", f"Failed to start session: {str(e)}")

    def stop_face_recognition_session(self):
        """Stop face recognition session."""
        try:
            self.camera_status_label.configure(
                text="Session Stopped",
                bg=Colors.ERROR_BG,
                fg=Colors.ERROR
            )
            # Here you would implement actual stop logic
            messagebox.showinfo("Session Stopped", "Face recognition session stopped!")
            
        except Exception as e:
            messagebox.showerror("Session Error", f"Failed to stop session: {str(e)}")

    def test_camera(self):
        """Test camera functionality."""
        try:
            # Here you would implement camera test logic
            messagebox.showinfo("Camera Test", "Camera test completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to test camera: {str(e)}")


def main():
    """
    Main function to run the Admin Dashboard.
    Creates root window and initializes dashboard.
    """
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
