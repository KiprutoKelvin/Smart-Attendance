import streamlit as st
import pandas as pd
import os
from datetime import datetime
import glob

st.set_page_config(page_title="Face Attendance Dashboard", layout="wide")
st.title("📊 Face Recognition Attendance System")

# Get absolute path to Attendance folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTENDANCE_DIR = os.path.join(BASE_DIR, "Attendance")

# If running from a subdirectory, try parent directory
if not os.path.exists(ATTENDANCE_DIR):
    ATTENDANCE_DIR = os.path.join(BASE_DIR, "..", "Attendance")

# Ensure Attendance folder exists
if not os.path.exists(ATTENDANCE_DIR):
    os.makedirs(ATTENDANCE_DIR)
    st.warning("📁 Attendance folder created. No attendance files found yet.")

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# Look for today's attendance files using pattern matching
today_pattern = os.path.join(ATTENDANCE_DIR, f"Attendance_{today}_*.csv")
today_files = glob.glob(today_pattern)

# Display today's attendance
if today_files:
    # Get the most recent file for today
    latest_file = max(today_files, key=os.path.getctime)
    
    try:
        df = pd.read_csv(latest_file)
        
        st.success(f"✅ Today's Attendance ({today})")
        
        # Display file info
        file_time = os.path.basename(latest_file).split('_')[-1].replace('.csv', '')
        st.info(f"📄 Latest file: {os.path.basename(latest_file)} (Created at {file_time.replace('-', ':')})")
        
        if not df.empty:
            # Display the dataframe
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Total Present", len(df))
            with col2:
                st.metric("🆔 Unique Students", df['Id'].nunique())
            with col3:
                if 'Time' in df.columns:
                    earliest_time = df['Time'].min()
                    st.metric("⏰ First Attendance", earliest_time)
            
            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Today's Attendance",
                data=csv,
                file_name=f"attendance_{today}.csv",
                mime='text/csv',
            )
            
            # Show all today's files if multiple
            if len(today_files) > 1:
                st.subheader("📋 All Today's Sessions")
                for file_path in sorted(today_files, key=os.path.getctime, reverse=True):
                    file_name = os.path.basename(file_path)
                    file_time = file_name.split('_')[-1].replace('.csv', '').replace('-', ':')
                    
                    with st.expander(f"Session at {file_time}"):
                        session_df = pd.read_csv(file_path)
                        if not session_df.empty:
                            st.dataframe(session_df, use_container_width=True)
                            st.write(f"Students present: {len(session_df)}")
                        else:
                            st.write("No attendance recorded in this session.")
        else:
            st.warning("📝 Attendance file exists but is empty.")
            
    except Exception as e:
        st.error(f"❌ Error reading attendance file: {e}")
        st.write(f"File path: {latest_file}")
        
else:
    st.warning(f"📅 No attendance recorded yet for today ({today}).")
    st.info("💡 Make sure to run the face recognition system first!")

# Sidebar - View all attendance files
st.sidebar.title("📁 Browse All Attendance Files")

# Get all CSV files in attendance directory
try:
    all_files = [f for f in os.listdir(ATTENDANCE_DIR) if f.endswith(".csv")]
    all_files.sort(reverse=True)  # Most recent first
    
    if all_files:
        st.sidebar.success(f"📊 Found {len(all_files)} attendance files")
        
        selected_file = st.sidebar.selectbox("Select File to View", all_files)
        
        if selected_file:
            selected_path = os.path.join(ATTENDANCE_DIR, selected_file)
            
            # Don't show the same file twice
            if not (today_files and selected_path == max(today_files, key=os.path.getctime)):
                try:
                    df_selected = pd.read_csv(selected_path)
                    
                    # Extract date from filename for display
                    file_parts = selected_file.replace('.csv', '').split('_')
                    if len(file_parts) >= 2:
                        file_date = file_parts[1]
                        file_time = file_parts[2] if len(file_parts) > 2 else "Unknown"
                        file_time = file_time.replace('-', ':')
                    else:
                        file_date = "Unknown"
                        file_time = "Unknown"
                    
                    st.subheader(f"🗂️ Attendance Records")
                    st.info(f"📅 Date: {file_date} | ⏰ Time: {file_time}")
                    
                    if not df_selected.empty:
                        st.dataframe(df_selected, use_container_width=True)
                        
                        # Statistics for selected file
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("👥 Students Present", len(df_selected))
                        with col2:
                            st.metric("🆔 Unique IDs", df_selected['Id'].nunique())
                    else:
                        st.warning("📝 This attendance file is empty.")
                        
                except Exception as e:
                    st.error(f"❌ Error reading file {selected_file}: {e}")
    else:
        st.sidebar.warning("📂 No attendance files found.")
        
except Exception as e:
    st.sidebar.error(f"❌ Error accessing attendance directory: {e}")
    st.sidebar.write(f"Looking in: {ATTENDANCE_DIR}")

# Debug information (can be removed in production)
with st.expander("🔧 Debug Information"):
    st.write(f"**Base Directory:** {BASE_DIR}")
    st.write(f"**Attendance Directory:** {ATTENDANCE_DIR}")
    st.write(f"**Directory Exists:** {os.path.exists(ATTENDANCE_DIR)}")
    st.write(f"**Today's Pattern:** Attendance_{today}_*.csv")
    
    if os.path.exists(ATTENDANCE_DIR):
        all_files_debug = os.listdir(ATTENDANCE_DIR)
        st.write(f"**Files in directory:** {all_files_debug}")
    else:
        st.write("**Attendance directory does not exist**")