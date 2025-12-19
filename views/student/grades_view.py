import tkinter as tk
from tkinter import ttk
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentGradesView(BaseView):
    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # 1. Layout
        main_layout = tk.Frame(self, bg=COLORS["background"])
        main_layout.pack(fill="both", expand=True)

        # Sidebar
        Sidebar(main_layout, self.controller).pack(side="left", fill="y")

        # Content Area
        content = tk.Frame(main_layout, bg=COLORS["background"], padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)

        # Header
        tk.Label(content, text="My Grades", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 20))

        # 2. The Grade Table (Treeview)
        # We use a Treeview widget to display columns
        columns = ("title", "date", "status", "grade", "feedback")
        
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=15)
        
        # Define Headings
        self.tree.heading("title", text="Assignment")
        self.tree.heading("date", text="Submitted Date")
        self.tree.heading("status", text="Status")
        self.tree.heading("grade", text="Grade")
        self.tree.heading("feedback", text="Feedback")
        
        # Define Column Widths
        self.tree.column("title", width=300)
        self.tree.column("date", width=150)
        self.tree.column("status", width=100)
        self.tree.column("grade", width=100)
        self.tree.column("feedback", width=200)
        
        self.tree.pack(fill="both", expand=True)

        # 3. Load Data
        self.controller.load_grades(self.update_table)

    def update_table(self, grades_data):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not grades_data:
            return

        # Insert new rows
        for item in grades_data:
            # Format the grade (e.g., "85 / 100")
            grade_display = f"{item['grade']} / {item['max_score']}" if item['grade'] != "-" else "-"
            
            self.tree.insert("", tk.END, values=(
                item['assignment_title'],
                item['submitted_at'],
                item['status'],
                grade_display,
                item['feedback']
            ))