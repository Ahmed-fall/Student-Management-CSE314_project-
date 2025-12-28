import tkinter as tk
from tkinter import messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class CourseEditorView(BaseView):
    def create_controller(self):
        from controllers.instructor_controller import InstructorController
        return InstructorController(self.router)

    def setup_ui(self):
        # --- Layout Setup ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=40, pady=40)
        self.content.pack(side="right", fill="both", expand=True)

        # --- Header ---
        header_frame = tk.Frame(self.content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_lbl = tk.Label(header_frame, text="Edit Course", font=FONTS["h1"], bg=COLORS["background"], fg=COLORS["primary"])
        self.title_lbl.pack(side="left")

        # --- Form Container ---
        self.card = tk.Frame(self.content, bg="white", padx=30, pady=30)
        self.card.pack(fill="both", expand=True)
        self.card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        # 1. Course Name (Read Only)
        tk.Label(self.card, text="Course Name", font=FONTS["caption"], bg="white", fg="gray").pack(anchor="w")
        self.name_lbl = tk.Label(self.card, text="Loading...", font=FONTS["h2"], bg="white", fg=COLORS["text"])
        self.name_lbl.pack(anchor="w", pady=(0, 15))

        # 2. Course Code (Read Only)
        tk.Label(self.card, text="Course Code", font=FONTS["caption"], bg="white", fg="gray").pack(anchor="w")
        self.code_lbl = tk.Label(self.card, text="...", font=FONTS["body"], bg="white", fg=COLORS["text"])
        self.code_lbl.pack(anchor="w", pady=(0, 20))

        # 3. Capacity (Editable)
        tk.Label(self.card, text="Max Students (Capacity)", font=FONTS["body_bold"], bg="white").pack(anchor="w", pady=(10, 5))
        self.capacity_entry = tk.Entry(self.card, font=FONTS["body"], bg="#F9F9F9", relief="flat", highlightthickness=1, highlightbackground="#DDD")
        self.capacity_entry.pack(fill="x", ipady=8)

        # 4. Description (Editable)
        tk.Label(self.card, text="Course Description", font=FONTS["body_bold"], bg="white").pack(anchor="w", pady=(20, 5))
        self.desc_text = tk.Text(self.card, height=6, font=FONTS["body"], bg="#F9F9F9", relief="flat", highlightthickness=1, highlightbackground="#DDD")
        self.desc_text.pack(fill="x", pady=(0, 20))

        # 5. Buttons
        btn_row = tk.Frame(self.card, bg="white")
        btn_row.pack(fill="x", pady=20)

        tk.Button(btn_row, text="Save Changes", bg=COLORS["primary"], fg="white", font=FONTS["button"], 
                  padx=20, pady=10, relief="flat", cursor="hand2", 
                  command=self.save_changes).pack(side="right")

        tk.Button(btn_row, text="Cancel", bg="white", fg=COLORS["text"], font=FONTS["button"], 
                  padx=20, pady=10, relief="flat", cursor="hand2", 
                  command=self.router.go_back).pack(side="right", padx=10)

        # --- Trigger Data Load ---
        self.after(100, self.load_data)

    def load_data(self):
        """
        CRITICAL FIX: checks self.kwargs for the course_id passed from the dashboard.
        """
        # 1. Check if ID exists in the arguments passed by the router
        if hasattr(self, 'kwargs') and 'course_id' in self.kwargs:
            self.course_id = self.kwargs['course_id']
            # 2. Ask controller to fetch data
            self.controller.get_course_details(self.course_id, self.populate_form)
        else:
            # 3. Handle missing ID (e.g., if user refreshed the page or navigated manually)
            messagebox.showerror("Error", "No Course ID provided.")
            self.router.go_back()

    def populate_form(self, course):
        """Fills the UI with data from the database."""
        if not course:
            messagebox.showerror("Error", "Course not found.")
            self.router.go_back()
            return

        self.name_lbl.config(text=course.name)
        self.code_lbl.config(text=course.code)
        
        # Fill Entry (Clear first, then insert)
        self.capacity_entry.delete(0, tk.END)
        # Use getattr to safely get capacity, default to 30 if missing
        self.capacity_entry.insert(0, str(getattr(course, 'capacity', 30)))
        
        # Fill Text Area
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", getattr(course, 'description', ""))

    def save_changes(self):
        try:
            capacity = int(self.capacity_entry.get())
            description = self.desc_text.get("1.0", tk.END).strip()
            
            data = {
                "capacity": capacity,
                "description": description
            }
            
            self.controller.update_course_details(
                self.course_id, 
                data, 
                lambda result: messagebox.showinfo("Success", "Course updated successfully!")
            )
        except ValueError:
            messagebox.showerror("Validation Error", "Capacity must be a number.")