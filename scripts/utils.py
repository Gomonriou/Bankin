from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st
import subprocess
from scripts.get_datas import *
from dotenv import load_dotenv
import os
from scripts.logging_config import logger
import pandas as pd
import json

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
                periods = get_periods(int(st.session_state.conf_periods))
                requete_data(periods)
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

    try :
        with open("datas/data.json", "r", encoding="utf-8") as f:              
            data = json.load(f)
    except FileNotFoundError:
        st.warning("Fichier data.json introuvable — récupération des données...")
        periods = get_periods(int(st.session_state.conf_periods))
        requete_data(periods)
        st.session_state.df_final = load_data()
        st.rerun()

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

def get_accounts_button():
    if st.sidebar.button("Mettre à jour les comptes"):
        try:
            with st.spinner("MaJ des données en cours..."):
                requete_accounts()
            st.sidebar.success("Accounts mis à jour avec succès !")
            logger.info(f"Accounts mis à jour avec succès !")
        except Exception as e:
            st.sidebar.error(f"Accounts Erreur lors de la mise à jour : {e}")
            logger.info(f"Accounts Erreur lors de la mise à jour : {e} Show /LOGS")

    if "df_accounts_clean" not in st.session_state:
        st.session_state.df_accounts_clean = load_accounts()


def load_accounts():
    try :
        with open("datas/accounts.json", "r", encoding="utf-8") as f:
            accounts_data = json.load(f)
    except FileNotFoundError:
        st.warning("Fichier data.json introuvable — récupération des données...")
        requete_accounts()
        st.session_state.df_accounts_clean = load_accounts()
        st.rerun()

    df_accounts = pd.DataFrame(accounts_data["resources"])
    df_accounts_clean = df_accounts[["name", "classification", "balance", "last_refresh"]].copy()

    return df_accounts_clean
    


    