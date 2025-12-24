import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from datetime import datetime
from ui.components.sidebar import Sidebar

class AssignmentDetailsView(BaseView):
    def __init__(self, parent, router, *args, **kwargs):
        self.assignment_id = kwargs.get("assignment_id")
        super().__init__(parent, router, *args, **kwargs)

    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # --- 1. Main Layout ---
        self.main_layout = tk.Frame(self, bg=COLORS["background"])
        self.main_layout.pack(fill="both", expand=True)

        self.sidebar = Sidebar(self.main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # Content Area (Right)
        self.content = tk.Frame(self.main_layout, bg=COLORS["background"], padx=40, pady=30)
        self.content.pack(side="right", fill="both", expand=True)

        # --- 2. Navigation & Header ---
        nav_frame = tk.Frame(self.content, bg=COLORS["background"])
        nav_frame.pack(fill="x", pady=(0, 15))

        # Back Button - Link Style
        btn_back = tk.Button(nav_frame, text="← Back to Assignments", 
                             command=self._go_back,
                             bg=COLORS["background"], 
                             fg=COLORS["placeholder"],      
                             activeforeground=COLORS["primary"], 
                             font=FONTS["small_bold"], 
                             bd=0, 
                             activebackground=COLORS["background"], 
                             cursor="hand2")
        btn_back.pack(anchor="w")

        # Title Row
        self.lbl_title = tk.Label(self.content, text="Loading...", font=FONTS["h1"], 
                                  bg=COLORS["background"], fg=COLORS["primary"], 
                                  wraplength=700, justify="left")
        self.lbl_title.pack(anchor="w", pady=(0, 10))

        # --- 3. Meta Data Ribbon (Card Style) ---
        self.meta_frame = tk.Frame(self.content, bg=COLORS["surface"], padx=20, pady=15)
        self.meta_frame.pack(fill="x", pady=(0, 20))

        self.meta_frame.configure(highlightbackground="#bdc3c7", highlightthickness=1) 

        # Labels inside the ribbon
        self.lbl_due = tk.Label(self.meta_frame, text="", font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"])
        self.lbl_due.pack(side="left", padx=(0, 20))

        self.lbl_points = tk.Label(self.meta_frame, text="", font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"])
        self.lbl_points.pack(side="left", padx=(0, 20))

        # Status Badge (Right aligned)
        self.lbl_status = tk.Label(self.meta_frame, text="Loading...", font=FONTS["small_bold"], 
                                   bg=COLORS["background"], fg=COLORS["text"], padx=10, pady=4)
        self.lbl_status.pack(side="right")

        # --- 4. Grade Result Section (Hidden by default) ---
        self.grade_frame = tk.Frame(self.content, bg=COLORS["surface"], padx=20, pady=20)
        self.grade_frame.configure(highlightbackground=COLORS["success"], highlightthickness=2)

        # --- 5. Instructions Section ---
        self.frame_instr = tk.LabelFrame(self.content, text="Instructions", font=FONTS["h2"], 
                                         bg=COLORS["background"], fg=COLORS["primary"], 
                                         padx=15, pady=15, relief="flat")
        self.frame_instr.pack(fill="x", pady=(0, 20))

        self.txt_desc = tk.Text(self.frame_instr, height=5, font=FONTS["body"], 
                                bg=COLORS["background"], fg=COLORS["text"],
                                bd=0, highlightthickness=0, wrap="word")
        self.txt_desc.pack(fill="both", expand=True)
        self.txt_desc.config(state="disabled")

        # --- 6. Submission Section ---
        self.frame_sub = tk.LabelFrame(self.content, text="Your Work", font=FONTS["h2"], 
                                       bg=COLORS["background"], fg=COLORS["primary"], 
                                       padx=15, pady=15, relief="flat")
        self.frame_sub.pack(fill="both", expand=True)

        # [IMPROVEMENT] Container for Text + Scrollbar
        txt_container = tk.Frame(self.frame_sub, bg=COLORS["surface"])
        txt_container.pack(fill="both", expand=True, pady=(0, 15))

        # Scrollbar
        self.scroll_sub = ttk.Scrollbar(txt_container)
        self.scroll_sub.pack(side="right", fill="y")

        # Text Area
        self.txt_submission = tk.Text(txt_container, height=10, font=FONTS["body"], 
                                      bg=COLORS["surface"], fg=COLORS["text"],
                                      relief="flat", 
                                      highlightbackground=COLORS["placeholder"], highlightthickness=1,
                                      padx=10, pady=10,
                                      yscrollcommand=self.scroll_sub.set)
        self.txt_submission.pack(side="left", fill="both", expand=True)
        
        # Link scrollbar to text
        self.scroll_sub.config(command=self.txt_submission.yview)

        # Action Button
        btn_container = tk.Frame(self.frame_sub, bg=COLORS["background"])
        btn_container.pack(fill="x")
        
        self.btn_submit = ttk.Button(btn_container, text="Turn In Assignment", style="Primary.TButton",
                                     command=self.submit_work, cursor="hand2")
        self.btn_submit.pack(side="right")

        # --- Load Data ---
        if self.assignment_id:
            self.controller.load_assignment_details(self.assignment_id, self.update_ui)
        else:
            self._go_back()

    def update_ui(self, data):
        if not data:
            messagebox.showerror("Error", "Could not load data.")
            self._go_back()
            return

        asm = data["assignment"]
        sub = data["submission"]
        grade = data["grade"]

        # 1. Basic Info
        self.lbl_title.config(text=asm.title)
        self.lbl_due.config(text=f"📅 Due: {asm.due_date}")
        self.lbl_points.config(text=f"🏆 Max Points: {asm.max_score}")

        # 2. Instructions
        self.txt_desc.config(state="normal")
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", asm.description or "No instructions provided.")
        self.txt_desc.config(state="disabled")

        # 3. Determine Logic State
        now = datetime.now()
        try:
            due_dt = datetime.fromisoformat(asm.due_date)
            if due_dt.hour == 0 and due_dt.minute == 0:
                due_dt = due_dt.replace(hour=23, minute=59, second=59)
            is_overdue = now > due_dt
        except ValueError:
            is_overdue = False

        # --- UI STATE MACHINE ---
        
        # A. GRADED
        if grade:
            self.set_status_badge("GRADED", COLORS["success"], "white") 
            self.show_grade_card(grade, asm.max_score)
            
            self.txt_submission.insert("1.0", sub.content)
            self.txt_submission.config(state="disabled", bg=COLORS["background"])
            self.btn_submit.pack_forget()

        # B. SUBMITTED (But not graded)
        elif sub:
            self.txt_submission.insert("1.0", sub.content)
            
            if is_overdue:
                self.set_status_badge("SUBMITTED (LATE)", "#f39c12", "white") 
                self.txt_submission.config(state="disabled", bg=COLORS["background"])
                self.btn_submit.config(text="Deadline Passed", state="disabled")
            else:
                self.set_status_badge("SUBMITTED", COLORS["secondary"], "white") # Teal
                self.btn_submit.config(text="Update Submission")

        # C. NOT SUBMITTED
        else:
            if is_overdue:
                self.set_status_badge("MISSING", COLORS["danger"], "white") # Red
                self.txt_submission.insert("1.0", "This assignment is overdue and can no longer be submitted.")
                self.txt_submission.config(state="disabled", bg="#fadbd8", fg=COLORS["danger"]) 
                self.btn_submit.config(text="Locked", state="disabled")
            else:
                self.set_status_badge("OPEN", "#BDC3C7", COLORS["text"]) # Light Gray badge
                self.btn_submit.config(text="Turn In Assignment")

    def show_grade_card(self, grade, max_score):
        """Displays the graded result prominently."""
        self.grade_frame.pack(fill="x", pady=(0, 20), after=self.meta_frame)
        
        # Grade Value
        lbl_score = tk.Label(self.grade_frame, text=f"Grade: {grade.grade_value} / {max_score}", 
                             font=("Helvetica", 18, "bold"), bg=COLORS["surface"], fg=COLORS["success"])
        lbl_score.pack(anchor="w")

        # Feedback Title
        tk.Label(self.grade_frame, text="Instructor Feedback:", font=FONTS["small_bold"], 
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(anchor="w", pady=(10, 0))
        
        # Feedback Text
        lbl_feed = tk.Label(self.grade_frame, text=grade.feedback or "No feedback provided.", 
                            font=FONTS["body"], bg=COLORS["surface"], fg=COLORS["text"],
                            wraplength=700, justify="left")
        lbl_feed.pack(anchor="w")

    def set_status_badge(self, text, bg, fg):
        self.lbl_status.config(text=text, bg=bg, fg=fg)

    def submit_work(self):
        content = self.txt_submission.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Validation", "You cannot submit empty work.")
            return

        if messagebox.askyesno("Confirm", "Are you ready to turn this in?"):
            self.controller.submit_assignment(self.assignment_id, content, self.on_submit_complete)

    def on_submit_complete(self, result):
        if result:
            messagebox.showinfo("Success", "Assignment submitted successfully!")
            self.router.navigate("student_assignments")
        else:
            messagebox.showerror("Error", "Submission failed.")

    def _go_back(self):
        self.router.navigate("student_assignments")