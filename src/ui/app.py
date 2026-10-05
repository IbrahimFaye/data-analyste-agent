"""
Interface Streamlit pour l'agent AI Data Analyst.
Lance avec : streamlit run src/ui/app.py
"""

import re
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import streamlit as st
from src.agent.loop import run_agent

# ============================================================
# Configuration de la page
# ============================================================
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
)

# ============================================================
# CSS custom : aligner les messages user à droite
# ============================================================
st.markdown("""
<style>
    /* Cible chaque conteneur de message chat */
    div[data-testid="stChatMessage"] {
        display: flex;
    }

    /* --- Messages USER : décalés à droite, largeur max 50% --- */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        flex-direction: row-reverse;
        text-align: right;
        justify-content: flex-start;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"])
        div[data-testid="stChatMessageContent"] {
        text-align: right;
        background-color: rgba(255, 75, 75, 0.10);
        border-radius: 12px;
        padding: 10px 14px;
        max-width: 50%;
        margin-left: auto;
        margin-right: 0;
    }

    /* --- Messages ASSISTANT : restent à gauche, largeur max 75% --- */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"])
        div[data-testid="stChatMessageContent"] {
        max-width: 75%;
    }
</style>
""", unsafe_allow_html=True)

st.caption("Bonjour ! Vos données ont beaucoup de choses à dire. Qu'aimeriez-vous découvrir aujourd'hui ?")

# ============================================================
# Initialisation de l'état persistant
# ============================================================
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "agent_history" not in st.session_state:
    st.session_state.agent_history = []

if "show_trace" not in st.session_state:
    st.session_state.show_trace = False


# ============================================================
# Helpers
# ============================================================
def strip_image_links(text: str) -> str:
    """Retire les liens markdown d'images du texte (on affiche les images autrement)."""
    pattern = r'!\[.*?\]\((.*?)\)'
    return re.sub(pattern, "", text).strip()


def stream_text(placeholder, text: str, delay: float = 0.005):
    """
    Affiche le texte caractère par caractère dans un placeholder Streamlit.
    Effet 'machine à écrire'.
    """
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(displayed + "▌")
        time.sleep(delay)
    placeholder.markdown(displayed)


# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.title("📊 AI Data Analyst Agent")
    st.header("⚙️ Options")
    st.session_state.show_trace = st.toggle(
        "Afficher les outils appelés", value=st.session_state.show_trace
    )

    if st.button("🗑️ Nouvelle conversation", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.agent_history = []
        st.rerun()

    st.divider()
    st.markdown("**Exemples de questions :**")
    st.markdown("- Quels sont les top 3 produits en 2024 ?")
    st.markdown("- Évolution du CA mensuel en 2024 ?")
    st.markdown("- Y a-t-il des anomalies dans les ventes ?")
    st.markdown("- Compare 2023 et 2024 par catégorie.")


# ============================================================
# Affichage de l'historique du chat
# ============================================================
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for img_path in msg.get("images", []):
            p = Path(img_path)
            if p.exists():
                st.image(str(p), use_container_width=True)


# ============================================================
# Zone de saisie
# ============================================================
if prompt := st.chat_input("Posez votre question sur les données..."):
    # 1. Afficher la question
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Générer la réponse
    with st.chat_message("assistant"):
        with st.spinner("L'agent analyse vos données..."):
            result = run_agent(
                prompt,
                history=st.session_state.agent_history,
                verbose=False,
            )

        # 3. Nettoyer le texte (retirer les liens markdown d'images)
        clean_text = strip_image_links(result["answer"])

        # 4. Effet machine à écrire
        placeholder = st.empty()
        stream_text(placeholder, clean_text, delay=0.005)

        # 5. Afficher les graphiques produits (via artifacts, PAS via regex)
        artifacts = result.get("artifacts", [])
        for img_path in artifacts:
            p = Path(img_path)
            if p.exists():
                st.image(str(p), use_container_width=True)
            else:
                st.warning(f"Image introuvable : {img_path}")

        # 6. Trace des tools (mode debug)
        if st.session_state.show_trace:
            with st.expander("🔍 Outils appelés", expanded=False):
                for msg in result["messages"]:
                    if msg["role"] == "assistant" and msg.get("tool_calls"):
                        for tc in msg["tool_calls"]:
                            st.code(
                                f"{tc['function']['name']}({tc['function']['arguments']})",
                                language="json",
                            )

    # 7. Persister dans l'état
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": clean_text,
        "images": artifacts,
    })
    st.session_state.agent_history = result["history"]