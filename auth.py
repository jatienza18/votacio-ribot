import streamlit as st
import os
import requests as std_requests
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

# Set this to False in production! Allows HTTP for local dev.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# The path to the OAuth client secrets downloaded from Google Cloud
# This needs to be configured by the administrator for the actual domain deployment.
CLIENT_SECRETS_FILE = "client_secret.json"

# Define the scopes we need (just basic profile and email)
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# Llegeix la URL dinàmicament o fa servir el valor local per defecte
if "google_oauth" in st.secrets:
    REDIRECT_URI = 'https://votacio-ribot.streamlit.app/'
else:
    REDIRECT_URI = 'http://localhost:8502/'

def get_auth_flow():
    # Attempt to load from Streamlit Secrets first (Production)
    if "google_oauth" in st.secrets:
        client_config = {"web": dict(st.secrets["google_oauth"])}
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        return flow
        
    # Fallback to local file
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
        st.warning("⚠️ Configuració OAuth no trobada.")
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
    auth_url, state = flow.authorization_url(prompt='consent', include_granted_scopes='true')
    
    # Embed the PKCE code_verifier into the state parameter since session_state is lost on redirect
    if hasattr(flow, "code_verifier") and flow.code_verifier:
        auth_url = auth_url.replace(f"state={state}", f"state={state}-pkce-{flow.code_verifier}")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            "🔑 Inicia sessió amb Google",
            url=auth_url,
            use_container_width=True,
            type="primary"
        )
        st.markdown(
            """<p style="text-align: center; color: #666; font-size: 0.8em; margin-top: 10px;">
                Només s'admeten comptes corporatius autoritzats.
            </p>""", 
            unsafe_allow_html=True
        )

def handle_oauth_callback():
    """Check if the user is returning from Google Auth with a code"""
    query_params = st.query_params
    
    if "code" in query_params and "user_email" not in st.session_state:
        # We have a code, let's exchange it for a token
        code = query_params["code"]
        
        flow = get_auth_flow()
        if flow:
            try:
                # Exchange the authorization code for access tokens manually to bypass PKCE
                client_config = flow.client_config
                token_url = client_config["token_uri"]
                
                data = {
                    "code": code,
                    "client_id": client_config["client_id"],
                    "client_secret": client_config["client_secret"],
                    "redirect_uri": flow.redirect_uri,
                    "grant_type": "authorization_code",
                }
                
                # Extract the code_verifier from the state parameter
                state = query_params.get("state", "")
                if "-pkce-" in state:
                    data["code_verifier"] = state.split("-pkce-")[1]
                
                response = std_requests.post(token_url, data=data)
                token_data = response.json()
                
                if "error" in token_data:
                    st.error(f"Error d'autenticació: {token_data['error']} - {token_data.get('error_description', '')}")
                    return
                    
                id_token_jwt = token_data.get("id_token")
                
                # Verify the ID token and get user info
                request = requests.Request()
                user_info = id_token.verify_oauth2_token(
                    id_token_jwt, request, flow.client_config["client_id"]
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
