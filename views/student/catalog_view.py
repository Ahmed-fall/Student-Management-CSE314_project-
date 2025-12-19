import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentCatalogView(BaseView):
    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # 1. Main Layout
        main_layout = tk.Frame(self, bg=COLORS["background"])
        main_layout.pack(fill="both", expand=True)

        # 2. Sidebar
        sidebar = Sidebar(main_layout, self.controller)
        sidebar.pack(side="left", fill="y")

        # 3. Content Area
        content = tk.Frame(main_layout, bg=COLORS["background"], padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)

        # Header
        header_frame = tk.Frame(content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Course Catalog", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # Search/Filter
        search_frame = tk.Frame(content, bg=COLORS["background"])
        search_frame.pack(fill="x", pady=(0, 20))

        self.search_entry = tk.Entry(search_frame, font=FONTS["body"], width=50)
        self.search_entry.pack(side="left", padx=10)

        ttk.Button(search_frame, text="Search", command=self.perform_search).pack(side="left")

        # 4. Scrollable Container
        self.canvas = tk.Canvas(content, bg=COLORS["background"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        
        self.cards_frame = tk.Frame(self.canvas, bg=COLORS["background"])
        
        self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.cards_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # 5. Load Data
        self.controller.load_catalog_data(self.display_courses)

    def perform_search(self):
        query = self.search_entry.get().strip()
        self.controller.load_catalog_data(self.display_courses, query)

    def display_courses(self, data):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        courses = data.get("courses", [])
        enrolled_ids = data.get("enrolled_ids", [])

        if not courses:
            tk.Label(self.cards_frame, text="No courses found.", 
                     font=FONTS["body"], bg=COLORS["background"], fg="gray").pack(pady=20)
            return

        for course in courses:
            self.create_course_card(course, course['id'] in enrolled_ids)

    def create_course_card(self, course, is_enrolled):
        card = tk.Frame(self.cards_frame, bg="white", padx=20, pady=15)
        card.pack(fill="x", pady=10, expand=True)
        
        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(side="left", fill="both", expand=True)
        
        title = course.get("name", "Untitled")
        code = course.get("code", "N/A")
        instructor = course.get("instructor_name", "Unknown")
        credits = course.get("credits", 3)
        desc = course.get("description", "")
        
        tk.Label(info_frame, text=f"{code} - {title}", font=FONTS["h2"], 
                 bg="white", fg=COLORS["text"], anchor="w").pack(fill="x")
        
        tk.Label(info_frame, text=f"Instructor: {instructor} | Credits: {credits}", 
                 font=FONTS["small"], bg="white", fg="gray", anchor="w").pack(fill="x")
        
        tk.Label(info_frame, text=desc[:100] + "..." if len(desc) > 100 else desc, 
                 font=FONTS["small"], bg="white", fg="gray", anchor="w").pack(fill="x", pady=(5, 0))

        action_frame = tk.Frame(card, bg="white")
        action_frame.pack(side="right")

        if is_enrolled:
            ttk.Button(action_frame, text="Enrolled", state="disabled").pack(side="right")
        else:
            ttk.Button(action_frame, text="Enroll", style="Secondary.TButton",
                       command=lambda cid=course['id']: self.controller.enroll_course(cid, self.refresh_after_enroll)
                       ).pack(side="right")

    def refresh_after_enroll(self, success):
        if success:
            messagebox.showinfo("Success", "Enrolled successfully!")
            self.controller.load_catalog_data(self.display_courses)
        else:
            messagebox.showerror("Error", "Enrollment failed.")