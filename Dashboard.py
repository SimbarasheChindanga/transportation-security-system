# ============================================================
# 🚛 TRANSPORTATION SECURITY SYSTEM - DASHBOARD
# ============================================================
# 
# PURPOSE: Main dashboard for driver safety monitoring
# RUN: streamlit run Dashboard.py
# 
# ============================================================

# ============================================================
# SECTION 1: IMPORT LIBRARIES
# ============================================================
# 
# WHAT WE'RE DOING:
# Importing all the Python packages needed for the dashboard.
# 
# WHY:
# - streamlit: Creates the web interface
# - pandas: Handles data (CSV files, DataFrames)
# - plotly: Creates interactive charts
# - os: Checks if files exist
# 
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path


# ============================================================
# SECTION 2: PAGE CONFIGURATION
# ============================================================
# 
# WHAT WE'RE DOING:
# Setting up the browser tab title, icon, and page layout.
# 
# WHY:
# - Professional appearance
# - "wide" layout uses full screen width
# - The icon shows in the browser tab
# 
# ============================================================

st.set_page_config(
    page_title="Transportation Security System", 
    page_icon="🚛", 
    layout="wide"
)

st.title("🚛 Transportation Security System")
st.subheader("Driver Safety Dashboard")


# ============================================================
# SECTION 3: LOAD DATA
# ============================================================
# 
# WHAT WE'RE DOING:
# Loading driver data from a CSV file.
# If the CSV doesn't exist, using sample data as a fallback.
# 
# DATA SOURCE: data/processed/driver_data_processed.csv
# 
# COLUMNS:
# - Driver ID: Unique identifier for each driver
# - Driving Style: Safe, Normal, Aggressive, Unsafe
# - Score: Safety score (0-100)
# - Speeding Violations: Number of speeding events
# - Braking Violations: Number of harsh braking events
# - Cornering Violations: Number of harsh cornering events
# 
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
csv_path = PROJECT_ROOT / 'data' / 'processed' / 'driver_data_processed.csv'

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    st.success(f"✅ Loaded {len(df)} drivers from CSV file")
else:
    data = {
        'Driver ID': [1, 2, 3, 4, 5, 6, 7, 8, 10],
        'Driving Style': ['Safe', 'Safe', 'Safe', 'Normal', 'Normal', 'Normal', 
                          'Aggressive', 'Aggressive', 'Unsafe'],
        'Score': [100, 98, 98, 83, 78, 75, 31, 16, 0],
        'Speeding Violations': [0, 0, 0, 2, 3, 3, 8, 10, 15],
        'Braking Violations': [0, 0, 0, 1, 1, 2, 5, 6, 13],
        'Cornering Violations': [0, 1, 1, 2, 2, 2, 7, 8, 9],
    }
    df = pd.DataFrame(data)
    st.info("ℹ️ Using sample data (CSV file not found)")


# ============================================================
# SECTION 4: ADD STATUS COLUMN
# ============================================================
# 
# WHAT WE'RE DOING:
# Adding a "Status" column based on the driver's score.
# 
# SCORING RULES:
# - 90-100: ✅ Excellent (Safe driver)
# - 70-89:  👍 Good (Some minor violations)
# - 50-69:  ⚠️ Needs Improvement (Too many violations)
# - 0-49:   🚨 Unsafe (Dangerous driver)
# 
# WHY: Makes it easy to categorize drivers at a glance.
# 
# ============================================================

def get_status(score):
    if score >= 90:
        return "✅ Excellent"
    elif score >= 70:
        return "👍 Good"
    elif score >= 50:
        return "⚠️ Needs Improvement"
    else:
        return "🚨 Unsafe"

df['Status'] = df['Score'].apply(get_status)
df['Total Violations'] = df['Speeding Violations'] + df['Braking Violations'] + df['Cornering Violations']


# ============================================================
# SECTION 5: SIDEBAR FILTERS  ← STAGE 1
# ============================================================
# 
# WHAT WE'RE DOING:
# Adding interactive filters to the sidebar.
# 
# FILTER 1: Status Filter - Show only Excellent/Good/Unsafe drivers
# FILTER 2: Score Range - Filter drivers by score range (0-100)
# 
# WHY: Makes the dashboard interactive and user-friendly.
# The filters update all charts and tables in real-time.
# 
# ============================================================

st.sidebar.header("🔍 Filter Drivers")

status_options = ['All'] + sorted(df['Status'].unique())
selected_status = st.sidebar.selectbox("Filter by Status", status_options)

score_range = st.sidebar.slider(
    "Score Range",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

filtered_df = df.copy()

if selected_status != 'All':
    filtered_df = filtered_df[filtered_df['Status'] == selected_status]

filtered_df = filtered_df[
    (filtered_df['Score'] >= score_range[0]) & 
    (filtered_df['Score'] <= score_range[1])
]

st.sidebar.markdown("---")
st.sidebar.metric("📊 Showing", f"{len(filtered_df)} drivers")


# ============================================================
# SECTION 6: KEY METRICS
# ============================================================
# 
# WHAT WE'RE DOING:
# Displaying the 4 most important numbers at the top.
# 
# METRICS:
# 1. Total Drivers - How many drivers are in the filtered data
# 2. Average Score - Average safety score (0-100)
# 3. Unsafe Drivers - Count of unsafe drivers
# 4. Safe Drivers - Count of excellent drivers
# 
# WHY: Gives a quick overview of the fleet's safety status.
# These numbers update when filters are applied.
# 
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Drivers", len(filtered_df))

with col2:
    avg_score = filtered_df['Score'].mean()
    st.metric("Average Score", f"{avg_score:.1f}/100")

with col3:
    unsafe_count = len(filtered_df[filtered_df['Status'] == '🚨 Unsafe'])
    st.metric("Unsafe Drivers", unsafe_count)

with col4:
    safe_count = len(filtered_df[filtered_df['Status'] == '✅ Excellent'])
    st.metric("Safe Drivers", safe_count)

st.markdown("---")


# ============================================================
# SECTION 7: DRIVER SCORES CHART
# ============================================================
# 
# WHAT WE'RE DOING:
# Creating a bar chart showing each driver's safety score.
# 
# CHART FEATURES:
# - X-axis: Driver ID
# - Y-axis: Score (0-100)
# - Color: Status (Green=Excellent, Blue=Good, Orange=Needs Improvement, Red=Unsafe)
# - Labels: Score displayed on top of each bar
# 
# WHY: Quickly see which drivers are safe and which are unsafe.
# 
# ============================================================

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        filtered_df, 
        x='Driver ID', 
        y='Score', 
        color='Status', 
        title='Driver Safety Scores',
        text='Score',
        color_discrete_map={
            '✅ Excellent': '#00cc44',
            '👍 Good': '#3498db',
            '⚠️ Needs Improvement': '#f39c12',
            '🚨 Unsafe': '#e74c3c'
        }
    )
    fig1.update_traces(textposition='outside')
    fig1.update_layout(yaxis_range=[0, 105], height=400)
    st.plotly_chart(fig1, use_container_width=True)


# ============================================================
# SECTION 8: VIOLATIONS CHART
# ============================================================
# 
# WHAT WE'RE DOING:
# Showing the breakdown of violations by driver.
# 
# VIOLATION TYPES:
# 1. Speeding Violations - Red bars
# 2. Braking Violations - Yellow bars  
# 3. Cornering Violations - Green bars
# 
# WHY: Shows which types of violations are most common.
# 
# ============================================================

with col2:
    fig2 = px.bar(
        filtered_df, 
        x='Driver ID', 
        y=['Speeding Violations', 'Braking Violations', 'Cornering Violations'],
        title='Violations by Driver',
        barmode='group',
        color_discrete_map={
            'Speeding Violations': '#ff6b6b',
            'Braking Violations': '#ffd93d',
            'Cornering Violations': '#6bcb77'
        }
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# SECTION 9: STATUS DISTRIBUTION
# ============================================================
# 
# WHAT WE'RE DOING:
# Showing what percentage of drivers fall into each category.
# 
# CATEGORIES:
# - ✅ Excellent (Green)
# - 👍 Good (Blue)
# - ⚠️ Needs Improvement (Orange)
# - 🚨 Unsafe (Red)
# 
# WHY: Shows the overall health of the fleet at a glance.
# 
# ============================================================

st.markdown("---")
st.subheader("📊 Driver Status Distribution")

col1, col2 = st.columns(2)

with col1:
    status_counts = filtered_df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig3 = px.pie(
        status_counts,
        values='Count',
        names='Status',
        title='Driver Status Distribution',
        color='Status',
        color_discrete_map={
            '✅ Excellent': '#00cc44',
            '👍 Good': '#3498db',
            '⚠️ Needs Improvement': '#f39c12',
            '🚨 Unsafe': '#e74c3c'
        },
        hole=0.4
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("### 📋 Summary Statistics")
    
    summary_data = {
        'Metric': [
            'Total Drivers',
            'Average Score',
            'Highest Score',
            'Lowest Score',
            'Total Violations',
            'Excellent Drivers',
            'Good Drivers',
            'Unsafe Drivers'
        ],
        'Value': [
            len(filtered_df),
            f"{filtered_df['Score'].mean():.1f}/100",
            f"{filtered_df['Score'].max()}/100",
            f"{filtered_df['Score'].min()}/100",
            filtered_df['Total Violations'].sum(),
            len(filtered_df[filtered_df['Status'] == '✅ Excellent']),
            len(filtered_df[filtered_df['Status'] == '👍 Good']),
            len(filtered_df[filtered_df['Status'] == '🚨 Unsafe'])
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, hide_index=True, use_container_width=True)


# ============================================================
# SECTION 10: DRIVER DATA TABLE
# ============================================================
# 
# WHAT WE'RE DOING:
# Displaying all driver data in a sortable table.
# 
# COLUMNS:
# - Driver ID: Unique identifier
# - Driving Style: Safe, Normal, Aggressive, Unsafe
# - Score: Safety score (0-100)
# - Speeding Violations: Count of speeding events
# - Braking Violations: Count of harsh braking events
# - Cornering Violations: Count of harsh cornering events
# - Status: Calculated status from score
# - Total Violations: Sum of all violations
# 
# WHY: Allows users to see all the detailed data.
# 
# ============================================================

st.markdown("---")
st.subheader("📋 Driver Data Table")
st.dataframe(filtered_df, hide_index=True, use_container_width=True)


# ============================================================
# SECTION 11: EXPORT DATA  ← STAGE 2
# ============================================================
# 
# WHAT WE'RE DOING:
# Allowing users to download driver data as CSV.
# 
# WHY:
# - Fleet managers can analyze data in Excel
# - Users can share data with stakeholders
# - Shows data export capabilities
# 
# KEY FEATURES:
# 1. Removes emojis from Status column (Excel compatibility)
# 2. Exports only filtered data (respects user filters)
# 3. Uses UTF-8-BOM encoding (Excel-friendly)
# 
# ============================================================

st.markdown("---")
st.subheader("📥 Export Data")

export_df = filtered_df.copy()

def clean_status_for_export(status):
    if status == "✅ Excellent":
        return "Excellent"
    elif status == "👍 Good":
        return "Good"
    elif status == "⚠️ Needs Improvement":
        return "Needs Improvement"
    elif status == "🚨 Unsafe":
        return "Unsafe"
    else:
        return status

export_df['Status'] = export_df['Status'].apply(clean_status_for_export)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

csv_data = convert_df_to_csv(export_df)

st.download_button(
    label="📥 Download Driver Data as CSV",
    data=csv_data,
    file_name='driver_data_export.csv',
    mime='text/csv',
)

st.caption("💡 Note: The CSV file uses text status (Excellent, Good, etc.) for Excel compatibility")


# ============================================================
# SECTION 12: FOOTER
# ============================================================
# 
# WHAT WE'RE DOING:
# Adding a footer at the bottom of the page.
# 
# WHY: Shows professionalism and gives credit.
# 
# ============================================================

st.markdown("---")
st.caption("🚛 Transportation Security System | Built with Streamlit | © 2026")


# ============================================================
# SECTION 13: CAMERA SNAPSHOT FACE DETECTION & FATIGUE ANALYSIS
# ============================================================

st.markdown("---")
st.subheader("Driver Face-Detection Snapshot")

st.caption(
    "Optional browser-camera snapshot for demonstration. "
    "The EAR result is a preliminary eye-closure indicator, "
    "not a validated driver-safety assessment."
)

# Camera is OFF by default.
if "camera_enabled" not in st.session_state:
    st.session_state["camera_enabled"] = False

st.toggle(
    "Enable camera",
    key="camera_enabled",
    help="Turn this off to remove the camera widget."
)

if st.session_state["camera_enabled"]:
    try:
        import cv2
        import numpy as np
        import dlib

        from src.driver_monitoring.face_detection import FaceDetector
        from src.driver_monitoring.fatigue_detection import FatigueAnalyzer

        camera_image = st.camera_input(
            "Take a driver-monitoring snapshot",
            key="driver_snapshot"
        )

        if camera_image is not None:
            image_bytes = np.frombuffer(
                camera_image.getvalue(), dtype=np.uint8
            )
            frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

            if frame is None:
                st.error("Could not read the image. Please try again.")
            else:
                # Keep the existing OpenCV face detection and display.
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cascade_path = (
                    cv2.data.haarcascades
                    + "haarcascade_frontalface_default.xml"
                )
                cascade = cv2.CascadeClassifier(cascade_path)

                if cascade.empty():
                    st.error("OpenCV's face-detection cascade could not load.")
                    faces = []
                else:
                    faces = cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                    )

                # For this single-driver demo, keep only the largest
                # detection to reduce background false positives.
                if len(faces) > 1:
                    largest_face = max(
                        faces,
                        key=lambda box: int(box[2]) * int(box[3])
                    )
                    faces = [largest_face]

                # Draw the selected OpenCV face rectangle.
                for (x, y, w, h) in faces:
                    cv2.rectangle(
                        frame,
                        (int(x), int(y)),
                        (int(x + w), int(y + h)),
                        (0, 255, 0),
                        2
                    )

                st.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    caption=f"Faces detected: {len(faces)}",
                    use_container_width=True
                )

                if len(faces) == 0:
                    st.warning(
                        "No face detected. Retake the snapshot with your "
                        "face clearly visible."
                    )
                else:
                    detector = FaceDetector()

                    if detector.predictor is None:
                        st.warning(
                            "The facial landmark model is unavailable. "
                            "Check notebooks/shape_predictor_68_face_landmarks.dat."
                        )
                    else:
                        # First try dlib's detector; fall back to the OpenCV box
                        # if dlib cannot locate a face in this snapshot.
                        dlib_faces = detector.detect_faces_dlib(frame)

                        if dlib_faces:
                            face_rect = max(
                                dlib_faces,
                                key=lambda face: face.width() * face.height()
                            )
                            detection_method = "dlib face detector"
                        else:
                            x, y, w, h = max(
                                faces,
                                key=lambda box: int(box[2]) * int(box[3])
                            )

                            margin_x = int(w * 0.15)
                            margin_top = int(h * 0.20)
                            margin_bottom = int(h * 0.10)

                            left = max(0, int(x - margin_x))
                            top = max(0, int(y - margin_top))
                            right = min(frame.shape[1] - 1, int(x + w + margin_x))
                            bottom = min(frame.shape[0] - 1, int(y + h + margin_bottom))

                            face_rect = dlib.rectangle(left, top, right, bottom)
                            detection_method = "OpenCV face-box fallback"

                        try:
                            landmarks = detector.get_landmarks(frame, face_rect)

                            if landmarks is None:
                                st.warning(
                                    "Could not extract facial landmarks from "
                                    "the detected face. Try another snapshot "
                                    "with your full face visible."
                                )
                            else:
                                analyzer = FatigueAnalyzer()
                                result = analyzer.analyze_landmarks(landmarks)

                                if result.get("average_ear") is not None:
                                    st.metric(
                                        "Average Eye Aspect Ratio (EAR)",
                                        f"{result['average_ear']:.4f}"
                                    )
                                    st.caption(
                                        f"Landmark region source: {detection_method}"
                                    )

                                ear = result.get("average_ear")
                                if ear is None:
                                    st.info("Eye status could not be determined.")
                                elif ear < analyzer.ear_threshold:
                                    st.warning(
                                        "Low EAR in this snapshot: possible eye "
                                        "closure. A single image cannot establish fatigue."
                                    )
                                else:
                                    st.info(
                                        "EAR is above the prototype threshold in "
                                        "this snapshot. This does not confirm driver alertness."
                                    )

                                st.caption(
                                    "Snapshot-based demonstration only: this capture "
                                    "does not measure eye-closure duration or provide "
                                    "continuous fatigue monitoring."
                                )

                        except (ValueError, RuntimeError) as exc:
                            st.warning(f"Eye analysis could not be completed: {exc}")

    except ImportError as exc:
        st.error(f"Camera or fatigue dependencies are missing: {exc}")
    except Exception as exc:
        st.error(f"Camera analysis failed: {exc}")
else:
    st.info("Camera is OFF. Enable it only when needed.")


# SECTION 14: NOTIFICATIONS & ALERTS  ← STAGE 4
# ============================================================
# 
# WHAT WE'RE DOING:
# Adding an alert system that notifies about unsafe drivers.
# 
# WHY:
# - Immediate awareness of safety issues
# - Fleet managers can take quick action
# - Shows proactive safety monitoring
# 
# ALERT RULES:
# 1. Driver score < 50 → UNSAFE ALERT (Critical)
# 2. Total violations > 20 → HIGH VIOLATIONS ALERT (Warning)
# 3. Score 50-69 → NEEDS IMPROVEMENT (Info)
# 
# ============================================================

st.markdown("---")
st.subheader("🔔 Safety Alerts & Notifications")

# Define alert rules
def check_alerts(df):
    """Check for unsafe conditions and generate alerts"""
    alerts = []
    
    for idx, row in df.iterrows():
        driver_id = row['Driver ID']
        score = row['Score']
        violations = row['Total Violations']
        status = row['Status']
        
        # Rule 1: Unsafe driver (score < 50)
        if score < 50:
            alerts.append({
                'Driver': driver_id,
                'Type': '🚨 UNSAFE DRIVER',
                'Message': f'Driver {driver_id} has score {score}/100 - URGENT attention needed!',
                'Severity': 'Critical'
            })
        
        # Rule 2: High violations (> 20)
        if violations > 20:
            alerts.append({
                'Driver': driver_id,
                'Type': '⚠️ HIGH VIOLATIONS',
                'Message': f'Driver {driver_id} has {violations} violations - Review required!',
                'Severity': 'Warning'
            })
        
        # Rule 3: Needs Improvement (score 50-69)
        if 50 <= score < 70:
            alerts.append({
                'Driver': driver_id,
                'Type': '📋 NEEDS IMPROVEMENT',
                'Message': f'Driver {driver_id} scored {score}/100 - Training recommended',
                'Severity': 'Info'
            })
    
    return alerts

# Check for alerts in the filtered data
alerts = check_alerts(filtered_df)

# Show alert count
if len(alerts) > 0:
    st.warning(f"⚠️ {len(alerts)} alert(s) found for the current filter")
else:
    st.success(f"✅ No alerts found - All drivers are safe!")

# Display alerts
if len(alerts) > 0:
    for alert in alerts:
        if alert['Severity'] == 'Critical':
            st.error(f"**{alert['Type']}** - {alert['Message']}")
        elif alert['Severity'] == 'Warning':
            st.warning(f"**{alert['Type']}** - {alert['Message']}")
        else:
            st.info(f"**{alert['Type']}** - {alert['Message']}")
else:
    st.info("All drivers are currently safe. No alerts to display.")


# ============================================================
# END OF DASHBOARD.PY
# ============================================================