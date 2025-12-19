import tkinter as tk
from tkinter import ttk, messagebox
from core.service_locator import ServiceLocator
from services.notification_service import NotificationService
from core.session import Session 
from ui.styles import COLORS, FONTS
from core.base_view import BaseView

class StudentNotificationsView(BaseView):
    """
    View for students to see their notifications/announcements.
    """
    def __init__(self, parent, router, *args, **kwargs):
        super().__init__(parent, router, *args, **kwargs)
        
        # Dependency Injection
        self.notification_service = ServiceLocator.get(NotificationService)
        
        # Get user directly from Session
        self.user = Session.current_user

    def create_controller(self):
        from controllers.student_controller import StudentController
        return StudentController(self.router)

    def setup_ui(self):
        """Builds the UI layout."""
        # 1. Header
        header_frame = tk.Frame(self, bg=COLORS["background"], height=60)
        header_frame.pack(fill="x", side="top")
        
        tk.Label(header_frame, text="🔔 My Notifications", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=15, padx=20, anchor="w")

        # 2. Toolbar (Buttons)
        toolbar = tk.Frame(self, bg="white", pady=10, padx=20)
        toolbar.pack(fill="x")
        
        # --- NEW: Back Button (Right aligned) ---
        ttk.Button(toolbar, text="← Back to Dashboard", 
                   command=lambda: self.router.navigate("student_dashboard")
        ).pack(side="right", padx=5)

        # Existing Buttons (Left aligned)
        ttk.Button(toolbar, text="Mark as Read", command=self.mark_selected_read).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_data).pack(side="left", padx=5)

        # 3. Treeview
        tree_frame = tk.Frame(self, padx=20, pady=10)
        tree_frame.pack(fill="both", expand=True)

        columns = ("course", "date", "message", "status")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("course", text="Course")
        self.tree.heading("date", text="Date")
        self.tree.heading("message", text="Message")
        self.tree.heading("status", text="Status")

        self.tree.column("course", width=150, anchor="w")
        self.tree.column("date", width=150, anchor="w")
        self.tree.column("message", width=450, anchor="w")
        self.tree.column("status", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure('unread', font=('Helvetica', 10, 'bold'), foreground='#e74c3c')
        self.tree.tag_configure('read', font=('Helvetica', 10, 'normal'), foreground='black')

        self.refresh_data()

    def refresh_data(self):
        """Fetches data from DB and repopulates the tree."""
        self.user = Session.current_user
        
        if not self.user:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            notifications = self.notification_service.get_dashboard_notifications(self.user.id)

            for notif in notifications:
                status_text = "Unread" if notif['read_flag'] == 0 else "Read"
                tag = 'unread' if notif['read_flag'] == 0 else 'read'
                display_date = notif['sent_at'][:16].replace('T', ' ')

                self.tree.insert(
                    "", "end", 
                    iid=notif['notification_id'], 
                    values=(notif['title'], display_date, notif['message'], status_text),
                    tags=(tag,)
                )
        except Exception as e:
            print(f"Error refreshing notifications: {e}")

    def mark_selected_read(self):
        selected_item_id = self.tree.selection()
        if not selected_item_id:
            messagebox.showinfo("Info", "Please select a notification to mark as read.")
            return

        notification_id = int(selected_item_id[0]) 

        try:
            self.notification_service.mark_as_read(self.user.id, notification_id)
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))