from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import subprocess
from scripts.get_datas import *
from dotenv import load_dotenv
import os
from scripts.logging_config import logger
import pandas as pd
import json

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
    load_data()
    st.set_page_config(layout="wide")
    export_button()
    get_datas_button()

def export_button():
    if st.sidebar.button("Exporter les données"):
        result = subprocess.run(["python", "scripts/export.py"], capture_output=True, text=True)
        if result.returncode == 0:
            st.sidebar.success("Export terminé avec succès ! Vous pouvez ouvrir le fichier datas/output.csv dans Excel.")
            logger.info("Export terminé")
        else:
            st.sidebar.error(f"Erreur lors de l’export :\n{result.stderr}")
            logger.info(f"Erreur lors de l’export :\n{result.stderr} Show /LOGS")


def get_datas_button():
    if st.sidebar.button("Mettre à jour les données"):
        try:
            with st.spinner("MaJ des données en cours..."):
                bearer = "Bearer " + get_bearer(client_id, client_secret, Bankin_Device, email, password)
                periods = get_periods(int(conf_periods))
                requete_data(bearer, client_id, client_secret, periods)
            st.sidebar.success("Données mises à jour avec succès !")
            logger.info(f"Données mises à jour avec succès !")
        except Exception as e:
            st.sidebar.error(f"Erreur lors de la mise à jour : {e}")
            logger.info(f"Erreur lors de la mise à jour : {e} Show /LOGS")

    if "df_final" not in st.session_state:
        st.session_state.df_final = load_data()
        
# CREATE DF
def load_data():
    with open("datas/id.json", "r", encoding="utf-8") as f:
        category_data = json.load(f)

    rows = []
    for parent in category_data["resources"]:
        parent_name = parent["name"]
        for cat in parent["categories"]:
            rows.append({
                "category_id": cat["id"],
                "category_name": cat["name"],
                "parent_category": parent_name
            })
    df_categories = pd.DataFrame(rows)

    with open("datas/data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data["resources"])
    df["category_id"] = df["category"].apply(lambda x: x["id"] if isinstance(x, dict) else None)
    df["account_id"] = df["account"].apply(lambda x: x["id"] if isinstance(x, dict) else None)
    df["date"] = pd.to_datetime(df["date"])
    df["year_month"] = df["date"].dt.to_period("M").astype(str)

    df_clean = df[["year_month", "description", "amount", "category_id", "account_id"]].copy()
    df_final = df_clean.merge(df_categories, on="category_id", how="left")

    df_final.rename(columns={
        "date": "Date",
        "description": "Description",
        "amount": "Montant",
        "category_id": "Categorie id",
        "category_name": "Categorie",
        "parent_category": "Categorie Parente",
        "account_id": "Account ID"
    }, inplace=True)

    # depenses_fixes = ["Notes de frais", "Téléphonie mobile", "Mutuelle", "Sport", "Dépenses pro - Autres", "Coiffeur"]
    # a_ignorer = ["Remboursement emprunt", "Virements internes", "Autres rentrées"]
    # entrees = ["Salaires"]

    def mapper_categorie_perso(nom_categorie):
        if nom_categorie in st.session_state.depenses_fixes:
            return "Dépense fixe"
        elif nom_categorie in st.session_state.a_ignorer:
            return "Ignore"
        elif nom_categorie in st.session_state.entrees:
            return "Entrées"
        else:
            return "Restes"

    df_final["Categorie perso"] = df_final["Categorie"].apply(mapper_categorie_perso)
    return df_final