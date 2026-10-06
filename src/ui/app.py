
import re
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import streamlit as st
from src.agent.loop import run_agent
from src.agent.graph import run_agent_langgraph

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
    div[data-testid="stChatMessage"] { display: flex; }
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
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"])
        div[data-testid="stChatMessageContent"] {
        max-width: 75%;
    }
</style>
""", unsafe_allow_html=True)

st.caption("Bonjour ! Vos données ont beaucoup de choses à dire. Qu'aimeriez-vous découvrir aujourd'hui ?")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "agent_history" not in st.session_state:
    st.session_state.agent_history = []

if "show_trace" not in st.session_state:
    st.session_state.show_trace = False

if "engine" not in st.session_state:
    st.session_state.engine = "LangGraph" 


def strip_image_links(text: str) -> str:
    pattern = r'!\[.*?\]\((.*?)\)'
    return re.sub(pattern, "", text).strip()


def stream_text(placeholder, text: str, delay: float = 0.005):
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(displayed + "▌")
        time.sleep(delay)
    placeholder.markdown(displayed)


def run_agent_dispatch(question: str, history: list):
    if st.session_state.engine == "LangGraph":
        return run_agent_langgraph(question, history=history, verbose=False)
    else:
        return run_agent(question, history=history, verbose=False)

with st.sidebar:
    st.title("📊 AI Data Analyst Agent")

    st.header("⚙️ Options")

    st.session_state.engine = st.radio(
        "🧠 Moteur d'agent",
        options=["LangGraph", "Manuel"],
        index=0 if st.session_state.engine == "LangGraph" else 1,
        help=(
            "**LangGraph** : version production, plus lente mais extensible.\n\n"
            "**Manuel** : boucle codée à la main, plus rapide et pédagogique."
        ),
    )

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


for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for img_path in msg.get("images", []):
            p = Path(img_path)
            if p.exists():
                st.image(str(p), use_container_width=True)


if prompt := st.chat_input("Posez votre question sur les données..."):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        spinner_msg = f"Analyse des données en cours..."
        with st.spinner(spinner_msg):
            result = run_agent_dispatch(prompt, st.session_state.agent_history)

        clean_text = strip_image_links(result["answer"])

        placeholder = st.empty()
        stream_text(placeholder, clean_text, delay=0.005)

        artifacts = result.get("artifacts", [])
        for img_path in artifacts:
            p = Path(img_path)
            if p.exists():
                st.image(str(p), use_container_width=True)
            else:
                st.warning(f"Image introuvable : {img_path}")

        if st.session_state.show_trace:
            with st.expander("🔍 Outils appelés", expanded=False):
                for msg in result["messages"]:
                    if isinstance(msg, dict):
                        if msg.get("role") == "assistant" and msg.get("tool_calls"):
                            for tc in msg["tool_calls"]:
                                st.code(
                                    f"{tc['function']['name']}({tc['function']['arguments']})",
                                    language="json",
                                )
                    else:
                        if getattr(msg, "tool_calls", None):
                            for tc in msg.tool_calls:
                                st.code(f"{tc['name']}({tc['args']})", language="json")

        #st.caption(f"⚡ Moteur : {st.session_state.engine} · Tours : {result['turns']}")

    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": clean_text,
        "images": artifacts,
    })
    st.session_state.agent_history = result["history"]