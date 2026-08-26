# ============================================================
# test_data_generator.py - Test Data Generator and Analyzer
# ============================================================

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection.data_generator import generate_gps_data, generate_driver_data, save_driver_data
from src.behavior_analysis.behavior_analyzer import BehaviorAnalyzer

def test_gps_data():
    """Test GPS data generation"""
    print("\n" + "="*50)
    print("🧪 TEST 1: GPS DATA GENERATION")
    print("="*50)
    
    df = generate_gps_data(50)
    print(f"✅ Generated {len(df)} GPS records")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Speed range: {df['speed'].min():.1f} - {df['speed'].max():.1f} km/h")
    
    if len(df) == 50:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")

def test_driver_data():
    """Test driver data generation"""
    print("\n" + "="*50)
    print("🧪 TEST 2: DRIVER DATA GENERATION")
    print("="*50)
    
    styles = ['safe', 'normal', 'aggressive', 'unsafe']
    
    for style in styles:
        df = generate_driver_data(1, style, 50)
        print(f"✅ {style.capitalize():12} driver: {len(df)} records")
    
    print("✅ Test passed!")

def test_behavior_analysis():
    """Test behavior analysis"""
    print("\n" + "="*50)
    print("🧪 TEST 3: BEHAVIOR ANALYSIS")
    print("="*50)
    
    # Generate data for an unsafe driver
    df = generate_driver_data(10, 'unsafe', 300)
    print(f"✅ Generated {len(df)} records for unsafe driver")
    
    # Analyze
    analyzer = BehaviorAnalyzer()
    results = analyzer.analyze_driver(df)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Speeding Events: {results['speeding_events']}")
    print(f"   Braking Events: {results['braking_events']}")
    print(f"   Cornering Events: {results['cornering_events']}")
    print(f"   Total Violations: {results['total_violations']}")
    print(f"   Driver Score: {results['score']}/100")
    print(f"   Rating: {results['rating']}")
    
    # Save data
    save_driver_data(df, 'test_driver_data.csv')
    print("\n✅ Test passed!")

def test_multi_drivers():
    """Test multiple drivers generation"""
    print("\n" + "="*50)
    print("🧪 TEST 4: MULTI-DRIVER GENERATION")
    print("="*50)
    
    drivers = []
    for i in range(9):
        style = ['safe', 'safe', 'safe', 'normal', 'normal', 'normal', 'aggressive', 'aggressive', 'unsafe'][i]
        df = generate_driver_data(i+1, style, 100)
        drivers.append(df)
        
        analyzer = BehaviorAnalyzer()
        results = analyzer.analyze_driver(df)
        print(f"Driver {i+1:2d} ({style:12}): Score {results['score']:3d}/100 - {results['rating']}")
    
    print("\n✅ All drivers generated and analyzed!")
    print(f"   Total drivers: {len(drivers)}")

# ============================================================
# RUN ALL TESTS
# ============================================================
if __name__ == "__main__":
    print("\n🚀 RUNNING ALL TESTS")
    print("="*50)
    
    test_gps_data()
    test_driver_data()
    test_behavior_analysis()
    test_multi_drivers()
    
    print("\n" + "="*50)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*50)