import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar
import platform

class StudentCoursesView(BaseView):
    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # --- 1. Main Layout ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # Content Area
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=30, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        # --- 2. Header Section ---
        header_frame = tk.Frame(self.content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        tk.Label(header_frame, text="My Enrolled Courses", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # Refresh Button
        ttk.Button(header_frame, text="↻ Refresh List", style="Secondary.TButton",
                   command=lambda: self.controller.load_my_courses(self.display_courses)
                   ).pack(side="right")

        # --- 3. Scrollable Area ---
        container = tk.Frame(self.content, bg=COLORS["background"])
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=COLORS["background"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        # Inner Frame for Cards
        self.cards_frame = tk.Frame(self.canvas, bg=COLORS["background"])
        
        # Create Window in Canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Event Bindings ---
        self.cards_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # [NEW] Robust Mousewheel Support
        self._bind_mousewheel(self.canvas)

        # --- 4. Load Data ---
        self.controller.load_my_courses(self.display_courses)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Resize the inner frame to match the canvas width"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    # --- ROBUST SCROLLING LOGIC ---
    def _bind_mousewheel(self, widget):
        """
        Binds the mousewheel ONLY when the mouse is hovering over the widget.
        This prevents 'invalid command' errors when switching views.
        """
        def _on_mousewheel(event):
            try:
                if widget.winfo_exists(): # Safety check
                    if platform.system() == "Windows" or platform.system() == "Darwin":
                        widget.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass
        
        def _on_linux_scroll_up(event):
            try:
                if widget.winfo_exists():
                    widget.yview_scroll(-1, "units")
            except tk.TclError:
                pass

        def _on_linux_scroll_down(event):
            try:
                if widget.winfo_exists():
                    widget.yview_scroll(1, "units")
            except tk.TclError:
                pass

        # Bind only when mouse enters the widget
        def _bind_to_system(event):
            widget.bind_all("<MouseWheel>", _on_mousewheel)
            widget.bind_all("<Button-4>", _on_linux_scroll_up)
            widget.bind_all("<Button-5>", _on_linux_scroll_down)

        # Unbind when mouse leaves the widget
        def _unbind_from_system(event):
            widget.unbind_all("<MouseWheel>")
            widget.unbind_all("<Button-4>")
            widget.unbind_all("<Button-5>")

        widget.bind("<Enter>", _bind_to_system)
        widget.bind("<Leave>", _unbind_from_system)
    
    def destroy(self):
        """Ensure bindings are removed on destruction."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
        super().destroy()

    def display_courses(self, courses):
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        if not courses:
            self._create_empty_state()
            return

        for course in courses:
            self.create_course_card(course)

    def _create_empty_state(self):
        empty_frame = tk.Frame(self.cards_frame, bg=COLORS["background"], pady=40)
        empty_frame.pack(fill="x")
        
        tk.Label(empty_frame, text="You are not enrolled in any courses yet.", 
                 font=FONTS["h2"], bg=COLORS["background"], fg=COLORS["placeholder"]).pack()
        
        ttk.Button(empty_frame, text="Browse Catalog", style="Primary.TButton",
                   command=lambda: self.router.navigate("student_catalog")).pack(pady=10)

    def create_course_card(self, course):
        """Draws a styled card for a single course."""
        # Card Container
        card = tk.Frame(self.cards_frame, bg=COLORS["surface"], padx=20, pady=20)
        card.pack(fill="x", pady=(0, 15))
        
        # Add border definition
        card.configure(highlightbackground=COLORS["placeholder"], highlightthickness=1)

        # --- Layout: Info (Left) | Actions (Right) ---
        
        # 1. Info Section
        info_frame = tk.Frame(card, bg=COLORS["surface"])
        info_frame.pack(side="left", fill="both", expand=True)
        
        title = course.get("name", "Untitled")
        code = course.get("code", "N/A")
        instructor = course.get("instructor_name", "Unknown")
        desc = course.get("description", "")
        course_id = course.get("id")

        # Header: CODE - Title
        header_text = f"{code} - {title}"
        tk.Label(info_frame, text=header_text, font=FONTS["h2"], 
                 bg=COLORS["surface"], fg=COLORS["primary"], anchor="w").pack(fill="x")
        
        # Subheader: Instructor
        tk.Label(info_frame, text=f"Instructor: {instructor}", 
                 font=FONTS["small_bold"], bg=COLORS["surface"], fg=COLORS["placeholder"], anchor="w").pack(fill="x", pady=(5, 5))
        
        # Description (Truncated)
        if len(desc) > 120: desc = desc[:120] + "..."
        tk.Label(info_frame, text=desc, font=FONTS["body"], 
                 bg=COLORS["surface"], fg=COLORS["text"], anchor="w", wraplength=600, justify="left").pack(fill="x")

        # 2. Action Section
        action_frame = tk.Frame(card, bg=COLORS["surface"])
        action_frame.pack(side="right", padx=(20, 0))

        # Enter Classroom Button
        ttk.Button(action_frame, text="Enter Classroom", style="Primary.TButton",
                   command=lambda cid=course_id: self.controller.open_classroom(cid)
                   ).pack(side="top", fill="x", pady=(0, 10))
        
        # Drop Button 
        btn_drop = tk.Button(action_frame, text="Drop Course", 
                             font=FONTS["button"], 
                             bg=COLORS["surface"], fg=COLORS["danger"], 
                             bd=0, activebackground=COLORS["surface"], activeforeground="#c0392b", cursor="hand2",
                             command=lambda cid=course_id: self.handle_drop(cid))
        btn_drop.pack(side="top", fill="x")

    def handle_drop(self, course_id):
        """Asks for confirmation before calling controller."""
        if messagebox.askyesno("Confirm Drop", "Are you sure you want to drop this course?\nYou will lose access to all materials."):
            self.controller.drop_course(course_id, self.on_drop_complete)

    def on_drop_complete(self, result):
        if result:
            messagebox.showinfo("Success", "Course dropped successfully.")
            self.controller.load_my_courses(self.display_courses)
        else:
            messagebox.showerror("Error", "Could not drop course. Please try again.")