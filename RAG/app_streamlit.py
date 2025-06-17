import os
import sys
import zipfile
import streamlit as st

# Ensure the RAG module is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from RAG.app import get_answer


def decompress_if_needed():
    """Décompresse chroma_db.zip dans chroma_db si besoin."""
    if not os.path.exists("chroma_db") and os.path.exists("chroma_db.zip"):
        with st.spinner("Décompression de la base vectorielle..."):
            with zipfile.ZipFile("chroma_db.zip", "r") as zip_ref:
                zip_ref.extractall("chroma_db")
        st.success("Base vectorielle décompressée.")


def app_streamlit():
    """
        Build the RAG application with Streamlit. 
    """
    st.set_page_config(page_title="Pokémon RAG", page_icon="🧠", layout="wide")
    
    decompress_if_needed()

    #CSS of the application
    st.markdown("""
    <style>
        .stApp {
            padding-top: 0px;
        }
        header {
            visibility: hidden;
            height: 0px !important;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem; 
            padding-left: 4rem; 
            padding-right: 4rem;
        }
        h1 {
            font-family: 'Tahoma', sans-serif !important;
            font-weight: 750; 
            margin-top: 1rem; 
            margin-bottom: 1rem;
        }
        h1 span {
            color: #e93a14;
        }
        .stMarkdown div {
            font-size: 1em; 
            line-height: 1.5;
            color: #4A4A4A;
            font-family: 'Tahoma', sans-serif !important;
        }
        .st-chat-message-user, .st-chat-message-assistant {
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            max-width: 90%; 
            background-color: #4A4A4A;
        }
    </style>
    """, unsafe_allow_html=True)

    # Titre
    st.markdown(
        "<h1 style='text-align: center; white-space: nowrap; font-size: 48px;'>"
        "<span style='color:#e93a14;'>Poké</span>Savant</h1>",
        unsafe_allow_html=True,
    )

    # Images Pokémon
    top_pokemon_urls = [
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/001.png",  # Bulbizarre
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/050.png",  # Taupiqueur
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/054.png",  # Psykokwak
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/016.png",  # Roucool
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/007.png",  # Carapuce
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/004.png",  # Salamèche
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/025.png",  # Pikachu
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/133.png",  # Evoli
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/129.png",  # Poissirène
        "https://assets.pokemon.com/assets/cms2/img/pokedex/full/043.png",  # Mystherbe
    ]

    st.markdown("""
    <style>
        .poke-hover {
            transition: transform 0.3s ease;
        }
        .poke-hover:hover {
            transform: scale(1.2);
        }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(top_pokemon_urls))
    for i, url in enumerate(top_pokemon_urls):
        with cols[i]:
            st.markdown(
                f"<img src='{url}' width='80' class='poke-hover'/>",
                unsafe_allow_html=True
            )

    # Description of the application
    st.markdown(
        "<div style='text-align:center; margin-bottom: 25px;'>"
        "Bienvenue sur <strong>PokéSavant</strong>, votre assistant intelligent qui connaît l'univers des <strong>Pokémon</strong>! Posez lui une question sur les Pokémon de la première et/ou de la seconde génération (selon les données contenues en base) et l'assistant vous répondra s'il connaît la réponse."
        "</div>",
        unsafe_allow_html=True,
    )


    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    chat_container = st.container(height=350, border=True)
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input for user question
    prompt = st.chat_input("Quel est le type de Salamèche ?")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display a spinner while waiting for the response
        with st.spinner("Recherche en cours..."):
            try:
                response = get_answer(prompt)
            except Exception as e:
                response = f"Désolé, une erreur est survenue : {e}"

        # Display the assistant's response
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.divider()
        st.rerun()


if __name__ == "__main__":
    app_streamlit()
