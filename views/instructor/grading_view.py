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
        # --- Layout ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=20, pady=20)
        self.content.pack(side="right", fill="both", expand=True)

        # Title
        tk.Label(self.content, text="📝 Grading & Assignment Center", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(anchor="w", pady=(0, 10))

        # --- STEP 1: Assignments List ---
        
        # Header Container (Label + Button)
        top_header = tk.Frame(self.content, bg=COLORS["background"])
        top_header.pack(fill="x", pady=(0, 5))

        tk.Label(top_header, text="Step 1: Select an Assignment", font=FONTS["h2"], bg=COLORS["background"]).pack(side="left")
        
        # [NEW] Create Assignment Button
        tk.Button(top_header, text="➕ New Assignment", 
                  command=self.open_assignment_popup,
                  bg=COLORS["secondary"], fg="white", font=FONTS["small_bold"]).pack(side="right")

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
        
        # Bind Click Event
        self.assign_tree.bind("<<TreeviewSelect>>", self.on_assignment_select)

        # --- STEP 2 & 3 Container ---
        bottom_frame = tk.Frame(self.content, bg=COLORS["background"])
        bottom_frame.pack(fill="both", expand=True, pady=20)

        # --- STEP 2: Submissions List (Left) ---
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

        # --- STEP 3: Grading Form (Right) ---
        grade_container = tk.Frame(bottom_frame, bg="white", padx=20, pady=20, relief="raised")
        grade_container.pack(side="right", fill="y", ipadx=20)

        tk.Label(grade_container, text="Step 3: Grade Work", font=FONTS["h2"], bg="white", fg=COLORS["primary"]).pack(pady=(0,20))

        tk.Label(grade_container, text="Score (0-100):", bg="white").pack(anchor="w")
        self.score_ent = tk.Entry(grade_container, font=FONTS["body"])
        self.score_ent.pack(fill="x", pady=(0, 10))

        tk.Label(grade_container, text="Feedback:", bg="white").pack(anchor="w")
        self.feedback_ent = tk.Text(grade_container, height=5, width=30, font=FONTS["small"])
        self.feedback_ent.pack(pady=(0, 20))

        tk.Button(grade_container, text="💾 Save Grade", command=self.submit_grade,
                  bg=COLORS["secondary"], fg="white", font=FONTS["button"]).pack(fill="x")

        # Initial Load
        self.refresh_assignments()

    # ------------------------------------------------------------------
    # EXISTING LOGIC (Data Loading)
    # ------------------------------------------------------------------

    def refresh_assignments(self):
        if self.course_id:
            self.controller.load_course_editor_data(self.course_id, self.update_assignment_list)
        else:
            messagebox.showerror("Error", "No course selected context.")
            self.router.go_back()

    def update_assignment_list(self, data):
        """Fills the top table."""
        assignments = data.get("assignments", [])

        self.assignments_map = {}

        for item in self.assign_tree.get_children():
            self.assign_tree.delete(item)
            
        for a in assignments:
            self.assignments_map[a.id] = a
            self.assign_tree.insert("", "end", values=(a.id, a.title, a.due_date))

    def on_assignment_select(self, event):
        """When assignment is clicked, load submissions."""
        selected = self.assign_tree.selection()
        if not selected: return
        
        assign_id_str = self.assign_tree.item(selected[0], "values")[0]
        assign_id = int(assign_id_str) 

        self.current_assignment_id = assign_id
        
        # Call Controller to get submissions
        self.controller.load_assignment_submissions(assign_id, self.update_submission_list)

    def update_submission_list(self, submissions):
        """Fills the bottom-left table."""
        for item in self.sub_tree.get_children():
            self.sub_tree.delete(item)
            
        self.submissions_map = {} 
        
        for sub in submissions:
            grade_display = sub['grade_value'] if sub['grade_value'] is not None else "Pending"
            row_id = self.sub_tree.insert("", "end", values=(sub['submission_id'], sub['student_name'], grade_display))
            self.submissions_map[row_id] = sub

    def on_submission_select(self, event):
        """When student is clicked, fill the grading form."""
        selected = self.sub_tree.selection()
        if not selected: return
        
        data = self.submissions_map.get(selected[0])
        if not data: return
        
        self.current_submission_id = data['submission_id']
        
        # Fill Form
        self.score_ent.delete(0, tk.END)
        if data['grade_value'] is not None:
            self.score_ent.insert(0, str(data['grade_value']))
            
        self.feedback_ent.delete("1.0", tk.END)
        if data['feedback']:
            self.feedback_ent.insert("1.0", data['feedback'])

    def submit_grade(self):
        if not hasattr(self, 'current_submission_id') or not self.current_submission_id:
            messagebox.showwarning("Error", "Select a student first.")
            return
            
        score_input = self.score_ent.get().strip()
        feedback = self.feedback_ent.get("1.0", tk.END).strip()
        
        # 1. Number Validation
        try:
            score_val = float(score_input)
        except ValueError:
            messagebox.showerror("Error", "Score must be a valid number.")
            return

        # 2. Max Score Validation
        current_assignment = self.assignments_map.get(self.current_assignment_id)
        
        if current_assignment:
            max_limit = current_assignment.max_score
            if score_val > max_limit:
                messagebox.showerror("Invalid Grade", f"Score cannot exceed the maximum of {max_limit}.")
                return
            if score_val < 0:
                messagebox.showerror("Invalid Grade", "Score cannot be negative.")
                return
        else:
            print(f"Warning: Could not find assignment ID {self.current_assignment_id} in map.")

        # 3. Submit to Controller
        self.controller.submit_grade(self.current_submission_id, score_input, feedback, self.on_grade_success)


    def on_grade_success(self, result):
        if result:
            messagebox.showinfo("Success", "Grade Saved!")
            self.controller.load_assignment_submissions(self.current_assignment_id, self.update_submission_list)

    # ------------------------------------------------------------------
    # [NEW] CREATE ASSIGNMENT POPUP LOGIC
    # ------------------------------------------------------------------

    def open_assignment_popup(self):
            """Opens the form with Dropdown Menus instead of typing."""
            self.popup = tk.Toplevel(self)
            self.popup.title("New Assignment")
            self.popup.geometry("400x500")
            self.popup.configure(bg=COLORS["background"])

            # 1. Title (Still needs typing)
            tk.Label(self.popup, text="Assignment Title", bg=COLORS["background"]).pack(pady=(15,0))
            self.title_ent = tk.Entry(self.popup)
            self.title_ent.pack(fill="x", padx=20, pady=5)

            # 2. Description
            tk.Label(self.popup, text="Description", bg=COLORS["background"]).pack(pady=(10,0))
            self.desc_ent = tk.Entry(self.popup)
            self.desc_ent.pack(fill="x", padx=20, pady=5)

            # 3. Due Date (NOW A MENU)
            tk.Label(self.popup, text="Due Date", bg=COLORS["background"]).pack(pady=(10,0))
            
            date_frame = tk.Frame(self.popup, bg=COLORS["background"])
            date_frame.pack(pady=5)
            
            # Year Menu
            years = [str(y) for y in range(2025, 2030)]
            self.year_var = tk.StringVar(value=years[0])
            ttk.Combobox(date_frame, textvariable=self.year_var, values=years, width=5, state="readonly").pack(side="left", padx=2)
            
            # Month Menu
            months = [f"{m:02d}" for m in range(1, 13)]
            self.month_var = tk.StringVar(value=months[0])
            ttk.Combobox(date_frame, textvariable=self.month_var, values=months, width=3, state="readonly").pack(side="left", padx=2)
            
            # Day Menu
            days = [f"{d:02d}" for d in range(1, 32)]
            self.day_var = tk.StringVar(value=days[0])
            ttk.Combobox(date_frame, textvariable=self.day_var, values=days, width=3, state="readonly").pack(side="left", padx=2)

            # 4. Type (Already a Menu)
            tk.Label(self.popup, text="Type", bg=COLORS["background"]).pack(pady=(10,0))
            self.type_var = tk.StringVar(value="homework")
            ttk.Combobox(self.popup, textvariable=self.type_var, 
                        values=["quiz", "project", "homework", "exam"], state="readonly").pack(pady=5)

            # 5. Max Score (NOW A MENU)
            tk.Label(self.popup, text="Max Score", bg=COLORS["background"]).pack(pady=(10,0))
            self.score_var = tk.StringVar(value="100")
            ttk.Combobox(self.popup, textvariable=self.score_var, 
                        values=["10", "20", "25", "50", "100", "200"], state="readonly").pack(pady=5)

            # Save Button
            tk.Button(self.popup, text="✅ Post Assignment", 
                    command=self.handle_save_assignment,
                    bg=COLORS["primary"], fg="white", font=FONTS["button"]).pack(pady=30)

    def handle_save_assignment(self):
            # 1. Construct the Date from the 3 menus
            date_str = f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"
            
            # 2. Gather Data
            assignment_data = {
                'title': self.title_ent.get().strip(),
                'description': self.desc_ent.get().strip(),
                'due_date': date_str, # Using the menu result
                'max_score': int(self.score_var.get()), # Using the menu result
                'type': self.type_var.get()
            }

            # 3. Validate & Send
            if self.course_id and assignment_data['title']:
                self.controller.create_assignment(self.course_id, assignment_data, self.on_save_success)
            else:
                messagebox.showwarning("Error", "Title is required.")

    def on_save_success(self, result):
        if result:
            messagebox.showinfo("Success", "Assignment Created!")
            self.popup.destroy()
            self.refresh_assignments() # Updates the list immediately