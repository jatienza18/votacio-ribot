import streamlit as st
import db
from auth import login_button, handle_oauth_callback, logout

st.set_page_config(page_title="Eleccions Consell Escolar - Claustre", page_icon="🗳️", layout="centered")

# In case we're returning from OAuth
handle_oauth_callback()

def main():
    st.title("🗳️ Eleccions Representants del Claustre")
    
    # 1. NOT LOGGED IN
    if "user_email" not in st.session_state:
        st.write("Benvingut/da al portal de votació del claustre.")
        st.write("Per garantir un procés de votació just i secret, si us plau, **inicia sessió amb el teu correu de l'institut.**")
        st.write("")
        login_button()
        return

    # 2. LOGGED IN - Check if Voted
    user_email = st.session_state["user_email"]
    user_name = st.session_state.get("user_name", user_email)
    
    # Quick header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Connectat com a: **{user_email}**")
    with col2:
        if st.button("Tancar Sessió", key="btn_logout"):
            logout()
            
    st.divider()

    # Is Admin?
    is_admin = user_email in ["admin@insestatut.cat", "director@insestatut.cat", "jan"] # Configurable
    if is_admin:
        if st.sidebar.checkbox("🔒 Panell d'Administració"):
            show_admin_panel()
            return
            
    # Check Whitelist (Is Active Professor?)
    if not db.is_authorized_voter(user_email) and not is_admin:
        st.error("⛔ Accés denegat.")
        st.write("Aquest correu no consta com a membre actiu del claustre amb dret a vot.")
        st.write("Si creus que és un error, contacta amb adreçdició/informàtica.")
        return
            
    # Has already voted?
    if db.has_voted(user_email):
        st.success("✅ Ja has exercit el teu dret a vot!")
        st.info("El teu vot ha estat emmagatzemat de forma completament anònima.")
        st.balloons()
        return
        
    # 3. VOTING SCREEN
    st.subheader("Selecció de Candidats")
    st.write("Has d'escollir **exactament a dues persones** de la següent llista de candidats.")
    
    candidates = db.get_candidates()
    
    if not candidates:
        st.warning("No s'han trobat candidats disponibles per votar.")
        return

    # Make a dictionary mapping names to IDs for the selectbox
    candidate_options = {c["nom"]: c["id"] for c in candidates}
    candidate_names = list(candidate_options.keys())
    
    selected_names = st.multiselect(
        "Tria els teus representants:",
        options=candidate_names,
        max_selections=2,
        placeholder="Selecciona 2 persones..."
    )
    
    if len(selected_names) == 2:
        st.success("Has seleccionat exactament 2 candidats. Pots procedir a enviar el teu vot.")
        
        # Confirm
        with st.expander("Resum del teu vot (Comprova-ho)", expanded=True):
            st.write(f"1. **{selected_names[0]}**")
            st.write(f"2. **{selected_names[1]}**")
            st.warning("Un cop enviat, el vot és **irrevocable**. L'aplicació guardarà els teus candidats a una urna de forma secreta i desvincularà el teu correu d'aquesta tria.")
            
            if st.button("🗳️ Emetre Vot Definitiu", type="primary", use_container_width=True):
                # Submit ballot
                selected_ids = [candidate_options[selected_names[0]], candidate_options[selected_names[1]]]
                db.cast_vote(user_email, selected_ids)
                st.rerun() # Reloads the page, and has_voted will kick in
    else:
        st.info("Si us plau, selecciona exactament 2 persones de la llista desplegable per poder emetre el vot.")


def show_admin_panel():
    st.title("Tauler d'Escrutini")
    
    # Simple Refresh
    if st.button("🔄 Actualitzar Resultats"):
        st.rerun()
        
    counts, total = db.get_voting_results()
    
    # Get all candidate names to map IDs back to Names
    candidates = db.get_candidates()
    id_to_name = {c["id"]: c["nom"] for c in candidates}
    
    st.metric(label="Total de Vots Emesos", value=total)
    
    if total == 0:
        st.info("Encara no hi ha cap vot registrat a l'urna.")
        return
        
    # Sort results
    sorted_results = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    
    st.subheader("Resultats Provisionals")
    
    for i, (cid, count) in enumerate(sorted_results):
        name = id_to_name.get(cid, cid)
        
        # Determine medals
        if i == 0: medal = "🥇"
        elif i == 1: medal = "🥈"
        elif i == 2: medal = "🥉"
        elif i == 3: medal = "🔄 (Suplent)"
        else: medal = ""
            
        st.markdown(f"**{i+1}.** {medal} {name}: **{count} vots**")
        
    st.divider()
    st.warning("En cas d'empat, prevaldrà el docent de més edat.")
    
if __name__ == "__main__":
    main()
