from datetime import datetime, timedelta
from core.base_service import BaseService

# Repositories
from repositories.course_repo import CourseRepository
from repositories.enrollment_repo import EnrollmentRepository
from repositories.assignment_repo import AssignmentRepository
from repositories.grade_repo import GradeRepository
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
        self.assignment_repo = AssignmentRepository()
        self.grade_repo = GradeRepository()

    # ---------------------------------------------------------
    # 1. ENROLLMENT: Join a Course
    # ---------------------------------------------------------
    def enroll_course(self, student_id: int, course_id: int):
        """
        Registers a student for a course if eligible.
        """
        try:
            # 1. Check Course Exists
            course = self.course_repo.get_by_id(course_id)
            if not course:
                raise ValueError("Course not found.")

            # 2. Check Duplicate Enrollment (Prevent double booking)
            if self.enrollment_repo.is_enrolled(student_id, course_id):
                raise ValueError("Student is already enrolled in this course.")

            # 3. Create Enrollment Object
            enrollment = Enrollment(
                id=None,
                student_id=student_id,
                course_id=course_id,
                date_enrolled=datetime.now().isoformat(),
                status='enrolled'
            )
            
            # 4. Save to DB
            return self.enrollment_repo.create(enrollment)

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
    def get_transcript(self, student_id: int):
        """
        Generates a Report Card using optimized Repository aggregations.
        Calculates grades dynamically: (Total Earned / Total Possible) * 100
        """
        try:
            report_card = []
            
            # 1. Get all active enrollments
            enrollments = self.enrollment_repo.get_by_student_id(student_id)
            active_enrollments = [e for e in enrollments if e.status == 'enrolled']

            for enrollment in active_enrollments:
                course = self.course_repo.get_by_id(enrollment.course_id)
                
                # --- OPTIMIZED SECTION ---
                # Let SQL do the heavy lifting
                possible_points = self.assignment_repo.get_course_max_score(course.id)
                earned_points = self.grade_repo.get_student_total_score(student_id, course.id)
                # -------------------------

                # Calculate Percentage
                if possible_points > 0:
                    percentage = (earned_points / possible_points) * 100
                else:
                    percentage = 0.0

                report_card.append({
                    "course_code": course.code,
                    "course_name": course.name,
                    "credits": course.credits,
                    "earned_points": earned_points,
                    "possible_points": possible_points,
                    "current_average": round(percentage, 2),
                    "letter_grade": self._calculate_letter_grade(percentage)
                })

            return report_card

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
    def get_my_courses(self, student_id: int):
        """
        Returns a list of Course objects that the student is currently enrolled in.
        """
        try:
            # 1. Get all enrollment records for this student
            enrollments = self.enrollment_repo.get_by_student_id(student_id)
            
            if not enrollments:
                return []

            # 2. Fetch the actual Course details for each enrollment
            # (Looping here is fine for this scale; larger apps might use a SQL JOIN)
            my_courses = []
            for record in enrollments:
                course = self.course_repo.get_by_id(record.course_id)
                # Ensure the course still exists before adding
                if course:
                    my_courses.append(course)
            
            return my_courses

        except Exception as e:
            self.handle_db_error(e)