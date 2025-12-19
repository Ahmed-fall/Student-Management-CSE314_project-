import tkinter as tk
from tkinter import ttk
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentAssignmentsView(BaseView):
    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # --- Layout ---
        main_layout = tk.Frame(self, bg=COLORS["background"])
        main_layout.pack(fill="both", expand=True)

        Sidebar(main_layout, self.controller).pack(side="left", fill="y")

        content = tk.Frame(main_layout, bg=COLORS["background"], padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)

        # Header
        tk.Label(content, text="My Assignments", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 20))

        # --- Table (Treeview) ---
        columns = ("course", "title", "due", "status")
        self.tree = ttk.Treeview(content, columns=columns, show="headings", height=15)
        
        self.tree.heading("course", text="Course")
        self.tree.heading("title", text="Assignment Title")
        self.tree.heading("due", text="Due Date")
        self.tree.heading("status", text="Status")
        
        self.tree.column("course", width=100)
        self.tree.column("title", width=250)
        self.tree.column("due", width=150)
        self.tree.column("status", width=100)
        
        self.tree.pack(fill="both", expand=True, pady=(0, 20))

        # --- Action Button ---
        btn_frame = tk.Frame(content, bg=COLORS["background"])
        btn_frame.pack(fill="x")
        
        tk.Button(btn_frame, text="Open Selected Assignment", 
                  command=self.on_open_click,
                  bg=COLORS["primary"], fg="white", font=FONTS["button"], 
                  padx=20, pady=10).pack(side="right")

        # Load Data
        self.controller.load_assignments(self.update_list)

    def update_list(self, data):
        # Clear old data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Store raw data so we can look up IDs later
        self.row_map = {} 

        for item in data:
            row_id = self.tree.insert("", tk.END, values=(
                item['course_code'],
                item['title'],
                item['due_date'],
                item['status']
            ))
            # Map the Treeview Row ID to the actual Assignment ID
            self.row_map[row_id] = item['id']

    def on_open_click(self):
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("Warning", "Please select an assignment first.")
            return
            
        # Get the assignment ID from our map
        row_id = selected[0]
        assignment_id = self.row_map.get(row_id)
        
        if assignment_id:
            self.controller.open_assignment_details(assignment_id)