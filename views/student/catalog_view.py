import tkinter as tk
from tkinter import ttk, messagebox
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentCatalogView(BaseView):
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
        
        tk.Label(header_frame, text="📚 Course Catalog", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # --- 3. Search Bar ---
        search_card = tk.Frame(self.content, bg=COLORS["surface"], padx=15, pady=15, relief="flat")
        search_card.pack(fill="x", pady=(0, 20))
        
        # Add a subtle border to the search bar
        search_card.configure(highlightbackground=COLORS["placeholder"], highlightthickness=1)
        
        tk.Label(search_card, text="Find a Course:", font=FONTS["body_bold"], 
                 bg=COLORS["surface"], fg=COLORS["text"]).pack(side="left", padx=(0, 10))

        self.search_entry = ttk.Entry(search_card, font=FONTS["body"], width=40)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        ttk.Button(search_card, text="Search", style="Primary.TButton", 
                   command=self.perform_search).pack(side="left")

        ttk.Button(search_card, text="Reset", style="Secondary.TButton", 
                   command=lambda: self.load_all()).pack(side="left", padx=10)

        # --- 4. Scrollable Container ---
        container = tk.Frame(self.content, bg=COLORS["background"])
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=COLORS["background"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.cards_frame = tk.Frame(self.canvas, bg=COLORS["background"])
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Event Bindings ---
        self.cards_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # BINDING LOGIC: Only bind scroll when hovering over the canvas
        self.canvas.bind('<Enter>', self._bind_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_mousewheel)

        # --- 5. Initial Load ---
        self.load_all()

    # --- SCROLLING LOGIC ---
    def _bind_mousewheel(self, event):
        """Enable scrolling when mouse enters the canvas area."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """Disable scrolling when mouse leaves."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Safe scrolling handler."""
        # 1. Check if canvas exists (fixes crash if view is destroyed)
        try:
            if not self.canvas.winfo_exists():
                return
        except Exception:
            return

        # 2. Perform Scroll
        try:
            if event.num == 5 or event.delta == -120:
                self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:
                self.canvas.yview_scroll(-1, "units")
        except tk.TclError:
            pass 

    def destroy(self):
        """Override destroy to ensure bindings are definitely removed."""
        self._unbind_mousewheel(None)
        super().destroy()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def load_all(self):
        self.search_entry.delete(0, tk.END)
        self.controller.load_catalog_data(self.display_courses)

    def perform_search(self):
        query = self.search_entry.get().strip()
        self.controller.load_catalog_data(self.display_courses, query)

    def display_courses(self, data):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        courses = data.get("courses", [])
        enrolled_ids = data.get("enrolled_ids", [])

        if not courses:
            tk.Label(self.cards_frame, text="No courses found matching your search.", 
                     font=FONTS["h2"], bg=COLORS["background"], fg=COLORS["placeholder"]).pack(pady=40)
            return

        for course in courses:
            self.create_course_card(course, course['id'] in enrolled_ids)

    def create_course_card(self, course, is_enrolled):
        card = tk.Frame(self.cards_frame, bg=COLORS["surface"], padx=20, pady=20)
        card.pack(fill="x", pady=(0, 15)) 
        card.configure(highlightbackground=COLORS["placeholder"], highlightthickness=1)

        info_frame = tk.Frame(card, bg=COLORS["surface"])
        info_frame.pack(side="left", fill="both", expand=True)

        header_text = f"{course.get('code', 'CODE')} - {course.get('name', 'Course Name')}"
        tk.Label(info_frame, text=header_text, font=FONTS["h2"], 
                 bg=COLORS["surface"], fg=COLORS["primary"], anchor="w").pack(fill="x")

        instructor = course.get("instructor_name", "Unknown Instructor")
        credits_num = course.get("credits", 3)
        meta_text = f"👨‍🏫 {instructor}   •   Credits: {credits_num}"
        
        tk.Label(info_frame, text=meta_text, font=FONTS["small_bold"], 
                 bg=COLORS["surface"], fg=COLORS["placeholder"], anchor="w").pack(fill="x", pady=(5, 5))

        desc = course.get("description", "No description available.")
        if len(desc) > 120: 
            desc = desc[:120] + "..."
            
        tk.Label(info_frame, text=desc, font=FONTS["body"], 
                 bg=COLORS["surface"], fg=COLORS["text"], 
                 anchor="w", wraplength=600, justify="left").pack(fill="x")

        action_frame = tk.Frame(card, bg=COLORS["surface"])
        action_frame.pack(side="right", padx=(20, 0))

        if is_enrolled:
            badge_frame = tk.Frame(action_frame, bg="#e8f5e9", padx=10, pady=5)
            badge_frame.pack()
            badge_frame.configure(highlightbackground=COLORS["success"], highlightthickness=1)
            
            lbl_badge = tk.Label(badge_frame, text="✓ Enrolled", 
                                 font=FONTS["small_bold"], bg="#e8f5e9", fg=COLORS["success"])
            lbl_badge.pack()
        else:
            btn = ttk.Button(action_frame, text="Enroll Now", style="Primary.TButton",
                             command=lambda cid=course['id']: self.confirm_enrollment(cid, header_text),
                             cursor="hand2")
            btn.pack()

    def confirm_enrollment(self, course_id, course_name):
        if messagebox.askyesno("Confirm Enrollment", f"Do you want to enroll in {course_name}?"):
            self.controller.enroll_course(course_id, self.refresh_after_enroll)

    def refresh_after_enroll(self, success):
        if success:
            messagebox.showinfo("Success", "You have successfully enrolled!")
            self.perform_search() 
        else:
            messagebox.showerror("Error", "Enrollment failed. You might already be enrolled.")