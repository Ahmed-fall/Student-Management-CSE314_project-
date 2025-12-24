from core.base_controller import BaseController
from core.session import Session
from services.announcement_service import AnnouncementService
from services.instructor_service import InstructorService
from services.course_service import CourseService
from services.assignment_service import AssignmentService
from services.student_service import StudentService

class InstructorController(BaseController):
    """
    Orchestrates the business logic for Instructor-related views.
    Coordinates between faculty profiles, courses, and grading.
    """

    def load_dashboard_data(self, callback):
        """
        Fetches the instructor profile and their assigned courses.
        Identifies the current instructor via Session.
        """
        user = Session.current_user
        if not user:
            return self.navigate("login")

        def task():
            return self.get_service(InstructorService).get_dashboard_data(user.id)

        self.run_async(task, callback)

    def load_course_editor_data(self, course_id, callback):
        """
        Fetches details for a specific course and its associated assignments.
        Used by the CourseEditorView to populate the management interface.
        """
        def task():
            course_service = self.get_service(CourseService)
            assignment_service = self.get_service(AssignmentService)
            
            # 1. Get Course details
            course = course_service.course_repo.get_by_id(course_id)
            
            # 2. Get all assignments for this specific course
            assignments = assignment_service.assignment_repo.get_by_course_id(course_id)
            
            return {
                "course": course,
                "assignments": assignments
            }

        self.run_async(task, callback)

    def delete_assignment(self, assignment_id, callback):
        """
        Allows an instructor to remove an assignment.
        Calls the AssignmentService to handle cleanup (like deleting notifications).
        """
        user = Session.current_user
        if not user: return

        def task():
            service = self.get_service(AssignmentService)
            # Service handles permission checks and secondary cleanup
            return service.delete_assignment(assignment_id)

        self.run_async(task, callback)

    def submit_grade(self, submission_id, grade_value, feedback, callback):
        """
        Submits a grade via the Service (triggers notifications and validation).
        """
        user = Session.current_user
        if not user: return

        def task():
            # 1. Get Service
            service = self.get_service(AssignmentService)
            
            # 2. Get Instructor Profile ID (Required for permission checks)
            inst_service = self.get_service(InstructorService)
            profile = inst_service.get_instructor_profile(user.id)
            
            if not profile:
                raise ValueError("Instructor profile not found.")

            # 3. Call the Service logic we fixed earlier
            return service.grade_assignment(
                instructor_id=profile.instructor_profile_id,
                submission_id=submission_id,
                grade_value=float(grade_value),
                feedback=feedback
            )

        # 4. Run async and update UI on completion
        self.run_async(task, callback)
    # ------------------------------------------------------------------
    # ANNOUNCEMENTS LOGIC
    # ------------------------------------------------------------------
    def load_my_courses_for_selector(self, callback):
        """
        Fetches the list of courses this instructor teaches.
        Used to populate the 'Select Course' dropdown on the Announcement page.
        """
        user = Session.current_user
        if not user: return

        def task():
            # 1. Get Instructor Profile
            inst_service = self.get_service(InstructorService)
            profile = inst_service.get_instructor_profile(user.id)
            if not profile: return []

            # 2. Get Courses
            course_service = self.get_service(CourseService)
            return course_service.get_courses_by_instructor(profile.instructor_profile_id)

        self.run_async(task, callback)

    def create_announcement(self, course_id, title, message, callback):
            """
            Creates the announcement and triggers notifications.
            """
            user = Session.current_user
            if not user: return

            def task():
                # 1. Get Profile
                inst_service = self.get_service(InstructorService)
                profile = inst_service.get_instructor_profile(user.id)
                if not profile: return False

                # 2. Create Announcement
                ann_service = AnnouncementService() 
                
                return ann_service.create_announcement(
                    instructor_id=profile.instructor_profile_id,
                    course_id=course_id,
                    title=title,
                    message=message
                )

            self.run_async(task, callback)

    def claim_teaching_rights(self, course_id, callback):
        """Matches the name called in CampusManagerView."""
        def task():
            # 1. Get the internal instructor profile ID
            inst_svc = self.get_service(InstructorService)
            profile = inst_svc.get_instructor_profile(Session.current_user.id)
            
            # 2. Use the course service to update the database
            course_svc = self.get_service(CourseService)
            # Ensure we use the profile_id for the courses table
            return course_svc.assign_instructor(int(course_id), profile.instructor_profile_id)
        
        self.run_async(task, callback)

    def load_unassigned_courses(self, callback):
        """Fetches courses with no instructor and returns them to the view."""
        def task():
            service = self.get_service(CourseService)
            return service.get_unassigned_courses()
        
        self.run_async(task, callback)
    def create_new_course(self, code, name, callback):
        def task():
            course_svc = self.get_service(CourseService)
            # Pass None for instructor_id so the course remains 'Unassigned'
            return course_svc.create_course(instructor_id=None, code=code, name=name)
        self.run_async(task, callback)

    def manage_course(self, course_id):
        """Navigate to editor with the CORRECT course_id."""
        # Store the current course context in the controller or pass via router
        self.current_course_id = course_id 
        self.navigate("course_editor")

    def open_course_editor(self, course_id):
            """Sets the 'Active' course before navigating."""
            # 1. Store the ID so the Editor knows which course we are talking about
            self.current_managed_course_id = course_id 
            # 2. Navigate to the view
            self.navigate("course_editor")

    def drop_teaching_course(self, course_id, callback):
        """Calls the new Drop logic in the Service."""
        def task():
            return self.get_service(CourseService).drop_course(course_id)
        self.run_async(task, callback)

    def get_course_students(self, course_id, callback):
        """Fetches student details for the popup."""
        def task():
            return self.get_service(StudentService).get_students_by_course(course_id)
        self.run_async(task, callback)

    def create_assignment(self, course_id, assignment_data, callback):
            """
            Orchestrates assignment creation. 
            Crucial: Resolves User ID -> Instructor Profile ID to prevent FK errors.
            """
            user = Session.current_user
            if not user: return

            def task():
                # 1. Get the specialized Instructor Profile 
                inst_service = self.get_service(InstructorService)
                profile = inst_service.get_instructor_profile(user.id)
                
                if not profile:
                    return False

                # 2. Call AssignmentService with the correct PROFILE ID
                service = self.get_service(AssignmentService)
                return service.create_assignment(
                    instructor_id=profile.instructor_profile_id, #
                    course_id=course_id,
                    title=assignment_data['title'],
                    description=assignment_data['description'],
                    due_date=assignment_data['due_date'],
                    max_score=assignment_data['max_score'],
                    type=assignment_data['type']
                )

            self.run_async(task, callback)

    def load_assignment_submissions(self, assignment_id, callback):
            """Fetches the list of students who submitted work for an assignment."""
            def task():
                # Access the repository directly for this specific report query
                repo = self.get_service(AssignmentService).submission_repo
                return repo.get_grading_queue(assignment_id)
            
            self.run_async(task, callback)

   