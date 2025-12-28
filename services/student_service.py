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
from services.announcement_service import AnnouncementService

class StudentService(BaseService):
    """
    Manages Student Logic: Enrollment, Dropping, and Academic Progress.
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

    # --- HELPER ---
    def _get_student_profile_id(self, user_id: int) -> int | None:
        return self.student_repo.get_profile_id_by_user_id(user_id)

    # =========================================================
    #  1. CORE PROFILE METHODS
    # =========================================================
    def get_student_by_user_id(self, user_id):
        student = self.student_repo.get_by_id(user_id)
        
        if student:
            if not hasattr(student, 'student_id'):
                student.student_id = student.student_profile_id
                
        return student

    def get_students_by_course(self, course_id: int):
        try:
            return self.student_repo.get_students_by_course(course_id)
        except Exception as e:
            self.handle_db_error(e)
            return []

    # =========================================================
    #  2. ENROLLMENT LOGIC
    # =========================================================
    def enroll_course(self, user_id: int, course_id: int):
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student profile not found.")

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
            return True
        except Exception as e:
            self.handle_db_error(e)

    def drop_course(self, user_id: int, course_id: int):
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id:
                raise ValueError("Student profile not found.")

            if not self.enrollment_repo.is_enrolled(user_id, course_id):
                raise ValueError("You are not enrolled in this course.")

            return self.enrollment_repo.delete_enrollment(student_profile_id, course_id)
        except Exception as e:
            self.handle_db_error(e)

    def get_my_courses(self, user_id):
        """Returns detailed list of enrolled courses."""
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id: return []
            
            courses = self.enrollment_repo.get_courses_by_student(student_profile_id)
            results = []
            for c in courses:
                d = c.to_dict() if hasattr(c, 'to_dict') else vars(c)
                
                # Manual Instructor Fetch using PostgreSQL placeholder %s
                with self.course_repo.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT u.name FROM instructors i 
                        JOIN users u ON i.user_id = u.id 
                        WHERE i.id = %s
                    """, (c.instructor_id,))
                    res = cur.fetchone()
                    d['instructor_name'] = res[0] if res else "Unknown"
                
                results.append(d)
            return results
        except Exception as e:
            self.handle_db_error(e)

    # =========================================================
    #  3. GRADES & TRANSCRIPT
    # =========================================================
    def get_grades(self, user_id):
        return self.get_student_grades(user_id)

    def get_student_grades(self, user_id):
        student_profile_id = self._get_student_profile_id(user_id)
        if not student_profile_id: return []

        submissions = self.submission_repo.get_by_student_id(student_profile_id)
        results = []
        for sub in submissions:
            assign = self.assignment_repo.get_by_id(sub.assignment_id)
            grade = self.grade_repo.get_by_submission_id(sub.id)
            
            results.append({
                "assignment_title": assign.title if assign else "Unknown",
                "submitted_at": sub.submitted_at,
                "status": "Graded" if grade else "Awaiting Grade",
                "grade": grade.grade_value if grade else "-",
                "max_score": assign.max_score if assign else 100,
                "feedback": grade.feedback if grade else ""
            })
        return results

    def get_transcript(self, user_id):
        try:
            student_profile_id = self._get_student_profile_id(user_id)
            if not student_profile_id: return []

            raw_data = self.grade_repo.get_transcript_data(student_profile_id)
            formatted = []
            for item in raw_data:
                score = item.get('total_score', 0.0)
                formatted.append({
                    'course_code': item.get('course_code'),
                    'course_name': item.get('course_name'),
                    'total_score': score,
                    'letter_grade': self._calculate_letter_grade(score),
                    'credits': item.get('credits', 3)
                })
            return formatted
        except Exception as e:
            self.handle_db_error(e)

    # =========================================================
    #  4. DASHBOARD CALCULATIONS
    # =========================================================
    def calculate_gpa(self, student_profile_id):
        raw_data = self.grade_repo.get_transcript_data(student_profile_id)
        if not raw_data: return 0.0

        total_weighted = 0
        total_credits = 0
        for item in raw_data:
            credits = item.get('credits', 3)
            points = self._calculate_gpa_point(item.get('total_score', 0))
            total_weighted += (points * credits)
            total_credits += credits
        
        return round(total_weighted / total_credits, 2) if total_credits > 0 else 0.0

    def get_upcoming_deadlines(self, student_profile_id):
        enrollments = self.enrollment_repo.get_by_student_id(student_profile_id)
        active_ids = [e.course_id for e in enrollments if e.status == 'enrolled']
        
        subs = self.submission_repo.get_by_student_id(student_profile_id)
        submitted_ids = {s.assignment_id for s in subs}
        
        upcoming = []
        now = datetime.now()
        limit = now + timedelta(days=30)

        for cid in active_ids:
            asses = self.assignment_repo.get_by_course_id(cid)
            for a in asses:
                if a.id in submitted_ids: continue
                
                try:
                    due = datetime.fromisoformat(str(a.due_date))
                    if due.hour == 0 and due.minute == 0:
                        due = due.replace(hour=23, minute=59, second=59)
                        
                    if now < due <= limit:
                        course = self.course_repo.get_by_id(cid)
                        upcoming.append({
                            "title": a.title,
                            "course_code": course.code if course else "",
                            "due_date": a.due_date
                        })
                except ValueError:
                    continue

        return sorted(upcoming, key=lambda x: x['due_date'])

    def get_dashboard_overview(self, user_id: int):
        try:
            student = self.get_student_by_user_id(user_id)
            if not student: return {}
            
            pid = student.student_profile_id
            
            return {
                "student": student.to_dict() if hasattr(student, "to_dict") else student.__dict__,
                "enrolled_courses_count": len(self.get_my_courses(user_id)),
                "current_gpa_average": self.calculate_gpa(pid),
                "upcoming_deadlines": self.get_upcoming_deadlines(pid),
                "unread_notifications": self.notification_service.get_unread_count(user_id),
                "announcements": [] 
            }
        except Exception as e:
            self.handle_db_error(e)
            return {}

    # --- UTILS ---
    def _calculate_letter_grade(self, percentage):
        if percentage >= 90: return 'A'
        if percentage >= 80: return 'B'
        if percentage >= 70: return 'C'
        if percentage >= 60: return 'D'
        return 'F'

    def _calculate_gpa_point(self, percentage):
        if percentage >= 90: return 4.0
        if percentage >= 80: return 3.0
        if percentage >= 70: return 2.0
        if percentage >= 60: return 1.0
        return 0.0