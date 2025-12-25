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
        # --- 0. Global Style Configuration for Treeview ---
        self._configure_treeview_style()

        # --- 1. Main Layout ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # Sidebar (Left)
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # Content Area (Right)
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=40, pady=40)
        self.content.pack(side="right", fill="both", expand=True)

        # --- 2. Header Section ---
        header_frame = tk.Frame(self.content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 25))

        # Title
        tk.Label(header_frame, text="Campus Manager", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # Refresh Button (Styled)
        tk.Button(header_frame, text="🔄 Refresh List", font=FONTS["button"],
                  bg="white", fg=COLORS["text"], relief="flat", padx=15, pady=8, cursor="hand2",
                  command=self.refresh_unassigned_list).pack(side="right")

        # --- 3. "Create New Course" Card ---
        # We use a frame with a highlightthickness to simulate a border
        create_card = tk.Frame(self.content, bg="white", padx=25, pady=25)
        create_card.pack(fill="x", pady=(0, 30))
        create_card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        # Card Title
        tk.Label(create_card, text="✨ Create a New Course", font=FONTS["h2"], 
                 bg="white", fg=COLORS["text"]).pack(anchor="w", pady=(0, 20))

        # Input Grid
        input_frame = tk.Frame(create_card, bg="white")
        input_frame.pack(fill="x")

        # Col 0: Code Label
        tk.Label(input_frame, text="Course Code", font=("Arial", 9, "bold"), 
                 fg="gray", bg="white").grid(row=0, column=0, sticky="w")
        
        # Col 1: Name Label
        tk.Label(input_frame, text="Course Name", font=("Arial", 9, "bold"), 
                 fg="gray", bg="white").grid(row=0, column=1, sticky="w", padx=20)

        # Row 1: Inputs
        self.code_ent = tk.Entry(input_frame, font=FONTS["body"], bg="#F9F9F9", 
                                 relief="flat", highlightthickness=1, highlightbackground="#DDD", width=15)
        self.code_ent.grid(row=1, column=0, sticky="w", pady=(5,0), ipady=8)

        self.name_ent = tk.Entry(input_frame, font=FONTS["body"], bg="#F9F9F9", 
                                 relief="flat", highlightthickness=1, highlightbackground="#DDD", width=40)
        self.name_ent.grid(row=1, column=1, sticky="w", padx=20, pady=(5,0), ipady=8)

        # Action Button
        tk.Button(input_frame, text="Initialize Course", bg=COLORS["secondary"], fg="white", 
                  font=FONTS["button"], relief="flat", padx=20, pady=8, cursor="hand2",
                  command=self.handle_create_course).grid(row=1, column=2, sticky="e", pady=(5,0))


        # --- 4. "Available Courses" Section ---
        
        # Section Header
        tk.Label(self.content, text="Unassigned Courses", font=FONTS["h2"], 
                 bg=COLORS["background"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 10))
        
        # Table Container (Card style)
        table_card = tk.Frame(self.content, bg="white", padx=2, pady=2) # Thin border wrapper
        table_card.pack(fill="both", expand=True)
        table_card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        # Scrollbar and Treeview container
        tree_frame = tk.Frame(table_card, bg="white")
        tree_frame.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Treeview
        columns = ("id", "code", "name")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                 yscrollcommand=scrollbar.set, selectmode="browse", style="Custom.Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="CODE")
        self.tree.heading("name", text="COURSE NAME")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("code", width=100, anchor="center")
        self.tree.column("name", width=400, anchor="w")

        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        # Claim Button (Bottom Right)
        btn_frame = tk.Frame(self.content, bg=COLORS["background"], pady=15)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="🙋‍♂️ Claim Selected Course", bg=COLORS["primary"], fg="white",
                  font=FONTS["button"], relief="flat", padx=20, pady=10, cursor="hand2",
                  command=self.handle_claim_course).pack(side="right")

        # Load Initial Data
        self.refresh_unassigned_list()

    def _configure_treeview_style(self):
        """Sets up a modern looking table style."""
        style = ttk.Style()
        style.theme_use("clam") # 'clam' usually allows for better color customization than 'vista'
        
        # Heading Style
        style.configure("Custom.Treeview.Heading", 
                        font=("Helvetica", 10, "bold"), 
                        background="#f0f0f0", 
                        foreground="#333", 
                        relief="flat")
        
        # Row Style
        style.configure("Custom.Treeview", 
                        font=("Helvetica", 11),
                        rowheight=35, # Taller rows
                        background="white", 
                        fieldbackground="white",
                        borderwidth=0)
        
        # Selection Color
        style.map("Custom.Treeview", background=[("selected", COLORS["primary"])])

    def handle_create_course(self):
        code = self.code_ent.get().strip()
        name = self.name_ent.get().strip()
        
        if not code or not name:
            messagebox.showwarning("Input Error", "Please enter both a Course Code and a Course Name.")
            return

        self.controller.create_new_course(code, name, self.on_success)

    def handle_claim_course(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a course from the list to claim.")
            return
            
        course_id = self.tree.item(selected[0], "values")[0]
        self.controller.claim_teaching_rights(course_id, self.on_success)

    def on_success(self, result):
        if result:
            messagebox.showinfo("Success", "Action completed successfully!")
            # Clear inputs
            self.code_ent.delete(0, tk.END)
            self.name_ent.delete(0, tk.END)
            # Refresh list
            self.refresh_unassigned_list()

    def refresh_unassigned_list(self):
        self.controller.load_unassigned_courses(self.render_unassigned_table)

    def render_unassigned_table(self, courses):
        if not hasattr(self, 'tree'): return

        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not courses:
            return

        for i, c in enumerate(courses):
            # Alternating row colors (Striping)
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(c.id, c.code, c.name), tags=(tag,))

        # Configure the tags for striping
        self.tree.tag_configure("even", background="white")
        self.tree.tag_configure("odd", background="#F9FAFB") # Very light gray