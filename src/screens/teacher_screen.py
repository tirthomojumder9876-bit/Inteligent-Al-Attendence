import time
import streamlit as st
from src.components.footer import footer_dashboard
from src.components.header import header_dashboard
from src.database.db import check_teacher_exists, create_teacher, teacher_login
from src.ui.base_layout import style_background_dashboard, style_base_layout


def teacher_screen():
    style_background_dashboard()
    # style_base_layout()
    
    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif (
        "teacher_login_type" not in st.session_state
        or st.session_state.teacher_login_type == "login"
    ):
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    st.header(f""" welcome back, {teacher_data['name']}!""")

def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button(
            "Go back to Home",
            type="secondary",
            key="teacher_login_back_btn",
            shortcut="control+backspace",
        ):
            st.session_state["login_type"] = None
            st.rerun()

    st.markdown(
        "<h2 style='text-align: center; color: #5865F2;'>Login using password</h2>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("")

    teacher_username = st.text_input(
        "Enter your username", placeholder="Username", key="teacher_login_user"
    )
    teacher_pass = st.text_input(
        "Enter your password",
        placeholder="Password",
        type="password",
        key="teacher_login_pass",
    )

    st.divider()

    btnc1, btnc2 = st.columns(2, gap="large")
    with btnc1:
        if st.button(
            "Login",
            icon=":material/passkey:",
            shortcut="control+enter",
            use_container_width=True,
        ):
            teacher = teacher_login(teacher_username, teacher_pass)
            if teacher:
                st.session_state["logged_in_teacher"] = teacher
                st.toast("Login successful, welcome back!", icon="✅")
                time.sleep(1)
                st.rerun()
            else:
                st.error(
                    "Invalid username or password. Please try again.", icon="❌"
                )

    with btnc2:
        if st.button(
            "Register Instead",
            type="primary",
            icon=":material/passkey:",
            use_container_width=True,
        ):
            st.session_state.teacher_login_type = "register"
            st.rerun()

    # footer_dashboard()


def register_teacher(
    teacher_username, teacher_name, teacher_pass, teacher_pass_confirm
):
    if (
        not teacher_username
        or not teacher_name
        or not teacher_pass
        or not teacher_pass_confirm
    ):
        return False, "Please fill all the fields"

    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match"

    if check_teacher_exists(teacher_username):
        return False, "Username already exists"

    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Teacher registered successfully. Please login now."
    except Exception as e:
        return False, f"An error occurred while registering: {str(e)}"


def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment="center", gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button(
            "Go back to Home",
            type="secondary",
            key="teacher_reg_back_btn",
            shortcut="control+backspace",
        ):
            st.session_state["login_type"] = None
            st.rerun()

    st.markdown(
        "<h2 style='text-align: center; color: #5865F2;'>Register your teacher profile</h2>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("")

    teacher_username = st.text_input(
        "Enter your username",
        placeholder="Tirtho Mojumdar",
        key="teacher_reg_user",
    )
    teacher_name = st.text_input(
        "Enter name", placeholder="Tirtho Mojumdar", key="teacher_reg_name"
    )
    teacher_pass = st.text_input(
        "Enter your password",
        placeholder="Password",
        type="password",
        key="teacher_reg_pass",
    )
    teacher_pass_confirm = st.text_input(
        "Confirm your password",
        placeholder="Confirm Password",
        type="password",
        key="teacher_reg_pass_conf",
    )

    st.divider()

    btnc1, btnc2 = st.columns(2, gap="large")
    with btnc1:
        if st.button(
            "Register now",
            icon=":material/passkey:",
            shortcut="control+enter",
            use_container_width=True,
        ):
            success, message = register_teacher(
                teacher_username,
                teacher_name,
                teacher_pass,
                teacher_pass_confirm,
            )
            if success:
                st.success(message)
                time.sleep(1.5)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button(
            "Login Instead",
            type="primary",
            icon=":material/passkey:",
            use_container_width=True,
        ):
            st.session_state.teacher_login_type = "login"
            st.rerun()

    # footer_dashboard()