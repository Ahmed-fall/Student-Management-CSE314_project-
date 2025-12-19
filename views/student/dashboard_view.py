import tkinter as tk
from tkinter import ttk
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentDashboardView(BaseView):
    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # --- Layout Setup ---
        main_layout = tk.Frame(self, bg=COLORS["background"])
        main_layout.pack(fill="both", expand=True)

        sidebar = Sidebar(main_layout, self.controller)
        sidebar.pack(side="left", fill="y")

        content = tk.Frame(main_layout, bg=COLORS["background"], padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)

        # --- Header ---
        tk.Label(content, text="Dashboard Overview", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 20))

        # --- KPI Cards with DYNAMIC DATA ---
        kpi_frame = tk.Frame(content, bg=COLORS["background"])
        kpi_frame.pack(fill="x", pady=20)

        # 1. Define Variables for Data
        self.gpa_var = tk.StringVar(value="Loading...")
        self.credits_var = tk.StringVar(value="--")
        self.courses_var = tk.StringVar(value="--")
        self.unread_var = tk.StringVar(value="--")

        # 2. Create Cards using these variables
        self.create_kpi_card(kpi_frame, "GPA", self.gpa_var, "#e74c3c")
        self.create_kpi_card(kpi_frame, "Credits", self.credits_var, "#3498db")
        self.create_kpi_card(kpi_frame, "Active Courses", self.courses_var, "#2ecc71")
        self.create_kpi_card(kpi_frame, "Unread Notifications", self.unread_var, "#f39c12")

        # --- Upcoming Deadlines Section ---
        tk.Label(content, text="Upcoming Deadlines (Next 7 Days)", font=FONTS["h2"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(20, 10))
        
        # Container for deadline rows
        self.deadline_container = tk.Frame(content, bg=COLORS["background"])
        self.deadline_container.pack(fill="x")
        
        # Initial Placeholder
        tk.Label(self.deadline_container, text="Checking for assignments...", 
                 bg=COLORS["background"], fg="gray").pack(anchor="w")

        # --- Trigger Data Fetch ---
        # The View asks the Controller to get data immediately after setup
        self.controller.load_dashboard_data(self.update_view)

    def update_view(self, data):
        """Called by Controller when data arrives from Database."""
        # 1. Update KPI Cards
        gpa = data.get("current_gpa_average", 0.0)
        count = data.get("enrolled_courses_count", 0)
        unread = data.get("unread_notifications", 0)
        
        self.gpa_var.set(f"{gpa:.2f}")
        self.courses_var.set(str(count))
        self.credits_var.set(str(count * 3)) # Estimating 3 credits per course
        self.unread_var.set(str(unread))

        # 2. Update Deadlines List
        # Clear existing widgets in container
        for widget in self.deadline_container.winfo_children():
            widget.destroy()

        deadlines = data.get("upcoming_deadlines", [])
        
        if not deadlines:
            tk.Label(self.deadline_container, text="No upcoming deadlines! 🎉", 
                     bg=COLORS["background"], fg="gray", font=FONTS["body"]).pack(anchor="w", pady=5)
        else:
            for item in deadlines:
                # Format: "Math 101 - Algebra Quiz"
                title_text = f"{item['course_code']} - {item['assignment_title']}"
                # Format Date: "2023-12-01 23:59"
                date_text = str(item['due_date']).replace("T", " ")[:16] 
                
                self.create_deadline_row(self.deadline_container, title_text, date_text)

    def create_kpi_card(self, parent, title, variable, color):
        card = tk.Frame(parent, bg="white", padx=20, pady=20)
        card.pack(side="left", fill="both", expand=True, padx=10)
        
        tk.Frame(card, bg=color, height=5).pack(fill="x", pady=(0, 10))
        tk.Label(card, text=title, font=FONTS["small"], fg="gray", bg="white").pack(anchor="w")
        # Use textvariable to make it dynamic
        tk.Label(card, textvariable=variable, font=("Helvetica", 24, "bold"), 
                 fg=COLORS["primary"], bg="white").pack(anchor="w")

    def create_deadline_row(self, parent, task, time):
        row = tk.Frame(parent, bg="white", padx=15, pady=10)
        row.pack(fill="x", pady=5)
        tk.Label(row, text=task, font=FONTS["body_bold"], bg="white", fg=COLORS["text"]).pack(side="left")
        tk.Label(row, text=time, font=FONTS["small"], bg="white", fg=COLORS["accent"]).pack(side="right")