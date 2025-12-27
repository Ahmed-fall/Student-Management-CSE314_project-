# Student Management System (CSE314 Project)

A GUI-based academic management system built with **Python** and **Tkinter**. This project was developed as part of the **CSE314** course to apply object-oriented programming, GUI development, and role-based access control (RBAC) concepts in a realistic university system.

The application supports two primary roles — **Students** and **Instructors** — each with distinct permissions and workflows.

---

## 🚀 Key Features

### 1. Authentication & Role-Based Authorization
* **Secure Login System:** User credentials are validated against a local SQLite database.
* **Role-Based Access Control (RBAC):** The interface dynamically adapts based on the authenticated user’s role.
  * **Student View:** Course registration and dropping, viewing grades and assignments.
  * **Instructor View:** Managing courses and assignments, grading students, and posting announcements.

### 2. Course Management
* **Course Registration:** Students can enroll in or drop courses.
* **Deadline Tracking:** Assignments are associated with due dates.
* **Grading System:** Instructors can input and update student grades stored persistently.

### 3. Communication Hub
* **Announcements:** Instructors can post announcements visible to all enrolled students.
* **Notifications:** In-app alerts for new assignments or grading updates.

---

## 🛠️ Technical Stack
* **Language:** Python 3.x
* **GUI Framework:** Tkinter
* **Database:** SQLite (persistent local storage)
* **Programming Paradigm:** Object-Oriented Programming (OOP)

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Ahmed-fall/Student-Management-CSE314_project-.git](https://github.com/Ahmed-fall/Student-Management-CSE314_project-.git)

---
Navigate to the project directory
```
cd Student-Management-CSE314_project-
```

Run the application
```
python main.py
```

---
📂 Project Structure
```
├── main.py              # Application entry point
├── auth.py              # Authentication and authorization logic
├── database.py          # SQLite database operations
├── ui/                  # Tkinter UI components
│   ├── student_tab.py
│   └── instructor_tab.py
└── data/
    └── database.db      # SQLite database file
```
---
🧠 Technical Challenges
One of the main challenges of this project was implementing role-based authorization in a Tkinter-based GUI application. This was addressed by:
-Validating user roles during the login process.
-Dynamically loading UI components based on user permissions.
-Centralizing authorization logic to prevent unauthorized access.
-Managing application state across multiple user sessions.
---

📘 Learning Outcomes
Through this project, I gained hands-on experience with:
-Designing and implementing Role-Based Access Control (RBAC).
-Building desktop GUI applications using Tkinter.
-Structuring applications using object-oriented principles.
-Integrating SQLite for persistent data storage.
-Handling deadlines, validation logic, and user workflows.
---