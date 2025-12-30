# Student Management System 

A professional GUI-based academic management system built with **Python** and **Tkinter**. This project was developed as part of the **CSE314** course to apply advanced object-oriented programming (OOP), design patterns, and role-based access control (RBAC) in a realistic university environment.

The application supports two primary roles — **Students** and **Instructors** — each with distinct permissions, workflows, and dynamically rendered interfaces.

---

## 🚀 Key Features

### 1. Authentication & Role-Based Authorization
* **Secure Login System:** User credentials and sessions are validated against a local SQLite database using a dedicated security layer.
* **Role-Based Access Control (RBAC):** The interface dynamically adapts based on the authenticated user’s role.
    * **Student View:** Course registration/dropping, viewing grades, assignments, and receiving real-time notifications.
    * **Instructor View:** Course management, assignment creation, student grading, and posting campus-wide announcements.

### 2. Course Management
* **Course Registration:** Students can browse the catalog to enroll in or drop courses.
* **Deadline Tracking:** Automated tracking for assignment due dates.
* **Grading System:** Robust instructor interface to input and update student grades with persistent storage.

### 3. Communication Hub
* **Announcements:** Instructors can broadcast updates visible to all enrolled students.
* **Notifications:** In-app alerts for new assignments, grading updates, or system messages.

---

## 🛠️ Technical Stack
* **Language:** Python 3.x
* **GUI Framework:** Tkinter (Custom styled components)
* **Data Migration & Consistency:** Transitioning business logic from a local file-based system (SQLite) to a distributed network-based system (PostgreSQL) while maintaining ACID properties.* **Architecture:** Model-View-Controller (MVC) with Repository and Service patterns.
* **Programming Paradigm:** Heavy emphasis on Object-Oriented Programming (OOP) and Separation of Concerns.

---
## 🌐 Distributed System Migration
The project has transitioned from a local standalone application to a distributed system architecture:
* **Cloud Database:** Migrated from SQLite to **Cloud PostgreSQL** to allow remote access and data persistence across multiple client instances.
* **Concurrency:** The system now handles multiple simultaneous connections, ensuring data integrity and real-time updates for both Students and Instructors.
* **Environment Configuration:** Secure database connection management using environment variables for cloud credentials.
---
## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
    git clone https://github.com/Ahmed-fall/Student-Management-CSE314_project-.git
    
    cd Student-Management-CSE314_project-
  ```
2. **Install dependencies**
    ```
      pip install psycopg2-binary python-dotenv
    ```
3. **Configure Environment Variables**
    ```
      DB_HOST=your_cloud_host_address
      DB_NAME=your_database_name
      DB_USER=your_username
      DB_PASS=your_password
      DB_PORT=5432
    ```
4. **Initialize the Database**
    ```
      python database/initialize_db.py
    ```


5. **Run the application**
    ```
      python main.py
    ```
---
Navigate to the project directory:
   ```
   cd Student-Management-CSE314_project-
   ```

---
Run the application:
```
python main.py
```

---
📂 Project Structure:
```
├── main.py                 
├── controllers/            
│   ├── auth_controller.py
│   ├── instructor_controller.py
│   └── student_controller.py
├── core/                   
│   ├── async_task.py
│   ├── base_controller.py
│   ├── security.py
│   └── service_locator.py
├── database/               
│   ├── db_connection.py
│   └── initialize_db.py
├── models/                 
│   ├── assignment.py
│   ├── enrollment.py
│   └── student.py
├── repositories/           
│   ├── course_repo.py
│   └── user_repo.py
├── services/               
│   ├── auth_service.py
│   └── notification_service.py
├── ui/                  
│   ├── components/
│   │   └── sidebar.py
│   ├── main_window.py
│   └── styles.py
└── views/
    ├── auth/            
    ├── instructor/         
    └── student/           

```
---
🧠 Technical Challenges:
One of the main challenges was implementing Role-Based Authorization and State Management in a Tkinter environment. This was addressed by:
  -Decoupled Logic: Using a Service-Repository pattern to separate database queries from UI logic.
  -Dynamic UI Loading: Implementing a custom Router to switch between dashboards based on user permissions without restarting the app.
  -Centralized Security: Validating user roles through a dedicated security.py layer to prevent unauthorized data access.
  -Session Management: Maintaining a persistent user session across multiple views.
---
📘 Learning Outcomes:
Through this project, I gained hands-on experience with:

  -Designing and implementing Role-Based Access Control (RBAC).
  -Building complex desktop GUI applications using Tkinter.
  -Applying Enterprise Design Patterns (MVC, Repository, Service Locator).
  -Database Schema Design and integration with SQLite.
  -Handling real-world logic like deadlines, input validation, and user workflows.

