import tkinter as tk
from tkinter import ttk, messagebox
import platform
from core.base_view import BaseView
from ui.styles import COLORS, FONTS
from ui.components.sidebar import Sidebar

class StudentNotificationsView(BaseView):
    """
    View for students to see their notifications/announcements.
    """
    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        # --- 1. Layout & Styling ---
        self.configure_treeview_style() # Ensure table looks good on all OS

        main_layout = tk.Frame(self, bg=COLORS["background"])
        main_layout.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = Sidebar(main_layout, self.controller)
        self.sidebar.pack(side="left", fill="y")

        # Content Area
        content = tk.Frame(main_layout, bg=COLORS["background"], padx=30, pady=30)
        content.pack(side="right", fill="both", expand=True)

        # --- 2. Header ---
        header_frame = tk.Frame(content, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="🔔 My Notifications", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(side="left")

        # --- 3. Toolbar (Action Buttons) ---
        toolbar = tk.Frame(content, bg=COLORS["background"], pady=10)
        toolbar.pack(fill="x")

        # Refresh
        ttk.Button(toolbar, text="↻ Refresh", style="Secondary.TButton",
                   command=lambda: self.controller.load_notifications(self.update_list)
                   ).pack(side="left", padx=(0, 10))

        # Mark Read
        ttk.Button(toolbar, text="✓ Mark Selected as Read", style="Secondary.TButton",
                   command=self.mark_selected_read).pack(side="left", padx=(0, 10))
        
        # Mark All Read
        ttk.Button(toolbar, text="✓✓ Mark All Read", style="Secondary.TButton",
                   command=self.mark_all_read).pack(side="left")

        # Back Button (Right)
        tk.Button(toolbar, text="Back to Dashboard", font=FONTS["small"],
                  bg=COLORS["background"], fg=COLORS["placeholder"], bd=0, cursor="hand2",
                  command=lambda: self.router.navigate("student_dashboard")
                  ).pack(side="right")

        # --- 4. Treeview (List) ---
        # Container for Treeview + Scrollbar
        tree_frame = tk.Frame(content, bg=COLORS["background"])
        tree_frame.pack(fill="both", expand=True)

        columns = ("title", "date", "message", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse", height=15)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Column Headings
        self.tree.heading("title", text="Title/Course")
        self.tree.heading("date", text="Date Received")
        self.tree.heading("message", text="Preview")
        self.tree.heading("status", text="Status")

        # Column Config
        self.tree.column("title", width=200, anchor="w")
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("message", width=400, anchor="w")
        self.tree.column("status", width=100, anchor="center")

        # Styles / Tags
        self.tree.tag_configure('unread', font=("Helvetica", 11, "bold"), foreground=COLORS["danger"])
        self.tree.tag_configure('read', font=("Helvetica", 11, "normal"), foreground=COLORS["text"])

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind Double Click for Details
        self.tree.bind("<Double-1>", self.on_double_click)

        self._setup_scroll_bindings(self.tree)

        # Initial Load
        self.controller.load_notifications(self.update_list)

    def _setup_scroll_bindings(self, widget):
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

    def update_list(self, notifications):
        """Callback: Updates the treeview with data from Controller."""
        # Clear current list
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not notifications:
            return

        # self.current_data stores the full objects so we can access them in popups
        self.current_data = notifications 

        for index, notif in enumerate(notifications):
            # Safe parsing
            is_read = notif.get('read_flag', 0)
            status_text = "Read" if is_read else "Unread"
            tag = 'read' if is_read else 'unread'
            
            # Date Formatting
            raw_date = str(notif.get('sent_at', ''))
            display_date = raw_date.replace('T', ' ')[:16]

            # Insert Row (Store index in iid)
            self.tree.insert(
                "", "end", 
                iid=index, 
                values=(
                    notif.get('title', 'Notification'), 
                    display_date, 
                    notif.get('message', ''), 
                    status_text
                ),
                tags=(tag,)
            )

    def mark_selected_read(self):
        """Gets selection and tells Controller to update DB."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a notification to mark as read.")
            return

        index = int(selected[0])
        notif_item = self.current_data[index]
        notif_id = notif_item.get('notification_id')

        # Call Controller
        self.controller.mark_notification_read(notif_id, lambda: self.controller.load_notifications(self.update_list))

    def mark_all_read(self):
        """Tells Controller to mark everything as read."""
        if messagebox.askyesno("Confirm", "Mark all notifications as read?"):
            self.controller.mark_all_notifications_read(lambda: self.controller.load_notifications(self.update_list))

    def on_double_click(self, event):
        """Shows the full message in a popup."""
        selected = self.tree.selection()
        if not selected:
            return
            
        index = int(selected[0])
        notif = self.current_data[index]
        
        # Show Popup
        messagebox.showinfo(notif.get('title'), f"Date: {notif.get('sent_at')}\n\n{notif.get('message')}")
        
        # Auto-mark as read on open if it's currently unread
        if notif.get('read_flag') == 0:
            self.controller.mark_notification_read(notif.get('notification_id'), 
                                                   lambda: self.controller.load_notifications(self.update_list))