import tkinter as tk
from tkinter import ttk
from core.base_view import BaseView
from ui.styles import COLORS, FONTS, LAYOUT

class RegisterView(BaseView):
    def create_controller(self):
        from controllers.auth_controller import AuthController
        return AuthController(self.router)

    def setup_ui(self):
        # Increased Width for Register form
        reg_width = LAYOUT["card_width"] + 100 
        
        self.card = tk.Frame(self, bg=COLORS["surface"], 
                             padx=LAYOUT["card_padding"], 
                             pady=LAYOUT["card_padding"])
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=reg_width)

        # Header
        tk.Label(self.card, text="Create Account", font=FONTS["h2"], 
                 bg=COLORS["surface"], fg=COLORS["primary"]).pack(pady=(0, 20))

        # --- Grid Layout ---
        form = tk.Frame(self.card, bg=COLORS["surface"])
        form.pack(fill="x")
        
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # --- HELPER: Creates a field but DOES NOT bind Enter globally anymore ---
        def add_field(row, col, label_text, var, is_pass=False):
            # Label
            tk.Label(form, text=label_text, font=FONTS["body_bold"], 
                     bg=COLORS["surface"], anchor="w").grid(row=row*2, column=col, sticky="ew", padx=5, pady=(10, 0))
            
            # Entry
            if is_pass:
                ent = ttk.Entry(form, textvariable=var, show="*")
            else:
                ent = ttk.Entry(form, textvariable=var)
            
            ent.grid(row=row*2 + 1, column=col, sticky="ew", padx=5, pady=(5, 0), ipady=3)
            return ent

        # 1. Create Fields (And save references to the widgets)
        self.name_var = tk.StringVar()
        self.name_ent = add_field(0, 0, "Full Name", self.name_var)

        self.user_var = tk.StringVar()
        self.user_ent = add_field(0, 1, "Username", self.user_var)

        self.email_var = tk.StringVar()
        self.email_ent = add_field(1, 0, "Email Address", self.email_var)

        self.pass_var = tk.StringVar()
        self.pass_ent = add_field(2, 0, "Password", self.pass_var, is_pass=True)

        # 2. Role Dropdown
        self.role_var = tk.StringVar(value="student")
        tk.Label(form, text="I am a...", font=FONTS["body_bold"], bg=COLORS["surface"], anchor="w").grid(row=2, column=1, sticky="ew", padx=5, pady=(10,0))
        
        self.role_cb = ttk.Combobox(form, textvariable=self.role_var, values=["student", "instructor"], state="readonly")
        self.role_cb.grid(row=3, column=1, sticky="ew", padx=5, pady=5, ipady=3)

        # 3. Gender Dropdown
        self.gender_var = tk.StringVar(value="male")
        tk.Label(form, text="Gender", font=FONTS["body_bold"], bg=COLORS["surface"], anchor="w").grid(row=4, column=1, sticky="ew", padx=5, pady=(10,0))
        
        self.gender_cb = ttk.Combobox(form, textvariable=self.gender_var, values=["male", "female"], state="readonly")
        self.gender_cb.grid(row=5, column=1, sticky="ew", padx=5, pady=5, ipady=3)

        # 4. Show Password Checkbox
        self.show_pass_var = tk.BooleanVar()
        cb = tk.Checkbutton(form, text="Show Password", variable=self.show_pass_var, 
                            bg=COLORS["surface"], activebackground=COLORS["surface"],
                            command=self.toggle_pass)
        cb.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        
        # --- Buttons ---
        btn_frame = tk.Frame(self.card, bg=COLORS["surface"])
        btn_frame.pack(fill="x", pady=30)

        # Register Button
        ttk.Button(btn_frame, text="Sign Up", style="Primary.TButton", 
                   command=self.handle_register).pack(fill="x", ipady=5)
        
        # Back Button
        tk.Button(btn_frame, text="← Back to Login", 
                  font=FONTS["body"], bg=COLORS["surface"], fg="#7f8c8d", bd=0, 
                  cursor="hand2", activebackground=COLORS["surface"],
                  command=lambda: self.controller.go_to_login()).pack(pady=10)


        # --- FOCUS CHAIN CONFIGURATION ---
        # This makes the "Enter" key move to the next field instead of submitting immediately.
        
        # 1. Name -> Username
        self.name_ent.bind('<Return>', lambda e: self.user_ent.focus())
        
        # 2. Username -> Email
        self.user_ent.bind('<Return>', lambda e: self.email_ent.focus())
        
        # 3. Email -> Role Dropdown
        self.email_ent.bind('<Return>', lambda e: self.role_cb.focus())
        
        # 4. Role -> Gender Dropdown
        self.role_cb.bind('<Return>', lambda e: self.gender_cb.focus())
        
        # 5. Gender -> Password
        self.gender_cb.bind('<Return>', lambda e: self.pass_ent.focus())

        # 6. Password -> SUBMIT FORM (Only this one submits)
        self.pass_ent.bind('<Return>', lambda e: self.handle_register())


    def toggle_pass(self):
        if self.show_pass_var.get():
            self.pass_ent.config(show="")
        else:
            self.pass_ent.config(show="*")

    def handle_register(self):
        user_data = {
            "username": self.user_var.get(),
            "name": self.name_var.get(),
            "email": self.email_var.get(),
            "password": self.pass_var.get(),
            "gender": self.gender_var.get()
        }
        
        role = self.role_var.get()
        if role == "student":
            profile = {"major": "General", "level": 1, "birthdate": "2000-01-01"}
        else:
            profile = {"department": "General"}

        self.controller.register(user_data, profile, role)