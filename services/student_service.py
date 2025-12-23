from datetime import datetime, timedelta
from core.base_service import BaseService

# Repositories
from repositories.course_repo import CourseRepository
from repositories.enrollment_repo import EnrollmentRepository
from repositories.grade_repo import GradeRepository
from repositories.student_repo import StudentRepository
from repositories.notification_repo import NotificationRepository
from repositories.assignment_repo import AssignmentRepository
from repositories.submission_repo import SubmissionRepository 

# Models
from models.submission import Submission
from models.enrollment import Enrollment

# Services
from services.notification_service import NotificationService

class StudentService(BaseService):
    """
    Manages Student Logic: Enrollment, Dropping, and Academic Progress (Transcript).
    """

    def __init__(self):
        self.course_repo = CourseRepository()
        self.enrollment_repo = EnrollmentRepository()
        self.grade_repo = GradeRepository()
        self.student_repo = StudentRepository()
        self.notification_repo = NotificationRepository()
        self.assignment_repo = AssignmentRepository()
        self.submission_repo = SubmissionRepository()
        self.notification_service = NotificationService()

    def _get_student_profile_id(self, user_id: int) -> int | None:
        """
        Helper to resolve student profile ID from user ID.
        """
        with self.student_repo.get_connection() as conn:
            res = conn.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
            return res[0] if res else None

    def get_students_by_course(self, course_id: int):
            """Fetches the list of students for the instructor's popup."""
            try:
                return self.student_repo.get_students_by_course(course_id)
            except Exception as e:
                self.handle_db_error(e)
                return []
            
    # ---------------------------------------------------------
    # 1. ENROLLMENT: Join a Course
    # ---------------------------------------------------------
    def enroll_course(self, user_id: int, course_id: int):
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student profile not found.")

            # Check if already enrolled
            if self.enrollment_repo.is_enrolled(user_id, course_id):
                raise ValueError("Already enrolled in this course.")

            enrollment = Enrollment(
                id=None,
                student_id=student_profile_id, 
                course_id=course_id,
                date_enrolled=datetime.now().isoformat(),
                status="enrolled"
            )
            
            self.enrollment_repo.create(enrollment)

            # Notify student (optional)
            # self.notification_service.notify_user(user_id, f"Enrolled in course {course_id}")

            return True

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 2. ENROLLMENT: Drop Course
    # ---------------------------------------------------------
    def drop_course(self, user_id: int, course_id: int):
        """Logic to drop a course for a student."""
        try:
            # 1. Resolve student profile
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student profile not found.")

            # 2. Check if actually enrolled
            if not self.enrollment_repo.is_enrolled(user_id, course_id):
                raise ValueError("You are not enrolled in this course.")

            # 3. Execute drop via the repository
            return self.enrollment_repo.delete_enrollment(student_profile_id, course_id)
        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 3. ACADEMIC: View Transcript
    # ---------------------------------------------------------
    def get_transcript(self, user_id):
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student not found")

            raw_data = self.grade_repo.get_transcript_data(student_profile_id)
            
            formatted_transcript = []
            for item in raw_data:
                score = item.get('total_score', 0.0)
                formatted_item = {
                    'course_code': item.get('course_code'),
                    'course_name': item.get('course_name'),
                    'total_score': score,
                    'letter_grade': self._calculate_letter_grade(score),
                    'status': 'enrolled' 
                }
                formatted_transcript.append(formatted_item)

            return formatted_transcript
            
        except Exception as e:
            self.handle_db_error(e)

    def _calculate_letter_grade(self, percentage):
        if percentage >= 90: return 'A'
        if percentage >= 80: return 'B'
        if percentage >= 70: return 'C'
        if percentage >= 60: return 'D'
        return 'F'

    # ---------------------------------------------------------
    # 4. DASHBOARD: Home Screen Aggregator
    # ---------------------------------------------------------
    def get_dashboard_overview(self, user_id: int):
        try:
            transcript = self.get_transcript(user_id)
            
            if transcript:
                gpa_avg = sum(item['total_score'] for item in transcript) / len(transcript)
            else:
                gpa_avg = 0.0

            upcoming = []
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student profile not found.")
            enrollments = self.enrollment_repo.get_by_student_id(student_profile_id)
            active_course_ids = [e.course_id for e in enrollments if e.status == 'enrolled']
            
            now = datetime.now()
            limit = now + timedelta(days=7)

            for cid in active_course_ids:
                course_assignments = self.assignment_repo.get_by_course_id(cid)
                for asm in course_assignments:
                    due = datetime.fromisoformat(asm.due_date)
                    if now < due <= limit:
                        course = self.course_repo.get_by_id(cid)
                        upcoming.append({
                            "assignment_title": asm.title,
                            "course_code": course.code,
                            "due_date": asm.due_date
                        })

            return {
                "enrolled_courses_count": len(active_course_ids),
                "current_gpa_average": round(gpa_avg, 2),
                "upcoming_deadlines": sorted(upcoming, key=lambda x: x['due_date']),
                "unread_notifications": self.notification_service.get_unread_count(user_id)
            }

        except Exception as e:
            self.handle_db_error(e)
    
    # ---------------------------------------------------------
    # 5. LIST ENROLLED COURSES      
    # ---------------------------------------------------------
    def get_my_courses(self, user_id):
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                return []
            courses = self.enrollment_repo.get_courses_by_student(student_profile_id)
            results = []
            for c in courses:
                d = c.to_dict() if hasattr(c, 'to_dict') else vars(c)
                with self.course_repo.get_connection() as conn:
                    res = conn.execute("""
                        SELECT u.name 
                        FROM instructors i 
                        JOIN users u ON i.user_id = u.id 
                        WHERE i.id = ?
                    """, (c.instructor_id,)).fetchone()
                    d['instructor_name'] = res[0] if res else "Unknown"
                results.append(d)
            return results
        except Exception as e:
            self.handle_db_error(e)
    
    def get_dashboard_notifications(self, user_id):
        try:
            return self.notification_repo.get_dashboard_notifications(user_id)
        except Exception as e:
            self.handle_db_error(e)
    
    def drop_course(self, user_id: int, course_id: int):
        """Logic to drop a course for a student."""
        try:
            # 1. Resolve student profile
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student profile not found.")

            # 2. Check if actually enrolled
            if not self.enrollment_repo.is_enrolled(user_id, course_id):
                raise ValueError("You are not enrolled in this course.")

            # 3. Execute drop
            return self.enrollment_repo.delete_enrollment(student_profile_id, course_id)
        except Exception as e:
            self.handle_db_error(e)
        
    def get_student_grades(self, user_id):
        """
        Fetches all submissions and combines them with assignment details.
        """
        student_profile_id = self._get_student_profile_id(user_id)
        if not student_profile_id: return []

        submissions = self.submission_repo.get_by_student_id(student_profile_id)
        
        results = []
        for sub in submissions:
            assign = self.assignment_repo.get_by_id(sub.assignment_id)
            grade = self.grade_repo.get_by_submission_id(sub.id)
            
            status = "Graded" if grade else "Awaiting Grade"
            grade_val = grade.grade_value if grade else "-"
            feedback = grade.feedback if grade else ""
            max_score = assign.max_score if assign else 100
            
            results.append({
                "assignment_title": assign.title if assign else "Unknown Assignment",
                "submitted_at": sub.submitted_at,
                "status": status,
                "grade": grade_val,
                "max_score": max_score,
                "feedback": feedback
            })
            
        return results
    
