import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class InstructorDashboardView(BaseView):
    """
    Primary landing page for Instructors.
    Displays profile information and a list of taught courses.
    """

    def create_controller(self):
        """Links the view to the specialized Instructor logic."""
        from controllers.instructor_controller import InstructorController
        return InstructorController(self.router)

    def setup_ui(self):
        # --- Main Container ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # --- Sidebar ---
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # --- Content Area ---
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=40, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        # 1. Header Section
        self.header_frame = tk.Frame(self.content, bg=COLORS["background"])
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.welcome_lbl = tk.Label(
            self.header_frame, 
            text="Instructor Dashboard", 
            font=FONTS["h1"], 
            bg=COLORS["background"], 
            fg=COLORS["primary"]
        )
        self.welcome_lbl.pack(side="left")

        # 2. Statistics Bar (New Feature)
        self.stats_container = tk.Frame(self.content, bg=COLORS["background"])
        self.stats_container.pack(fill="x", pady=(0, 30))

        # 3. Courses Section Header
        course_header = tk.Frame(self.content, bg=COLORS["background"])
        course_header.pack(fill="x", pady=(10, 10))
        
        tk.Label(course_header, text="Active Semesters", font=FONTS["h2"], bg=COLORS["background"]).pack(side="left")
        
        # 4. Scrollable Course List
        # We use a canvas to make the list scrollable if there are many courses
        self.canvas_frame = tk.Frame(self.content, bg=COLORS["background"])
        self.canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=COLORS["background"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.course_list_container = tk.Frame(self.canvas, bg=COLORS["background"])

        self.canvas.create_window((0, 0), window=self.course_list_container, anchor="nw", width=800) # Width matches layout
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.course_list_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # 5. Load Data
        self.controller.load_dashboard_data(self.render_dashboard)

        
    def render_dashboard(self, data):
        """Populates the Stats Bar and Course List."""
        profile = data.get("profile")
        courses = data.get("courses", [])
        stats = data.get("stats", {"students": 0, "courses": 0, "pending_grades": 0})

        # Update Header
        if profile:
            self.welcome_lbl.config(text=f"Welcome, Prof. {profile.name}")

        # --- Render Stats Cards ---
        for widget in self.stats_container.winfo_children(): widget.destroy()

        self._create_stat_card("Total Students", stats['students'], "#E3F2FD", "#1565C0") # Blue
        self._create_stat_card("Active Courses", stats['courses'], "#E8F5E9", "#2E7D32")  # Green
        self._create_stat_card("Pending Grading", stats['pending_grades'], "#FFF3E0", "#EF6C00") # Orange

        # --- Render Course Cards ---
        for widget in self.course_list_container.winfo_children(): widget.destroy()

        if not courses:
            tk.Label(self.course_list_container, text="No active courses found.", 
                     font=FONTS["body"], bg=COLORS["background"], fg="gray").pack(pady=40)
            return

        for course in courses:
            self._create_rich_course_card(course)

    
        
    def _create_stat_card(self, title, value, bg_color, text_color):
        """Helper to create those colorful boxes at the top."""
        card = tk.Frame(self.stats_container, bg=bg_color, padx=20, pady=15, width=200)
        card.pack(side="left", padx=(0, 20), fill="y")
        card.pack_propagate(False) # Forces size to respect width=200

        tk.Label(card, text=str(value), font=("Helvetica", 24, "bold"), bg=bg_color, fg=text_color).pack(anchor="w")
        tk.Label(card, text=title, font=FONTS["small_bold"], bg=bg_color, fg=text_color).pack(anchor="w")

    def _create_rich_course_card(self, course):
        """Creates a detailed card with metadata."""
        # Main Card Frame
        card = tk.Frame(self.course_list_container, bg="white", padx=20, pady=20, relief="flat")
        card.pack(fill="x", pady=(0, 15), padx=(0, 20)) # Spacing between cards

        # -- Top Row: Code, Name, Credits --
        header = tk.Frame(card, bg="white")
        header.pack(fill="x", pady=(0, 10))
        
        # Course Title
        tk.Label(header, text=f"{course.code} | {course.name}", font=FONTS["h2"], bg="white", fg=COLORS["primary"]).pack(side="left")
        
        # Credits Badge (Safe check in case 'credits' is missing from DB)
        credits_val = getattr(course, 'credits', 3) 
        badge = tk.Label(header, text=f"{credits_val} Credits", bg="#F5F5F5", fg="#666", padx=8, pady=4, font=FONTS["small"])
        badge.pack(side="right")

        # -- Middle Row: Details (Grid-like info) --
        details = tk.Frame(card, bg="white")
        details.pack(fill="x", pady=(5, 15))

        # Helper to create detail columns
        def add_detail(label, value, icon="📍"):
            f = tk.Frame(details, bg="white")
            f.pack(side="left", padx=(0, 40))
            tk.Label(f, text=label, font=("Arial", 8, "bold"), fg="#999", bg="white").pack(anchor="w")
            tk.Label(f, text=f"{icon}  {value}", font=FONTS["body"], fg="#333", bg="white").pack(anchor="w")

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
        actions.pack(fill="x", pady=(5, 0))

        # 1. Manage (Primary)
        tk.Button(actions, text="📝 Grade Center", bg=COLORS["primary"], fg="white", font=FONTS["button"], padx=15, pady=5,
                  command=lambda: self.router.navigate("instructor_grading", course_id=course.id)).pack(side="left", padx=(0, 10))

        # 2. View Roster (Secondary)
        tk.Button(actions, text="👥 Roster", bg="white", fg=COLORS["text"], font=FONTS["button"], padx=15, pady=5, relief="solid", borderwidth=1,
                  command=lambda: self.show_students_popup(course.id)).pack(side="left")

        # 3. Drop (Danger - pushed to far right)
        tk.Button(actions, text="Drop Course", bg="white", fg="red", font=FONTS["small"], relief="flat",
                  command=lambda: self.confirm_drop(course.id)).pack(side="right")

    def show_students_popup(self, course_id):
        """Triggers the controller to fetch and show student details."""
        self.controller.get_course_students(course_id, self.render_students_list)

    def confirm_drop(self, course_id):
            """Confirms and then calls the drop logic via controller."""
            if messagebox.askyesno("Unassign Course", "Are you sure you want to stop teaching this course?"):
                # We do NOT call 'setup_ui' because that draws a whole new screen on top.
                self.controller.drop_teaching_course(
                    course_id, 
                    lambda result: self.controller.load_dashboard_data(self.render_dashboard) if result else None
                )

    def refresh_view(self):
        """Clears the entire screen and rebuilds the UI."""
        # 1. Destroy all existing widgets (Sidebar, Content, etc.)
        for widget in self.winfo_children():
            widget.destroy()
        
        # 2. Re-run setup to build a fresh UI
        self.setup_ui()

    def render_students_list(self, students):
            """Creates a popup window to display enrollment details."""
            popup = tk.Toplevel(self)
            popup.title("Course Enrollment")
            popup.geometry("350x450")
            popup.configure(bg="white")

            tk.Label(popup, text=f"Enrolled Students ({len(students)})", font=FONTS["h2"], bg="white").pack(pady=15)
            
            list_frame = tk.Frame(popup, bg="white")
            list_frame.pack(fill="both", expand=True, padx=20, pady=10)

            for s in students:
                # FIX: Use dictionary syntax ['name'] instead of object syntax .name
                name = s.get('name', 'Unknown')
                major = s.get('major', 'N/A')
                
                lbl = tk.Label(list_frame, text=f"• {name} [{major}]", bg="white", font=FONTS["body"], anchor="w")
                lbl.pack(fill="x", pady=2)