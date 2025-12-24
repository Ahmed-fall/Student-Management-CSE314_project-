import tkinter as tk
from tkinter import ttk

COLORS = {
    "primary": "#2C3E50",       # Navy Blue
    "secondary": "#18BC9C",     # Teal
    "accent": "#E74C3C",        # Red
    "background": "#ECF0F1",    # Light Gray
    "surface": "#FFFFFF",       # White (Card Background)
    "text": "#2C3E50",          # Dark Blue (For text on white)
    "text_light": "#FFFFFF",    # White (For text on dark)
    "placeholder": "#95a5a6",
    
    "card": "#FFFFFF",          # White for cards
    "sidebar": "#2C3E50",       # Matches primary for consistency
    "danger": "#E74C3C",        # Red
    "success": "#2ECC71"        # Green
}

FONTS = {
    "h1": ("Helvetica", 26, "bold"),
    "h2": ("Helvetica", 22, "bold"),
    "body": ("Helvetica", 12),
    "body_bold": ("Helvetica", 12, "bold"),
    "small": ("Helvetica", 10),
    "small_bold": ("Helvetica", 10, "bold"),
    "icon": ("Segoe UI Emoji", 14),
    "button": ("Helvetica", 11, "bold") 
}

LAYOUT = {
    "card_width": 450,
    "card_padding": 50,
    "input_height": 35,
    "radius": 10
}

def setup_theme(root):
    style = ttk.Style(root)
    style.theme_use('clam')

    root.configure(bg=COLORS["background"])

    # Generic Frame
    style.configure("TFrame", background=COLORS["background"])
    style.configure("Card.TFrame", background=COLORS["surface"]) 

    # Labels
    style.configure("Header.TLabel", font=FONTS["h2"], background=COLORS["surface"], foreground=COLORS["primary"])
    style.configure("Body.TLabel", font=FONTS["body"], background=COLORS["surface"], foreground=COLORS["text"])
    style.configure("Link.TLabel", font=FONTS["small"], background=COLORS["surface"], foreground=COLORS["secondary"])

    # Buttons
    style.configure("Primary.TButton", font=FONTS["body_bold"], background=COLORS["primary"], foreground=COLORS["text_light"], borderwidth=0)
    style.map("Primary.TButton", background=[('active', COLORS["secondary"])])
    
    style.configure("Secondary.TButton", font=FONTS["body"], background=COLORS["surface"], foreground=COLORS["primary"], borderwidth=1)
    
    # Entry Fields
    style.configure("TEntry", padding=5, relief="flat", fieldbackground=COLORS["background"])

    # --- Sidebar Styles ---
    style.configure("Sidebar.TFrame", background=COLORS["sidebar"]) 
    
    style.configure("Sidebar.TButton", 
                    font=("Helvetica", 11), 
                    background=COLORS["sidebar"], 
                    foreground="white", 
                    borderwidth=0, 
                    anchor="w",    
                    padding=(20, 10))
    
    style.map("Sidebar.TButton", 
              background=[('active', '#34495e')], 
              foreground=[('active', '#1abc9c')]) 
    
    # KPI Card Style
    style.configure("Card.TFrame", background="white", relief="raised")

    # ==========================================================
    # FIXED TREEVIEW STYLES (ISOLATED)
    # ==========================================================
    
    # We define a CUSTOM style named "Primary.Treeview".
    # This prevents other views from accidentally resetting the global "Treeview" style.
    
    # 1. Main Table Rows
    style.configure("Primary.Treeview",
                    background="white",
                    fieldbackground="white",
                    foreground=COLORS["text"],
                    rowheight=30,
                    font=FONTS["body"],
                    borderwidth=0)
    
    # 2. Table Header (Notice the syntax: StyleName + .Heading)
    style.configure("Primary.Treeview.Heading",
                    background=COLORS["primary"],
                    foreground="white",
                    font=FONTS["button"],
                    relief="flat") 
    
    # 3. Header Interaction (Hover/Press)
    style.map("Primary.Treeview.Heading",
              background=[('active', COLORS["primary"]), ('pressed', COLORS["primary"])],
              foreground=[('active', 'white'), ('pressed', 'white')])

    # 4. Row Selection State
    style.map("Primary.Treeview",
              background=[('selected', COLORS["secondary"])], 
              foreground=[('selected', 'white')])