import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import uuid
from datetime import datetime

# Initialize Firebase
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # Check if secrets file exists first
        secrets_path = os.path.join(".streamlit", "secrets.toml")
        
        if os.path.exists(secrets_path) and "firebase" in st.secrets:
            # We have secrets configured
            cred_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for local development using the platform's service account
            fallback_path = "../educational-platform/backend/serviceAccountKey.json"
            if os.path.exists(fallback_path):
                cred = credentials.Certificate(fallback_path)
                firebase_admin.initialize_app(cred)
            else:
                st.error("No s'han trobat les credencials de Firebase ni a secrets.toml ni a serviceAccountKey.json")
                st.stop()
    return firestore.client()

db = init_firebase()

# Helpers db
def is_authorized_voter(email: str):
    # Cerca si aquest correu pertany a un professor actiu
    docs = db.collection("professors").where("email", "==", email).where("actiu", "==", True).limit(1).stream()
    return any(docs)

def get_candidates():
    # Obté els professors actius que NO són de l'equip directiu
    docs = db.collection("professors").where("actiu", "==", True).stream()
    candidates = []
    for doc in docs:
        data = doc.to_dict()
        roles = data.get("rols", [])
        
        # Consider candidates ONLY if they don't have "DIRECCIO" role
        if "DIRECCIO" not in [r.upper() for r in roles]:
            nom_complet = f"{data.get('nom', '')} {data.get('cognoms', '')}".strip()
            # If name is empty, try using the email or id
            if not nom_complet:
                nom_complet = data.get("email", doc.id)
            candidates.append({"id": doc.id, "nom": nom_complet, "roles": roles})
            
    # Sort alphabetically
    return sorted(candidates, key=lambda x: x["nom"])

def has_voted(email: str):
    doc = db.collection("who_voted").document(email).get()
    return doc.exists

def cast_vote(email: str, selected_candidate_ids: list):
    # 1. Register that the email has voted
    db.collection("who_voted").document(email).set({
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    
    # 2. Store the anonymous ballot
    db.collection("voting_ballots").add({
        "vots": selected_candidate_ids,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

def get_voting_results():
    ballots = db.collection("voting_ballots").stream()
    counts = {}
    total_ballots = 0
    for b in ballots:
        total_ballots += 1
        data = b.to_dict()
        vots = data.get("vots", [])
        for v in vots:
            counts[v] = counts.get(v, 0) + 1
            
    return counts, total_ballots
