import tkinter as tk
from tkinter import ttk, messagebox
import platform
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentGradesView(BaseView):
    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # --- 1. Layout & Styling ---
        self.configure_treeview_style() # Apply custom table styles

        main_layout = tk.Frame(self, bg=COLORS["background"])
        main_layout.pack(fill="both", expand=True)

        # Sidebar
        Sidebar(main_layout, self.controller).pack(side="left", fill="y")

        # Content Area
        content = tk.Frame(main_layout, bg=COLORS["background"], padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)

        # Header
        header_frame = tk.Frame(content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="📊 My Grades & Feedback", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # Refresh Button
        ttk.Button(header_frame, text="↻ Refresh", style="Secondary.TButton",
                   command=lambda: self.controller.load_grades(self.update_table)).pack(side="right")

        # --- 2. The Grade Table (Treeview) ---
        # Container for Treeview + Scrollbar
        table_frame = tk.Frame(content, bg=COLORS["background"])
        table_frame.pack(fill="both", expand=True)

        columns = ("course", "title", "date", "grade", "status")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, selectmode="browse")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Define Headings
        self.tree.heading("course", text="Course Code")
        self.tree.heading("title", text="Assignment Name")
        self.tree.heading("date", text="Submitted Date")
        self.tree.heading("grade", text="Score")
        self.tree.heading("status", text="Status")
        
        # Define Columns (widths & alignment)
        self.tree.column("course", width=100, anchor="center")
        self.tree.column("title", width=300, anchor="w")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("grade", width=100, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        # Tag Configurations for Color Coding
        self.tree.tag_configure("graded", foreground=COLORS["success"])  # Green text
        self.tree.tag_configure("pending", foreground=COLORS["text"])    # Standard text
        self.tree.tag_configure("missing", foreground=COLORS["danger"])  # Red text
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind Double Click to show details
        self.tree.bind("<Double-1>", self.on_row_double_click)

        # [NEW] Robust Mousewheel Support
        self._setup_scroll_bindings(self.tree)

        # Help Text
        tk.Label(content, text="* Double-click a row to view full feedback.", 
                 font=FONTS["small"], bg=COLORS["background"], fg=COLORS["placeholder"]).pack(anchor="w", pady=10)

        # --- 3. Load Data ---
        self.controller.load_grades(self.update_table)

    # --- ROBUST SCROLLING LOGIC ---
    def _setup_scroll_bindings(self, widget):
        """Attaches robust scroll listeners to a widget."""
        widget.bind('<Enter>', lambda e: self._bind_mousewheel(widget))
        widget.bind('<Leave>', lambda e: self._unbind_mousewheel(widget))

    def _bind_mousewheel(self, widget):
        self.active_scroll_widget = widget 
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
        self._unbind_mousewheel(self.tree)
        super().destroy()

    def configure_treeview_style(self):
        """Sets up a modern look for the Treeview widget."""
        style = ttk.Style()
        
        # Header Style
        style.configure("Treeview.Heading", 
                        font=FONTS["body_bold"], 
                        foreground=COLORS["text"],
                        padding=(0, 10)) 
        
        # Row Style
        style.configure("Treeview", 
                        font=FONTS["body"], 
                        rowheight=35,           
                        background=COLORS["surface"], 
                        fieldbackground=COLORS["surface"],
                        borderwidth=0)
        
        # Selection Color
        style.map('Treeview', 
                  background=[('selected', COLORS["primary"])],
                  foreground=[('selected', 'white')])

    def update_table(self, grades_data):
        """Populates the table with data from the controller."""
        # 1. Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not grades_data:
            return

        # 2. Store data references for the popup later
        self.current_data = grades_data 

        # 3. Insert new rows
        for index, item in enumerate(grades_data):
            # Parse Data
            course_code = item.get('course_code', '---')
            title = item.get('assignment_title', 'Untitled')
            
            # Date Formatting
            raw_date = str(item.get('submitted_at', ''))
            date_display = raw_date.replace("T", " ")[:10] if raw_date and raw_date != "None" else "-"
            
            # Grade Formatting
            grade_val = item.get('grade')
            max_val = item.get('max_score', 100)
            grade_display = f"{grade_val} / {max_val}" if grade_val is not None else "--"
            
            # Status Logic
            status = item.get('status', 'Pending').title()
            
            # Determine Tag for Color
            tag = "pending"
            if "Graded" in status: tag = "graded"
            elif "Missing" in status or "Overdue" in status: tag = "missing"

            # Insert Row (Store the index in 'iid' so we can find the data object later)
            self.tree.insert("", tk.END, iid=index, values=(
                course_code,
                title,
                date_display,
                grade_display,
                status
            ), tags=(tag,))

    def on_row_double_click(self, event):
        """Opens a popup with full feedback when a row is clicked."""
        selected_id = self.tree.selection()
        
        if not selected_id:
            return

        # Get the index from the IID
        try:
            index = int(selected_id[0])
            data = self.current_data[index]

            # Prepare Message
            title = data.get('assignment_title', 'Assignment Details')
            grade = data.get('grade', '--')
            max_score = data.get('max_score', 100)
            feedback = data.get('feedback')
            
            if not feedback:
                feedback = "No written feedback provided."

            details = f"Assignment: {title}\n" \
                      f"Score: {grade} / {max_score}\n\n" \
                      f"--- Instructor Feedback ---\n{feedback}"

            messagebox.showinfo("Grade Details", details)
        except (ValueError, IndexError):
            pass