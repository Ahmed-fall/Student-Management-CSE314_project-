import tkinter as tk
from tkinter import ttk
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentCoursesView(BaseView):
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
        
        tk.Label(header_frame, text="My Enrolled Courses", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # "Refresh" Button
        ttk.Button(header_frame, text="↻ Refresh", 
                   command=lambda: self.controller.load_my_courses(self.display_courses)
                   ).pack(side="right")

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
        self.controller.load_my_courses(self.display_courses)

    def display_courses(self, courses):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        if not courses:
            tk.Label(self.cards_frame, text="You are not enrolled in any courses yet.", 
                     font=FONTS["body"], bg=COLORS["background"], fg="gray").pack(pady=20)
            return

        for course in courses:
            self.create_course_card(course)

    def create_course_card(self, course):
        """Draws a nice box for a single course."""
        card = tk.Frame(self.cards_frame, bg="white", padx=20, pady=15)
        card.pack(fill="x", pady=10, expand=True)
        
        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(side="left", fill="both", expand=True)
        
        # --- FIX: Safe Attribute Access for Objects ---
        # The Repo returns Objects, so we use dot notation or getattr.
        # We do NOT use .get() because that is for dictionaries.
        
        title = course.get("name", "Untitled")
        code = course.get("code", "N/A")
        instructor = course.get("instructor_name", "Unknown")
        credits = course.get("credits", 3)
        desc = course.get("description", "")
        course_id = course.get("id", None)
        
        tk.Label(info_frame, text=f"{code} - {title}", font=FONTS["h2"], 
                 bg="white", fg=COLORS["text"], anchor="w").pack(fill="x")
        
        tk.Label(info_frame, text=f"Instructor: {instructor} | Credits: {credits}", 
                 font=FONTS["small"], bg="white", fg="gray", anchor="w").pack(fill="x")
        
        tk.Label(info_frame, text=desc[:100] + "..." if len(desc) > 100 else desc, 
                 font=FONTS["small"], bg="white", fg="gray", anchor="w").pack(fill="x", pady=(5, 0))

        action_frame = tk.Frame(card, bg="white")
        action_frame.pack(side="right")

        ttk.Button(action_frame, text="Enter Classroom", style="Secondary.TButton",
            command=lambda cid=course_id: self.controller.open_classroom(cid)
            ).pack(side="right")