import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import uuid

# =============================
# Page Config + Style
# =============================
st.set_page_config(
    page_title="Clinic Management System",
    page_icon="🩺",
    layout="wide"
)

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
[data-testid="stMetricValue"] {font-size: 1.6rem;}
.small-note {opacity: 0.75; font-size: 0.9rem;}
.card {
    border: 1px solid rgba(49,51,63,0.2);
    border-radius: 12px;
    padding: 14px;
    background: rgba(255,255,255,0.02);
}
</style>
""", unsafe_allow_html=True)

# =============================
# Helpers
# =============================
def new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def init_db():
    if "patients" not in st.session_state:
        st.session_state.patients = pd.DataFrame(columns=[
            "patient_id","full_name","gender","age","phone","city","notes","created_at"
        ])
    if "doctors" not in st.session_state:
        st.session_state.doctors = pd.DataFrame(columns=[
            "doctor_id","full_name","specialty","phone","room","created_at"
        ])
    if "appointments" not in st.session_state:
        st.session_state.appointments = pd.DataFrame(columns=[
            "appt_id","patient_id","patient_name",
            "doctor_id","doctor_name","specialty",
            "appt_date","appt_time","status","reason","created_at"
        ])

def validate_phone(p):
    if not p:
        return True
    digits = "".join([c for c in p if c.isdigit()])
    return len(digits) >= 9

def badge_status(s):
    if s == "Scheduled": return "🟦 Scheduled"
    if s == "Completed": return "🟩 Completed"
    if s == "Cancelled": return "🟥 Cancelled"
    return s

def export_buttons(df, name):
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ CSV",
            df.to_csv(index=False).encode("utf-8-sig"),
            f"{name}.csv",
            "text/csv",
            use_container_width=True
        )
    with col2:
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            "⬇️ Excel",
            buffer.getvalue(),
            f"{name}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# =============================
# App Start (NO LOGIN)
# =============================
init_db()

st.title("🩺 Clinic Management System")
st.caption("نظام إدارة عيادة – متاح للجميع بدون تسجيل دخول")

patients = st.session_state.patients
doctors = st.session_state.doctors
appointments = st.session_state.appointments

# =============================
# KPIs
# =============================
k1, k2, k3, k4 = st.columns(4)
k1.metric("👤 المرضى", len(patients))
k2.metric("👨‍⚕️ الأطباء", len(doctors))
k3.metric("📅 المواعيد", len(appointments))
today = date.today().isoformat()
k4.metric("🕒 مواعيد اليوم", len(appointments[appointments["appt_date"] == today]))

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["👤 المرضى","👨‍⚕️ الأطباء","📅 المواعيد","📊 التقارير"]
)

# =============================
# Patients
# =============================
with tab1:
    c1, c2 = st.columns([1,2])

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ➕ إضافة مريض")
        with st.form("add_patient", clear_on_submit=True):
            name = st.text_input("اسم المريض *")
            gender = st.selectbox("الجنس", ["Female","Male"])
            age = st.number_input("العمر",0,120,25)
            phone = st.text_input("الجوال")
            city = st.text_input("المدينة")
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ"):
                if not name.strip():
                    st.error("الاسم مطلوب")
                elif not validate_phone(phone):
                    st.error("رقم غير صحيح")
                else:
                    st.session_state.patients = pd.concat([
                        patients,
                        pd.DataFrame([{
                            "patient_id": new_id("P"),
                            "full_name": name,
                            "gender": gender,
                            "age": age,
                            "phone": phone,
                            "city": city,
                            "notes": notes,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }])
                    ], ignore_index=True)
                    st.success("تمت الإضافة ✅")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.dataframe(patients, use_container_width=True, hide_index=True)

# =============================
# Doctors
# =============================
with tab2:
    c1, c2 = st.columns([1,2])

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ➕ إضافة طبيب")
        with st.form("add_doctor", clear_on_submit=True):
            name = st.text_input("اسم الطبيب *")
            spec = st.text_input("التخصص *")
            phone = st.text_input("الجوال")
            room = st.text_input("الغرفة")
            if st.form_submit_button("حفظ"):
                if not name or not spec:
                    st.error("الاسم والتخصص مطلوبين")
                else:
                    st.session_state.doctors = pd.concat([
                        doctors,
                        pd.DataFrame([{
                            "doctor_id": new_id("D"),
                            "full_name": name,
                            "specialty": spec,
                            "phone": phone,
                            "room": room,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }])
                    ], ignore_index=True)
                    st.success("تمت الإضافة ✅")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.dataframe(doctors, use_container_width=True, hide_index=True)

# =============================
# Appointments
# =============================
with tab3:
    st.markdown("### ➕ حجز موعد")
    if len(patients)==0 or len(doctors)==0:
        st.warning("أضيفي مرضى وأطباء أولًا")
    else:
        with st.form("add_appt", clear_on_submit=True):
            p = st.selectbox("المريض", patients["full_name"])
            d = st.selectbox("الطبيب", doctors["full_name"])
            drow = doctors[doctors["full_name"]==d].iloc[0]
            appt_date = st.date_input("التاريخ", date.today())
            appt_time = st.time_input("الوقت", time(10,0))
            status = st.selectbox("الحالة",["Scheduled","Completed","Cancelled"])
            reason = st.text_input("السبب")
            if st.form_submit_button("حجز"):
                prow = patients[patients["full_name"]==p].iloc[0]
                st.session_state.appointments = pd.concat([
                    appointments,
                    pd.DataFrame([{
                        "appt_id": new_id("A"),
                        "patient_id": prow["patient_id"],
                        "patient_name": p,
                        "doctor_id": drow["doctor_id"],
                        "doctor_name": d,
                        "specialty": drow["specialty"],
                        "appt_date": appt_date.isoformat(),
                        "appt_time": appt_time.strftime("%H:%M"),
                        "status": status,
                        "reason": reason,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }])
                ], ignore_index=True)
                st.success("تم الحجز ✅")

    if len(appointments)>0:
        show = appointments.copy()
        show["status"] = show["status"].apply(badge_status)
        st.dataframe(show, use_container_width=True, hide_index=True)

# =============================
# Reports
# =============================
with tab4:
    st.markdown("### 📊 التقارير والتصدير")
    choice = st.selectbox("اختر الجدول",["Patients","Doctors","Appointments"])
    if choice=="Patients":
        export_buttons(patients,"patients")
    elif choice=="Doctors":
        export_buttons(doctors,"doctors")
    else:
        export_buttons(appointments,"appointments")

st.sidebar.divider()
if st.sidebar.button("🔄 مسح كل البيانات"):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown(
    '<div class="small-note">✅ مشروع جاهز للتسليم – Clinic Management System</div>',
    unsafe_allow_html=True
)
