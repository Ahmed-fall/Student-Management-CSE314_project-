import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar
from datetime import datetime
import platform

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
        # --- 1. Main Layout ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # Content Area
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=30, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        # --- 2. Header & Navigation ---
        self.header_frame = tk.Frame(self.content, bg=COLORS["background"])
        self.header_frame.pack(fill="x", pady=(0, 20))

        # Back Link
        btn_back = tk.Button(self.header_frame, text="← Back to My Courses", 
                             font=FONTS["small_bold"], bg=COLORS["background"], fg=COLORS["placeholder"], 
                             bd=0, cursor="hand2", activebackground=COLORS["background"],
                             command=lambda: self.controller.navigate("student_courses"))
        btn_back.pack(anchor="w")

        # Course Title
        self.course_title_lbl = tk.Label(self.header_frame, text="Loading Classroom...", 
                                         font=FONTS["h1"], bg=COLORS["background"], fg=COLORS["primary"])
        self.course_title_lbl.pack(anchor="w", pady=(5,0))

        # --- 3. Tabs (Notebook) ---
        self.tabs = ttk.Notebook(self.content)
        self.tabs.pack(fill="both", expand=True)

        # ============================================================
        # TAB 1: STREAM (SCROLLABLE)
        # ============================================================
        self.tab_stream = tk.Frame(self.tabs, bg=COLORS["background"])
        self.tabs.add(self.tab_stream, text="  📢 Stream  ")
        
        # Helper to create scrollable area
        self.stream_canvas, self.stream_content = self._create_scrollable_area(self.tab_stream)


        # ============================================================
        # TAB 2: CLASSWORK (SCROLLABLE)
        # ============================================================
        self.tab_classwork = tk.Frame(self.tabs, bg=COLORS["background"])
        self.tabs.add(self.tab_classwork, text="  📝 Classwork  ")
        
        # Helper to create scrollable area
        self.classwork_canvas, self.classwork_content = self._create_scrollable_area(self.tab_classwork)

        # --- 4. Load Data ---
        if self.course_id:
            self.controller.load_classroom_data(self.course_id, self.update_ui)
        else:
            self.course_title_lbl.config(text="Error: No Course ID provided")

    def _create_scrollable_area(self, parent_tab):
        """Creates a canvas, scrollbar, and inner frame for scrolling."""
        canvas = tk.Canvas(parent_tab, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent_tab, orient="vertical", command=canvas.yview)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Inner Frame
        content_frame = tk.Frame(canvas, bg=COLORS["background"], padx=20, pady=20)
        
        # Window
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Bindings
        content_frame.bind("<Configure>", 
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.bind("<Configure>", 
            lambda e: canvas.itemconfig(canvas_window, width=e.width))

        self._setup_scroll_bindings(canvas)
        
        return canvas, content_frame

    def _setup_scroll_bindings(self, canvas_widget):
        """Attaches robust scroll listeners to a canvas."""
        canvas_widget.bind('<Enter>', lambda e: self._bind_mousewheel(canvas_widget))
        canvas_widget.bind('<Leave>', lambda e: self._unbind_mousewheel(canvas_widget))

    def _bind_mousewheel(self, widget):
        self.active_scroll_widget = widget # Track which widget is active
        widget.bind_all("<MouseWheel>", self._on_mousewheel)
        widget.bind_all("<Button-4>", self._on_mousewheel)
        widget.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, widget):
        widget.unbind_all("<MouseWheel>")
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")
        self.active_scroll_widget = None

    def _on_mousewheel(self, event):
        if not hasattr(self, 'active_scroll_widget') or not self.active_scroll_widget:
            return

        try:
            if not self.active_scroll_widget.winfo_exists():
                return
            
            # Windows/Mac
            if event.delta:
                self.active_scroll_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            # Linux
            elif event.num == 5:
                self.active_scroll_widget.yview_scroll(1, "units")
            elif event.num == 4:
                self.active_scroll_widget.yview_scroll(-1, "units")
        except tk.TclError:
            pass

    def destroy(self):
        """Clean up bindings on destroy."""
        self._unbind_mousewheel(self)
        super().destroy()

    def update_ui(self, data):
        if not data:
            messagebox.showerror("Error", "Could not load classroom data.")
            return

        course = data.get("course")
        assignments = data.get("assignments", [])
        announcements = data.get("announcements", [])

        # Update Header
        if course:
            title = getattr(course, "name", "Course")
            code = getattr(course, "code", "")
            self.course_title_lbl.config(text=f"{code} - {title}")

        # --- Render Stream ---
        self._render_stream(announcements)

        # --- Render Classwork ---
        self._render_classwork(assignments)

    def _render_stream(self, announcements):
        # Clear previous items
        for w in self.stream_content.winfo_children(): w.destroy()
        
        tk.Label(self.stream_content, text="Latest Announcements", font=FONTS["h2"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(0,15))

        if not announcements:
            self._create_empty_state(self.stream_content, "No announcements posted yet.")
            return

        for ann in announcements: 
            self._create_announcement_card(ann)

    def _render_classwork(self, assignments):
        # Clear previous items
        for w in self.classwork_content.winfo_children(): w.destroy()

        tk.Label(self.classwork_content, text="Assignments & Tasks", font=FONTS["h2"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(0,15))

        if not assignments:
            self._create_empty_state(self.classwork_content, "No assignments due.")
            return

        for asm in assignments: 
            self._create_assignment_row(asm)

    def _create_empty_state(self, parent, message):
        frame = tk.Frame(parent, bg=COLORS["background"], pady=40)
        frame.pack(fill="x")
        tk.Label(frame, text=message, font=FONTS["body"], fg=COLORS["placeholder"], bg=COLORS["background"]).pack()

    def _create_announcement_card(self, data):
        card = tk.Frame(self.stream_content, bg=COLORS["surface"], bd=0, padx=20, pady=20)
        card.pack(fill="x", pady=(0, 15)) 
        
        # Subtle border
        tk.Frame(card, bg="#e0e0e0", height=1).pack(side="bottom", fill="x")

        # Header
        header = tk.Frame(card, bg=COLORS["surface"])
        header.pack(fill="x", pady=(0, 10))

        title_text = data.get('title', 'Announcement')
        tk.Label(header, text=title_text, font=FONTS["h2"], bg=COLORS["surface"], fg=COLORS["primary"]).pack(side="left")

        raw_date = str(data.get('created_at', ''))
        date_text = raw_date.replace('T', ' ')[:16] 
        tk.Label(header, text=date_text, font=FONTS["small"], bg=COLORS["surface"], fg=COLORS["placeholder"]).pack(side="right")

        # Body
        msg_text = data.get('message', '')
        tk.Label(card, text=msg_text, font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"], 
                 justify="left", anchor="w", wraplength=700).pack(fill="x")

    def _create_assignment_row(self, asm):
        # Add to self.classwork_content
        row = tk.Frame(self.classwork_content, bg=COLORS["surface"], padx=15, pady=15)
        row.pack(fill="x", pady=(0, 10))
        
        row.configure(highlightbackground=COLORS["placeholder"], highlightthickness=1)
        
        info_frame = tk.Frame(row, bg=COLORS["surface"])
        info_frame.pack(side="left", fill="x", expand=True)

        title = asm.get("title", "Untitled")
        status = asm.get("status", "Pending")
        
        tk.Label(info_frame, text=title, font=FONTS["body_bold"], bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w")

        status_fg = COLORS["placeholder"]
        s_lower = status.lower()
        if "graded" in s_lower: status_fg = COLORS["success"]
        elif "overdue" in s_lower or "missing" in s_lower: status_fg = COLORS["danger"]
        elif "submitted" in s_lower: status_fg = COLORS["secondary"]

        tk.Label(info_frame, text=f"Status: {status}", font=FONTS["small_bold"], bg=COLORS["surface"], fg=status_fg).pack(anchor="w")

        action_frame = tk.Frame(row, bg=COLORS["surface"])
        action_frame.pack(side="right")

        due = asm.get("due_date", "")
        if due:
            tk.Label(action_frame, text=f"Due: {due}", font=FONTS["small"], 
                     bg=COLORS["surface"], fg=COLORS["placeholder"]).pack(side="left", padx=15)

        asm_id = asm.get("id")
        ttk.Button(action_frame, text="View Details", style="Secondary.TButton",
                   command=lambda a=asm_id: self.controller.open_assignment_details(a)).pack(side="left")