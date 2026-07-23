import cv2
import os


def capture_face_images(student_code, num_images=40):
    """
    Capture face images using webcam and Haar Cascade.
    """

    # OpenCV internal haarcascade path (MOST STABLE)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    if face_cascade.empty():
        raise Exception("Haar cascade not loaded")

    # Dataset directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(
        BASE_DIR, "..", "datasets", "students", student_code
    )
    os.makedirs(dataset_dir, exist_ok=True)

    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Camera not accessible")

    count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5
            )

            for (x, y, w, h) in faces:
                count += 1
                face_img = gray[y:y+h, x:x+w]

                img_path = os.path.join(
                    dataset_dir, f"{student_code}_{count}.jpg"
                )
                cv2.imwrite(img_path, face_img)

                cv2.rectangle(
                    frame, (x, y), (x+w, y+h), (0, 255, 0), 2
                )
            
            # Display helpful guidance for users
            cv2.putText(
                frame,
                f"Captured: {count}/{num_images}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
            cv2.putText(
                frame,
                "Move your head slightly for better data",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

            cv2.imshow("Face Capture - Press Q to Exit", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            if count >= num_images:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

    return True, count
