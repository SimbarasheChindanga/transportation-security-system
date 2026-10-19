import numpy as np


class FatigueAnalyzer:
    """EAR-based eye-closure monitoring prototype."""

    def __init__(self, ear_threshold=0.25, consecutive_frames=15):
        if not 0 < ear_threshold < 1:
            raise ValueError("ear_threshold must be between 0 and 1")
        if consecutive_frames < 1:
            raise ValueError("consecutive_frames must be positive")

        self.ear_threshold = ear_threshold
        self.consecutive_frames = consecutive_frames
        self.closed_frames = 0

    @staticmethod
    def eye_aspect_ratio(points):
        points = np.asarray(points, dtype=float)

        if points.shape != (6, 2):
            raise ValueError("Expected six 2D eye landmarks")

        vertical_1 = np.linalg.norm(points[1] - points[5])
        vertical_2 = np.linalg.norm(points[2] - points[4])
        horizontal = np.linalg.norm(points[0] - points[3])

        if horizontal == 0:
            raise ValueError("Invalid eye landmarks: zero eye width")

        return float(
            (vertical_1 + vertical_2) / (2.0 * horizontal)
        )

    def analyze_landmarks(self, landmarks):
        """Analyze one frame containing 68 facial landmarks."""

        if landmarks is None:
            self.reset()
            return {
                "status": "NO_FACE",
                "average_ear": None,
                "closed_frames": 0,
                "alert": False,
            }

        if landmarks.num_parts < 68:
            raise ValueError("Expected 68 facial landmarks")

        left_eye = [
            (landmarks.part(i).x, landmarks.part(i).y)
            for i in range(36, 42)
        ]
        right_eye = [
            (landmarks.part(i).x, landmarks.part(i).y)
            for i in range(42, 48)
        ]

        left_ear = self.eye_aspect_ratio(left_eye)
        right_ear = self.eye_aspect_ratio(right_eye)
        average_ear = (left_ear + right_ear) / 2.0

        if average_ear < self.ear_threshold:
            self.closed_frames += 1
        else:
            self.closed_frames = 0

        alert = self.closed_frames >= self.consecutive_frames

        if alert:
            status = "PROLONGED_EYE_CLOSURE"
        elif self.closed_frames > 0:
            status = "EYES_POSSIBLY_CLOSED"
        else:
            status = "EYES_OPEN"

        return {
            "status": status,
            "left_ear": round(left_ear, 4),
            "right_ear": round(right_ear, 4),
            "average_ear": round(average_ear, 4),
            "closed_frames": self.closed_frames,
            "alert": alert,
        }

    def reset(self):
        self.closed_frames = 0