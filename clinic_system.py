# ==============================
# Clinic Management System
# نظام إدارة عيادة - عربي
# ==============================

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ------------------------------
# Page Config (RTL + Arabic)
# ------------------------------
st.set_page_config(
    page_title="نظام إدارة العيادة",
    page_icon="🩺",
    layout="wide"
)

st.markdown("""
<style>
body { direction: rtl; }
h1, h2, h3, h4, h5, h6, p, label, div {
    font-family: 'Segoe UI', Tahoma, Arial;
}
.metric {
    background-color: #f7f9fc;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Database
# ------------------------------
conn = sqlite3.connect("clinic.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    gender TEXT,
    age INTEGER,
    phone TEXT,
    city TEXT,
    notes TEXT,
    created_at TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialty TEXT,
    phone TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    doctor_name TEXT,
    date TEXT,
    time TEXT
)
""")

conn.commit()

# ------------------------------
# Header
# ------------------------------
st.title("🩺 نظام إدارة العيادة")
st.caption("نظام متكامل لإدارة المرضى، الأطباء، والمواعيد باستخدام Streamlit و SQLite")

# ------------------------------
# Statistics
# ------------------------------
col1, col2, col3 = st.columns(3)

patients_count = pd.read_sql("SELECT COUNT(*) as c FROM patients", conn)["c"][0]
doctors_count = pd.read_sql("SELECT COUNT(*) as c FROM doctors", conn)["c"][0]
appointments_count = pd.read_sql("SELECT COUNT(*) as c FROM appointments", conn)["c"][0]

col1.metric("👤 المرضى", patients_count)
col2.metric("👨‍⚕️ الأطباء", doctors_count)
col3.metric("📅 المواعيد", appointments_count)

st.divider()

# ------------------------------
# Tabs
# ------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["👤 المرضى", "👨‍⚕️ الأطباء", "📅 المواعيد", "📊 التقارير"])

# ==============================
# Patients
# ==============================
with tab1:
    st.subheader("إضافة مريض")

    with st.form("add_patient"):
        name = st.text_input("اسم المريض")
        gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
        age = st.number_input("العمر", 0, 120, 25)
        phone = st.text_input("رقم الهاتف")
        city = st.text_input("المدينة")
        notes = st.text_area("ملاحظات")
        submit = st.form_submit_button("➕ إضافة")

        if submit and name:
            c.execute("""
            INSERT INTO patients (name, gender, age, phone, city, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, gender, age, phone, city, notes, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("تم إضافة المريض بنجاح")

    st.divider()
    st.subheader("قائمة المرضى")

    df_patients = pd.read_sql("SELECT * FROM patients", conn)
    st.dataframe(df_patients, use_container_width=True)

# ==============================
# Doctors
# ==============================
with tab2:
    st.subheader("إضافة طبيب")

    with st.form("add_doctor"):
        d_name = st.text_input("اسم الطبيب")
        specialty = st.text_input("التخصص")
        d_phone = st.text_input("رقم الهاتف")
        submit_d = st.form_submit_button("➕ إضافة")

        if submit_d and d_name:
            c.execute("""
            INSERT INTO doctors (name, specialty, phone)
            VALUES (?, ?, ?)
            """, (d_name, specialty, d_phone))
            conn.commit()
            st.success("تم إضافة الطبيب")

    st.divider()
    st.subheader("قائمة الأطباء")

    df_doctors = pd.read_sql("SELECT * FROM doctors", conn)
    st.dataframe(df_doctors, use_container_width=True)

# ==============================
# Appointments
# ==============================
with tab3:
    st.subheader("إضافة موعد")

    patients = pd.read_sql("SELECT name FROM patients", conn)["name"].tolist()
    doctors = pd.read_sql("SELECT name FROM doctors", conn)["name"].tolist()

    with st.form("add_appointment"):
        p_name = st.selectbox("المريض", patients)
        d_name = st.selectbox("الطبيب", doctors)
        date = st.date_input("التاريخ")
        time = st.time_input("الوقت")
        submit_a = st.form_submit_button("➕ إضافة موعد")

        if submit_a and p_name and d_name:
            c.execute("""
            INSERT INTO appointments (patient_name, doctor_name, date, time)
            VALUES (?, ?, ?, ?)
            """, (p_name, d_name, str(date), str(time)))
            conn.commit()
            st.success("تم إضافة الموعد")

    st.divider()
    st.subheader("قائمة المواعيد")

    df_app = pd.read_sql("SELECT * FROM appointments", conn)
    st.dataframe(df_app, use_container_width=True)

# ==============================
# Reports
# ==============================
with tab4:
    st.subheader("تقارير سريعة")

    st.write("عدد المرضى حسب الجنس")
    gender_report = pd.read_sql("""
        SELECT gender, COUNT(*) as العدد
        FROM patients
        GROUP BY gender
    """, conn)

    st.bar_chart(gender_report.set_index("gender"))

st.caption("© مشروع جامعي – نظام إدارة عيادة باستخدام Streamlit")
