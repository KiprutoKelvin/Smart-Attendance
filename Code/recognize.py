import datetime
import os
import time
import cv2
import pandas as pd

def recognize_attendence():
    # Check if model and student details exist
    if not os.path.exists("TrainingImageLabel/Trainner.yml"):
        print("❌ Error: Training model file not found.")
        return

    if not os.path.exists("StudentDetails/StudentDetails.csv"):
        print("❌ Error: Student details file not found.")
        return

    # Ensure Attendance directory exists
    if not os.path.exists("Attendance"):
        os.makedirs("Attendance")

    # Load recognizer
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        print("❌ Error: OpenCV was not built with the 'face' module. Install it with:")
        print("   pip install opencv-contrib-python")
        return

    recognizer.read("TrainingImageLabel/Trainner.yml")

    # Check if haarcascade file exists
    cascade_path = "haarcascade_default.xml"
    if not os.path.exists(cascade_path):
        # Try alternative paths
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            print("❌ Error: Haar cascade file not found.")
            return

    faceCascade = cv2.CascadeClassifier(cascade_path)
    
    try:
        df = pd.read_csv("StudentDetails/StudentDetails.csv")
        print(f"📊 Loaded {len(df)} student records")
    except Exception as e:
        print(f"❌ Error reading StudentDetails.csv: {e}")
        return

    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)
    
    # Keep track of already marked attendance for this session
    marked_attendance = set()

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Error: Could not access the webcam.")
        return

    cam.set(3, 640)
    cam.set(4, 480)
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    print("📷 Face recognition started. Press 'q', 'Q', or 'Esc' to quit and save attendance.")
    print("🎯 Confidence threshold: 51%")
    print("💡 Make sure to click on the camera window first!")

    while True:
        ret, im = cam.read()
        if not ret:
            print("❌ Failed to grab frame.")
            break

        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (10, 159, 255), 2)
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])

            if conf < 100:
                # Find name from dataframe
                name_rows = df.loc[df['Id'] == Id]['Name']
                if len(name_rows) > 0:
                    aa_str = name_rows.values[0]
                    tt = f"{Id} - {aa_str}"
                else:
                    aa_str = "Unknown"
                    tt = f"{Id} - Unknown"
            else:
                Id = "Unknown"
                aa_str = "Unknown"
                tt = "Unknown"

            confidence_percent = round(100 - conf)
            confstr = f"  {confidence_percent}%"

            # Mark attendance if confidence is above threshold and not already marked
            if confidence_percent > 51 and Id != "Unknown" and Id not in marked_attendance:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                
                # Create new row as DataFrame and concatenate
                new_row = pd.DataFrame({
                    'Id': [Id],
                    'Name': [aa_str],
                    'Date': [date],
                    'Time': [timeStamp]
                })
                attendance = pd.concat([attendance, new_row], ignore_index=True)
                marked_attendance.add(Id)
                
                tt += " [PRESENT]"
                print(f"✅ Attendance marked: {aa_str} (ID: {Id}) at {timeStamp}")

            # Display text on image
            cv2.putText(im, tt, (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            
            # Color coding based on confidence
            if confidence_percent > 51:
                color = (0, 255, 0)  # Green for recognized
            elif confidence_percent > 30:
                color = (0, 255, 255)  # Yellow for uncertain
            else:
                color = (0, 0, 255)  # Red for unrecognized
                
            cv2.putText(im, confstr, (x + 5, y + h - 5), font, 1, color, 1)

        # Show attendance count and instructions on screen
        attendance_text = f"Attendance Count: {len(attendance)}"
        cv2.putText(im, attendance_text, (10, 30), font, 0.7, (255, 255, 255), 2)
        
        # Show instructions on the video feed
        cv2.putText(im, "Press 'q', 'Q' or 'Esc' to quit", (10, im.shape[0] - 10), font, 0.5, (255, 255, 255), 1)

        cv2.imshow('Attendance', im)

        # Check for key press (multiple ways to exit)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q') or key == 27:  # q, Q, or Esc
            break

    # Always save attendance file, even if empty
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S')
    fileName = f"Attendance/Attendance_{date}_{timeStamp}.csv"
    
    try:
        # Save the file
        attendance.to_csv(fileName, index=False)
        print(f"\n✅ Attendance saved to: {fileName}")
        print(f"📊 Total students marked present: {len(attendance)}")
        
        # Display attendance summary
        if len(attendance) > 0:
            print("\n📋 Attendance Summary:")
            print("-" * 50)
            for _, row in attendance.iterrows():
                print(f"ID: {row['Id']}, Name: {row['Name']}, Time: {row['Time']}")
            print("-" * 50)
        else:
            print("ℹ️ No students were recognized with sufficient confidence.")
            print("🔧 Try adjusting lighting or camera position.")
            
    except Exception as e:
        print(f"❌ Error saving attendance: {e}")

    cam.release()
    cv2.destroyAllWindows()