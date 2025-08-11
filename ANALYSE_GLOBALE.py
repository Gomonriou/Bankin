import streamlit as st
import pandas as pd
import json
from scripts.utils import *
import plotly.graph_objects as go
import plotly.express as px

init_page()

# CREATE DF
if "df_final" not in st.session_state:
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

    depenses_fixes = ["Notes de frais", "Téléphonie mobile", "Mutuelle", "Sport", "Dépenses pro - Autres", "Coiffeur"]
    a_ignorer = ["Remboursement emprunt", "Virements internes", "Autres rentrées"]
    entrees = ["Salaires"]

    def mapper_categorie_perso(nom_categorie):
        if nom_categorie in depenses_fixes:
            return "Dépense fixe"
        elif nom_categorie in a_ignorer:
            return "Ignore"
        elif nom_categorie in entrees:
            return "Entrées"
        else:
            return "Restes"

    df_final["Categorie perso"] = df_final["Categorie"].apply(mapper_categorie_perso)

    st.session_state.df_final = df_final

all_months = sorted(st.session_state.df_final["year_month"].unique())
default_end = all_months[-1]
default_start = all_months[-3] if len(all_months) >= 3 else all_months[0]

if "date_range" not in st.session_state:
    st.session_state.date_range = (default_start, default_end)

st.sidebar.header("Filtres :")
st.session_state.date_range = st.sidebar.select_slider(
    "",
    options=all_months,
    value=st.session_state.date_range
)

# Données filtrées
start, end = st.session_state.date_range
filtered_df = st.session_state.df_final[
    (st.session_state.df_final["year_month"] >= start) &
    (st.session_state.df_final["year_month"] <= end)
]

# --- Filtre par account_id ---
all_accounts = filtered_df["Account ID"].dropna().unique().tolist()
account_choisi = st.sidebar.selectbox(
    "Compte",
    options=all_accounts,
    index=0 if all_accounts else None
)

filtered_df = filtered_df[filtered_df["Account ID"] == account_choisi]

################################################################# DISPLAY
### Tables
st.title("Page générale")
aggrid_interactive_table(filtered_df)

total_montant = filtered_df["Montant"].abs().sum()
nb_transactions = len(filtered_df)
st.metric(label="Total", value=f"{total_montant:,.2f} €")
st.metric(label="Transactions", value=nb_transactions)

df_filtered_graph = filtered_df[filtered_df["Categorie perso"].isin(["Dépense fixe", "Restes"])]

df_graph = (
    df_filtered_graph
    .groupby(["year_month", "Categorie perso"])["Montant"]
    .sum()
    .abs()
    .reset_index()
)

df_pivot = df_graph.pivot(index="year_month", columns="Categorie perso", values="Montant").fillna(0)

if {"Dépense fixe", "Restes"}.issubset(df_pivot.columns):
    df_pivot["Total"] = df_pivot["Dépense fixe"] + df_pivot["Restes"]
    df_pivot = df_pivot[["Dépense fixe", "Restes", "Total"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot["Dépense fixe"], mode='lines+markers', name='Dépense fixe'))
    fig.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot["Restes"], mode='lines+markers', name='Restes'))
    fig.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot["Total"], mode='lines+markers', name='Total'))
    fig.update_layout(
        xaxis_title="Mois",
        yaxis_title="Montant (€)",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Graphique non disponible : données insuffisantes pour 'Dépense fixe' et 'Restes'.")
