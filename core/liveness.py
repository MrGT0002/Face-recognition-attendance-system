"""
Liveness Detection Module
Detects whether a face is from a real person or a photo/screen spoof.
Uses multiple techniques: eye blink detection, head movement, and texture analysis.
Supports multiple simultaneous faces with per-face state tracking.
"""

import cv2
import numpy as np
from scipy.spatial import distance
from collections import deque
import time


class LivenessDetector:
    """
    Detects liveness for multiple faces simultaneously.
    Tracks each face over time to detect blinks and natural movements.
    """
    
    def __init__(self, 
                 blink_threshold=0.21,
                 movement_threshold=5.0,
                 texture_threshold=100.0,
                 observation_window=90):
        """
        Initialize liveness detector with configurable thresholds.
        
        Args:
            blink_threshold: Eye aspect ratio threshold for blink detection
            movement_threshold: Minimum movement variance for liveness
            texture_threshold: Laplacian variance threshold for real skin
            observation_window: Number of frames to track (3 seconds at 30fps)
        """
        self.blink_threshold = blink_threshold
        self.movement_threshold = movement_threshold
        self.texture_threshold = texture_threshold
        self.observation_window = observation_window
        
        # Per-face tracking state
        # Key: face_id, Value: dict with tracking data
        self.face_states = {}
        
        # Try to load dlib models (optional, fallback to simpler methods if unavailable)
        self.use_dlib = False
        try:
            import dlib
            # Load dlib's face landmark predictor
            # This requires shape_predictor_68_face_landmarks.dat
            # We'll try to load it, but fall back gracefully if not available
            predictor_path = "models/shape_predictor_68_face_landmarks.dat"
            try:
                self.predictor = dlib.shape_predictor(predictor_path)
                self.detector = dlib.get_frontal_face_detector()
                self.use_dlib = True
                print("✓ Dlib facial landmarks loaded - using advanced blink detection")
            except:
                print("⚠ Dlib model not found, using simplified liveness detection")
                self.use_dlib = False
        except ImportError:
            print("⚠ Dlib not installed, using simplified liveness detection")
            self.use_dlib = False
    
    def _calculate_eye_aspect_ratio(self, eye_points):
        """
        Calculate Eye Aspect Ratio (EAR) for blink detection.
        
        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        
        When eye is open: EAR ≈ 0.3
        When eye is closed: EAR < 0.2
        """
        # Compute vertical eye distances
        vertical_1 = distance.euclidean(eye_points[1], eye_points[5])
        vertical_2 = distance.euclidean(eye_points[2], eye_points[4])
        
        # Compute horizontal eye distance
        horizontal = distance.euclidean(eye_points[0], eye_points[3])
        
        # Calculate EAR
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return ear
    
    def _detect_blink_dlib(self, frame_gray, face_rect):
        """
        Detect blinks using dlib facial landmarks.
        Returns current EAR value or None if detection fails.
        """
        if not self.use_dlib:
            return None
        
        import dlib
        
        try:
            # Convert OpenCV rect to dlib rect
            x, y, w, h = face_rect
            dlib_rect = dlib.rectangle(int(x), int(y), int(x+w), int(y+h))
            
            # Get facial landmarks
            shape = self.predictor(frame_gray, dlib_rect)
            
            # Extract eye coordinates
            # Left eye: landmarks 36-41
            # Right eye: landmarks 42-47
            left_eye = []
            right_eye = []
            
            for i in range(36, 42):
                left_eye.append((shape.part(i).x, shape.part(i).y))
            for i in range(42, 48):
                right_eye.append((shape.part(i).x, shape.part(i).y))
            
            # Calculate EAR for both eyes
            left_ear = self._calculate_eye_aspect_ratio(left_eye)
            right_ear = self._calculate_eye_aspect_ratio(right_eye)
            
            # Average EAR
            avg_ear = (left_ear + right_ear) / 2.0
            return avg_ear
            
        except Exception as e:
            return None
    
    def _detect_blink_simple(self, face_roi):
        """
        Simplified blink detection using eye region intensity changes.
        Fallback method when dlib is not available.
        """
        h, w = face_roi.shape
        
        # Define eye regions (approximate positions)
        left_eye_region = face_roi[int(h*0.25):int(h*0.45), int(w*0.15):int(w*0.35)]
        right_eye_region = face_roi[int(h*0.25):int(h*0.45), int(w*0.65):int(w*0.85)]
        
        if left_eye_region.size == 0 or right_eye_region.size == 0:
            return None
        
        # Calculate average intensity (darker = closed eyes)
        left_intensity = np.mean(left_eye_region)
        right_intensity = np.mean(right_eye_region)
        avg_intensity = (left_intensity + right_intensity) / 2.0
        
        # Normalize to pseudo-EAR (higher when eyes open)
        pseudo_ear = avg_intensity / 255.0
        return pseudo_ear
    
    def _calculate_texture_variance(self, face_roi):
        """
        Calculate texture variance using Laplacian.
        Real faces have higher texture variance than printed photos.
        """
        # Apply Laplacian operator to detect edges/texture
        laplacian = cv2.Laplacian(face_roi, cv2.CV_64F)
        variance = laplacian.var()
        return variance
    
    def _calculate_face_centroid(self, face_rect):
        """Calculate center point of face bounding box."""
        x, y, w, h = face_rect
        cx = x + w // 2
        cy = y + h // 2
        return (cx, cy)
    
    def _get_face_id(self, face_rect, frame_timestamp):
        """
        Assign consistent face ID based on position proximity.
        Matches face to existing tracked face or creates new ID.
        """
        current_centroid = self._calculate_face_centroid(face_rect)
        
        # Clean up stale face states (not seen for >2 seconds)
        stale_ids = []
        for face_id, state in self.face_states.items():
            if frame_timestamp - state['last_seen'] > 2.0:
                stale_ids.append(face_id)
        for face_id in stale_ids:
            del self.face_states[face_id]
        
        # Try to match with existing tracked faces
        min_distance = float('inf')
        matched_id = None
        
        for face_id, state in self.face_states.items():
            last_centroid = state['last_centroid']
            dist = distance.euclidean(current_centroid, last_centroid)
            
            # If within 50 pixels, consider it the same face
            if dist < 50 and dist < min_distance:
                min_distance = dist
                matched_id = face_id
        
        if matched_id is not None:
            return matched_id
        
        # Create new face ID
        new_id = len(self.face_states)
        return new_id
    
    def _initialize_face_state(self, face_id, face_rect, frame_timestamp):
        """Initialize tracking state for a new face."""
        self.face_states[face_id] = {
            'ear_history': deque(maxlen=self.observation_window),
            'centroid_history': deque(maxlen=self.observation_window),
            'texture_history': deque(maxlen=30),  # Smaller window for texture
            'blink_detected': False,
            'movement_detected': False,
            'last_centroid': self._calculate_face_centroid(face_rect),
            'last_seen': frame_timestamp,
            'frames_tracked': 0
        }
    
    def check_liveness(self, frame_gray, face_rect, frame_timestamp=None):
        """
        Check if a face is live (real person) or a spoof (photo/screen).
        
        Args:
            frame_gray: Grayscale frame
            face_rect: Face bounding box (x, y, w, h)
            frame_timestamp: Current time in seconds (optional)
        
        Returns:
            dict: {
                'is_live': bool,
                'confidence': float (0-1),
                'reason': str (explanation),
                'blink_detected': bool,
                'movement_detected': bool,
                'texture_ok': bool
            }
        """
        if frame_timestamp is None:
            frame_timestamp = time.time()
        
        # Get or assign face ID
        face_id = self._get_face_id(face_rect, frame_timestamp)
        
        # Initialize state if new face
        if face_id not in self.face_states:
            self._initialize_face_state(face_id, face_rect, frame_timestamp)
        
        state = self.face_states[face_id]
        state['last_seen'] = frame_timestamp
        state['frames_tracked'] += 1
        
        # Extract face ROI
        x, y, w, h = face_rect
        face_roi = frame_gray[y:y+h, x:x+w]
        
        if face_roi.size == 0:
            return self._create_result(False, 0.0, "Invalid face region")
        
        # 1. Blink Detection
        ear = None
        if self.use_dlib:
            ear = self._detect_blink_dlib(frame_gray, face_rect)
        if ear is None:
            ear = self._detect_blink_simple(face_roi)
        
        if ear is not None:
            state['ear_history'].append(ear)
            
            # Detect blink: EAR drops below threshold then rises above
            if len(state['ear_history']) >= 3:
                recent_ears = list(state['ear_history'])[-10:]  # Last 10 frames
                
                # Check for blink pattern: was high, went low, went high again
                for i in range(1, len(recent_ears) - 1):
                    if (recent_ears[i] < self.blink_threshold and 
                        recent_ears[i-1] >= self.blink_threshold and 
                        recent_ears[i+1] >= self.blink_threshold):
                        state['blink_detected'] = True
                        break
        
        # 2. Movement Detection
        current_centroid = self._calculate_face_centroid(face_rect)
        state['centroid_history'].append(current_centroid)
        state['last_centroid'] = current_centroid
        
        if len(state['centroid_history']) >= 10:
            # Calculate movement variance
            centroids = np.array(list(state['centroid_history']))
            x_variance = np.var(centroids[:, 0])
            y_variance = np.var(centroids[:, 1])
            total_variance = x_variance + y_variance
            
            if total_variance > self.movement_threshold:
                state['movement_detected'] = True
        
        # 3. Texture Analysis
        texture_variance = self._calculate_texture_variance(face_roi)
        state['texture_history'].append(texture_variance)
        
        avg_texture = np.mean(list(state['texture_history'])) if state['texture_history'] else 0
        texture_ok = avg_texture > self.texture_threshold
        
        # Decision Logic
        # Need at least 30 frames (1 second) of observation
        if state['frames_tracked'] < 30:
            return self._create_result(
                False, 0.3, "Observing... (need 1 sec)",
                state['blink_detected'], state['movement_detected'], texture_ok
            )
        
        # Liveness check: (blink OR movement) AND texture_ok
        liveness_score = 0.0
        reasons = []
        
        if state['blink_detected']:
            liveness_score += 0.4
            reasons.append("blink detected")
        
        if state['movement_detected']:
            liveness_score += 0.4
            reasons.append("movement detected")
        
        if texture_ok:
            liveness_score += 0.2
            reasons.append("texture OK")
        
        is_live = liveness_score >= 0.5  # Need at least 50% confidence
        
        reason = ", ".join(reasons) if is_live else "No liveness indicators detected (photo/screen suspected)"
        
        return self._create_result(
            is_live, liveness_score, reason,
            state['blink_detected'], state['movement_detected'], texture_ok
        )
    
    def _create_result(self, is_live, confidence, reason, 
                       blink=False, movement=False, texture=False):
        """Create standardized result dictionary."""
        return {
            'is_live': is_live,
            'confidence': confidence,
            'reason': reason,
            'blink_detected': blink,
            'movement_detected': movement,
            'texture_ok': texture
        }
    
    def reset_face(self, face_id):
        """Reset tracking state for a specific face."""
        if face_id in self.face_states:
            del self.face_states[face_id]
    
    def reset_all(self):
        """Reset all face tracking states."""
        self.face_states.clear()


# Global liveness detector instance (singleton pattern)
_liveness_detector = None


def get_liveness_detector():
    """Get or create global liveness detector instance."""
    global _liveness_detector
    if _liveness_detector is None:
        _liveness_detector = LivenessDetector()
    return _liveness_detector
