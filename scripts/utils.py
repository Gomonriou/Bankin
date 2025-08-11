from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import subprocess
from scripts.get_datas import *
from dotenv import load_dotenv
import os

load_dotenv()
client_id = os.environ["client_id"]
client_secret = os.environ["client_secret"]
Bankin_Device = os.environ["Bankin_Device"]
email = os.environ["email"]
password = os.environ["password"]
conf_file = 'datas/data.json'
conf_periods = os.environ["periods"]

def aggrid_interactive_table(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, filter=True, sortable=True)
    gridOptions = gb.build()
    AgGrid(
        df,
        gridOptions=gridOptions,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
    )

def init_page():
    st.set_page_config(layout="wide")
    export_button()
    get_datas_button()

def export_button():
    if st.sidebar.button("Exporter les données"):
        result = subprocess.run(["python", "scripts/export.py"], capture_output=True, text=True)
        if result.returncode == 0:
            st.sidebar.success("Export terminé avec succès ! Vous pouvez ouvrir le fichier datas/output.csv dans Excel.")
        else:
            st.sidebar.error(f"Erreur lors de l’export :\n{result.stderr}")


def get_datas_button():
    if st.sidebar.button("Mettre à jour les données"):
        try:
            with st.spinner("MaJ des données en cours..."):
                bearer = "Bearer " + get_bearer(client_id, client_secret, Bankin_Device, email, password)
                periods = get_periods(int(conf_periods))
                requete_data(bearer, client_id, client_secret, periods)
            st.sidebar.success("Données mises à jour avec succès !")
        except Exception as e:
            st.sidebar.error(f"Erreur lors de la mise à jour : {e}")