
    def handle_save_assignment(self):
        # Use the dropdown selection to get a valid, existing course ID
        selected_label = self.course_var.get()
        course_id = self.course_mapping.get(selected_label) if selected_label else None
        
        if not course_id:
            messagebox.showerror("Error", "Please select a valid course from the list.")
            return

        assignment_data = {
            'title': self.title_ent.get().strip(),
            'description': self.desc_ent.get("1.0", tk.END).strip(),
            'due_date': self.due_ent.get().strip(),
            'max_score': int(self.score_ent.get() if self.score_ent.get().isdigit() else 100),
            'type': self.type_var.get()
        }
        
        # Passing a valid course_id prevents the Foreign Key failure
        self.controller.create_assignment(course_id, assignment_data, self.on_save_success)
