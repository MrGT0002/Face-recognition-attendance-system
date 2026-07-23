# Face Recognition Attendance System - Architecture Design

## 1. Complete Folder Structure

```
FaceRecognitionAttendance/
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── face_detector.py          # Haar Cascade face detection
│   │   ├── face_trainer.py           # LBPH face recognizer training
│   │   ├── face_recognizer.py        # LBPH face recognition
│   │   └── camera_handler.py         # Camera interface management
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py             # SQLite connection & operations
│   │   ├── models.py                 # Database models/schema definitions
│   │   └── queries.py                # SQL query templates
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py            # Main Tkinter application window
│   │   ├── register_panel.py         # User registration interface
│   │   ├── attendance_panel.py       # Attendance marking interface
│   │   ├── view_panel.py             # View attendance records interface
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── camera_preview.py     # Live camera preview widget
│   │       └── attendance_table.py   # Attendance records table widget
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── image_processor.py        # Image preprocessing utilities
│   │   ├── validators.py             # Input validation functions
│   │   └── helpers.py                # General utility functions
│   │
│   └── config/
│       ├── __init__.py
│       └── settings.py               # Configuration constants & paths
│
├── data/
│   ├── database/
│   │   └── attendance.db             # SQLite database file
│   │
│   ├── faces/
│   │   └── training/                 # Raw face images for training
│   │       └── [user_id]/            # User-specific folders
│   │           └── *.jpg             # Face training images
│   │
│   └── models/
│       ├── haarcascade_frontalface_default.xml  # Haar Cascade model
│       └── lbph_model.yml            # Trained LBPH recognizer model
│
├── tests/
│   ├── __init__.py
│   ├── test_face_detector.py
│   ├── test_face_recognizer.py
│   ├── test_database.py
│   └── test_utils.py
│
├── logs/
│   └── .gitkeep                      # Log files directory
│
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation
├── ARCHITECTURE.md                   # This file
└── .gitignore                        # Git ignore rules

```

---

## 2. Database Schema (Tables + Relations)

### Database: `attendance.db`

#### Table 1: `users`
Stores registered user information.

| Column Name      | Data Type    | Constraints              | Description                    |
|------------------|--------------|--------------------------|--------------------------------|
| user_id          | INTEGER      | PRIMARY KEY, AUTOINCREMENT | Unique user identifier        |
| full_name        | TEXT         | NOT NULL                 | User's full name              |
| employee_id      | TEXT         | NOT NULL, UNIQUE         | Employee/student ID           |
| email            | TEXT         | UNIQUE                   | Email address (optional)      |
| department       | TEXT         |                          | Department/class (optional)   |
| registered_date  | TEXT         | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Registration timestamp |
| is_active        | INTEGER      | NOT NULL, DEFAULT 1      | 1=active, 0=inactive          |

#### Table 2: `face_encodings`
Links users to their face training data.

| Column Name      | Data Type    | Constraints              | Description                    |
|------------------|--------------|--------------------------|--------------------------------|
| encoding_id      | INTEGER      | PRIMARY KEY, AUTOINCREMENT | Unique encoding identifier   |
| user_id          | INTEGER      | NOT NULL, FOREIGN KEY    | References users.user_id      |
| training_images  | INTEGER      | NOT NULL, DEFAULT 0      | Number of training images     |
| model_version    | TEXT         |                          | LBPH model version identifier |
| last_trained     | TEXT         | DEFAULT CURRENT_TIMESTAMP | Last training timestamp       |

**Foreign Key:**
- `user_id` → `users.user_id` ON DELETE CASCADE

#### Table 3: `attendance_records`
Stores attendance marking events.

| Column Name      | Data Type    | Constraints              | Description                    |
|------------------|--------------|--------------------------|--------------------------------|
| record_id        | INTEGER      | PRIMARY KEY, AUTOINCREMENT | Unique record identifier     |
| user_id          | INTEGER      | NOT NULL, FOREIGN KEY    | References users.user_id      |
| attendance_date  | TEXT         | NOT NULL                 | Date of attendance (YYYY-MM-DD) |
| attendance_time  | TEXT         | NOT NULL                 | Time of attendance (HH:MM:SS) |
| attendance_type  | TEXT         | NOT NULL, DEFAULT 'check_in' | 'check_in' or 'check_out' |
| confidence_score | REAL         |                          | Recognition confidence (0-100) |
| status           | TEXT         | DEFAULT 'verified'       | 'verified', 'manual', 'error' |
| remarks          | TEXT         |                          | Additional notes              |

**Foreign Key:**
- `user_id` → `users.user_id` ON DELETE CASCADE

**Indexes:**
- `idx_attendance_date` on `attendance_date`
- `idx_user_date` on (`user_id`, `attendance_date`)
- `idx_attendance_datetime` on (`attendance_date`, `attendance_time`)

#### Table 4: `system_logs`
Optional: System operation logs.

| Column Name      | Data Type    | Constraints              | Description                    |
|------------------|--------------|--------------------------|--------------------------------|
| log_id           | INTEGER      | PRIMARY KEY, AUTOINCREMENT | Unique log identifier        |
| log_type         | TEXT         | NOT NULL                 | 'info', 'warning', 'error'    |
| log_message      | TEXT         | NOT NULL                 | Log message content           |
| timestamp        | TEXT         | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Log timestamp          |
| user_id          | INTEGER      |                          | Associated user (optional)    |

---

## 3. Module Responsibilities

### 3.1 Core Module (`src/core/`)

#### `face_detector.py`
- **Purpose**: Face detection using Haar Cascade
- **Responsibilities**:
  - Load Haar Cascade classifier model
  - Detect faces in images/video frames
  - Return bounding box coordinates
  - Handle multiple face detection
  - Convert color spaces (BGR to grayscale)

#### `face_trainer.py`
- **Purpose**: Train LBPH face recognizer
- **Responsibilities**:
  - Collect face images for a user
  - Preprocess training images (resize, grayscale, normalize)
  - Train LBPH recognizer on user's face data
  - Save trained model to file
  - Update face_encodings table with training metadata

#### `face_recognizer.py`
- **Purpose**: Recognize faces using trained LBPH model
- **Responsibilities**:
  - Load trained LBPH recognizer model
  - Recognize faces in video frames
  - Return user_id and confidence score
  - Handle unknown faces (confidence threshold)
  - Manage recognizer state (loaded/unloaded)

#### `camera_handler.py`
- **Purpose**: Manage camera interface
- **Responsibilities**:
  - Initialize camera connection
  - Capture frames from camera
  - Release camera resources
  - Handle camera errors/exceptions
  - Provide frame resolution settings

### 3.2 Database Module (`src/database/`)

#### `db_manager.py`
- **Purpose**: Database connection and transaction management
- **Responsibilities**:
  - Create database connection
  - Initialize database schema (tables, indexes)
  - Execute SQL queries (CRUD operations)
  - Handle transactions (commit/rollback)
  - Manage database connection lifecycle
  - Database backup/restore utilities

#### `models.py`
- **Purpose**: Data models and schema definitions
- **Responsibilities**:
  - Define table creation SQL statements
  - Define index creation statements
  - Define foreign key constraints
  - Schema version management

#### `queries.py`
- **Purpose**: SQL query templates
- **Responsibilities**:
  - Centralized SQL query strings
  - Parameterized query templates
  - Common query patterns (insert, select, update, delete)

### 3.3 GUI Module (`src/gui/`)

#### `main_window.py`
- **Purpose**: Main application window and navigation
- **Responsibilities**:
  - Initialize Tkinter application
  - Create main menu/navigation bar
  - Manage panel switching (Register/Attendance/View)
  - Application lifecycle management
  - Global error handling

#### `register_panel.py`
- **Purpose**: User registration interface
- **Responsibilities**:
  - Display user registration form
  - Collect user information (name, ID, email, etc.)
  - Camera preview for face capture
  - Capture multiple face images for training
  - Trigger face training process
  - Validate input fields

#### `attendance_panel.py`
- **Purpose**: Attendance marking interface
- **Responsibilities**:
  - Display live camera preview
  - Continuous face detection and recognition
  - Display recognized user information
  - Mark attendance (check-in/check-out)
  - Show attendance confirmation
  - Handle duplicate attendance prevention

#### `view_panel.py`
- **Purpose**: View attendance records interface
- **Responsibilities**:
  - Display attendance records table
  - Filter records by date, user, department
  - Export attendance data (CSV/Excel)
  - Generate attendance reports
  - Search functionality

#### `widgets/camera_preview.py`
- **Purpose**: Reusable camera preview widget
- **Responsibilities**:
  - Display live video feed in Tkinter
  - Handle frame updates (FPS management)
  - Overlay face detection boxes
  - Display recognition results

#### `widgets/attendance_table.py`
- **Purpose**: Reusable attendance records table widget
- **Responsibilities**:
  - Display attendance data in tabular format
  - Sorting functionality
  - Pagination support
  - Row selection handling

### 3.4 Utils Module (`src/utils/`)

#### `image_processor.py`
- **Purpose**: Image preprocessing utilities
- **Responsibilities**:
  - Image resizing and normalization
  - Grayscale conversion
  - Face region extraction
  - Image quality enhancement
  - Format conversion

#### `validators.py`
- **Purpose**: Input validation functions
- **Responsibilities**:
  - Email validation
  - Employee ID format validation
  - Date/time validation
  - Required field validation

#### `helpers.py`
- **Purpose**: General utility functions
- **Responsibilities**:
  - Date/time formatting
  - File path operations
  - Configuration loading
  - Logging utilities

### 3.5 Config Module (`src/config/`)

#### `settings.py`
- **Purpose**: Application configuration and constants
- **Responsibilities**:
  - Database path configuration
  - Model file paths (Haar Cascade, LBPH)
  - Training images path
  - Camera settings (resolution, FPS)
  - Recognition thresholds (confidence, minimum faces)
  - Application constants

---

## 4. System Workflow Explanation

### 4.1 User Registration Workflow

```
1. User opens Registration Panel
   ↓
2. User fills registration form:
   - Full Name
   - Employee ID
   - Email (optional)
   - Department (optional)
   ↓
3. User clicks "Start Face Capture"
   ↓
4. Camera activates and shows live preview
   ↓
5. System detects face using Haar Cascade:
   - Face detected? → Continue
   - No face? → Show error, retry
   ↓
6. System captures multiple face images (e.g., 20-30):
   - Saves images to data/faces/training/[user_id]/
   - Ensures good quality (lighting, angle, distance)
   ↓
7. User completes image capture
   ↓
8. System processes images:
   - Preprocesses (grayscale, resize, normalize)
   - Extracts face regions
   ↓
9. System trains LBPH recognizer:
   - Creates/updates LBPH model with new user data
   - Saves model to data/models/lbph_model.yml
   ↓
10. System saves user data to database:
    - Inserts record in users table
    - Inserts record in face_encodings table
    ↓
11. Registration complete - success message shown
```

### 4.2 Attendance Marking Workflow

```
1. User opens Attendance Panel
   ↓
2. Camera activates and shows live preview
   ↓
3. System continuously processes video frames:
   For each frame:
   a. Detect faces using Haar Cascade
      ↓
   b. If face detected:
      - Extract face region
      - Recognize face using LBPH recognizer
      - Get user_id and confidence score
      ↓
   c. Check confidence threshold (e.g., > 70%)
      - Above threshold? → Valid recognition
      - Below threshold? → Unknown person
      ↓
   d. Display recognition result on screen:
      - Show user name and employee ID
      - Show confidence score
   ↓
4. User clicks "Mark Attendance" button
   ↓
5. System verifies current recognition:
   - User still detected? → Proceed
   - No user detected? → Show error
   ↓
6. System determines attendance type:
   - Check if user already checked in today:
     * No record today → Mark as "check_in"
     * Has check_in, no check_out → Mark as "check_out"
     * Has both today → Show error (already completed)
   ↓
7. System records attendance in database:
   - Insert record in attendance_records table
   - Include: user_id, date, time, type, confidence
   ↓
8. System shows confirmation:
   - Display success message
   - Show attendance details (time, type)
   ↓
9. Continue monitoring for next attendance
```

### 4.3 View Attendance Records Workflow

```
1. User opens View Panel
   ↓
2. System loads attendance records from database:
   - Queries attendance_records table
   - Joins with users table for user details
   - Default: Show today's records or last 7 days
   ↓
3. Display records in table format:
   - Columns: Name, Employee ID, Date, Time, Type, Status
   - Sortable columns
   ↓
4. User can apply filters:
   - Date range picker
   - User/Employee ID search
   - Department filter
   - Attendance type filter
   ↓
5. User can export data:
   - Select export format (CSV/Excel)
   - Generate and download file
   ↓
6. User can view detailed record:
   - Click on record row
   - Show full details popup
```

### 4.4 Application Initialization Workflow

```
1. Application starts (main.py or main_window.py)
   ↓
2. Initialize configuration:
   - Load settings from config/settings.py
   - Verify paths exist (create if needed)
   ↓
3. Initialize database:
   - Check if database exists
   - If not exists: Create database and tables
   - If exists: Verify schema (migrations if needed)
   - Test database connection
   ↓
4. Initialize face recognition components:
   - Load Haar Cascade classifier
   - Check if LBPH model exists:
     * Exists: Load LBPH recognizer
     * Not exists: Initialize empty recognizer
   ↓
5. Initialize GUI:
   - Create main window
   - Load main menu/navigation
   - Set default panel (e.g., Attendance Panel)
   ↓
6. Application ready - display main window
```

### 4.5 Error Handling Workflow

```
Throughout the system:
- Camera errors: Show error message, allow retry
- Recognition errors: Log error, continue monitoring
- Database errors: Show error message, rollback transaction
- Invalid input: Show validation errors on form
- Face not detected: Show user guidance message
- Low confidence: Show warning, allow manual override
```

---

## 5. Key Design Decisions

### 5.1 Face Recognition Approach
- **Haar Cascade**: Fast face detection, good for real-time processing
- **LBPH**: Simple, effective for small to medium datasets, works well with controlled lighting

### 5.2 Database Choice
- **SQLite**: Lightweight, file-based, no server required, suitable for single-user/desktop app

### 5.3 GUI Framework
- **Tkinter**: Built-in with Python, simple desktop UI, cross-platform

### 5.4 Training Strategy
- Multiple images per user (20-30) for better accuracy
- User-specific folders for organization
- Incremental training (add new users without retraining all)

### 5.5 Attendance Logic
- Single check-in/check-out per day
- Prevents duplicate entries
- Tracks confidence scores for quality assurance

---

## 6. Future Enhancements (Out of Scope)

- Face recognition model updates (Deep Learning: FaceNet, ArcFace)
- Multi-camera support
- Network database (PostgreSQL/MySQL)
- Web interface
- Mobile app integration
- Email notifications
- Attendance analytics dashboard
- Export to payroll systems
