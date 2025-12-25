import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentAssignmentsView(BaseView):
    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # --- 1. Main Layout ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # Sidebar (Left)
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # Content Area (Right)
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=30, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        # --- 2. Header ---
        header_frame = tk.Frame(self.content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 20))

        tk.Label(header_frame, text="My Assignments", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # --- 3. Table Container (Card Style) ---
        self.table_card = tk.Frame(self.content, bg=COLORS["surface"], padx=1, pady=1)
        self.table_card.pack(fill="both", expand=True, pady=(0, 20))

        # --- 4. The Treeview (Table) ---
        columns = ("course", "title", "due", "status")
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.table_card, orient="vertical")
        
        self.tree = ttk.Treeview(self.table_card, columns=columns, show="headings", 
                                 height=15, selectmode="browse", 
                                 style="Primary.Treeview",       # <--- THIS FIXES THE COLORS
                                 yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.config(command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Columns Configuration
        self.tree.heading("course", text="Course")
        self.tree.heading("title", text="Assignment Title")
        self.tree.heading("due", text="Due Date")
        self.tree.heading("status", text="Status")
        
        self.tree.column("course", width=100, anchor="center")
        self.tree.column("title", width=300, anchor="w")
        self.tree.column("due", width=150, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        
        self.tree.tag_configure("overdue", foreground=COLORS["danger"])   # Red
        self.tree.tag_configure("graded", foreground=COLORS["success"])   # Green
        self.tree.tag_configure("submitted", foreground=COLORS["secondary"]) # Teal
        self.tree.tag_configure("pending", foreground=COLORS["text"])     # Dark Blue

        # Bindings
        self.tree.bind("<Double-1>", self.on_double_click)

        self.lbl_empty = tk.Label(self.table_card, text="No assignments found.", 
                                  font=FONTS["body"], bg="white", fg=COLORS["placeholder"])

        # --- 6. Action Button ---
        btn_frame = tk.Frame(self.content, bg=COLORS["background"])
        btn_frame.pack(fill="x")
        
        self.btn_open = ttk.Button(btn_frame, text="Open Selected Assignment", 
                                   command=self.on_open_click, 
                                   style="Primary.TButton", cursor="hand2")
        self.btn_open.pack(side="right")

        # --- 7. Load Data ---
        self.controller.load_assignments(self.update_list)

    def update_list(self, data):
        # 1. Clear old data
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_empty.place_forget() # Hide empty message
            
        self.row_map = {} 

        # 2. Handle Empty Data
        if not data:
            # Show the empty state label right in the middle of the tree area
            self.lbl_empty.place(relx=0.5, rely=0.5, anchor="center")
            return

        # 3. Populate Tree
        for item in data:
            status_text = item['status']
            
            # Determine visual tag
            row_tag = "pending"
            s_lower = status_text.lower()
            
            if "overdue" in s_lower or "missing" in s_lower:
                row_tag = "overdue"
            elif "graded" in s_lower:
                row_tag = "graded"
            elif "submitted" in s_lower:
                row_tag = "submitted"

            row_id = self.tree.insert("", tk.END, values=(
                item['course_code'],
                item['title'],
                item['due_date'],
                status_text
            ), tags=(row_tag,)) 
            
            self.row_map[row_id] = item['id']

    def on_double_click(self, event):
        self.on_open_click()

    def on_open_click(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an assignment to view.")
            return
            
        row_id = selected[0]
        assignment_id = self.row_map.get(row_id)
        
        if assignment_id:
            self.controller.open_assignment_details(assignment_id)