import streamlit as st
from scripts.utils import *

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

