import streamlit as st
import firebase_admin
from firebase_admin import credentials, db, auth, storage
import pandas as pd
import tempfile
import os

# Firebase setup
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")  # 🔐 Add this file (download from Firebase console)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://esp-os-project-default-rtdb.firebaseio.com/',
        'storageBucket': 'esp-os-project.appspot.com'
    })

# Firebase Realtime DB reference
led_ref = db.reference('led/state')

# App title
st.title("ESP32 LED Controller & Timetable Uploader")

# Current LED State
try:
    led_state = led_ref.get()
    st.subheader(f"Current LED State: {'ON' if led_state == 1 else 'OFF'}")
except Exception as e:
    st.error(f"Failed to fetch LED state: {e}")

# Control LED
col1, col2 = st.columns(2)

with col1:
    if st.button("Turn ON"):
        led_ref.set(1)
        st.success("LED turned ON")

with col2:
    if st.button("Turn OFF"):
        led_ref.set(0)
        st.success("LED turned OFF")

# Timetable Upload
st.markdown("---")
st.subheader("Upload Timetable (CSV)")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)

    # Save temporarily and upload to Firebase Storage
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    df.to_csv(temp_file.name, index=False)

    # Upload to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob("timetable.csv")
    blob.upload_from_filename(temp_file.name)
    blob.make_public()
    st.success(f"Timetable uploaded. [View CSV]({blob.public_url})")

    os.remove(temp_file.name)
