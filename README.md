Student Management System (CSE314 Project)
A GUI-based academic management system built with Python and Tkinter.
This project was developed as part of the CSE314 course to apply object-oriented programming, GUI development, and role-based access control (RBAC) concepts in a realistic university system.
The application supports two distinct user roles — Students and Instructors — each with independent permissions, workflows, and interfaces.
________________________________________
🚀 Key Features
1. Authentication & Role-Based Authorization
•	Secure Login System
User credentials are validated against a local SQLite database.
•	Role-Based Access Control (RBAC)
After authentication, users are directed to a role-specific interface based on their assigned role.
________________________________________
👨‍🎓 Student Features
•	Register for available courses
•	Drop registered courses
•	View assignments and deadlines
•	View grades for enrolled courses
•	Receive announcements and notifications
________________________________________
👨‍🏫 Instructor Features
•	Manage assignments for assigned courses
•	Grade students and update grades
•	Post announcements to enrolled students
•	Monitor student participation
________________________________________
🛠️ Technical Stack
•	Language: Python 3.x
•	GUI Framework: Tkinter
•	Database: SQLite (persistent local storage)
•	Programming Paradigm: Object-Oriented Programming (OOP)
________________________________________
📸 Screenshots
![login](https://github.com/user-attachments/assets/0a4ab134-1fda-4a34-8592-10c2d272f872)


		
________________________________________
⚙️ Installation & Setup
1.	Clone the repository
git clone https://github.com/Ahmed-fall/Student-Management-CSE314_project-.git
2.	Navigate to the project directory
cd Student-Management-CSE314_project-
3.	Run the application
python main.py
Ensure Python 3 is installed on your system.
________________________________________
📂 Project Structure
```
├── controllers
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── instructor_controller.py
│   └── student_controller.py
├── core
│   ├── __init__.py
│   ├── async_task.py
│   ├── base_controller.py
│   ├── base_model.py
│   ├── base_repository.py
│   ├── base_service.py
│   ├── base_view.py
│   ├── router.py
│   ├── security.py
│   ├── service_locator.py
│   └── session.py
├── database
│   ├── __init__.py
│   ├── db_connection.py
│   └── initialize_db.py
├── main.py
├── models
│   ├── __init__.py
│   ├── announcement.py
│   ├── assignment.py
│   ├── course.py
│   ├── enrollment.py
│   ├── grade.py
│   ├── instructor.py
│   ├── notification.py
│   ├── student.py
│   ├── submission.py
│   └── user.py
├── repositories
│   ├── __init__.py
│   ├── announcement_repo.py
│   ├── assignment_repo.py
│   ├── course_repo.py
│   ├── enrollment_repo.py
│   ├── grade_repo.py
│   ├── instructor_repo.py
│   ├── notification_repo.py
│   ├── student_repo.py
│   ├── submission_repo.py
│   └── user_repo.py
├── services
│   ├── __init__.py
│   ├── announcement_service.py
│   ├── assignment_service.py
│   ├── auth_service.py
│   ├── course_service.py
│   ├── instructor_service.py
│   ├── notification_service.py
│   ├── student_service.py
│   └── user_service.py
├── ui
│   ├── components
│   │   └── sidebar.py
│   ├── main_window.py
│   └── styles.py
└── views
    ├── __init__.py
    ├── auth
    │   ├── login_view.py
    │   └── register_view.py
    ├── instructor
    │   ├── announcements_view.py
    │   ├── campus_manager_view.py
    │   ├── course_editor_view.py
    │   ├── dashboard_view.py
    │   └── grading_view.py
    └── student
        ├── assignment_details_view.py
        ├── assignments_view.py
        ├── catalog_view.py
        ├── classroom_view.py
        ├── courses_view.py
        ├── dashboard_view.py
        ├── grades_view.py
        └── notifications_view.py
```
________________________________________
👥 Team Members & Contributions
This project was developed collaboratively, with clear ownership of both role-specific logic and content modules.
🧑‍💻 People Team
Student Role
•	Maram Elsayed Mohamed
Implemented student-side functionality including course registration and dropping, grade viewing, and assignment access.
Instructor Role
•	Hassan Abouelgoud Mohamed
Developed instructor-side features such as assignment management, student grading, and instructor workflows.
Authentication
•	Mohamed Ahmed Mohamed
Designed and implemented secure login, user validation, and role-based access control (RBAC).
________________________________________
📚 Content Team
•	Seifeldin Elsaadi
Courses Module
Managed course data, enrollment logic, and related database interactions.
•	Ahmed Hassan Madi
Assignments Module
Implemented assignment handling, deadline management, and assignment persistence.
•	Ali Ahmed Elzwawy
Announcements & Notifications Module
Developed the announcement system and in-app notifications for assignments and grading updates.
________________________________________
🧠 Technical Challenges
During development, the team encountered several real-world software engineering challenges:
•	Team Coordination
Synchronizing work across multiple developers required clear module boundaries and frequent integration.
•	Maintaining MVC Separation
Preserving separation between View (Tkinter UI), Controller (logic), and Model (SQLite operations) was challenging and required disciplined code organization.
•	Managing Database Relations
Designing relationships between students, instructors, courses, assignments, grades, and announcements demanded careful schema planning.
•	Avoiding Spaghetti Code
Growth in application complexity was controlled through modular design, OOP principles, and centralized logic.
•	Role-Based Authorization
Enforcing strict separation between student and instructor permissions while dynamically loading interfaces was a key challenge.
________________________________________
📘 Learning Outcomes
Through this project, the team gained practical experience in:
•	Implementing role-based access control (RBAC)
•	Developing GUI applications using Tkinter
•	Applying MVC and object-oriented design principles
•	Managing relational data using SQLite
•	Collaborating on a multi-developer software project
________________________________________
✅ Status
✔ Completed
✔ Core functionality implemented and stable
✔ Ready for demonstration and future extension
