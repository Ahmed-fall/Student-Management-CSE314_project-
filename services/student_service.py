from datetime import datetime, timedelta
from core.base_service import BaseService

# Repositories
from repositories.course_repo import CourseRepository
from repositories.enrollment_repo import EnrollmentRepository

from repositories.grade_repo import GradeRepository
from repositories.student_repo import StudentRepository
from repositories.notification_repo import NotificationRepository
# Note: SubmissionRepo is no longer needed here because GradeRepo handles the complex joins now.

# Models
from models.enrollment import Enrollment

class StudentService(BaseService):
    """
    Manages Student Logic: Enrollment, Dropping, and Academic Progress (Transcript).
    
    Optimized Implementation:
    - Uses specialized Repository methods to calculate scores via SQL aggregation 
      instead of Python loops (prevents N+1 query performance issues).
    """

    def __init__(self):
        self.course_repo = CourseRepository()
        self.enrollment_repo = EnrollmentRepository()
        
        self.grade_repo = GradeRepository()
        self.student_repo = StudentRepository()
        self.notification_repo = NotificationRepository()

    # ---------------------------------------------------------
    # 1. ENROLLMENT: Join a Course
    # ---------------------------------------------------------
    def enroll_course(self, student_id: int, course_id: int):
        """
        Registers a student for a course if eligible.
        """
        try:
            student = self.student_repo.get_by_id(student_id)
            if not student:
                raise ValueError("Student profile not found.")

            # 2. Create Enrollment Object
            # We use student.student_profile_id, NOT user_id
            enrollment = Enrollment(
                id=None,
                student_id=student.student_profile_id, 
                course_id=course_id,
                date_enrolled=None,
                status="enrolled"
            )
            
            self.enrollment_repo.create(enrollment)
            return True

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 2. ENROLLMENT: Drop Course
    # ---------------------------------------------------------
    def drop_course(self, student_id: int, course_id: int):
        """
        Updates status to 'dropped'.
        """
        try:
            # 1. Get the specific enrollment record
            enrollments = self.enrollment_repo.get_by_student_id(student_id)
            target_enrollment = next((e for e in enrollments if e.course_id == course_id), None)
            
            if not target_enrollment:
                raise ValueError("You are not enrolled in this course.")

            # 2. Update Status
            target_enrollment.status = 'dropped'
            self.enrollment_repo.update(target_enrollment)
            return True

        except Exception as e:
            self.handle_db_error(e)

    # ---------------------------------------------------------
    # 3. ACADEMIC: View Transcript (Optimized)
    # ---------------------------------------------------------
    def get_transcript(self, user_id):
        try:
            student = self.student_repo.get_by_id(user_id)
            if not student:
                raise ValueError("Student not found")

            # 1. Get data from Repo (now returns 'course_code', 'course_name', 'total_score')
            raw_data = self.grade_repo.get_transcript_data(student.student_profile_id)
            
            formatted_transcript = []
            for item in raw_data:
                score = item.get('total_score', 0.0)
                
                # 2. Add the letter grade logic
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
        """Helper to convert % to Letter."""
        if percentage >= 90: return 'A'
        if percentage >= 80: return 'B'
        if percentage >= 70: return 'C'
        if percentage >= 60: return 'D'
        return 'F'

    # ---------------------------------------------------------
    # 4. DASHBOARD: Home Screen Aggregator
    # ---------------------------------------------------------
    def get_dashboard_overview(self, student_id: int):
        """
        Provides a summary for the UI to reduce API calls.
        """
        try:
            # 1. Transcript Data (Reuse logic above)
            transcript = self.get_transcript(student_id)
            
            # 2. Calculate GPA (Simple average of current percentages for MVP)
            if transcript:
                gpa_avg = sum(item['current_average'] for item in transcript) / len(transcript)
            else:
                gpa_avg = 0.0

            # 3. Find Upcoming Deadlines (Next 7 days)
            upcoming = []
            enrollments = self.enrollment_repo.get_by_student_id(student_id)
            active_course_ids = [e.course_id for e in enrollments if e.status == 'enrolled']
            
            now = datetime.now()
            limit = now + timedelta(days=7)

            for cid in active_course_ids:
                # Get assignments for the course
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
                "upcoming_deadlines": sorted(upcoming, key=lambda x: x['due_date'])
            }

        except Exception as e:
            self.handle_db_error(e)
    
    # ---------------------------------------------------------
    # 5. LIST ENROLLED COURSES      
    # ---------------------------------------------------------
    def get_my_courses(self, user_id):
        try:
            student = self.student_repo.get_by_id(user_id)
            if not student:
                return []
            
            # Delegates the JOIN logic to the repository
            return self.enrollment_repo.get_courses_by_student(student.student_profile_id)
        except Exception as e:
            self.handle_db_error(e)
    
    def get_dashboard_notifications(self, user_id):
        """Fetches alerts for the student."""
        try:
            
            return self.notification_repo.get_dashboard_notifications(user_id)
        except Exception as e:
            self.handle_db_error(e)