"""
Test Script for Liveness Detection
Run this to verify that liveness detection works correctly.
"""

import cv2
import time
from core.liveness import get_liveness_detector


def test_liveness_detection():
    """
    Test liveness detection with live camera feed.
    
    Instructions:
    1. First, test with your real face (should pass after ~1 second of observation)
    2. Then, show a printed photo to the camera (should fail)
    3. Then, show a phone screen with a photo (should fail)
    4. Test with multiple people in frame (both should be detected)
    """
    
    print("=" * 60)
    print("LIVENESS DETECTION TEST")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Show your REAL FACE to camera - blink or move slightly")
    print("   → Should show GREEN box with 'LIVE' after ~1 second")
    print("\n2. Show a PRINTED PHOTO to camera")
    print("   → Should show RED box with 'SPOOF DETECTED'")
    print("\n3. Show a PHONE SCREEN with a face photo")
    print("   → Should show RED box with 'SPOOF DETECTED'")
    print("\n4. Have MULTIPLE PEOPLE in frame")
    print("   → All real faces should show GREEN, photos RED")
    print("\nPress ESC to exit")
    print("=" * 60)
    
    # Initialize liveness detector
    liveness_detector = get_liveness_detector()
    
    # Load face cascade for detection
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Cannot access camera")
        return
    
    print("\n✓ Camera opened successfully")
    print("✓ Liveness detector initialized")
    print("\nStarting live test...\n")
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error reading frame")
            break
        
        frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        current_time = time.time()
        
        # Process each detected face
        for (x, y, w, h) in faces:
            face_rect = (x, y, w, h)
            
            # Run liveness check
            liveness_result = liveness_detector.check_liveness(
                gray, face_rect, current_time
            )
            
            # Display results
            if liveness_result['is_live']:
                # ✅ LIVE FACE DETECTED
                color = (0, 255, 0)  # Green
                label = "LIVE ✓"
                status = f"Conf: {liveness_result['confidence']:.2f}"
                
                # Additional info
                info_lines = []
                if liveness_result['blink_detected']:
                    info_lines.append("Blink: YES")
                if liveness_result['movement_detected']:
                    info_lines.append("Move: YES")
                if liveness_result['texture_ok']:
                    info_lines.append("Texture: OK")
                
            else:
                # ❌ SPOOF DETECTED
                color = (0, 0, 255)  # Red
                label = "SPOOF DETECTED ✗"
                status = liveness_result['reason'][:30]
                info_lines = []
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
            
            # Draw label
            cv2.putText(
                frame, label, (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
            )
            
            # Draw status
            cv2.putText(
                frame, status, (x, y+h+25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
            )
            
            # Draw additional info
            for i, info in enumerate(info_lines):
                cv2.putText(
                    frame, info, (x, y+h+45+i*20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1
                )
        
        # Display frame info
        fps = frame_count / (time.time() - start_time)
        cv2.putText(
            frame, f"FPS: {fps:.1f}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )
        
        cv2.putText(
            frame, "Press ESC to exit", (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
        )
        
        # Show frame
        cv2.imshow("Liveness Detection Test", frame)
        
        # Check for ESC key
        if cv2.waitKey(1) == 27:
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print(f"\nTotal frames processed: {frame_count}")
    print(f"Average FPS: {fps:.1f}")
    print("\nTest Results Summary:")
    print("- If real faces showed GREEN with 'LIVE': ✅ PASS")
    print("- If photos showed RED with 'SPOOF': ✅ PASS")
    print("- If multiple faces were detected: ✅ PASS")
    print("\nIf all tests passed, liveness detection is working correctly!")


if __name__ == "__main__":
    try:
        test_liveness_detection()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
