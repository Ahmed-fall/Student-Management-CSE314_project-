import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class InstructorGradingView(BaseView):
    def __init__(self, parent, router, *args, **kwargs):
        self.course_id = kwargs.get("course_id")
        super().__init__(parent, router, *args, **kwargs)

    def create_controller(self):
        from controllers.instructor_controller import InstructorController
        controller = InstructorController(self.router)
        if self.course_id:
            controller.current_managed_course_id = self.course_id
        return controller

    def setup_ui(self):
        # --- Main Layout ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # Content Area
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=20, pady=20)
        self.content.pack(side="right", fill="both", expand=True)

        # Page Title
        tk.Label(self.content, text="📝 Grading & Assignment Center", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 10))

        # =================================================================
        # SECTION 1: ASSIGNMENTS LIST
        # =================================================================
        
        # Header Container (Label + Buttons)
        top_header = tk.Frame(self.content, bg=COLORS["background"])
        top_header.pack(fill="x", pady=(0, 5))

        tk.Label(top_header, text="Step 1: Select an Assignment", font=FONTS["h2"], bg=COLORS["background"]).pack(side="left")
        
        # Action Buttons (Delete & New)
        btn_frame = tk.Frame(top_header, bg=COLORS["background"])
        btn_frame.pack(side="right")

        tk.Button(btn_frame, text="🗑️ Delete Selected", command=self.handle_delete_assignment,
                  bg=COLORS["danger"], fg="white", font=FONTS["small"]).pack(side="left", padx=(0, 10))

        tk.Button(btn_frame, text="➕ New Assignment", command=self.open_assignment_popup,
                  bg=COLORS["secondary"], fg="white", font=FONTS["small_bold"]).pack(side="left")

        # Assignment Table
        assign_frame = tk.Frame(self.content, bg="white", height=150)
        assign_frame.pack(fill="x", pady=5)
        
        self.assign_tree = ttk.Treeview(assign_frame, columns=("id", "title", "due"), show="headings", height=5)
        self.assign_tree.heading("id", text="ID")
        self.assign_tree.heading("title", text="Title")
        self.assign_tree.heading("due", text="Due Date")
        self.assign_tree.column("id", width=50, anchor="center")
        self.assign_tree.column("title", width=400)
        self.assign_tree.column("due", width=150, anchor="center")
        self.assign_tree.pack(side="left", fill="both", expand=True)
        
        self.assign_tree.bind("<<TreeviewSelect>>", self.on_assignment_select)

        # =================================================================
        # SPLIT VIEW: SUBMISSIONS (Left) & GRADING (Right)
        # =================================================================
        bottom_frame = tk.Frame(self.content, bg=COLORS["background"])
        bottom_frame.pack(fill="both", expand=True, pady=20)

        # --- SECTION 2: SUBMISSIONS LIST (Left) ---
        sub_container = tk.Frame(bottom_frame, bg=COLORS["background"])
        sub_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(sub_container, text="Step 2: Select a Student", font=FONTS["h2"], bg=COLORS["background"]).pack(anchor="w")
        
        self.sub_tree = ttk.Treeview(sub_container, columns=("id", "student", "grade"), show="headings")
        self.sub_tree.heading("id", text="ID")
        self.sub_tree.heading("student", text="Student Name")
        self.sub_tree.heading("grade", text="Grade")
        self.sub_tree.column("id", width=50, anchor="center")
        self.sub_tree.pack(fill="both", expand=True)
        
        self.sub_tree.bind("<<TreeviewSelect>>", self.on_submission_select)

        # --- SECTION 3: GRADING FORM & WORK DISPLAY (Right) ---
        grade_container = tk.Frame(bottom_frame, bg="white", padx=20, pady=20, relief="raised")
        grade_container.pack(side="right", fill="both", expand=True, ipadx=10)

        tk.Label(grade_container, text="Step 3: Grade Work", font=FONTS["h2"], bg="white", fg=COLORS["primary"]).pack(pady=(0,15))

        tk.Label(grade_container, text="Student's Submitted Work:", bg="white", font=FONTS["small_bold"]).pack(anchor="w")
        
        # Text widget is DISABLED by default so instructor cannot edit student's work accidentally
        self.work_display = tk.Text(grade_container, height=10, width=40, font=FONTS["body"], bg="#f9f9f9", state="disabled")
        self.work_display.pack(fill="both", expand=True, pady=(0, 15))

        # Score Input
        tk.Label(grade_container, text="Score (0-100):", bg="white", font=FONTS["small_bold"]).pack(anchor="w")
        self.score_ent = tk.Entry(grade_container, font=FONTS["body"])
        self.score_ent.pack(fill="x", pady=(0, 10))

        # Feedback Input
        tk.Label(grade_container, text="Feedback:", bg="white", font=FONTS["small_bold"]).pack(anchor="w")
        self.feedback_ent = tk.Text(grade_container, height=4, width=30, font=FONTS["small"])
        self.feedback_ent.pack(fill="x", pady=(0, 15))

        # Save Button
        tk.Button(grade_container, text="💾 Save Grade", command=self.submit_grade,
                  bg=COLORS["secondary"], fg="white", font=FONTS["button"]).pack(fill="x", side="bottom")

        # Initial Load
        self.refresh_assignments()

    # ------------------------------------------------------------------
    # DATA LOADING & SELECTION LOGIC
    # ------------------------------------------------------------------

    def refresh_assignments(self):
        """Reloads assignments from the controller."""
        if self.course_id:
            self.controller.load_course_editor_data(self.course_id, self.update_assignment_list)
        else:
            messagebox.showerror("Error", "No course selected context.")
            self.router.go_back()

    def update_assignment_list(self, data):
        """Callback to populate the top table."""
        assignments = data.get("assignments", [])
        self.assignments_map = {}

        for item in self.assign_tree.get_children():
            self.assign_tree.delete(item)
            
        for a in assignments:
            self.assignments_map[a.id] = a
            self.assign_tree.insert("", "end", values=(a.id, a.title, a.due_date))

    def on_assignment_select(self, event):
        """When assignment is clicked, load the submissions queue."""
        selected = self.assign_tree.selection()
        if not selected: return
        
        assign_id_str = self.assign_tree.item(selected[0], "values")[0]
        assign_id = int(assign_id_str) 

        self.current_assignment_id = assign_id
        
        # Clear previous student data from UI
        self.clear_grading_form()
        
        # Call Controller
        self.controller.load_assignment_submissions(assign_id, self.update_submission_list)

    def update_submission_list(self, submissions):
        """Callback to populate the bottom-left table."""
        for item in self.sub_tree.get_children():
            self.sub_tree.delete(item)
            
        self.submissions_map = {} 
        
        for sub in submissions:
            grade_display = sub['grade_value'] if sub['grade_value'] is not None else "Pending"
            row_id = self.sub_tree.insert("", "end", values=(sub['submission_id'], sub['student_name'], grade_display))
            self.submissions_map[row_id] = sub

    def on_submission_select(self, event):
        """
        When a student is selected:
        1. Fetch data from map.
        2. Unlock text box -> Write Content -> Lock text box.
        3. Fill existing grade/feedback.
        """
        selected = self.sub_tree.selection()
        if not selected: return
        
        data = self.submissions_map.get(selected[0])
        if not data: return
        
        self.current_submission_id = data['submission_id']
        
        # --- 1. Display Student Work ---
        self.work_display.config(state="normal") # Enable editing to insert text
        self.work_display.delete("1.0", tk.END)
        
        content = data.get('submission_content')
        if content:
            self.work_display.insert("1.0", content)
        else:
            self.work_display.insert("1.0", "[Student submitted no text content or file]")
            
        self.work_display.config(state="disabled") # Disable again

        # --- 2. Fill Grade Form ---
        self.score_ent.delete(0, tk.END)
        if data['grade_value'] is not None:
            self.score_ent.insert(0, str(data['grade_value']))
            
        self.feedback_ent.delete("1.0", tk.END)
        if data.get('feedback'):
            self.feedback_ent.insert("1.0", data['feedback'])

    def clear_grading_form(self):
        """Helper to clear the right-side panel."""
        self.work_display.config(state="normal")
        self.work_display.delete("1.0", tk.END)
        self.work_display.config(state="disabled")
        self.score_ent.delete(0, tk.END)
        self.feedback_ent.delete("1.0", tk.END)
        if hasattr(self, 'current_submission_id'):
            del self.current_submission_id

    # ------------------------------------------------------------------
    # ACTIONS: GRADING & DELETING
    # ------------------------------------------------------------------

    def submit_grade(self):
        if not hasattr(self, 'current_submission_id') or not self.current_submission_id:
            messagebox.showwarning("Error", "Select a student first.")
            return
            
        score_input = self.score_ent.get().strip()
        feedback = self.feedback_ent.get("1.0", tk.END).strip()
        
        # Validation
        try:
            score_val = float(score_input)
        except ValueError:
            messagebox.showerror("Error", "Score must be a valid number.")
            return

        current_assignment = self.assignments_map.get(self.current_assignment_id)
        if current_assignment:
            max_limit = current_assignment.max_score
            if score_val > max_limit:
                messagebox.showerror("Invalid Grade", f"Score cannot exceed max of {max_limit}.")
                return
            if score_val < 0:
                messagebox.showerror("Invalid Grade", "Score cannot be negative.")
                return

        # Submit to Controller
        self.controller.submit_grade(self.current_submission_id, score_input, feedback, self.on_grade_success)

    def on_grade_success(self, result):
        if result:
            messagebox.showinfo("Success", "Grade Saved!")
            # Refresh the list to show the new grade in the table
            self.controller.load_assignment_submissions(self.current_assignment_id, self.update_submission_list)

    def handle_delete_assignment(self):
        """Deletes the selected assignment."""
        selected = self.assign_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an assignment to delete.")
            return

        assign_id = int(self.assign_tree.item(selected[0], "values")[0])
        
        if messagebox.askyesno("Confirm Delete", "Are you sure? This will delete the assignment and ALL student submissions associated with it."):
            self.controller.delete_assignment(assign_id, self.on_delete_success)

    def on_delete_success(self, result):
        if result:
            messagebox.showinfo("Deleted", "Assignment deleted successfully.")
            self.refresh_assignments()
            # Clear the submissions view as the assignment is gone
            for item in self.sub_tree.get_children(): 
                self.sub_tree.delete(item)
            self.clear_grading_form()

    # ------------------------------------------------------------------
    # POPUP: CREATE ASSIGNMENT
    # ------------------------------------------------------------------

    def open_assignment_popup(self):
        """Opens the form with Dropdown Menus."""
        self.popup = tk.Toplevel(self)
        self.popup.title("New Assignment")
        self.popup.geometry("400x550")
        self.popup.configure(bg=COLORS["background"])

        # 1. Title
        tk.Label(self.popup, text="Assignment Title", bg=COLORS["background"], font=FONTS["small_bold"]).pack(pady=(15,0))
        self.title_ent = tk.Entry(self.popup)
        self.title_ent.pack(fill="x", padx=20, pady=5)

        # 2. Description
        tk.Label(self.popup, text="Description", bg=COLORS["background"], font=FONTS["small_bold"]).pack(pady=(10,0))
        self.desc_ent = tk.Entry(self.popup)
        self.desc_ent.pack(fill="x", padx=20, pady=5)

        # 3. Due Date (Dropdowns)
        tk.Label(self.popup, text="Due Date", bg=COLORS["background"], font=FONTS["small_bold"]).pack(pady=(10,0))
        
        date_frame = tk.Frame(self.popup, bg=COLORS["background"])
        date_frame.pack(pady=5)
        
        years = [str(y) for y in range(2025, 2030)]
        self.year_var = tk.StringVar(value=years[0])
        ttk.Combobox(date_frame, textvariable=self.year_var, values=years, width=6, state="readonly").pack(side="left", padx=2)
        
        months = [f"{m:02d}" for m in range(1, 13)]
        self.month_var = tk.StringVar(value=months[0])
        ttk.Combobox(date_frame, textvariable=self.month_var, values=months, width=4, state="readonly").pack(side="left", padx=2)
        
        days = [f"{d:02d}" for d in range(1, 32)]
        self.day_var = tk.StringVar(value=days[0])
        ttk.Combobox(date_frame, textvariable=self.day_var, values=days, width=4, state="readonly").pack(side="left", padx=2)

        # 4. Type
        tk.Label(self.popup, text="Type", bg=COLORS["background"], font=FONTS["small_bold"]).pack(pady=(10,0))
        self.type_var = tk.StringVar(value="homework")
        ttk.Combobox(self.popup, textvariable=self.type_var, 
                     values=["quiz", "project", "homework", "exam"], state="readonly").pack(pady=5)

        # 5. Max Score
        tk.Label(self.popup, text="Max Score", bg=COLORS["background"], font=FONTS["small_bold"]).pack(pady=(10,0))
        self.score_var = tk.StringVar(value="100")
        ttk.Combobox(self.popup, textvariable=self.score_var, 
                     values=["10", "20", "25", "50", "100", "200"], state="readonly").pack(pady=5)

        # Save Button
        tk.Button(self.popup, text="✅ Post Assignment", 
                  command=self.handle_save_assignment,
                  bg=COLORS["primary"], fg="white", font=FONTS["button"]).pack(pady=30)

    def handle_save_assignment(self):
        # Construct Date
        date_str = f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"
        
        assignment_data = {
            'title': self.title_ent.get().strip(),
            'description': self.desc_ent.get().strip(),
            'due_date': date_str,
            'max_score': int(self.score_var.get()),
            'type': self.type_var.get()
        }

        # Validate
        if not assignment_data['title']:
            messagebox.showwarning("Error", "Title is required.")
            return

        # Send to Controller
        self.controller.create_assignment(self.course_id, assignment_data, self.on_save_success)

    def on_save_success(self, result):
        if result:
            messagebox.showinfo("Success", "Assignment Created!")
            self.popup.destroy()
            self.refresh_assignments()