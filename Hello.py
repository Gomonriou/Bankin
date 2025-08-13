import streamlit as st
from scripts.utils import *
from dotenv import load_dotenv

load_dotenv()
st.session_state.depenses_fixes = os.environ["depenses_fixes"]
st.session_state.entrees = os.environ["entrees"]
st.session_state.a_ignorer = os.environ["a_ignorer"]
st.session_state.default_account = int(os.environ["default_account"])

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# HI ! READ ME 👋")

with st.spinner("Chargement des données en cours..."):
    if "df_final" not in st.session_state:
        st.session_state.df_final = load_data()
        logger.info(f"Datas load")
        st.success(f"Hi! App just started, Datas just loaded")

with open("Readme.md", "r", encoding="utf-8") as f:
    content = f.read()
st.markdown(content)

st.header("⚙️ Paramètres actuels :")

st.markdown(f"""
            <h3> Configuration des catégories persos :</h3>  

            <b> :red[Dépenses fixes :]</b> {st.session_state.depenses_fixes}  
            <b> :red[Entrées :]</b> {st.session_state.entrees}  
            <b> :red[À ignorer :]</b> {st.session_state.a_ignorer}  
            

            <h3> Configuration des catégories persos :</h3> 

            <b> :red[Compte par défaut sélectionné :]</b> {st.session_state.default_account}  
            """,unsafe_allow_html=True
)