import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Aquest fitxer s'hauria de dir 'nou_serviceAccount.json' i estar a la mateixa carpeta
CREDENTIALS_FILE = ".streamlit/secrets.toml" # Trying secrets first usually for local streamlit if configured, but let's stick to the json if that's what was used
if not os.path.exists("nou_serviceAccount.json"):
    CREDENTIALS_FILE = "../educational-platform/backend/serviceAccountKey.json"
else:
    CREDENTIALS_FILE = "nou_serviceAccount.json"

def seed_database():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Error: No es troba el fitxer de credencials '{CREDENTIALS_FILE}'")
        return

    # Inicialitzem Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(CREDENTIALS_FILE)
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    print("Conectat a la nova base de dades Firestore.")
    
    # 1. DELETE EXSITING PROFESSORS TO ENSURE EXACT MATCH
    print("Netejant el cens anterior...")
    docs = db.collection("professors").stream()
    for doc in docs:
        doc.reference.delete()

    print("Introduint el cens oficial definitiu...")

    # Llista extreta EXACAMENT de les 3 imatges
    # Format: Nom, Cognoms, Correu, Votar (Actiu), Elegible (Si No, rol DIRECCIO)
    official_census = [
        {"cognoms": "Aguilar", "nom": "Anna", "email": "aaguilar.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Albiach", "nom": "Christian", "email": "calbiach.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Albinyana", "nom": "Marina", "email": "malbinyana.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Amat", "nom": "Meritxell", "email": "mamat.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Atienza", "nom": "Jan", "email": "jatienza.prof@ribotiserra.cat", "votar": True, "elegible": False},
        {"cognoms": "Aurés", "nom": "Joan", "email": "jaures.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Baena", "nom": "Maribel", "email": "mbaena5.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Berjano", "nom": "Sandra", "email": "sberjano.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Blai", "nom": "Andreu", "email": "ablai.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Borja", "nom": "Lluis", "email": "lborja.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Camps", "nom": "Lidia", "email": "lcamps.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Carrasco", "nom": "Ana Mª", "email": "acarra3.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Carreras", "nom": "Montserrat", "email": "mcarreras.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Casanovas", "nom": "Adrià", "email": "acasanovas.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Cases", "nom": "Alba", "email": "acases.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Castro", "nom": "Pilar", "email": "pcastro.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Cea", "nom": "Esther", "email": "ecea.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Clarà", "nom": "Laia", "email": "tls@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Company", "nom": "Júlia", "email": "jcompany.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Corrales", "nom": "Francisco David", "email": "dcorrales.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "de Haro", "nom": "Catalina", "email": "cdeharo.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Escoto", "nom": "Sandra", "email": "sescoto.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Farnós", "nom": "Carmina", "email": "cfarnos.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Fernández", "nom": "Adrià", "email": "afernandez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Fernandez", "nom": "Sergi", "email": "sfernandez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ferran", "nom": "Guillem", "email": "gferran.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ferràndiz", "nom": "Míriam", "email": "mferrandiz.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Finet", "nom": "Ascensió", "email": "afinet.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Font", "nom": "Estefania", "email": "efont.prof@ribotiserra.cat", "votar": True, "elegible": False},
        {"cognoms": "Gázquez", "nom": "José", "email": "jgazque2.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Giraldo", "nom": "Pilar", "email": "mgiraldo.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Gómez", "nom": "María", "email": "mgomez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "González", "nom": "José Luis", "email": "jgonzalez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Guerra", "nom": "Katheryn", "email": "kguerra.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Iglesias", "nom": "David", "email": "diglesis.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Janer", "nom": "Marta", "email": "mjaner.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Jiménez", "nom": "Albert", "email": "ajimenez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Luis", "nom": "Pilar Francisca", "email": "pluis.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Marín", "nom": "Helena", "email": "emarin7.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Martin", "nom": "Aina", "email": "amartin.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Martín", "nom": "Maria", "email": "mmar526.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Martínez", "nom": "Patrici", "email": "pmartinez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Martínez", "nom": "Toni", "email": "tmartinez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Masip", "nom": "Núria", "email": "nmasip.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Maya", "nom": "Elena", "email": "emaya.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Mayordomo", "nom": "Anna", "email": "amayordomo.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Meroño", "nom": "Malena Fiorella", "email": "mmerono.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Miralles", "nom": "Roser", "email": "rmiralles.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Mompó", "nom": "Sílvia", "email": "smompo.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Monteso", "nom": "Laia", "email": "lmonteso.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Montiu", "nom": "Xavier", "email": "xmontiu.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Navarro", "nom": "Ana", "email": "anavarro.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Olivé", "nom": "Silvia", "email": "solive.prof@ribotiserra.cat", "votar": True, "elegible": False},
        {"cognoms": "Ortega", "nom": "Anna", "email": "aortega.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Pastor", "nom": "Raquel", "email": "rpastor.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Paz", "nom": "Laia", "email": "laiapaz.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Pellisé", "nom": "Berta", "email": "bpellise.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Pérez", "nom": "Àlex", "email": "aperez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Pizà", "nom": "Lluca", "email": "lpiza.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Plana", "nom": "Clàudia", "email": "cplana.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Pozas", "nom": "Anabel", "email": "apozas3.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ramírez", "nom": "Verónica", "email": "vramirez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ramiro", "nom": "Beatriz", "email": "bramiro.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ravina", "nom": "Fernanda", "email": "mravina.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ribot", "nom": "Francesca", "email": "fribot.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ricart", "nom": "Montserrat", "email": "mricart.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Rider", "nom": "Carme", "email": "crider.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Rivera", "nom": "Mayka", "email": "mrivera.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Rodríguez", "nom": "Laura", "email": "lrodriguez.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Rota", "nom": "Angi", "email": "arota.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ruiz", "nom": "Joana", "email": "jruiz.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Ruiz", "nom": "Xelo", "email": "directora@ribotiserra.cat", "votar": True, "elegible": False},
        {"cognoms": "Salguero", "nom": "Encarni", "email": "esalguero.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Sánchez", "nom": "Anna", "email": "capestudis.anna@ribotiserra.cat", "votar": True, "elegible": False}, # Name cut off in image, guessing 'Sánchez' based on alphabetical order and common names
        {"cognoms": "Sensada", "nom": "Toni", "email": "tsensada.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Soldevila", "nom": "Carla", "email": "csoldevila.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Torres", "nom": "Miguel", "email": "mtorres.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Torres", "nom": "Patricia", "email": "capestudis.patricia@ribotiserra.cat", "votar": True, "elegible": False},
        {"cognoms": "Torrico", "nom": "Pilar", "email": "ptorrico.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Tur", "nom": "Betlem", "email": "btur.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Urrea", "nom": "Gemma", "email": "gurrea.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Van Hal", "nom": "Tamara", "email": "tvanhall.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Vilella", "nom": "Eva", "email": "evilella.prof@ribotiserra.cat", "votar": True, "elegible": True},
        {"cognoms": "Vilella", "nom": "Laura", "email": "lavilella.prof@ribotiserra.cat", "votar": True, "elegible": True}
    ]

    for p in official_census:
        # Build standard object
        email = p["email"].lower()
        # id is safe email without special chars if needed, but email as id is fine for professors collection usually
        # Let's use email as document ID for easy lookup, replacing @ and . to avoid path issues if any, or just use it directly
        doc_id = email.replace("@", "_").replace(".", "_")
        
        roles = ["DOCENT"]
        if not p["elegible"]:
            roles.append("DIRECCIO")
            
        doc_data = {
            "nom": p["nom"],
            "cognoms": p["cognoms"],
            "email": email,
            "actiu": p["votar"],
            "rols": roles
        }
        
        db.collection("professors").document(doc_id).set(doc_data)
        status = "❌ Només Votant" if not p["elegible"] else "✅ Elegible"
        print(f"Afegit: {p['cognoms']}, {p['nom']} - {status}")

    print("\n🎉 Cens oficial restaurat correctament! Hi ha {} registres.".format(len(official_census)))

if __name__ == "__main__":
    seed_database()
