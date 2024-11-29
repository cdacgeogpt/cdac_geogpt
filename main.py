import os
import streamlit as st
import yaml
from streamlit_authenticator import Authenticate
from yaml.loader import SafeLoader
import logging
from pathlib import Path
from dotenv import dotenv_values
from detectaicore import set_up_logging
import time


def add_custom_css():
    """
    Adds custom CSS for styling and animations.
    """
    st.markdown(
        """
        <style>
        /* Fade-in animation for header and footer */
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }

        .header {
            animation: fadeIn 2s;
        }

        .footer {
                animation: fadeIn 2s;
                position: relative; /* Changed from fixed to relative */
                bottom: 0;
                left: 0;
                width: 100%;
                text-align: center;
                padding: 10px 0;
                font-size: 14px;
                color: white;
                margin-top: 50px; /* Ensures spacing from content */
            }

        /* Button hover effect */
        .stButton button:hover {
            background-color: #0056b3 !important;
            color: white !important;
            transition: 0.3s ease;
        }

        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f9f9f9;
            padding: 10px;
        }

        /* Welcome text styling */
        .welcome-text {
            font-size: 24px;
            color: #2c3e50;
            text-align: center;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def animated_welcome():
    """
    Displays an animated welcome message after login.
    """
    welcome_placeholder = st.empty()
    for i in range(1, 6):
        welcome_placeholder.markdown(f"<h3 style='text-align: center;'>Welcome{'!' * i}</h3>", unsafe_allow_html=True)
        time.sleep(0.3)
    welcome_placeholder.empty()


def main(config):
    """
    Main page APP
    """
    # Set up page configuration
    st.set_page_config(
        layout="wide",
        page_title="CDAC GeoGPT",
        page_icon="🌍",
        initial_sidebar_state="expanded",
    )

    # Apply custom CSS
    add_custom_css()

    # Display logo at the top
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=False, width=200)


    # Authentication
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "name" not in st.session_state:
        st.session_state["name"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None

    st.title("Welcome to CDAC GeoGPT 🌍")

    # Main app content
    authenticator = Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    authenticator.login(key="Login", location="main")

    logging.info(
        f'Name: {st.session_state["name"]}, '
        f'Authentication Status: {st.session_state["authentication_status"]}, '
        f'Username: {st.session_state["username"]}'
    )

    if st.session_state["authentication_status"]:
        authenticator.logout("Logout", "sidebar")
        st.success(f"Welcome, *{st.session_state['name']}*!")
        animated_welcome()  # Display animated welcome
        with st.container():
            st.metric("Active Users", 128, delta="+12 this week")
            st.metric("Processed Files", 420, delta="+34 this month")
    elif st.session_state["authentication_status"] == False:
        st.error("Invalid username or password.")
    elif st.session_state["authentication_status"] == None:
        st.warning("Please log in to access the app.")

    # Footer
    st.markdown(
        """
        <div class="footer">
            © 2024 C-DAC Chennai AI for EarthScience. All Rights Reserved.<br>
            Made with ❤️ by Arun, Yaythish Kannaa
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    # Set up environment
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUT_FOLDER = os.path.join(ROOT_DIR, "out")
    TMP_FOLDER = os.path.join(ROOT_DIR, "tmp")
    ANSWERS_FOLDER = os.path.join(ROOT_DIR, "answers")
    SAVE_FOLDER = os.path.join(ROOT_DIR, "saves")

    # Logging setup
    LOGS_PATH = os.path.join(ROOT_DIR, "logs")
    Path(LOGS_PATH).mkdir(parents=True, exist_ok=True)
    script_name = os.path.join(LOGS_PATH, "debug.log")

    if not set_up_logging(
        console_log_output="stdout",
        console_log_level="info",
        console_log_color=True,
        logfile_file=script_name,
        logfile_log_level="info",
        logfile_log_color=False,
        log_line_template="%(color_on)s[%(asctime)s] [%(threadName)s] [%(levelname)-8s] %(message)s%(color_off)s",
    ):
        print("Failed to set up logging.")
        raise AttributeError("Failed to create logging.")

    os.makedirs(OUT_FOLDER, exist_ok=True)
    os.makedirs(TMP_FOLDER, exist_ok=True)
    os.makedirs(ANSWERS_FOLDER, exist_ok=True)
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    # Read environment variables
    config = dotenv_values(os.path.join(ROOT_DIR, "keys", ".env"))
    if "NVIDIA_API_KEY" not in os.environ:
        os.environ["NVIDIA_API_KEY"] = config.get("NVIDIA_API_KEY")

    with open(os.path.join(ROOT_DIR, "keys/config.yaml")) as file:
        auth = yaml.load(file, Loader=SafeLoader)

    main(config=auth)
