from datetime import datetime
from core.base_service import BaseService

# Repositories
from repositories.assignment_repo import AssignmentRepository
from repositories.submission_repo import SubmissionRepository
from repositories.course_repo import CourseRepository
from repositories.enrollment_repo import EnrollmentRepository
from repositories.grade_repo import GradeRepository
from repositories.notification_repo import NotificationRepository

# Models
from models.assignment import Assignment
from models.submission import Submission
from models.grade import Grade

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

    # ---------------------------------------------------------
    # 1. INSTRUCTOR: Create Assignment
    # ---------------------------------------------------------
    def create_assignment(self, instructor_id: int, course_id: int, data: dict):
        """
        Creates an assignment. 
        Note: instructor_id here must be the Instructor Profile ID (not User ID).
        """
        try:
            # 1. Validation (Course exists)
            course = self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found.")

            # 2. Validation (Security: Ownership)
            # Ensure the instructor creating this actually owns the course
            self.check_permission(course.instructor_id, instructor_id)

            # 3. Validation (Type)
            valid_types = {"quiz", "project", "homework", "exam"}
            if data['type'] not in valid_types:
                raise ValueError(f"Invalid type. Must be one of: {valid_types}")

            # 4. Validation (Time)
            due_date = datetime.fromisoformat(data['due_date'])
            if due_date < datetime.now():
                raise ValueError("Due date must be in the future.")

            # 5. Action: Create Assignment
            assignment = Assignment(
                id=None,
                course_id=course_id,
                title=data['title'],
                description=data.get('description', ''),
                type=data['type'],
                due_date=data['due_date'],
                max_score=data.get('max_score', 100)
            )
            saved_assignment = self.assignment_repo.create(assignment)

            # 6. Future: Notification Logic would go here
            # (We would create an announcement, then loop enrollments to notify students)
            
            return saved_assignment

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 2. GENERAL: View Assignments
    # ---------------------------------------------------------
    def get_assignments_by_course(self, course_id: int):
        """Returns list sorted by closest deadline (ASC)."""
        try:
            return self.assignment_repo.get_by_course_id(course_id)
        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 3. STUDENT UI: Get Status List (Critical for UI)
    # ---------------------------------------------------------
    def get_student_assignments_status(self, student_id: int, course_id: int):
        """
        Merges Assignments table with Submissions table.
        Returns: List of dicts with { ...assignment_data, 'status': 'Submitted'|'Pending'|'Overdue' }
        """
        try:
            # 1. Fetch all assignments for the course (Sorted by date)
            assignments = self.assignment_repo.get_by_course_id(course_id)
            
            # 2. Fetch all submissions by this student for this course
            submissions = self.submission_repo.get_by_student_and_course(student_id, course_id)
            
            # Create a lookup map for faster checking: { assignment_id: submission_obj }
            submission_map = {s.assignment_id: s for s in submissions}

            results = []
            now = datetime.now()

            # 3. Merge Logic
            for asm in assignments:
                status = "Pending"
                submission = submission_map.get(asm.id)

                if submission:
                    status = "Submitted"
                elif datetime.fromisoformat(asm.due_date) < now:
                    status = "Overdue"

                # Convert object to dict to add the extra 'status' field
                asm_data = asm.to_dict()
                asm_data['status'] = status
                asm_data['submission_id'] = submission.id if submission else None
                
                # Check if graded
                if submission:
                    grade = self.grade_repo.get_by_submission_id(submission.id)
                    if grade:
                        asm_data['grade'] = grade.grade_value
                        asm_data['feedback'] = grade.feedback

                results.append(asm_data)

            return results

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 4. STUDENT: Submit Assignment
    # ---------------------------------------------------------
    def submit_assignment(self, student_id: int, assignment_id: int, content: str):
        try:
            # 1. Fetch Assignment to check dates and course
            assignment = self.assignment_repo.get_by_id(assignment_id)
            if not assignment:
                raise ValueError("Assignment not found.")

            # 2. Security: Check Enrollment
            if not self.enrollment_repo.is_enrolled(student_id, assignment.course_id):
                raise PermissionError("You are not enrolled in this course.")

            # 3. Validation: Late Check
            due_date = datetime.fromisoformat(assignment.due_date)
            if datetime.now() > due_date:
                raise ValueError("Submission Deadline has passed.")

            # 4. Duplicate Check
            existing_sub = self.submission_repo.get_by_student_and_assignment(student_id, assignment_id)
            
            if existing_sub:
                # Update existing
                existing_sub.content = content
                existing_sub.submitted_at = datetime.now().isoformat()
                self.submission_repo.update(existing_sub)
                return existing_sub
            else:
                # Create new
                new_sub = Submission(
                    id=None,
                    assignment_id=assignment_id,
                    student_id=student_id,
                    content=content,
                    submitted_at=datetime.now().isoformat()
                )
                return self.submission_repo.create(new_sub)

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 5. INSTRUCTOR: Grade Assignment
    # ---------------------------------------------------------
    def grade_assignment(self, instructor_id: int, submission_id: int, grade_value: float, feedback: str):
        try:
            # 1. Fetch Submission to find context
            submission = self.submission_repo.get_by_id(submission_id)
            if not submission:
                raise ValueError("Submission not found.")
            
            # 2. Fetch Assignment -> Course to verify Instructor ownership
            assignment = self.assignment_repo.get_by_id(submission.assignment_id)
            course = self.course_repo.get_by_id(assignment.course_id)
            self.check_permission(course.instructor_id, instructor_id)
            
            # 3. Validation: Grade Range
            if not (0 <= grade_value <= assignment.max_score):
                raise ValueError(f"Grade must be between 0 and {assignment.max_score}.")

            # 4. Create Grade Record
            grade = Grade(
                id=None,
                submission_id=submission_id,
                grade_value=grade_value,
                feedback=feedback
            )
            saved_grade = self.grade_repo.create(grade)

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