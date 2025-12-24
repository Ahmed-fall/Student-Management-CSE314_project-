import tkinter as tk
from tkinter import ttk
from datetime import datetime
import platform
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentDashboardView(BaseView):
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

        # --- 2. Scrollable Canvas for Dashboard Content ---
        container = tk.Frame(self.main_layout, bg=COLORS["background"])
        container.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=COLORS["background"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.content = tk.Frame(self.canvas, bg=COLORS["background"], padx=30, pady=30)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind resizing
        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        # [NEW] Robust Mousewheel Support
        self._setup_scroll_bindings(self.canvas)

        # --- 3. Header Section ---
        self.create_header()

        # --- 4. KPI Cards Section ---
        # Grid layout for equal width cards
        self.kpi_frame = tk.Frame(self.content, bg=COLORS["background"])
        self.kpi_frame.pack(fill="x", pady=(0, 30))
        
        # Configure grid weights for 4 columns
        for i in range(4):
            self.kpi_frame.columnconfigure(i, weight=1, uniform="kpi_group")

        # Initialize StringVars
        self.gpa_var = tk.StringVar(value="--")
        self.credits_var = tk.StringVar(value="--")
        self.courses_var = tk.StringVar(value="--")
        self.notifs_var = tk.StringVar(value="--")

        # Create the Cards (Colors aligned with theme or distinct indicators)
        self.create_kpi_card(0, "Current GPA", self.gpa_var, COLORS["danger"], "📈")
        self.create_kpi_card(1, "Credits Earned", self.credits_var, "#3498db", "🎓") 
        self.create_kpi_card(2, "Active Courses", self.courses_var, COLORS["success"], "📚")
        self.create_kpi_card(3, "Notifications", self.notifs_var, "#f39c12", "🔔") 

        # --- 5. Upcoming Deadlines Section ---
        tk.Label(self.content, text="📅 Upcoming Deadlines (Next 7 Days)", font=FONTS["h2"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 15))
        
        self.deadline_container = tk.Frame(self.content, bg=COLORS["background"])
        self.deadline_container.pack(fill="x")
        
        # Loading State
        self.loading_lbl = tk.Label(self.deadline_container, text="Loading data...", 
                                    font=FONTS["body"], bg=COLORS["background"], fg=COLORS["placeholder"])
        self.loading_lbl.pack(anchor="w")

        # --- Trigger Data Fetch ---
        self.controller.load_dashboard_data(self.update_view)

    # --- ROBUST SCROLLING LOGIC ---
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
        self._unbind_mousewheel(self.canvas)
        super().destroy()

    def create_header(self):
        """Creates the Welcome section."""
        header_frame = tk.Frame(self.content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 30))

        self.welcome_var = tk.StringVar(value="Welcome back!")
        self.details_var = tk.StringVar(value="Loading profile...")

        # Welcome Text
        tk.Label(header_frame, textvariable=self.welcome_var, font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w")

        # Details Text
        tk.Label(header_frame, textvariable=self.details_var, font=FONTS["body"], 
                 bg=COLORS["background"], fg=COLORS["placeholder"]).pack(anchor="w", pady=(5, 0))
        
        # Separator line
        tk.Frame(self.content, bg=COLORS["placeholder"], height=1).pack(fill="x", pady=(0, 20))

    def create_kpi_card(self, col_index, title, variable, color, icon):
        """Creates a nice card inside the grid."""
        # Outer wrapper for padding/margins
        wrapper = tk.Frame(self.kpi_frame, bg=COLORS["background"], padx=5) # horizontal spacing
        wrapper.grid(row=0, column=col_index, sticky="nsew")

        # The Card itself
        card = tk.Frame(wrapper, bg=COLORS["surface"], padx=20, pady=20)
        card.pack(fill="both", expand=True)
        # [POLISH] Border for definition
        card.configure(highlightbackground=COLORS["placeholder"], highlightthickness=1)

        # Top Color Strip
        tk.Frame(card, bg=color, height=4).pack(fill="x", side="top")
        tk.Frame(card, bg=COLORS["surface"], height=10).pack() # Spacer

        # Title & Icon
        header = tk.Frame(card, bg=COLORS["surface"])
        header.pack(fill="x")
        tk.Label(header, text=title, font=FONTS["small_bold"], fg=COLORS["placeholder"], bg=COLORS["surface"]).pack(side="left")
        tk.Label(header, text=icon, font=("Segoe UI Emoji", 12), bg=COLORS["surface"]).pack(side="right")

        # The Number
        tk.Label(card, textvariable=variable, font=("Helvetica", 22, "bold"), 
                 fg=COLORS["text"], bg=COLORS["surface"]).pack(anchor="w", pady=(10, 0))

    def update_view(self, data):
        """Called by Controller when data arrives."""
        
        # 1. Update Profile
        student = data.get("student", {})
        if student:
            name = student.get("name", "Student")
            major = student.get("major", "Undeclared")
            self.welcome_var.set(f"Hello, {name}! 👋")
            self.details_var.set(f"Student ID: {student.get('user_id', '--')}   |   Major: {major}")

        # 2. Update KPIs
        gpa = data.get("current_gpa_average", 0.0)
        self.gpa_var.set(f"{gpa:.2f}")
        
        courses_count = data.get("enrolled_courses_count", 0)
        self.courses_var.set(str(courses_count))
        self.credits_var.set(str(courses_count * 3)) # Assuming 3 credits per course
        self.notifs_var.set(str(data.get("unread_notifications", 0)))

        # 3. Update Deadlines
        self.loading_lbl.destroy() # Remove loading text
        
        # Clear old rows
        for widget in self.deadline_container.winfo_children():
            widget.destroy()

        deadlines = data.get("upcoming_deadlines", [])

        if not deadlines:
            self._create_empty_state()
        else:
            for item in deadlines:
                self._create_deadline_row(item)

    def _create_deadline_row(self, item):
        course_code = item.get('course_code', '???')
        title = item.get('title', 'Assignment')
        raw_date = item.get('due_date')
        
        # Format Date nicely
        display_date = "No Date"
        urgency_color = COLORS["success"] # Default Green
        
        if raw_date:
            try:
                dt_obj = datetime.fromisoformat(str(raw_date).replace(" ", "T")) 
                display_date = dt_obj.strftime("%b %d, %I:%M %p")
                
                # Simple Urgency Logic
                days_left = (dt_obj - datetime.now()).days
                if days_left < 0: urgency_color = COLORS["danger"] # Overdue
                elif days_left < 2: urgency_color = "#f39c12" # Orange (Soon)
            except:
                display_date = str(raw_date)

        # Container
        row = tk.Frame(self.deadline_container, bg=COLORS["surface"], height=60)
        row.pack(fill="x", pady=(0, 10))
        row.pack_propagate(False) # Force height
        
        # [POLISH] Border
        row.configure(highlightbackground=COLORS["placeholder"], highlightthickness=1)

        # Color Strip (Left)
        tk.Frame(row, bg=urgency_color, width=6).pack(side="left", fill="y")

        # Content Frame
        content = tk.Frame(row, bg=COLORS["surface"], padx=15)
        content.pack(side="left", fill="both", expand=True)

        # Title
        tk.Label(content, text=f"{course_code} - {title}", font=FONTS["body_bold"], 
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", pady=(10, 2))
        
        # Date
        tk.Label(content, text=f"Due: {display_date}", font=FONTS["small"], 
                 bg=COLORS["surface"], fg=COLORS["placeholder"]).pack(anchor="w")

        # Action Button
        # Note: 'student_assignments' is not defined in the original router map we discussed,
        # but I will leave it here. If you need that view created, let me know.
        tk.Button(row, text="View", font=FONTS["small_bold"], 
                  bg=COLORS["background"], fg=COLORS["primary"], bd=0, cursor="hand2",
                  command=lambda: self.controller.navigate("student_assignments")
                  ).pack(side="right", padx=20)

    def _create_empty_state(self):
        frame = tk.Frame(self.deadline_container, bg=COLORS["surface"], pady=30)
        frame.pack(fill="x")
        # [POLISH] Border
        frame.configure(highlightbackground=COLORS["placeholder"], highlightthickness=1)
        
        tk.Label(frame, text="🎉 No immediate deadlines!", font=FONTS["h2"], 
                 bg=COLORS["surface"], fg=COLORS["success"]).pack()
        tk.Label(frame, text="You are all caught up.", font=FONTS["body"], 
                 bg=COLORS["surface"], fg=COLORS["placeholder"]).pack()