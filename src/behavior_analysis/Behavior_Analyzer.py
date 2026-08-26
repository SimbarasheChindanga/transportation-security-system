# ============================================================
# behavior_analyzer.py - Behavior Analysis Functions
# ============================================================
# SOURCE: From Phase 4 Notebook (04_Behavior_Analysis.ipynb)
# PURPOSE: Detect speeding, braking, cornering and calculate driver scores

import numpy as np
import pandas as pd

class BehaviorAnalyzer:
    """
    Driver behavior analysis class.
    Detects violations and calculates driver scores.
    """
    
    def __init__(self, speed_limit=60, braking_threshold=-3.0, cornering_threshold=2.0):
        """
        Initialize behavior analyzer with thresholds.
        
        Parameters:
        - speed_limit: Speed limit in km/h
        - braking_threshold: Harsh braking threshold (m/s²)
        - cornering_threshold: Harsh cornering threshold (m/s²)
        """
        self.speed_limit = speed_limit
        self.braking_threshold = braking_threshold
        self.cornering_threshold = cornering_threshold
        
        print(f"✅ BehaviorAnalyzer initialized")
        print(f"   Speed Limit: {speed_limit} km/h")
        print(f"   Braking Threshold: {braking_threshold} m/s²")
        print(f"   Cornering Threshold: {cornering_threshold} m/s²")
    
    def detect_speeding(self, speed):
        """
        Detect if vehicle is speeding.
        
        Parameters:
        - speed: Current speed in km/h
        
        Returns:
        - (is_speeding, over_limit)
        """
        over_limit = speed - self.speed_limit
        if speed > self.speed_limit * 1.1:  # 10% over limit
            return True, over_limit
        return False, 0
    
    def detect_harsh_braking(self, acceleration):
        """
        Detect harsh braking.
        
        Parameters:
        - acceleration: Current acceleration in m/s²
        
        Returns:
        - (is_braking, strength)
        """
        if acceleration < self.braking_threshold:
            return True, abs(acceleration)
        return False, 0
    
    def detect_harsh_cornering(self, lateral_accel):
        """
        Detect harsh cornering.
        
        Parameters:
        - lateral_accel: Lateral acceleration in m/s²
        
        Returns:
        - (is_cornering, strength)
        """
        if abs(lateral_accel) > self.cornering_threshold:
            return True, abs(lateral_accel)
        return False, 0
    
    def calculate_driver_score(self, speed_violations, braking_violations, cornering_violations):
        """
        Calculate driver scorecard (0-100).
        
        Parameters:
        - speed_violations: Number of speeding events
        - braking_violations: Number of harsh braking events
        - cornering_violations: Number of harsh cornering events
        
        Returns:
        - Score from 0 to 100
        """
        score = 100
        score -= speed_violations * 5
        score -= braking_violations * 3
        score -= cornering_violations * 2
        return max(0, min(100, score))
    
    def get_score_rating(self, score):
        """
        Get rating based on score.
        
        Parameters:
        - score: Driver score (0-100)
        
        Returns:
        - Rating string and emoji
        """
        if score >= 90:
            return "⭐ Excellent", "green"
        elif score >= 70:
            return "👍 Good", "blue"
        elif score >= 50:
            return "⚠️ Needs Improvement", "orange"
        else:
            return "🚨 Unsafe", "red"
    
    def analyze_driver(self, df):
        """
        Analyze a driver's behavior from DataFrame.
        
        Parameters:
        - df: DataFrame with driving data
        
        Returns:
        - Dictionary with analysis results
        """
        speeding_events = 0
        braking_events = 0
        cornering_events = 0
        
        # Check if lateral_accel column exists
        has_lateral = 'lateral_accel' in df.columns or 'harsh_cornering' in df.columns
        
        for idx, row in df.iterrows():
            # Check speeding
            is_speeding, _ = self.detect_speeding(row['speed'])
            if is_speeding:
                speeding_events += 1
            
            # Check braking
            is_braking, _ = self.detect_harsh_braking(row['acceleration'])
            if is_braking:
                braking_events += 1
            
            # Check cornering
            if 'lateral_accel' in df.columns:
                is_cornering, _ = self.detect_harsh_cornering(row['lateral_accel'])
                if is_cornering:
                    cornering_events += 1
            elif 'harsh_cornering' in df.columns:
                if row['harsh_cornering'] > self.cornering_threshold:
                    cornering_events += 1
        
        score = self.calculate_driver_score(speeding_events, braking_events, cornering_events)
        rating, color = self.get_score_rating(score)
        
        return {
            'speeding_events': speeding_events,
            'braking_events': braking_events,
            'cornering_events': cornering_events,
            'total_violations': speeding_events + braking_events + cornering_events,
            'score': score,
            'rating': rating,
            'color': color
        }

# ============================================================
# TEST CODE
# ============================================================
if __name__ == "__main__":
    print("="*50)
    print("🧪 TESTING BEHAVIOR ANALYZER")
    print("="*50)
    
    # Create analyzer
    analyzer = BehaviorAnalyzer()
    
    # Test detection functions
    print("\n📊 Testing detection:")
    is_speeding, over = analyzer.detect_speeding(70)
    print(f"   Speeding: {is_speeding} (over by {over:.1f} km/h)")
    
    is_braking, strength = analyzer.detect_harsh_braking(-4.5)
    print(f"   Harsh Braking: {is_braking} (strength: {strength:.1f} m/s²)")
    
    is_cornering, strength = analyzer.detect_harsh_cornering(2.8)
    print(f"   Harsh Cornering: {is_cornering} (strength: {strength:.1f} m/s²)")
    
    # Test score calculation
    print("\n📊 Testing score calculation:")
    score = analyzer.calculate_driver_score(5, 3, 2)
    rating, color = analyzer.get_score_rating(score)
    print(f"   Score: {score}/100")
    print(f"   Rating: {rating}")
    
    # Create sample data and analyze
    print("\n📊 Testing full analysis:")
    data = {
        'speed': [70, 45, 80, 30, 60],
        'acceleration': [-2, -4.5, 1, 0, -3.5],
        'lateral_accel': [0.5, 1.2, 2.8, 0.3, 1.8]
    }
    df = pd.DataFrame(data)
    
    results = analyzer.analyze_driver(df)
    print(f"   Speeding Events: {results['speeding_events']}")
    print(f"   Braking Events: {results['braking_events']}")
    print(f"   Cornering Events: {results['cornering_events']}")
    print(f"   Total Violations: {results['total_violations']}")
    print(f"   Score: {results['score']}/100")
    print(f"   Rating: {results['rating']}")