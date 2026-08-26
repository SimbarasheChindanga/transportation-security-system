# ============================================================
# face_detection.py - Face Detection Functions
# ============================================================
# SOURCE: From Phase 2 Notebook (02_Face_Detection.ipynb)
# PURPOSE: Detect faces using OpenCV and dlib

import cv2
import dlib
import numpy as np
import os

class FaceDetector:
    """Face detection class using OpenCV and dlib"""
    
    def __init__(self):
        """Initialize face detectors"""
        print("📥 Loading face detectors...")
        
        # OpenCV detector (Haar Cascade)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if os.path.exists(cascade_path):
            self.opencv_detector = cv2.CascadeClassifier(cascade_path)
            print("✅ OpenCV detector loaded")
        else:
            print("⚠️ OpenCV cascade file not found")
            self.opencv_detector = None
        
        # dlib detector (HOG + SVM)
        try:
            self.dlib_detector = dlib.get_frontal_face_detector()
            print("✅ dlib detector loaded")
        except:
            print("⚠️ dlib detector failed to load")
            self.dlib_detector = None
        
        # dlib predictor (for 68 landmarks)
        self.predictor = None
        landmark_file = 'shape_predictor_68_face_landmarks.dat'
        if os.path.exists(landmark_file):
            try:
                self.predictor = dlib.shape_predictor(landmark_file)
                print("✅ Landmark predictor loaded")
            except:
                print("⚠️ Landmark predictor failed to load")
    
    def detect_faces_opencv(self, image):
        """
        Detect faces using OpenCV Haar Cascade.
        
        Parameters:
        - image: BGR image
        
        Returns:
        - List of (x, y, w, h) face coordinates
        """
        if self.opencv_detector is None:
            print("⚠️ OpenCV detector not available")
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.opencv_detector.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        return faces
    
    def detect_faces_dlib(self, image):
        """
        Detect faces using dlib HOG + SVM.
        
        Parameters:
        - image: BGR image
        
        Returns:
        - List of dlib face rectangles
        """
        if self.dlib_detector is None:
            print("⚠️ dlib detector not available")
            return []
        
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faces = self.dlib_detector(rgb)
        return faces
    
    def get_landmarks(self, image, face):
        """
        Get 68 facial landmarks for a face.
        
        Parameters:
        - image: BGR image
        - face: dlib face rectangle
        
        Returns:
        - dlib landmarks object
        """
        if self.predictor is None:
            print("⚠️ Predictor not available")
            return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        landmarks = self.predictor(gray, face)
        return landmarks
    
    def draw_bounding_boxes(self, image, faces, color=(0, 255, 0), label=''):
        """
        Draw bounding boxes around detected faces.
        
        Parameters:
        - image: BGR image
        - faces: List of face coordinates
        - color: RGB color tuple
        - label: Text label for boxes
        
        Returns:
        - Image with bounding boxes
        """
        img_copy = image.copy()
        
        for (x, y, w, h) in faces:
            cv2.rectangle(img_copy, (x, y), (x+w, y+h), color, 2)
            if label:
                cv2.putText(img_copy, label, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return img_copy
    
    def draw_landmarks(self, image, landmarks):
        """
        Draw 68 facial landmarks on image.
        
        Parameters:
        - image: BGR image
        - landmarks: dlib landmarks object
        
        Returns:
        - Image with landmarks
        """
        img_copy = image.copy()
        
        for i in range(landmarks.num_parts):
            x = landmarks.part(i).x
            y = landmarks.part(i).y
            cv2.circle(img_copy, (x, y), 2, (0, 255, 0), -1)
        
        return img_copy

# ============================================================
# TEST CODE
# ============================================================
if __name__ == "__main__":
    print("="*50)
    print("🧪 TESTING FACE DETECTOR")
    print("="*50)
    
    detector = FaceDetector()
    print("\n✅ FaceDetector initialized!")
    
    # Create a test image
    test_img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.circle(test_img, (200, 150), 80, (200, 200, 200), -1)
    cv2.circle(test_img, (200, 150), 80, (0, 0, 0), 2)
    cv2.circle(test_img, (170, 130), 15, (0, 0, 0), -1)
    cv2.circle(test_img, (230, 130), 15, (0, 0, 0), -1)
    
    print("✅ Test image created")
    
    # Test detection
    faces = detector.detect_faces_opencv(test_img)
    print(f"✅ OpenCV detection: {len(faces)} faces")