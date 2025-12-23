import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class CampusManagerView(BaseView):
    def create_controller(self):
        from controllers.instructor_controller import InstructorController
        return InstructorController(self.router)

    def setup_ui(self):
        # 1. Main Layout
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        Sidebar(self.main_layout, self.controller).pack(side="left", fill="y")

        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=30, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        header_frame = tk.Frame(self.content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 20))

        tk.Label(header_frame, text="🏫 Campus Manager", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # The Refresh Button
        tk.Button(header_frame, text="🔄 Refresh", font=FONTS["small_bold"],
                  bg=COLORS["background"], command=self.refresh_unassigned_list).pack(side="right")

        # --- SECTION 1: CREATE NEW COURSE ---
        create_frame = tk.LabelFrame(self.content, text=" Create a New Course ", bg="white", padx=15, pady=15)
        create_frame.pack(fill="x", pady=(0, 20))

        tk.Label(create_frame, text="Course Code (e.g., CS101):", bg="white").grid(row=0, column=0, sticky="w")
        self.code_ent = tk.Entry(create_frame)
        self.code_ent.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(create_frame, text="Course Name:", bg="white").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.name_ent = tk.Entry(create_frame)
        self.name_ent.grid(row=0, column=3, padx=10, pady=5)

        tk.Button(create_frame, text="✨ Initialize Course", bg=COLORS["secondary"], fg="white",
                  command=self.handle_create_course).grid(row=0, column=4, padx=20)

        # --- SECTION 2: ENROLL IN EXISTING COURSE ---
        enroll_frame = tk.LabelFrame(self.content, text=" Available Unassigned Courses ", bg="white", padx=15, pady=15)
        enroll_frame.pack(fill="both", expand=True)

        columns = ("id", "code", "name")
        self.tree = ttk.Treeview(enroll_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Code")
        self.tree.heading("name", text="Course Name")
        self.tree.pack(fill="both", expand=True, pady=10)

        tk.Button(enroll_frame, text="🙋‍♂️ Claim Teaching Rights", bg=COLORS["primary"], fg="white",
                  command=self.handle_claim_course).pack(anchor="e")
        
        # Load the data after the UI is fully built
        self.refresh_unassigned_list()

    def handle_create_course(self):
        """Gathers input and triggers the controller's creation logic."""
        code = self.code_ent.get().strip()
        name = self.name_ent.get().strip()
        
        if not code or not name:
            messagebox.showwarning("Input Error", "Please enter both a Course Code and a Course Name.")
            return

        self.controller.create_new_course(code, name, self.on_success)

    def handle_claim_course(self):
        """Assigns the instructor to an existing course"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Choose a course to claim.")
            return
            
        course_id = self.tree.item(selected[0], "values")[0]
        # Ensure the controller has this method re-added!
        self.controller.claim_teaching_rights(course_id, self.on_success)

    def on_success(self, result):
        """Standard callback for successful database actions."""
        if result:
            messagebox.showinfo("Success", "Action completed successfully!")
            self.router.navigate("instructor_dashboard")

    def refresh_unassigned_list(self):
        """Calls the controller to get unassigned courses."""
        self.controller.load_unassigned_courses(self.render_unassigned_table)

    def render_unassigned_table(self, courses):
        """Populates the Treeview with safety checks."""
        # Safety check: Avoid AttributeError if UI is still loading
        if not hasattr(self, 'tree'):
            return

        # Clear the table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not courses:
            return

        for c in courses:
            # Use course object attributes
            self.tree.insert("", "end", values=(c.id, c.code, c.name))