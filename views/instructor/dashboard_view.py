import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class InstructorDashboardView(BaseView):
    """
    Primary landing page for Instructors.
    Displays profile information, statistics, and a scrollable list of courses.
    """

    def create_controller(self):
        from controllers.instructor_controller import InstructorController
        return InstructorController(self.router)

    def setup_ui(self):
        # --- 1. Main Layout ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # --- Sidebar (Fixed Left) ---
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # --- Content Area (Right) ---
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"])
        self.content.pack(side="right", fill="both", expand=True)

        # --- Header & Stats (Fixed Top) ---
        # This frame stays at the top while the course list below it scrolls.
        self.top_section = tk.Frame(self.content, bg=COLORS["background"], padx=40, pady=30)
        self.top_section.pack(fill="x")

        # Header
        self.welcome_lbl = tk.Label(
            self.top_section, 
            text="Instructor Dashboard", 
            font=FONTS["h1"], 
            bg=COLORS["background"], 
            fg=COLORS["primary"]
        )
        self.welcome_lbl.pack(anchor="w", pady=(0, 20))

        # Stats Bar Container
        self.stats_container = tk.Frame(self.top_section, bg=COLORS["background"])
        self.stats_container.pack(fill="x")

        # --- Scrollable Course List Area ---
        self.list_area_frame = tk.Frame(self.content, bg=COLORS["background"], padx=40)
        self.list_area_frame.pack(fill="both", expand=True)

        # Section Title
        tk.Label(self.list_area_frame, text="Active Semesters", font=FONTS["h2"], 
                 bg=COLORS["background"], fg=COLORS["text"]).pack(anchor="w", pady=(10, 10))

        # Canvas Setup for Scrolling
        self.canvas = tk.Canvas(self.list_area_frame, bg=COLORS["background"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.list_area_frame, orient="vertical", command=self.canvas.yview)
        
        # The Frame INSIDE the canvas
        self.course_list_container = tk.Frame(self.canvas, bg=COLORS["background"])

        # Configure Scrolling
        self.canvas.create_window((0, 0), window=self.course_list_container, anchor="nw", tags="self.course_list_container")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bindings for resizing and mousewheel
        self.course_list_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Enable MouseWheel scrolling when hovering over the canvas
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # --- Load Data ---
        self.controller.load_dashboard_data(self.render_dashboard)

    # --- SCROLLING LOGIC ---
    def _on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """When the canvas resizes, force the inner frame to match the width."""
        canvas_width = event.width
        self.canvas.itemconfig("self.course_list_container", width=canvas_width)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel) # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)   # Linux Up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)   # Linux Down

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Cross-platform mousewheel scrolling."""
        if self.canvas.winfo_exists():
            if event.num == 5 or event.delta == -120:
                self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:
                self.canvas.yview_scroll(-1, "units")

    # --- RENDERING LOGIC ---

    def render_dashboard(self, data):
        """Populates the Stats Bar and Course List."""
        profile = data.get("profile")
        courses = data.get("courses", [])
        stats = data.get("stats", {"students": 0, "courses": 0, "pending_grades": 0})

        # 1. Update Header
        if profile:
            self.welcome_lbl.config(text=f"Welcome, Prof. {profile.name}")

        # 2. Render Stats Cards
        for widget in self.stats_container.winfo_children(): widget.destroy()

        self._create_stat_card("Total Students", stats['students'], "#E3F2FD", "#1565C0") # Blue
        self._create_stat_card("Active Courses", stats['courses'], "#E8F5E9", "#2E7D32")  # Green
        self._create_stat_card("Pending Grading", stats['pending_grades'], "#FFF3E0", "#EF6C00") # Orange

        # 3. Render Course Cards
        for widget in self.course_list_container.winfo_children(): widget.destroy()

        if not courses:
            tk.Label(self.course_list_container, text="No active courses found.", 
                     font=FONTS["body"], bg=COLORS["background"], fg="gray").pack(pady=40)
            return

        for course in courses:
            self._create_rich_course_card(course)

    # --- UI HELPERS ---

    def _create_stat_card(self, title, value, bg_color, text_color):
        """Creates a colorful dashboard metric box."""
        card = tk.Frame(self.stats_container, bg=bg_color, padx=20, pady=15)
        card.pack(side="left", fill="y", expand=True, padx=(0, 20))
        
        # Value (Big)
        tk.Label(card, text=str(value), font=("Helvetica", 26, "bold"), bg=bg_color, fg=text_color).pack(anchor="w")
        # Title (Small)
        tk.Label(card, text=title.upper(), font=("Helvetica", 9, "bold"), bg=bg_color, fg=text_color, pady=2).pack(anchor="w")

    def _create_rich_course_card(self, course):
        """Creates a detailed card with metadata."""
        # Main Card Frame (White box with subtle border)
        card = tk.Frame(self.course_list_container, bg="white", padx=25, pady=20)
        card.pack(fill="x", pady=(0, 15))
        
        # Border simulation
        card.config(highlightbackground="#E0E0E0", highlightthickness=1)

        # -- Top Row: Code, Name, Credits --
        header = tk.Frame(card, bg="white")
        header.pack(fill="x", pady=(0, 15))
        
        # Course Title
        tk.Label(header, text=f"{course.code} | {course.name}", font=FONTS["h2"], bg="white", fg=COLORS["primary"]).pack(side="left")
        
        # Credits Badge
        credits_val = getattr(course, 'credits', 3) 
        badge_frame = tk.Frame(header, bg="#F5F5F5", padx=10, pady=5)
        badge_frame.pack(side="right")
        tk.Label(badge_frame, text=f"{credits_val} Credits", bg="#F5F5F5", fg="#666", font=("Helvetica", 9, "bold")).pack()

        # -- Middle Row: Details (Grid-like info) --
        details = tk.Frame(card, bg="white")
        details.pack(fill="x", pady=(0, 20))

        # Helper to create detail columns
        def add_detail(label, value, icon):
            f = tk.Frame(details, bg="white")
            f.pack(side="left", padx=(0, 50))
            tk.Label(f, text=label, font=("Arial", 8, "bold"), fg="#999", bg="white").pack(anchor="w")
            tk.Label(f, text=f"{icon}  {value}", font=FONTS["body"], fg="#333", bg="white", pady=2).pack(anchor="w")

        # Safely get attributes or use defaults
        schedule = getattr(course, 'schedule', 'TBA')
        room = getattr(course, 'room', 'Virtual')
        enrolled = getattr(course, 'enrolled_count', 0)
        capacity = getattr(course, 'capacity', 40)

        add_detail("SCHEDULE", schedule, "🕒")
        add_detail("LOCATION", room, "📍")
        add_detail("ENROLLMENT", f"{enrolled} / {capacity} Students", "👥")

        # -- Bottom Row: Action Buttons --
        actions = tk.Frame(card, bg="white")
        actions.pack(fill="x")

        # 1. Manage (Primary)
        self._create_btn(actions, "📝 Grade Center", COLORS["primary"], "white", 
                         lambda: self.router.navigate("instructor_grading", course_id=course.id))

        # 2. View Roster (Secondary)
        self._create_btn(actions, "👥 Roster", "#F0F0F0", COLORS["text"], 
                         lambda: self.show_students_popup(course.id))

        # 3. Settings (NEW - Added this button)
        self._create_btn(actions, "⚙️ Settings", "#F0F0F0", COLORS["text"], 
                         lambda: self.router.navigate("course_editor", course_id=course.id))

        # 4. Drop (Danger - Right Aligned)
        drop_btn = tk.Button(actions, text="Drop Course", bg="white", fg="#D32F2F", font=("Helvetica", 9, "bold"),
                             relief="flat", cursor="hand2", 
                             command=lambda: self.confirm_drop(course.id))
        drop_btn.pack(side="right")

    def _create_btn(self, parent, text, bg, fg, command):
        """Helper for nice flat buttons."""
        btn = tk.Button(parent, text=text, bg=bg, fg=fg, font=FONTS["button"], 
                        padx=15, pady=8, relief="flat", cursor="hand2", command=command)
        btn.pack(side="left", padx=(0, 10))
        return btn

    # --- INTERACTIONS ---

    def show_students_popup(self, course_id):
        self.controller.get_course_students(course_id, self.render_students_list)

    def confirm_drop(self, course_id):
        if messagebox.askyesno("Unassign Course", "Are you sure you want to stop teaching this course?"):
            self.controller.drop_teaching_course(
                course_id, 
                lambda result: self.controller.load_dashboard_data(self.render_dashboard) if result else None
            )

    def render_students_list(self, students):
        """Creates a popup window to display enrollment details."""
        popup = tk.Toplevel(self)
        popup.title("Class Roster")
        popup.geometry("400x500")
        popup.configure(bg="white")

        tk.Label(popup, text=f"Enrolled Students ({len(students)})", font=FONTS["h2"], bg="white", fg=COLORS["primary"]).pack(pady=20)
        
        list_frame = tk.Frame(popup, bg="white")
        list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        if not students:
            tk.Label(list_frame, text="No students enrolled yet.", bg="white", font=FONTS["caption"]).pack()
            return

        for i, s in enumerate(students):
            # Striping effect (alternating row colors)
            row_bg = "#F9F9F9" if i % 2 == 0 else "white"
            
            row = tk.Frame(list_frame, bg=row_bg, pady=8, padx=10)
            row.pack(fill="x")
            
            # Using .get() for safety since student data might be a dict
            name = s.get('name', 'Unknown')
            major = s.get('major', 'N/A')
            
            tk.Label(row, text=name, font=FONTS["body_bold"], bg=row_bg).pack(side="left")
            tk.Label(row, text=major, font=FONTS["caption"], fg="gray", bg=row_bg).pack(side="right")