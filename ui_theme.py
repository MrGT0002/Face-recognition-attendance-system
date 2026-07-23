"""
Modern UI Theme Configuration
Premium, soft green academic dashboard styling for Face Recognition Attendance System.
"""

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    CTK_AVAILABLE = False

import tkinter as tk

def apply_gradient(parent, color1="#0F766E", color2="#6EE7B7"):
    canvas = tk.Canvas(parent, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)

    def draw_gradient(event=None):
        canvas.delete("gradient")
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        r1, g1, b1 = 15, 118, 110   # #0F766E
        r2, g2, b2 = 110, 231, 183  # #6EE7B7

        r_ratio = (r2 - r1) / height
        g_ratio = (g2 - g1) / height
        b_ratio = (b2 - b1) / height

        for i in range(height):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr//256:02x}{ng//256:02x}{nb//256:02x}"
            canvas.create_line(0, i, width, i, tags=("gradient",), fill=color)

        canvas.lower("gradient")

    canvas.bind("<Configure>", draw_gradient)
    return canvas

# ===== COLOR PALETTE =====
class Colors:
    """
    Centralized color system.
    Modern gradient-inspired teal to green theme.
    """

    # App backgrounds (modern gradient-inspired teal to green)
    BG_MAIN = "#0E9F6E"           # Primary teal green background
    BG_DARK = "#0F766E"           # Deep teal green for depth
    BG_MEDIUM = "#34D399"         # Medium aqua green
    BG_LIGHT = "#6EE7B7"          # Soft aqua green (lightest)

    # Card backgrounds
    CARD_BG = "#FFFFFF"           # Pure white for cards
    CARD_SECONDARY = "#F7FFF8"    # Very light green for secondary sections

    # Text colors
    TEXT_PRIMARY = "#1F2D1F"      # Deep greenish gray
    TEXT_SECONDARY = "#5F6F5F"    # Softer secondary
    TEXT_LIGHT = "#FFFFFF"        # On primary green
    TEXT_MUTED = "#9EAA9E"        # Muted/supporting

    # Primary & secondary accents
    ACCENT_PRIMARY = "#5DBB63"    # Soft light green
    ACCENT_HOVER = "#4AA954"      # Slightly darker green on hover
    ACCENT_LIGHT = "#A8E6A3"      # Pastel green
    ACCENT_BG = "#E3F9E5"         # Very light accent background

    # Status colors (soft)
    SUCCESS = "#5DBB63"
    SUCCESS_BG = "#E3F9E5"
    WARNING = "#FFB74D"
    WARNING_BG = "#FFF3E0"
    ERROR = "#E57373"
    ERROR_BG = "#FFEBEE"
    INFO = "#42A5F5"
    INFO_BG = "#E3F2FD"

    # Borders
    BORDER_LIGHT = "#CDEED2"
    BORDER_MEDIUM = "#97D4A3"
    BORDER_DARK = "#5DBB63"


# ===== TYPOGRAPHY =====
class Fonts:
    """Professional typography settings."""
    
    # Font families
    PRIMARY = "Segoe UI"
    SECONDARY = "Arial"
    MONOSPACE = "Consolas"
    
    # Font sizes and weights
    HEADING_LARGE = (PRIMARY, 24, "bold")
    HEADING_MEDIUM = (PRIMARY, 18, "bold")
    HEADING_SMALL = (PRIMARY, 14, "bold")
    
    BODY_LARGE = (PRIMARY, 13)
    BODY_MEDIUM = (PRIMARY, 12)
    BODY_SMALL = (PRIMARY, 11)
    
    LABEL = (PRIMARY, 12)
    INPUT = (PRIMARY, 12)
    BUTTON = (PRIMARY, 11, "bold")


# ===== SPACING =====
class Spacing:
    """Consistent spacing values."""
    
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32


def configure_styles(root):
    """
    Configure ttk styles for modern appearance.
    Call this function once at app startup.
    
    Args:
        root: tk.Tk root window
    """
    style = ttk.Style()
    style.theme_use("clam")  # Modern base theme
    
    # ===== GENERAL =====
    style.configure(
        ".",
        background=Colors.BG_MAIN,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.BODY_MEDIUM,
        borderwidth=0
    )
    
    # ===== LABELS =====
    style.configure(
        "TLabel",
        background=Colors.CARD_BG,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.LABEL
    )
    
    style.configure(
        "Header.TLabel",
        background=Colors.BG_DARK,
        foreground=Colors.TEXT_LIGHT,
        font=Fonts.HEADING_LARGE,
        padding=(Spacing.LG, Spacing.MD)
    )
    
    style.configure(
        "Title.TLabel",
        font=Fonts.HEADING_MEDIUM,
        foreground=Colors.TEXT_PRIMARY
    )
    
    style.configure(
        "Subtitle.TLabel",
        font=Fonts.BODY_LARGE,
        foreground=Colors.TEXT_SECONDARY
    )
    
    style.configure(
        "Secondary.TLabel",
        foreground=Colors.TEXT_SECONDARY,
        font=Fonts.BODY_SMALL
    )
    
    # ===== FRAMES =====
    style.configure("TFrame", background=Colors.BG_MAIN)
    style.configure("Card.TFrame", background=Colors.CARD_BG, relief="flat")
    style.configure("Header.TFrame", background=Colors.ACCENT_PRIMARY)
    style.configure("Accent.TFrame", background=Colors.ACCENT_BG)
    
    # ===== LABELFRAMES =====
    style.configure(
        "TLabelframe",
        background=Colors.CARD_BG,
        bordercolor=Colors.BORDER_LIGHT,
        relief="solid",
        borderwidth=1
    )
    
    style.configure(
        "TLabelframe.Label",
        background=Colors.CARD_BG,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.HEADING_SMALL
    )
    
    # ===== ENTRIES (GLOBAL INPUT STYLE) =====
    style.configure(
        "TEntry",
        fieldbackground=Colors.CARD_BG,
        foreground=Colors.TEXT_PRIMARY,
        bordercolor=Colors.BORDER_LIGHT,
        lightcolor=Colors.BORDER_LIGHT,
        darkcolor=Colors.BORDER_MEDIUM,
        insertcolor=Colors.TEXT_PRIMARY,
        padding=(Spacing.MD, Spacing.SM),
        font=Fonts.INPUT
    )
    
    style.map(
        "TEntry",
        fieldbackground=[("focus", Colors.CARD_BG), ("active", Colors.CARD_BG)],
        bordercolor=[("focus", Colors.ACCENT_PRIMARY), ("active", Colors.BORDER_MEDIUM)],
        lightcolor=[("focus", Colors.ACCENT_PRIMARY)]
    )
    
    # ===== COMBOBOX =====
    style.configure(
        "TCombobox",
        fieldbackground=Colors.CARD_BG,
        foreground=Colors.TEXT_PRIMARY,
        background=Colors.CARD_BG,
        bordercolor=Colors.BORDER_LIGHT,
        arrowcolor=Colors.TEXT_SECONDARY,
        padding=(Spacing.MD, Spacing.SM),
        font=Fonts.INPUT
    )
    
    style.map(
        "TCombobox",
        fieldbackground=[("focus", Colors.CARD_BG), ("active", Colors.CARD_BG)],
        bordercolor=[("focus", Colors.ACCENT_PRIMARY), ("active", Colors.BORDER_MEDIUM)],
        foreground=[("readonly", Colors.TEXT_PRIMARY)]
    )
    
    # ===== BUTTONS =====
    # Primary button (accent color)
    style.configure(
        "Primary.TButton",
        background=Colors.ACCENT_PRIMARY,
        foreground=Colors.TEXT_LIGHT,
        bordercolor=Colors.ACCENT_PRIMARY,
        focuscolor=Colors.ACCENT_PRIMARY,
        font=Fonts.BUTTON,
        padding=(Spacing.XL, Spacing.MD),
        cursor="hand2"
    )
    
    style.map(
        "Primary.TButton",
        background=[("active", Colors.ACCENT_HOVER), ("pressed", Colors.ACCENT_HOVER)],
        relief=[("pressed", "sunken")],
        foreground=[("active", Colors.TEXT_LIGHT)]
    )
    
    # Secondary button (neutral)
    style.configure(
        "Secondary.TButton",
        background=Colors.CARD_BG,
        foreground=Colors.TEXT_PRIMARY,
        bordercolor=Colors.BORDER_LIGHT,
        focuscolor=Colors.BORDER_MEDIUM,
        font=Fonts.BUTTON,
        padding=(Spacing.XL, Spacing.MD),
        cursor="hand2"
    )
    
    style.map(
        "Secondary.TButton",
        background=[("active", Colors.CARD_SECONDARY), ("pressed", Colors.CARD_SECONDARY)]
    )
    
    # Success button (green)
    style.configure(
        "Success.TButton",
        background=Colors.SUCCESS,
        foreground=Colors.TEXT_LIGHT,
        bordercolor=Colors.SUCCESS,
        focuscolor=Colors.SUCCESS,
        font=Fonts.BUTTON,
        padding=(Spacing.XL, Spacing.MD),
        cursor="hand2"
    )
    
    style.map(
        "Success.TButton",
        background=[("active", Colors.ACCENT_HOVER), ("pressed", "#388E3C")],
        foreground=[("active", Colors.TEXT_LIGHT)]
    )
    
    # Danger button (red)
    style.configure(
        "Danger.TButton",
        background=Colors.ERROR,
        foreground=Colors.TEXT_LIGHT,
        bordercolor=Colors.ERROR,
        focuscolor=Colors.ERROR,
        font=Fonts.BUTTON,
        padding=(Spacing.XL, Spacing.MD),
        cursor="hand2"
    )
    
    style.map(
        "Danger.TButton",
        background=[("active", "#D32F2F"), ("pressed", "#C62828")],
        foreground=[("active", Colors.TEXT_LIGHT)]
    )
    
    # Default button (green primary)
    style.configure(
        "TButton",
        background=Colors.ACCENT_PRIMARY,
        foreground=Colors.TEXT_LIGHT,
        bordercolor=Colors.ACCENT_PRIMARY,
        focuscolor=Colors.ACCENT_PRIMARY,
        font=Fonts.BUTTON,
        padding=(Spacing.XL, Spacing.MD),
        cursor="hand2"
    )

    style.map(
        "TButton",
        background=[("active", Colors.ACCENT_HOVER), ("pressed", Colors.ACCENT_HOVER)],
        relief=[("pressed", "sunken")],
        foreground=[("active", Colors.TEXT_LIGHT)]
    )

    # Sidebar navigation buttons
    style.configure(
        "Nav.TButton",
        background=Colors.CARD_BG,
        foreground=Colors.ACCENT_PRIMARY,
        bordercolor=Colors.BORDER_LIGHT,
        focuscolor=Colors.BORDER_MEDIUM,
        font=Fonts.BUTTON,
        padding=(Spacing.XL, Spacing.MD),
        anchor="w",
        cursor="hand2"
    )

    style.map(
        "Nav.TButton",
        background=[("active", Colors.CARD_SECONDARY)],
        foreground=[("active", Colors.ACCENT_PRIMARY)]
    )

    style.configure(
        "NavActive.TButton",
        background=Colors.ACCENT_PRIMARY,
        foreground=Colors.TEXT_LIGHT,
        bordercolor=Colors.ACCENT_PRIMARY,
        focuscolor=Colors.ACCENT_PRIMARY,
        font=Fonts.BUTTON,
        padding=(Spacing.XL, Spacing.MD),
        anchor="w",
        cursor="hand2"
    )

    style.map(
        "NavActive.TButton",
        background=[("active", Colors.ACCENT_HOVER), ("pressed", Colors.ACCENT_HOVER)],
        foreground=[("active", Colors.TEXT_LIGHT)]
    )
    
    # ===== NOTEBOOK (TABS) =====
    style.configure(
        "TNotebook",
        background=Colors.BG_MAIN,
        bordercolor=Colors.BORDER_LIGHT,
        tabmargins=[2, 5, 2, 0]
    )

    style.configure(
        "TNotebook.Tab",
        background=Colors.CARD_SECONDARY,
        foreground=Colors.TEXT_SECONDARY,
        padding=(Spacing.LG, Spacing.SM),
        font=Fonts.BODY_MEDIUM
    )

    style.map(
        "TNotebook.Tab",
        background=[("selected", Colors.CARD_BG)],
        foreground=[("selected", Colors.ACCENT_PRIMARY)],
        expand=[("selected", [1, 1, 1, 0])]
    )
    
    # ===== TREEVIEW =====
    style.configure(
        "Treeview",
        background=Colors.CARD_BG,
        foreground=Colors.TEXT_PRIMARY,
        fieldbackground=Colors.CARD_BG,
        bordercolor=Colors.BORDER_LIGHT,
        font=Fonts.BODY_MEDIUM,
        rowheight=28
    )
    
    style.configure(
        "Treeview.Heading",
        background=Colors.ACCENT_PRIMARY,
        foreground=Colors.TEXT_LIGHT,
        borderwidth=0,
        relief="flat",
        font=Fonts.HEADING_SMALL
    )
    
    style.map(
        "Treeview",
        background=[("selected", Colors.ACCENT_BG)],
        foreground=[("selected", Colors.TEXT_PRIMARY)]
    )
    
    style.map(
        "Treeview.Heading",
        background=[("active", Colors.BORDER_LIGHT)]
    )
    
    # ===== SCROLLBAR =====
    style.configure(
        "TScrollbar",
        background=Colors.BORDER_LIGHT,
        troughcolor=Colors.CARD_SECONDARY,
        bordercolor=Colors.BORDER_LIGHT,
        arrowcolor=Colors.TEXT_SECONDARY
    )


def create_card_frame(parent, padding=Spacing.LG):
    """
    Create a modern card-style frame with visual elevation.
    
    Args:
        parent: Parent widget
        padding: Internal padding
        
    Returns:
        tuple: (outer_frame, inner_frame) for shadow effect
    """
    # Outer frame for soft shadow / border
    outer = tk.Frame(
        parent,
        bg=Colors.BORDER_LIGHT,
        highlightthickness=0,
        bd=0,
    )
    
    # Inner frame (actual card)
    inner = tk.Frame(
        outer,
        bg=Colors.CARD_BG,
        highlightthickness=0,
        bd=0,
    )
    inner.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
    
    # Content frame with padding
    content = tk.Frame(inner, bg=Colors.CARD_BG)
    content.pack(padx=padding, pady=padding, fill=tk.BOTH, expand=True)
    
    return outer, content


def create_header_bar(parent, title, subtitle=None, show_user=None):
    """
    Create a professional header bar with title and optional user info.
    
    Args:
        parent: Parent widget
        title: Main title text
        subtitle: Optional subtitle text
        show_user: Optional user info string
        
    Returns:
        tk.Frame: Header frame
    """
    header = tk.Frame(parent, bg=Colors.ACCENT_PRIMARY, height=72)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    # Left side: Title and subtitle
    left_frame = tk.Frame(header, bg=Colors.ACCENT_PRIMARY)
    left_frame.pack(side=tk.LEFT, padx=Spacing.XL, pady=Spacing.LG)
    
    title_label = tk.Label(
        left_frame,
        text=title,
        bg=Colors.ACCENT_PRIMARY,
        fg=Colors.TEXT_LIGHT,
        font=Fonts.HEADING_LARGE
    )
    title_label.pack(anchor=tk.W)
    
    if subtitle:
        subtitle_label = tk.Label(
            left_frame,
            text=subtitle,
            bg=Colors.ACCENT_PRIMARY,
            fg=Colors.ACCENT_BG,
            font=Fonts.BODY_MEDIUM
        )
        subtitle_label.pack(anchor=tk.W)
    
    # Right side: User info
    if show_user:
        right_frame = tk.Frame(header, bg=Colors.ACCENT_PRIMARY)
        right_frame.pack(side=tk.RIGHT, padx=Spacing.XL, pady=Spacing.LG)
        
        user_label = tk.Label(
            right_frame,
            text=show_user,
            bg=Colors.ACCENT_PRIMARY,
            fg=Colors.TEXT_LIGHT,
            font=Fonts.BODY_MEDIUM
        )
        user_label.pack()
    
    return header


def create_stat_card(parent, title, value, color=Colors.ACCENT_PRIMARY):
    """
    Create a statistics card with title and value.
    
    Args:
        parent: Parent widget
        title: Card title
        value: Display value
        color: Accent color for value
        
    Returns:
        tk.Frame: Card frame
    """
    card = tk.Frame(
        parent,
        bg=Colors.CARD_BG,
        highlightbackground=Colors.BORDER_LIGHT,
        highlightthickness=1,
        bd=0,
    )
    
    # Value label (large, colored)
    value_label = tk.Label(
        card,
        text=str(value),
        bg=Colors.CARD_BG,
        fg=color,
        font=(Fonts.PRIMARY, 28, "bold")
    )
    value_label.pack(pady=(Spacing.LG, Spacing.XS))
    
    # Title label (small, grey)
    title_label = tk.Label(
        card,
        text=title,
        bg=Colors.CARD_BG,
        fg=Colors.TEXT_SECONDARY,
        font=Fonts.BODY_MEDIUM
    )
    title_label.pack(pady=(0, Spacing.LG))
    
    return card


def create_rounded_entry(parent, width=32):
    """
    Create a rounded-style entry using a Canvas wrapper.
    Visually simulates 12–16px radius with green borders and hover/focus states.

    Returns:
        tuple: (container_frame, tk.Entry)
    """
    container = tk.Frame(parent, bg=Colors.CARD_BG)

    height = 40
    radius = 16
    pixel_width = width * 8

    canvas = tk.Canvas(
        container,
        bg=Colors.CARD_BG,
        bd=0,
        highlightthickness=0,
        height=height,
        width=pixel_width,
    )
    canvas.pack(fill=tk.X, expand=True)

    def _rounded_rect(x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    rect = _rounded_rect(
        2,
        2,
        pixel_width - 2,
        height - 2,
        radius,
        outline=Colors.BORDER_LIGHT,
        width=2,
        fill=Colors.CARD_BG,
    )

    entry = tk.Entry(
        container,
        bd=0,
        relief="flat",
        font=Fonts.INPUT,
        bg=Colors.CARD_BG,
        fg=Colors.TEXT_PRIMARY,
        insertbackground=Colors.TEXT_PRIMARY,
    )

    canvas.create_window(16, height // 2, window=entry, anchor="w")

    state = {"focused": False}

    def on_enter(_event):
        if not state["focused"]:
            canvas.itemconfigure(rect, outline=Colors.BORDER_MEDIUM)

    def on_leave(_event):
        if not state["focused"]:
            canvas.itemconfigure(rect, outline=Colors.BORDER_LIGHT)

    def on_focus_in(_event):
        state["focused"] = True
        canvas.itemconfigure(rect, outline=Colors.ACCENT_PRIMARY)

    def on_focus_out(_event):
        state["focused"] = False
        canvas.itemconfigure(rect, outline=Colors.BORDER_LIGHT)

    entry.bind("<Enter>", on_enter)
    entry.bind("<Leave>", on_leave)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    return container, entry


class RoundedInput(tk.Frame):
    """
    Reusable rounded input component with green borders and hover/focus states.
    """
    
    def __init__(self, parent, width=32, **kwargs):
        super().__init__(parent, bg=Colors.CARD_BG, **kwargs)
        self.width = width
        self.create_widget()
    
    def create_widget(self):
        height = 40
        radius = 16
        pixel_width = self.width * 8

        self.canvas = tk.Canvas(
            self,
            bg=Colors.CARD_BG,
            bd=0,
            highlightthickness=0,
            height=height,
            width=pixel_width,
        )
        self.canvas.pack(fill=tk.X, expand=True)

        def _rounded_rect(x1, y1, x2, y2, r, **kwargs):
            points = [
                x1 + r, y1,
                x2 - r, y1,
                x2, y1,
                x2, y1 + r,
                x2, y2 - r,
                x2, y2,
                x2 - r, y2,
                x1 + r, y2,
                x1, y2,
                x1, y2 - r,
                x1, y1 + r,
                x1, y1,
            ]
            return self.canvas.create_polygon(points, smooth=True, **kwargs)

        self.rect = _rounded_rect(
            2,
            2,
            pixel_width - 2,
            height - 2,
            radius,
            outline=Colors.BORDER_LIGHT,
            width=2,
            fill=Colors.CARD_BG,
        )

        self.entry = tk.Entry(
            self,
            bd=0,
            relief="flat",
            font=Fonts.INPUT,
            bg=Colors.CARD_BG,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
        )

        self.canvas.create_window(16, height // 2, window=self.entry, anchor="w")

        self.focused = False

        def on_enter(_event):
            if not self.focused:
                self.canvas.itemconfigure(self.rect, outline=Colors.BORDER_MEDIUM)

        def on_leave(_event):
            if not self.focused:
                self.canvas.itemconfigure(self.rect, outline=Colors.BORDER_LIGHT)

        def on_focus_in(_event):
            self.focused = True
            self.canvas.itemconfigure(self.rect, outline=Colors.ACCENT_PRIMARY)

        def on_focus_out(_event):
            self.focused = False
            self.canvas.itemconfigure(self.rect, outline=Colors.BORDER_LIGHT)

        self.entry.bind("<Enter>", on_enter)
        self.entry.bind("<Leave>", on_leave)
        self.entry.bind("<FocusIn>", on_focus_in)
        self.entry.bind("<FocusOut>", on_focus_out)
    
    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
    
    def focus_set(self):
        self.entry.focus_set()


class GreenButton(tk.Button):
    """
    Reusable green button with rounded corners and hover effects.
    """
    
    def __init__(self, parent, text="", command=None, **kwargs):
        # Set default styling
        defaults = {
            'bg': Colors.ACCENT_PRIMARY,
            'fg': Colors.TEXT_LIGHT,
            'font': Fonts.BUTTON,
            'bd': 0,
            'highlightthickness': 0,
            'cursor': 'hand2',
            'relief': 'flat',
            'padx': Spacing.XL,
            'pady': Spacing.MD,
            'activebackground': Colors.ACCENT_HOVER,
            'activeforeground': Colors.TEXT_LIGHT
        }
        defaults.update(kwargs)
        
        super().__init__(parent, text=text, command=command, **defaults)
        
        # Bind hover effects
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        # Store original colors
        self.original_bg = Colors.ACCENT_PRIMARY
        self.hover_bg = Colors.ACCENT_HOVER
    
    def on_enter(self, event):
        self.configure(bg=self.hover_bg)
    
    def on_leave(self, event):
        self.configure(bg=self.original_bg)


def create_modern_layout(root):
    """
    Create a clean layout structure using only pack() geometry.
    All original logic functions remain unchanged.
    
    Returns:
        dict: Dictionary containing layout components
    """
    # Main container - fills entire window
    main_container = tk.Frame(root)
    main_container.pack(fill="both", expand=True)
    
    # Sidebar - left side, fixed width
    sidebar = tk.Frame(main_container, width=220, bg="white")
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    
    # Right container - fills remaining space
    right_container = tk.Frame(main_container)
    right_container.pack(side="right", fill="both", expand=True)
    
    # Header - top of right container
    header = tk.Frame(right_container, height=70, bg="#5DBB63")
    header.pack(side="top", fill="x")
    header.pack_propagate(False)
    
    # App title in header
    title_label = tk.Label(
        header,
        text="Face Recognition Attendance System",
        bg="#5DBB63",
        fg="white",
        font=Fonts.HEADING_LARGE
    )
    title_label.pack(side="left", padx=20, pady=15)
    
    # Content - fills remaining space below header
    content = tk.Frame(right_container, bg="#F3FBF4")
    content.pack(side="top", fill="both", expand=True)
    
    return {
        'navbar': header,
        'sidebar': sidebar,
        'content_area': content,
        'title_label': title_label
    }


def create_sidebar_button(parent, text, command, is_active=False):
    """
    Create a styled sidebar navigation button.
    
    Args:
        parent: Parent widget (sidebar)
        text: Button text
        command: Button command
        is_active: Whether this button is the active one
        
    Returns:
        tk.Button: Styled button
    """
    if is_active:
        bg_color = Colors.ACCENT_PRIMARY
        fg_color = Colors.TEXT_LIGHT
        hover_bg = Colors.ACCENT_HOVER
    else:
        bg_color = Colors.CARD_BG
        fg_color = Colors.ACCENT_PRIMARY
        hover_bg = Colors.ACCENT_BG
    
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_color,
        fg=fg_color,
        font=Fonts.BUTTON,
        bd=0,
        highlightthickness=0,
        cursor='hand2',
        relief='flat',
        padx=Spacing.XL,
        pady=Spacing.MD,
        anchor='w'
    )
    
    # Store colors for hover effects
    btn.original_bg = bg_color
    btn.original_fg = fg_color
    btn.hover_bg = hover_bg if not is_active else Colors.ACCENT_HOVER
    btn.hover_fg = fg_color
    
    def on_enter(e):
        btn.configure(bg=btn.hover_bg)
    
    def on_leave(e):
        btn.configure(bg=btn.original_bg)
    
    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)
    
    return btn


def create_content_card(parent):
    """
    Create a centered white card for main content.
    
    Args:
        parent: Parent widget (content_area)
        
    Returns:
        tk.Frame: Card frame for content
    """
    # Outer frame for shadow effect
    outer = tk.Frame(parent, bg=Colors.BORDER_LIGHT, highlightthickness=0)
    outer.pack(expand=True, fill=tk.BOTH)
    
    # Inner card frame
    card = tk.Frame(outer, bg=Colors.CARD_BG, highlightthickness=0)
    card.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
    
    # Content frame with padding
    content = tk.Frame(card, bg=Colors.CARD_BG)
    content.pack(padx=Spacing.XL, pady=Spacing.XL, fill=tk.BOTH, expand=True)
    
    return content
