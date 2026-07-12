import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard


def student_screen():
    style_background_dashboard()
    #style_base_layout()

    if "student_screen_type" not in st.session_state or st.session_state.student_screen_type=="home":
         student_screen_home()
    elif st.session_state.student_screen_type=="attendance":
         student_screen_attendance()
    elif st.session_state.student_screen_type=="update":
         student_screen_update()



def student_screen_home():
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type="secondary", key="studenthomebackbtn", shortcut="control+backspace"):
            st.session_state["login_type"] = None
            st.rerun()

    st.header("Welcome, Student", text_alignment="center")
    st.space()
    st.space()

    btnc1, btnc2 = st.columns(2, gap="large")
    with btnc1:
        if st.button("Give Attendance", icon=":material/how_to_reg:", shortcut="control+enter", width="stretch"):
            st.session_state.student_screen_type = "attendance"

    with btnc2:
        if st.button("Update Attendance", type="primary", icon=":material/fact_check:", width="stretch"):
            st.session_state.student_screen_type = "update"

    #footer_dashboard()


def student_screen_attendance():
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type="secondary", key="attendancebackbtn", shortcut="control+backspace"):
            st.session_state.student_screen_type = "home"
            st.rerun()

    st.header("Give Attendance", text_alignment="center")
    st.space()
    st.space()

    # TODO: hook up face recognition capture here
    # (see requirements.txt -> face_recognition_models, dlib-bin, scikit-learn)
    st.write("Face recognition attendance capture goes here.")

    st.divider()

    if st.button("Update Attendance Instead", type="primary", icon=":material/fact_check:", width="stretch"):
        st.session_state.student_screen_type = "update"

    #footer_dashboard()


def student_screen_update():
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type="secondary", key="updatebackbtn", shortcut="control+backspace"):
            st.session_state.student_screen_type = "home"
            st.rerun()

    st.header("Update Attendance", text_alignment="center")
    st.space()
    st.space()

    # TODO: fetch + display / edit attendance records from Supabase here
    st.write("Attendance history and update options go here.")

    st.divider()

    if st.button("Give Attendance Instead", icon=":material/how_to_reg:", shortcut="control+enter", width="stretch"):
        st.session_state.student_screen_type = "attendance"

    #footer_dashboard()
    