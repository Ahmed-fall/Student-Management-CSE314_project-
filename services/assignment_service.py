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
from models.assignment import Assignment
from models.submission import Submission
from models.grade import Grade
from models.notification import Notification
from models.announcement import Announcement

class AssignmentService(BaseService):
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
            cur = conn.cursor()
            cur.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
            res = cur.fetchone()
            return res[0] if res else None

    # --- HELPER: Recalculate Course Grade for GPA ---
    def _recalculate_course_grade(self, student_id: int, course_id: int):
        """
        Calculates the average of all graded assignments for a specific student/course
        and updates the 'enrollments' table so the GPA service can read it.
        """
        try:
            with self.grade_repo.get_connection() as conn:
                with conn.cursor() as cur:
                    # 1. Calculate Average
                    # Joins Grades -> Submissions -> Assignments to ensure we only average this course's work
                    sql_avg = """
                        SELECT AVG(g.grade_value)
                        FROM grades g
                        JOIN submissions s ON g.submission_id = s.id
                        JOIN assignments a ON s.assignment_id = a.id
                        WHERE s.student_id = %s AND a.course_id = %s
                    """
                    cur.execute(sql_avg, (student_id, course_id))
                    result = cur.fetchone()
                    new_average = result[0] if result and result[0] is not None else 0.0

                    # 2. Update Enrollment Table
                    sql_update = """
                        UPDATE enrollments 
                        SET current_grade = %s 
                        WHERE student_id = %s AND course_id = %s
                    """
                    cur.execute(sql_update, (new_average, student_id, course_id))
                    conn.commit()
        except Exception as e:
            # Log error but don't crash the grading process
            print(f"Error recalculating course grade: {e}")

    def create_assignment(self, instructor_id: int, course_id: int, title: str, description: str, type: str, due_date: str, max_score: int = 100):
        try:
            course = self.course_repo.get_by_id(course_id)
            if not course: raise ValueError("Course not found.")
            self.check_permission(course.instructor_id, instructor_id)

            if datetime.fromisoformat(due_date) < datetime.now():
                raise ValueError("Due date must be in the future.")

            assignment = Assignment(None, course_id, title, description, type, due_date, max_score)
            saved_assignment = self.assignment_repo.create(assignment)

            sys_announcement = Announcement(
                id=None,
                course_id=course_id,
                title=f"New Assignment: {title}",
                message=f"A new {type} has been posted. Due: {due_date}",
                created_at=datetime.now().isoformat()
            )
            saved_ann = self.announcement_repo.create(sys_announcement)

            notification_service = NotificationService()
            notification_service.notify_course(course_id, saved_ann.id)
            
            return saved_assignment

        except Exception as e:
            self.handle_db_error(e)

    def get_assignments_by_course(self, course_id: int):
        try:
            return self.assignment_repo.get_by_course_id(course_id)
        except Exception as e:
            self.handle_db_error(e)
            return []

    def get_student_assignments(self, user_id: int, course_id: int = None):
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                return []

            results = []
            now = datetime.now()
            courses_map = {}

            if course_id:
                if not self.enrollment_repo.is_enrolled(user_id, course_id):
                    raise PermissionError("Not enrolled in this course.")
                courses_map[course_id] = self.course_repo.get_by_id(course_id)
                assignments = self.assignment_repo.get_by_course_id(course_id)
                submissions = self.submission_repo.get_by_student_and_course(student_profile_id, course_id)
            else:
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
                    continue
                
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

            results.sort(key=lambda x: x['due_date'])
            return results

        except Exception as e:
            self.handle_db_error(e)

    def submit_assignment(self, user_id: int, assignment_id: int, content: str):
        try:
            assignment = self.assignment_repo.get_by_id(assignment_id)
            if not assignment:
                raise ValueError("Assignment not found.")

            if not self.enrollment_repo.is_enrolled(user_id, assignment.course_id):
                raise PermissionError("You are not enrolled in this course.")
            
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student profile not found.")

            due_date = datetime.fromisoformat(assignment.due_date)
            if datetime.now() > due_date:
                raise ValueError("Submission Deadline has passed.")

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
            
            # Update status to submitted manually to ensure consistency
            with self.submission_repo.get_connection() as conn:
                with conn.cursor() as cur:
                     cur.execute("UPDATE submissions SET status = 'submitted' WHERE id = %s", (sub.id,))
                     conn.commit()

            # Notify Instructor
            course = self.course_repo.get_by_id(assignment.course_id)
            instructor_user_id = None
            
            with self.course_repo.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT user_id FROM instructors WHERE id = %s", (course.instructor_id,))
                res = cur.fetchone()
                instructor_user_id = res[0] if res else None

            if instructor_user_id:
                announcement_title = f"New Submission for {assignment.title}"
                announcement_message = "A student has submitted the assignment."
                
                sys_ann = Announcement(
                    id=None, 
                    course_id=assignment.course_id, 
                    title=announcement_title, 
                    message=announcement_message, 
                    created_at=datetime.now().isoformat()
                )
                saved_ann = self.announcement_repo.create(sys_ann)

                notification = Notification(
                    id=None,
                    user_id=instructor_user_id,
                    announcement_id=saved_ann.id,
                    read_flag=0,
                    sent_at=datetime.now().isoformat()
                )
                self.notification_repo.create(notification)

            return sub

        except Exception as e:
            self.handle_db_error(e)

    def grade_assignment(self, instructor_id: int, submission_id: int, grade_value: float, feedback: str):
        try:
            submission = self.submission_repo.get_by_id(submission_id)
            if not submission: 
                raise ValueError("Submission not found.")
            
            assignment = self.assignment_repo.get_by_id(submission.assignment_id)
            
            try:
                val = float(grade_value)
            except ValueError:
                raise ValueError("Grade must be a valid number.")

            if val < 0:
                raise ValueError("Grade cannot be negative.")
            
            if val > assignment.max_score:
                raise ValueError(f"Grade {val} exceeds the maximum score of {assignment.max_score}.")

            existing_grade = self.grade_repo.get_by_submission_id(submission_id)
            
            saved_grade = None
            if existing_grade:
                existing_grade.grade_value = val
                existing_grade.feedback = feedback
                saved_grade = self.grade_repo.update(existing_grade)
            else:
                grade = Grade(None, submission_id, val, feedback)
                saved_grade = self.grade_repo.create(grade)

            # --- FIX 1: UPDATE STATUS ---
            # Explicitly mark submission as 'graded' so it disappears from Pending list
            with self.submission_repo.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE submissions SET status = 'graded' WHERE id = %s", (submission_id,))
                    conn.commit()

            # --- FIX 2: RECALCULATE COURSE GRADE (GPA) ---
            # Update the student's average in enrollments table
            self._recalculate_course_grade(submission.student_id, assignment.course_id)

            # Notifications
            student_user_id = None
            with self.enrollment_repo.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT user_id FROM students WHERE id = %s", (submission.student_id,))
                res = cur.fetchone()
                student_user_id = res[0] if res else None

            if student_user_id:
                ann_title = f"Grade Posted: {assignment.title}"
                ann_message = f"You received a score of {val}/{assignment.max_score}."
                
                sys_announcement = Announcement(
                    id=None,
                    course_id=assignment.course_id,
                    title=ann_title,
                    message=ann_message,
                    created_at=datetime.now().isoformat()
                )
                saved_ann = self.announcement_repo.create(sys_announcement)

                notification = Notification(
                    id=None,
                    user_id=student_user_id,
                    announcement_id=saved_ann.id,
                    read_flag=0,
                    sent_at=datetime.now().isoformat()
                )
                self.notification_repo.create(notification)

            return saved_grade

        except ValueError as ve:
            raise ve
        except Exception as e:
            self.handle_db_error(e)

    def delete_assignment(self, instructor_id: int, assignment_id: int):
        try:
            asm = self.assignment_repo.get_by_id(assignment_id)
            if not asm:
                raise ValueError("Assignment not found.")
            
            course = self.course_repo.get_by_id(asm.course_id)
            self.check_permission(course.instructor_id, instructor_id)

            self.assignment_repo.delete(assignment_id)
            return True

        except Exception as e:
            self.handle_db_error(e)

    def get_assignment_detail_for_student(self, user_id: int, assignment_id: int):
        try:
            assignment = self.assignment_repo.get_by_id(assignment_id)
            if not assignment:
                return None

            student_profile_id = self._get_student_profile_id(user_id)

            submission = None
            if student_profile_id:
                submission = self.submission_repo.get_by_student_and_assignment(student_profile_id, assignment_id)
            
            grade = None
            if submission:
                grade = self.grade_repo.get_by_submission_id(submission.id)

            return {
                "assignment": assignment,
                "submission": submission,
                "grade": grade
            }

        except Exception as e:
            self.handle_db_error(e)
            return None