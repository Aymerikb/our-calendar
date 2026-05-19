import sqlite3
from datetime import datetime, time
from zoneinfo import ZoneInfo
import streamlit as st

# ========================================================
# 1. FONCTIONS DE LA BASE DE DONNÉES (Le Backend)
# ========================================================
def initialiser_db():
    conn = sqlite3.connect('connectedplan.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evenements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        debut TEXT NOT NULL,
        fin TEXT NOT NULL,
        cree_par TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def ajouter_evenement(titre, debut_dt, fin_dt, cree_par):
    conn = sqlite3.connect('connectedplan.db')
    cursor = conn.cursor()
    debut_str = debut_dt.strftime("%Y-%m-%d %H:%M")  
    fin_str = fin_dt.strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO evenements (titre, debut, fin, cree_par)
    VALUES (?, ?, ?, ?)
    """, (titre, debut_str, fin_str, cree_par))
    conn.commit()
    conn.close()

def recuperer_events():
    conn = sqlite3.connect('connectedplan.db')
    cursor = conn.cursor()
    cursor.execute("SELECT titre, debut, fin, cree_par FROM evenements ORDER BY debut ASC")
    resultats = cursor.fetchall()
    conn.close()
    return resultats

initialiser_db()

# ========================================================
# 2. DICTIONNAIRE DE TRADUCTION (Dictionnaire Python)
# ========================================================
traductions = {
    "En France 🇫🇷": {
        "titre_app": "📅 Notre Emploi du Temps Connecté",
        "sous_titre": "Planifions nos moments ensemble, sans se tromper d'heure !",
        "sidebar_titre": "Où es-tu actuellement ?",
        "h_ajouter": "➕ Ajouter un événement",
        "label_activite": "Nom de l'activité (ex: Resto, FaceTime, Dodo...)",
        "label_jour": "Sélectionne le jour",
        "label_debut": "Heure de début",
        "label_fin": "Heure de fin",
        "label_qui": "Qui crée cet événement ?",
        "btn_valider": "Ajouter au calendrier",
        "succes": "Événement enregistré avec succès !",
        "h_liste": "👀 Les rendez-vous planifiés",
        "vide": "Aucun événement prévu pour le moment.",
        "cree_par": "Créé par",
        "heure_locale": "Heure locale"
    },
    "En Corée du Sud 🇰🇷": {
        "titre_app": "📅 연결된 우리 일정표",
        "sous_titre": "시차 걱정 없이 함께할 시간을 계획해요!",
        "sidebar_titre": "현재 어디에 계신가요?",
        "h_ajouter": "➕ 일정 추가하기",
        "label_activite": "활동 이름 (예: 데이트, 영상통화, 취침...)",
        "label_jour": "날짜 선택",
        "label_debut": "시작 시간",
        "label_fin": "종료 시간",
        "label_qui": "작성자",
        "btn_valider": "일정표에 추가",
        "succes": "일정이 성공적으로 저장되었습니다!",
        "h_liste": "👀 계획된 일정 보기",
        "vide": "현재 계획된 일정이 없습니다.",
        "cree_par": "작성자",
        "heure_locale": "현지 시간"
    }
}

# ========================================================
# 3. L'INTERFACE GRAPHIQUE (Le Frontend)
# ========================================================
# 1. Sélection de la langue/lieu dans la barre latérale
emplacement = st.sidebar.radio("Où es-tu actuellement ? / 현재 어디 계신가요?", ["En France 🇫🇷", "En Corée du Sud 🇰🇷"])

# On sélectionne le bon dictionnaire de mots selon le choix
langue = traductions[emplacement]

# Titres de l'application traduits
st.title(langue["titre_app"])
st.write(langue["sous_titre"])

# Définition des fuseaux horaires
tz_france = ZoneInfo("Europe/Paris")
tz_coree = ZoneInfo("Asia/Seoul")

# --- FORMULAIRE D'AJOUT ---
st.header(langue["h_ajouter"])

with st.form("form_evenement", clear_on_submit=True):
    titre = st.text_input(langue["label_activite"])
    date = st.date_input(langue["label_jour"], datetime.now())
    heure_debut = st.time_input(langue["label_debut"], time(14, 0))
    heure_fin = st.time_input(langue["label_fin"], time(15, 0))
    
    # Choix des prénoms ou rôles simples
    qui = st.selectbox(langue["label_qui"], ["Moi / 나", "Ma Copine / 여자친구"])
    
    bouton_valider = st.form_submit_button(langue["btn_valider"])

if bouton_valider and titre:
    fuseau_local = tz_france if emplacement == "En France 🇫🇷" else tz_coree
    
    debut_local = datetime.combine(date, heure_debut).replace(tzinfo=fuseau_local)
    fin_local = datetime.combine(date, heure_fin).replace(tzinfo=fuseau_local)
    
    debut_utc = debut_local.astimezone(ZoneInfo("UTC"))
    fin_utc = fin_local.astimezone(ZoneInfo("UTC"))
    
    ajouter_evenement(titre, debut_utc, fin_utc, qui)
    st.success(langue["succes"])

st.markdown("---")

# --- AFFICHAGE CONVERTI ---
st.header(langue["h_liste"])

evenements_stockes = recuperer_events()

if not evenements_stockes:
    st.info(langue["vide"])
else:
    tz_affichage = tz_france if emplacement == "En France 🇫🇷" else tz_coree
    
    for rdv in evenements_stockes:
        debut_utc = datetime.strptime(rdv[1], "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("UTC"))
        fin_utc = datetime.strptime(rdv[2], "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("UTC"))
        
        debut_converti = debut_utc.astimezone(tz_affichage)
        fin_converti = fin_utc.astimezone(tz_affichage)
        
        str_debut = debut_converti.strftime("%d/%m à %H:%M" if emplacement == "En France 🇫🇷" else "%m/%d %H:%M")
        str_fin = fin_converti.strftime("%H:%M")
        
        st.write(f"**{rdv[0]}**")
        st.caption(f"🗓️ {str_debut} ~ {str_fin} ({langue['heure_locale']}) | ✍️ {langue['cree_par']} : {rdv[3]}")
        st.markdown("---")