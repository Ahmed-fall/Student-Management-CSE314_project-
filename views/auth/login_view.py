import tkinter as tk
from tkinter import ttk
from core.base_view import BaseView
from ui.styles import COLORS, FONTS, LAYOUT

class LoginView(BaseView):
    def create_controller(self):
        from controllers.auth_controller import AuthController
        return AuthController(self.router)

    def setup_ui(self):
        # 1. The Centered Card
        self.card = tk.Frame(self, bg=COLORS["surface"], 
                             padx=LAYOUT["card_padding"], 
                             pady=LAYOUT["card_padding"])
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=LAYOUT["card_width"])

        # Title
        tk.Label(self.card, text="Welcome Back", font=FONTS["h1"], 
                 bg=COLORS["surface"], fg=COLORS["primary"]).pack(pady=(0, 10))
        
        tk.Label(self.card, text="Enter your credentials to access your account", 
                 font=FONTS["small"], bg=COLORS["surface"], fg="gray").pack(pady=(0, 30))

        # --- Username ---
        self.create_label("Username or Email")
        self.username_var = tk.StringVar()
        # FIX: Capture the return value into self.user_entry
        self.user_entry = self.create_entry(self.username_var)
        self.user_entry.focus() # Auto-focus start

        # --- Password with Toggle ---
        self.create_label("Password")
        self.password_var = tk.StringVar()
        
        pass_frame = tk.Frame(self.card, bg=COLORS["surface"])
        pass_frame.pack(fill="x", pady=5)
        
        # FIX: Define self.pass_entry here
        self.pass_entry = ttk.Entry(pass_frame, textvariable=self.password_var, show="*")
        self.pass_entry.pack(side="left", fill="x", expand=True, ipady=3)
        
        # Eye Icon
        self.show_pass_var = tk.BooleanVar(value=False)
        self.eye_btn = tk.Button(pass_frame, text="👁", font=FONTS["icon"],
                                 bg=COLORS["surface"], bd=0, cursor="hand2",
                                 activebackground=COLORS["surface"],
                                 command=self.toggle_password)
        self.eye_btn.pack(side="right", padx=5)

        # --- KEY BINDINGS (The UX Polish) ---
        # Enter on Username -> Go to Password
        self.user_entry.bind('<Return>', lambda e: self.pass_entry.focus())
        # Enter on Password -> Login
        self.pass_entry.bind('<Return>', lambda e: self.handle_login())
        
        # --- Actions ---
        btn = ttk.Button(self.card, text="Sign In", style="Primary.TButton", 
                         command=self.handle_login)
        btn.pack(fill="x", pady=(30, 10), ipady=5)

        # Divider
        tk.Label(self.card, text="— OR —", font=FONTS["small"], 
                 bg=COLORS["surface"], fg="#bdc3c7").pack(pady=10)

        # Register Link
        reg_btn = tk.Button(self.card, text="Create New Account", 
                            font=FONTS["body_bold"], bg=COLORS["surface"], 
                            fg=COLORS["secondary"], bd=0, cursor="hand2",
                            activebackground=COLORS["surface"],
                            command=lambda: self.controller.go_to_register())
        reg_btn.pack()

    def create_label(self, text):
        tk.Label(self.card, text=text, font=FONTS["body_bold"], 
                 bg=COLORS["surface"], fg=COLORS["text"], anchor="w").pack(fill="x", pady=(15, 5))

    def create_entry(self, variable):
        entry = ttk.Entry(self.card, textvariable=variable)
        entry.pack(fill="x", ipady=3)
        return entry

    def toggle_password(self):
        if self.show_pass_var.get():
            self.pass_entry.config(show="*")
            self.eye_btn.config(fg="black")
            self.show_pass_var.set(False)
        else:
            self.pass_entry.config(show="")
            self.eye_btn.config(fg=COLORS["secondary"])
            self.show_pass_var.set(True)

    def handle_login(self):
        u = self.username_var.get()
        p = self.password_var.get()
        self.controller.login(u, p)