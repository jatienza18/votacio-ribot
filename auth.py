import streamlit as st
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

# Set this to False in production! Allows HTTP for local dev.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# The path to the OAuth client secrets downloaded from Google Cloud
# This needs to be configured by the administrator for the actual domain deployment.
CLIENT_SECRETS_FILE = "client_secret.json"

# This should match the Authorized Redirect URI in Google Cloud Console
# For Streamlit local dev (default port 8501)
REDIRECT_URI = "http://localhost:8501" 

# Define the scopes we need (just basic profile and email)
SCOPES = [
    "openid", 
    "https://www.googleapis.com/auth/userinfo.email", 
    "https://www.googleapis.com/auth/userinfo.profile"
]

def get_auth_flow():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return None
        
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return flow

def login_button():
    flow = get_auth_flow()
    
    if flow is None:
        st.warning("⚠️ Configuració OAuth no trobada (client_secret.json falta).")
        st.info("Per a proves locals sense Google Auth, usa l'entrada manual a continuació.")
        
        # MOCK LOGIN FOR DEVELOPMENT
        mock_email = st.text_input("Simula un Login (introdueix el teu correu @insestatut.cat):")
        if st.button("Simular Login"):
            if mock_email and "@" in mock_email:
                st.session_state["user_email"] = mock_email
                st.session_state["user_name"] = mock_email.split('@')[0]
                st.rerun()
            else:
                st.error("Introdueix un correu vàlid per simular.")
        return

    # Generate the authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'''
            <a href="{auth_url}" target="_self" style="text-decoration: none;">
                <div style="background-color: #4285F4; color: white; padding: 12px; border-radius: 4px; text-align: center; font-weight: bold; font-family: sans-serif; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    🔑 Inicia sessió amb Google
                </div>
            </a>
            <p style="text-align: center; color: #666; font-size: 0.8em; margin-top: 10px;">
                Només s'admeten comptes corporatius autoritzats.
            </p>
        ''', unsafe_allow_html=True)

def handle_oauth_callback():
    """Check if the user is returning from Google Auth with a code"""
    query_params = st.query_params
    
    if "code" in query_params and "user_email" not in st.session_state:
        # We have a code, let's exchange it for a token
        code = query_params["code"]
        
        flow = get_auth_flow()
        if flow:
            try:
                # Exchange the authorization code for access tokens
                flow.fetch_token(code=code)
                credentials = flow.credentials
                
                # Verify the ID token and get user info
                request = requests.Request()
                user_info = id_token.verify_oauth2_token(
                    credentials.id_token, request, flow.client_config["client_id"]
                )
                
                # Store user info in session state
                st.session_state["user_email"] = user_info.get("email")
                st.session_state["user_name"] = user_info.get("name")
                
                # Clean up the URL
                st.query_params.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"Error d'autenticació: {e}")
                
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
