import os
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from yaml.loader import SafeLoader
from streamlit_authenticator import Authenticate
import yaml
import logging
import time
from pathlib import Path
from urllib.parse import urlencode

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
            position: relative;
            bottom: 0;
            left: 0;
            width: 100%;
            text-align: center;
            padding: 10px 0;
            font-size: 14px;
            color: white;
            margin-top: 50px;
        }

        /* Button hover effect */
        .stButton button:hover {
            background-color: #0056b3 !important;
            color: white !important;
            transition: 0.3s ease;
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
    
def google_login(client_secrets_path, redirect_uri):
    """
    Generates Google OAuth URL for login and returns flow instance.
    """
    flow = Flow.from_client_secrets_file(
        client_secrets_path,
        scopes=["https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=redirect_uri,
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    return auth_url, flow

def main(config):
    """
    Main App Logic
    """
    st.set_page_config(
        layout="wide",
        page_title="CDAC GeoGPT",
        page_icon="🌍",
        initial_sidebar_state="expanded",
    )

    add_custom_css()

    # Display logo at the top
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=False, width=200)

    # Initialize session state variables for authentication
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "name" not in st.session_state:
        st.session_state["name"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "google_credentials" not in st.session_state:
        st.session_state["google_credentials"] = None

    st.title("Welcome to CDAC GeoGPT 🌍")

    # Google Login
    client_secrets_path = os.path.join(os.path.dirname(__file__), "client_secrets.json")
    redirect_uri = "https://cdacgeogpt.streamlit.app" # Replace with your deployed app URL

    auth_url, flow = google_login(client_secrets_path, redirect_uri)

    # Google Login Form
    st.subheader("Login with Google")
    if st.button("Login with Google"):
        st.markdown(
            f"<a href='{auth_url}' target='_self'>Click here to login with Google</a>",
            unsafe_allow_html=True,
        )

    # Traditional Login Form
    st.subheader("Login with Username/Password")
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

    # Handle Google OAuth redirect response using st.query_params
    query_params = st.query_params
    if "code" in query_params:
        credentials, user_email = handle_google_auth(flow)
        if credentials:
            st.session_state["google_credentials"] = credentials
            st.session_state["authentication_status"] = True
            st.session_state["name"] = user_email
            st.rerun()

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

# Update handle_google_auth
def handle_google_auth(flow):
    """
    Handles Google OAuth Authentication response.
    """
    query_params = st.query_params  # Use st.query_params to get query parameters
    
    # Check if the response contains the 'code' parameter
    if "code" in query_params:
        try:
            # Fetch the credentials using the authorization code
            credentials = flow.fetch_token(authorization_response=query_params["code"])
            user_email = credentials.id_token.get("email", "Unknown User")
            return credentials, user_email
        except Exception as e:
            st.error(f"Error during Google authentication: {e}")
            return None, None
    return None, None

if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(ROOT_DIR, "keys/config.yaml")) as file:
        auth = yaml.load(file, Loader=SafeLoader)

    main(config=auth)
