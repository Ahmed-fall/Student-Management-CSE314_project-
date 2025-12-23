from repositories.assignment_repo import AssignmentRepository
from repositories.submission_repo import SubmissionRepository
from repositories.course_repo import CourseRepository
from repositories.enrollment_repo import EnrollmentRepository
from repositories.grade_repo import GradeRepository
from repositories.notification_repo import NotificationRepository
from repositories.announcement_repo import AnnouncementRepository
from datetime import datetime
from core.base_service import BaseService

from services.notification_service import NotificationService

from database.db_connection import get_db_connection

# Models
from models.assignment import Assignment
from models.submission import Submission
from models.grade import Grade
from models.notification import Notification
from models.announcement import Announcement

class AssignmentService(BaseService):
    """
    Central module for managing the Assignment Lifecycle:
    Creation -> Notification -> Submission -> Grading -> Status Tracking
    """

    def __init__(self):
        self.assignment_repo = AssignmentRepository()
        self.submission_repo = SubmissionRepository()
        self.course_repo = CourseRepository()
        self.enrollment_repo = EnrollmentRepository()
        self.grade_repo = GradeRepository()
        self.notification_repo = NotificationRepository()
        self.announcement_repo = AnnouncementRepository()

    def _get_student_profile_id(self, user_id: int) -> int | None:
        with self.enrollment_repo.get_connection() as conn:
            res = conn.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
            return res[0] if res else None

# ---------------------------------------------------------
    # 1. INSTRUCTOR: Create Assignment (With Auto-Announcement)
    # ---------------------------------------------------------
    def create_assignment(self, instructor_id: int, course_id: int, title: str, description: str, type: str, due_date: str, max_score: int = 100):
        try:
            # 1. Validation
            course = self.course_repo.get_by_id(course_id)
            if not course: raise ValueError("Course not found.")
            self.check_permission(course.instructor_id, instructor_id)

            if datetime.fromisoformat(due_date) < datetime.now():
                raise ValueError("Due date must be in the future.")

            # 2. Create Assignment
            assignment = Assignment(None, course_id, title, description, type, due_date, max_score)
            saved_assignment = self.assignment_repo.create(assignment)

            # 3. [BRIDGE] Create System Announcement
            # This satisfies the Foreign Key requirement for notifications
            sys_announcement = Announcement(
                id=None,
                course_id=course_id,
                title=f"New Assignment: {title}",
                message=f"A new {type} has been posted. Due: {due_date}",
                created_at=datetime.now().isoformat()
            )
            saved_ann = self.announcement_repo.create(sys_announcement)

            # 4. Send Notifications linked to the Announcement
            #notification_service = NotificationService()
            #notification_service.notify_course(course_id, saved_ann.id)
            # 6. Notification Logic
            # Create announcement for the new assignment
            announcement_title = f"New Assignment: {title}"
            announcement_message = description
            announcement_created_at = datetime.now().isoformat()
            
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO announcements (course_id, title, message, created_at)
                    VALUES (?, ?, ?, ?)
                """, (course_id, announcement_title, announcement_message, announcement_created_at))
                announcement_id = cursor.lastrowid

            # Now notify the course with the announcement_id
            notification_service = NotificationService()
            notification_service.notify_course(course_id, announcement_id)
            
            return saved_assignment

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 2. GENERAL: View Assignments
    # ---------------------------------------------------------
    def get_assignments_by_course(self, course_id: int):
        """
        Fetches all assignments for a specific course.
        """
        try:
            return self.assignment_repo.get_by_course_id(course_id)
        except Exception as e:
            self.handle_db_error(e)
            return []

    # ---------------------------------------------------------
    # 3. STUDENT UI: Get Status List (Critical for UI)
    # ---------------------------------------------------------
    def get_student_assignments(self, user_id: int, course_id: int = None):
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                return []

            results = []
            now = datetime.now()
            courses_map = {}

            if course_id:
                # Single course mode
                if not self.enrollment_repo.is_enrolled(user_id, course_id):
                    raise PermissionError("Not enrolled in this course.")
                courses_map[course_id] = self.course_repo.get_by_id(course_id)
                assignments = self.assignment_repo.get_by_course_id(course_id)
                submissions = self.submission_repo.get_by_student_and_course(student_profile_id, course_id)
            else:
                # All courses mode
                enrollments = self.enrollment_repo.get_by_student_id(student_profile_id)
                course_ids = [e.course_id for e in enrollments if e.status == 'enrolled']
                if not course_ids:
                    return []
                courses_map = {cid: self.course_repo.get_by_id(cid) for cid in course_ids}
                assignments = []
                for cid in course_ids:
                    assignments.extend(self.assignment_repo.get_by_course_id(cid))
                submissions = self.submission_repo.get_by_student_id(student_profile_id)

            submission_map = {s.assignment_id: s for s in submissions}

            for asm in assignments:
                if asm.course_id not in courses_map:
                    continue  # Skip if course not loaded (edge case)
                
                status = "Pending"
                submission = submission_map.get(asm.id)
                grade = None
                if submission:
                    status = "Submitted"
                    grade = self.grade_repo.get_by_submission_id(submission.id)
                elif datetime.fromisoformat(asm.due_date) < now:
                    status = "Overdue"

                asm_data = asm.to_dict()
                asm_data['course_code'] = courses_map[asm.course_id].code
                asm_data['status'] = status
                asm_data['submission_id'] = submission.id if submission else None
                
                if grade:
                    asm_data['grade'] = grade.grade_value
                    asm_data['feedback'] = grade.feedback

                results.append(asm_data)

            # Sort by due date
            results.sort(key=lambda x: x['due_date'])
            return results

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 4. STUDENT: Submit Assignment
    # ---------------------------------------------------------
    def submit_assignment(self, user_id: int, assignment_id: int, content: str):
        try:
            # 1. Fetch Assignment to check dates and course
            assignment = self.assignment_repo.get_by_id(assignment_id)
            if not assignment:
                raise ValueError("Assignment not found.")

            # 2. Security: Check Enrollment
            if not self.enrollment_repo.is_enrolled(user_id, assignment.course_id):
                raise PermissionError("You are not enrolled in this course.")
            
            # 3. Get the Student Profile ID for the database record
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student profile not found.")

            # 4. Validation: Late Check
            due_date = datetime.fromisoformat(assignment.due_date)
            if datetime.now() > due_date:
                raise ValueError("Submission Deadline has passed.")

            # 5. Duplicate Check
            existing_sub = self.submission_repo.get_by_student_and_assignment(student_profile_id, assignment_id)
            
            if existing_sub:
                existing_sub.content = content
                existing_sub.submitted_at = datetime.now().isoformat()
                self.submission_repo.update(existing_sub)
                sub = existing_sub
            else:
                new_sub = Submission(
                    id=None,
                    assignment_id=assignment_id,
                    student_id=student_profile_id,
                    content=content,
                    submitted_at=datetime.now().isoformat()
                )
                sub = self.submission_repo.create(new_sub)

            # 6. Notify Instructor
            course = self.course_repo.get_by_id(assignment.course_id)
            with self.course_repo.get_connection() as conn:
                res = conn.execute("SELECT user_id FROM instructors WHERE id = ?", (course.instructor_id,)).fetchone()
                instructor_user_id = res[0] if res else None

            if instructor_user_id:
                # Create announcement for submission
                announcement_title = f"New Submission for {assignment.title}"
                announcement_message = f"A student has submitted the assignment."
                announcement_created_at = datetime.now().isoformat()
                
                with get_db_connection() as conn_ann:
                    cursor = conn_ann.execute("""
                        INSERT INTO announcements (course_id, title, message, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (assignment.course_id, announcement_title, announcement_message, announcement_created_at))
                    announcement_id = cursor.lastrowid

                notification = Notification(
                    id=None,
                    user_id=instructor_user_id,
                    announcement_id=announcement_id,
                    read_flag=0,
                    sent_at=datetime.now().isoformat()
                )
                self.notification_repo.create(notification)

            return sub

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 2. INSTRUCTOR: Grade Assignment (With Student Notification)
    # ---------------------------------------------------------
    def grade_assignment(self, instructor_id: int, submission_id: int, grade_value: float, feedback: str):
        try:
            # 1. Fetch Context
            submission = self.submission_repo.get_by_id(submission_id)
            if not submission: raise ValueError("Submission not found.")
            
            assignment = self.assignment_repo.get_by_id(submission.assignment_id)
            course = self.course_repo.get_by_id(assignment.course_id)
            self.check_permission(course.instructor_id, instructor_id)
            
            # 2. Validate & Save Grade
            if not (0 <= grade_value <= assignment.max_score):
                raise ValueError(f"Grade must be between 0 and {assignment.max_score}.")

            grade = Grade(None, submission_id, grade_value, feedback)
            saved_grade = self.grade_repo.create(grade)

            # 3. [BRIDGE] Create Notification Bridge
            # We create a generic "Grades Updated" announcement so we can link the notification
            sys_announcement = Announcement(
                id=None,
                course_id=course.id,
                title=f"Grade Posted: {assignment.title}",
                message=f"Grades for {assignment.title} have been updated.",
                created_at=datetime.now().isoformat()
            )
            saved_ann = self.announcement_repo.create(sys_announcement)

            # 4. Notify ONLY the specific student
            with self.enrollment_repo.get_connection() as conn:
                res = conn.execute("SELECT user_id FROM students WHERE id = ?", (submission.student_id,)).fetchone()
                student_user_id = res[0] if res else None

            if student_user_id:
                # Create announcement for grade
                announcement_title = f"Grade Posted for {assignment.title}"
                announcement_message = f"Your grade has been posted."
                announcement_created_at = datetime.now().isoformat()
                
                with get_db_connection() as conn_ann:
                    cursor = conn_ann.execute("""
                        INSERT INTO announcements (course_id, title, message, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (assignment.course_id, announcement_title, announcement_message, announcement_created_at))
                    announcement_id = cursor.lastrowid

                notification = Notification(
                    id=None,
                    user_id=student_user_id,
                    announcement_id=announcement_id,
                    read_flag=0,
                    sent_at=datetime.now().isoformat()
                )
                self.notification_repo.create(notification)

            return saved_grade

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 6. INSTRUCTOR: Delete Assignment
    # ---------------------------------------------------------
    def delete_assignment(self, instructor_id: int, assignment_id: int):
        try:
            # 1. Fetch Assignment
            asm = self.assignment_repo.get_by_id(assignment_id)
            if not asm:
                raise ValueError("Assignment not found.")
            
            # 2. Fetch Course to verify ownership
            course = self.course_repo.get_by_id(asm.course_id)
            self.check_permission(course.instructor_id, instructor_id)

            # 3. Delete
            self.assignment_repo.delete(assignment_id)
            return True

        except Exception as e:
            self.handle_db_error(e)

    def get_assignment_detail_for_student(self, user_id: int, assignment_id: int):
        """
        Fetches the assignment details AND the student's current submission (if any).
        Returns a dictionary for the View.
        """
        try:
            # 1. Fetch Assignment
            assignment = self.assignment_repo.get_by_id(assignment_id)
            if not assignment:
                return None

            # 2. Resolve Student Profile ID
            # (We need this to look up the specific submission for this student)
            student_profile_id = self._get_student_profile_id(user_id)

            # 3. Fetch Submission (if student exists)
            submission = None
            if student_profile_id:
                submission = self.submission_repo.get_by_student_and_assignment(student_profile_id, assignment_id)
            
            grade = None
            if submission:
                # Add this line to fetch the grade!
                grade = self.grade_repo.get_by_submission_id(submission.id)

            # 4. Return the Dictionary the View expects
            return {
                "assignment": assignment,
                "submission": submission,
                "grade": grade
            }

        except Exception as e:
            self.handle_db_error(e)
            return None