import cv2
import os
import time
import numpy as np
from core.liveness import get_liveness_detector

MODEL_PATH = "models/lbph_model.yml"
LABELS_PATH = "models/labels.npy"


def load_labels():
    """
    Load label mapping saved during training
    label_id -> student_code
    """
    if not os.path.exists(LABELS_PATH):
        raise FileNotFoundError("labels.npy not found. Train model first.")

    return np.load(LABELS_PATH, allow_pickle=True).item()


def recognize_students(duration=20, confidence_threshold=70, duration_seconds=None):
    """
    Opens camera and recognizes students for given duration (seconds)
    Now includes liveness detection to prevent photo/screen spoofing.

    Returns:
        set of recognized student_codes
    """

    # 🔧 backward compatibility fix
    if duration_seconds is not None:
        duration = duration_seconds

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Trained model not found.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    labels = load_labels()

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Initialize liveness detector
    liveness_detector = get_liveness_detector()
    print("🔒 Liveness detection enabled - photos/screens will be blocked")

    cap = cv2.VideoCapture(0)
    recognized_students = set()

    print("📷 Camera started. Press ESC to stop early.")
    start_time = time.time()

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        current_time = time.time()

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            face_rect = (x, y, w, h)

            # ✅ LIVENESS CHECK: Verify this is a real face, not a photo
            liveness_result = liveness_detector.check_liveness(gray, face_rect, current_time)
            
            # Only proceed with recognition if liveness check passes
            if liveness_result['is_live']:
                label_id, confidence = recognizer.predict(roi)

                if confidence < confidence_threshold:
                    student_code = labels.get(label_id)
                    recognized_students.add(student_code)

                    # Green box for recognized + live face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        f"{student_code} - LIVE",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                else:
                    # Yellow box for live but unknown face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    cv2.putText(
                        frame,
                        "Unknown - LIVE",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )
            else:
                # ❌ SPOOF DETECTED: Red box for failed liveness check
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                
                # Display liveness status
                status_text = liveness_result['reason'][:20]  # Truncate for display
                cv2.putText(
                    frame,
                    "PHOTO/SCREEN?",
                    (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )
                cv2.putText(
                    frame,
                    status_text,
                    (x, y+h+20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 0, 255),
                    1
                )

        # Display instructions
        cv2.putText(
            frame,
            "Liveness: Blink or move slightly",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow("Attendance Recognition", frame)
        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

    print("✅ Recognized students (liveness verified):", recognized_students)
    return recognized_students
from core.attendance import mark_attendance

def start_attendance_recognition(session_id, duration=20, confidence_threshold=70):
    """
    Wrapper used by Teacher Dashboard.
    Recognizes students and marks attendance automatically.
    """
    students = recognize_students(
        duration=duration,
        confidence_threshold=confidence_threshold
    )

    for student_code in students:
        mark_attendance(student_code, session_id)
