import streamlit as st
from scripts.utils import *

init_page()

# AFFICHER LES LOGS LE PLUS RECENT EN HAUT
with open("logs/app.log", "r") as f:
    lines = f.readlines()
    lines.reverse()
    st.text("".join(lines))
