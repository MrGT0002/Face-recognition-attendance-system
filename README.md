# Face Recognition Attendance System (Tkinter + OpenCV + SQLite)

A desktop-based **Face Recognition Attendance System** built with **Python**, **Tkinter**, **OpenCV (Haar Cascade + LBPH)**, and **SQLite**. It supports **Admin**, **Teacher**, and **Student** roles with separate dashboards.

---

## Technologies Used

- **Python 3.x**
- **Tkinter** (desktop GUI)
- **OpenCV**:
  - Haar Cascade (face detection)
  - LBPH (face recognition via `cv2.face`)
- **SQLite** (local database)

> Note: LBPH requires **opencv-contrib-python** (because `cv2.face` is part of *opencv-contrib*).

---

## Project Structure (High Level)

- **`main.py`**: Unified login screen (Admin / Teacher / Student)
- **`core/`**: DB connection, authentication, camera capture, model training, recognition/attendance
- **`database/schema.sql`**: SQLite schema for all required tables
- **`admin/admin_dashboard.py`**: Admin GUI (years/subjects/courses + register teachers/students + capture faces)
- **`teacher/teacher_dashboard.py`**: Teacher GUI (start/resume/end session + launch recognition + view session attendance)
- **`student/student_dashboard.py`**: Student GUI (view own attendance + subject/date views + percentage)
- **`datasets/students/<student_code>/`**: Captured student face images
- **`models/lbph_model.yml`**: Trained LBPH model output

---

## Installation Steps (Windows)

1) **Clone / open** this project folder.

2) Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate
```

3) Install dependencies:

```bash
pip install opencv-contrib-python numpy
```

> Tkinter comes bundled with most Python Windows installations (no separate install needed).

---

## Database Setup

This project uses: **`database/attendance.db`**

1) Create the DB and tables by running the schema:

```bash
sqlite3 database/attendance.db ".read database/schema.sql"
```

2) (Optional) Create a default admin:
- The `admins` table stores `password_hash` (SHA-256).
- You can generate a SHA-256 hash using `core/auth.py`’s `hash_password()` or any SHA-256 tool.

Example SQL (replace values):

```sql
INSERT INTO admins (username, password_hash, full_name, email)
VALUES ('admin', '<sha256_hash_here>', 'System Admin', 'admin@example.com');
```

---

## How to Run the Project

Start the application:

```bash
python main.py
```

You will see a **login screen** where you choose:
- Admin
- Teacher
- Student

After login, you are redirected to the correct dashboard.

---

## System Features

- **Face detection** with Haar Cascade (real-time)
- **Face recognition** with LBPH (OpenCV `cv2.face`)
- **Student face dataset capture** (30–50 grayscale face images per student)
- **Model training** and saving to `models/lbph_model.yml`
- **Class sessions** stored in SQLite
- **Attendance marking** with timestamp and duplicate prevention
- **Attendance viewing**:
  - Teacher: session attendance list
  - Student: personal attendance (subject-wise and date-wise) + percentage

---

## Role-Based Access (What Each Role Can Do)

### Admin
- Add **Years**
- Add **Subjects**
- Add **Courses** (linked to Year + Subject)
- Register **Teachers**
- Register **Students**
- Trigger **face image capture** during student registration
- Optionally trigger **model training** after registration

### Teacher
- Login and access teacher dashboard
- Select course and **start a class session**
- Session is saved with status **`ongoing`** so it stays **ACTIVE across app restarts**
- Launch **live face recognition** to mark attendance
- End class session manually (status becomes **`completed`**)

### Student
- Login and view **only their own attendance**
- Attendance shown:
  - **Date-wise**
  - **Subject-wise**
  - **Summary + percentages**

---

## Exam / Viva Usage Notes (Recommended Demo Flow)

1) **Initialize DB** using `database/schema.sql`.
2) **Login as Admin** (create an admin row first).
3) Add **Year → Subject → Course**.
4) Register a **Teacher** and a **Student**.
5) During student registration, **capture face images** into `datasets/students/<student_code>/`.
6) Run **model training** (Admin dashboard prompts for it).
7) Login as **Teacher**:
   - Start session (status becomes `ongoing`)
   - Start recognition to mark attendance
8) Login as **Student** to verify attendance is visible and percentages are calculated.

### Common Viva Questions You Can Answer From This Project
- Why **Haar Cascade** for detection? (fast, classical detector)
- Why **LBPH** for recognition? (works well with small datasets; robust to lighting changes)
- How duplicates are prevented? (SQLite `UNIQUE(student_id, session_id)` + check before insert)
- How sessions persist across restarts? (`class_sessions.status = 'ongoing'` is queried on startup)

### Important Notes / Limitations (Current Build)
- **Teacher/Student password verification** is currently simplified because the `teachers` and `students` tables do **not** include `password_hash` columns. Admin passwords are hashed and verified.
  - If you want full password auth for Teacher/Student, add `password_hash` fields to those tables and update `core/auth.py`.
- Recognition requires a trained model file: **`models/lbph_model.yml`**.
- Camera access depends on your device permissions and available webcam.

---

## Reference

- Architecture overview: `ARCHITECTURE.md`

