import tkinter as tk
from tkinter import ttk
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class ClassroomView(BaseView):
    def __init__(self, parent, router, *args, **kwargs):
        # 1. Capture the passed argument BEFORE initializing UI
        self.course_id = kwargs.get("course_id")
        
        # 2. Initialize Parent (which calls setup_ui)
        super().__init__(parent, router, *args, **kwargs)

    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # Layout Setup
        main_layout = tk.Frame(self, bg=COLORS["background"])
        main_layout.pack(fill="both", expand=True)

        Sidebar(main_layout, self.controller).pack(side="left", fill="y")

        content = tk.Frame(main_layout, bg=COLORS["background"], padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)

        # Header
        self.header_frame = tk.Frame(content, bg=COLORS["background"])
        self.header_frame.pack(fill="x", pady=(0, 20))

        tk.Button(self.header_frame, text="← Back to Courses", 
                  font=FONTS["small"], bg=COLORS["background"], fg="gray", bd=0, cursor="hand2",
                  command=lambda: self.controller.navigate("student_courses")).pack(anchor="w")

        self.course_title_lbl = tk.Label(self.header_frame, text="Loading...", 
                                         font=FONTS["h1"], bg=COLORS["background"], fg=COLORS["primary"])
        self.course_title_lbl.pack(anchor="w", pady=(5,0))

        # Tabs
        self.tabs = ttk.Notebook(content)
        self.tabs.pack(fill="both", expand=True)

        self.tab_stream = tk.Frame(self.tabs, bg="white", padx=20, pady=20)
        self.tabs.add(self.tab_stream, text="  📢 Stream  ")

        self.tab_classwork = tk.Frame(self.tabs, bg="white", padx=20, pady=20)
        self.tabs.add(self.tab_classwork, text="  📝 Classwork  ")

        # 3. Use the captured ID to load data
        if self.course_id:
            self.controller.load_classroom_data(self.course_id, self.update_ui)
        else:
            self.course_title_lbl.config(text="Error: No Course Selected")

    def update_ui(self, data):
        course = data.get("course")
        assignments = data.get("assignments", [])
        announcements = data.get("announcements", [])

        if course:
            title = getattr(course, "name", "Course")
            code = getattr(course, "code", "")
            self.course_title_lbl.config(text=f"{code} - {title}")

        # Stream Tab
        for w in self.tab_stream.winfo_children(): w.destroy()
        tk.Label(self.tab_stream, text="Announcements", font=FONTS["h2"], bg="white").pack(anchor="w", pady=(0,10))
        
        if not announcements:
            self._create_empty_state(self.tab_stream, "No announcements yet.")
        else:
            for ann in announcements: self._create_announcement_card(ann)

        # Classwork Tab
        for w in self.tab_classwork.winfo_children(): w.destroy()
        tk.Label(self.tab_classwork, text="Assignments", font=FONTS["h2"], bg="white").pack(anchor="w", pady=(0,10))

        if not assignments:
            self._create_empty_state(self.tab_classwork, "No assignments yet.")
        else:
            for asm in assignments: self._create_assignment_row(asm)

    # ... Helper methods (create_row, etc.) remain the same ...
    def _create_empty_state(self, parent, message):
        tk.Label(parent, text=message, font=FONTS["body"], fg="gray", bg="white").pack(pady=20)

    def _create_announcement_card(self, data):
        tk.Label(self.tab_stream, text=data.get('message', 'Msg'), bg="white").pack()

    def _create_assignment_row(self, asm):
        row = tk.Frame(self.tab_classwork, bg="white", pady=5)
        row.pack(fill="x")
        
        # 1. Safely get attributes (handles if asm is a dict or an object)
        # We try to get 'id', defaulting to None if it's missing
        asm_id = asm.get("id")

        type_str = asm.get("type", "Assignment").title()
        title = asm.get("title", "Untitled")
        due = asm.get("due_date", "")
        status = asm.get("status", "Pending")
        
        tk.Label(row, text=f"[{type_str}] {title} ({status})", font=FONTS["body"], bg="white").pack(side="left")
        tk.Label(row, text=due, font=FONTS["small"], fg="gray", bg="white").pack(side="right", padx=10)
        
        # 2. THE FIX: Add the command with a lambda
        # We use 'a=asm_id' to "freeze" the correct ID for this specific button.
        # If you don't use 'a=asm_id', every button might open the last assignment!
        btn = ttk.Button(row, text="Open", style="Secondary.TButton",
                   command=lambda a=asm_id: self.controller.open_assignment_details(a))
        btn.pack(side="right")
        
        # Separator
        tk.Frame(self.tab_classwork, bg="#ecf0f1", height=1).pack(fill="x")