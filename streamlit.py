import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")
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

########################################################################################################### DATAFRAME
## DATAFRAME CATEGORIES
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

## DATAFRAME TRANSACTIONS
with open("datas/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data["resources"])
df["category_id"] = df["category"].apply(lambda x: x["id"] if isinstance(x, dict) else None)
df["date"] = pd.to_datetime(df["date"])
df["year_month"] = df["date"].dt.to_period("M").astype(str)

df_clean = df[[
    "year_month",
    "description",
    "amount",
    "category_id",
]].copy()

## DATAFRAMES MERGES
df_final = df_clean.merge(df_categories, on="category_id", how="left")

df_final.rename(columns={
    "date": "Date",
    "description": "Description",
    "amount": "Montant",
    "category_id": "Categorie id",
    "category_name": "Categorie",
    "parent_category": "Categorie Parente"
}, inplace=True)


depenses_fixes = ["Notes de frais", "Téléphonie mobile", "Mutuelle", "Sport", "Dépenses pro - Autres", "Coiffeur"]
a_ignorer = ["Remboursement emprunt","Virements internes", "Autres rentrées"]
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


########################################################################################################### FILTRE
## FILTRE DATE
all_months = sorted(df_final["year_month"].unique())
# month_min, month_max = all_months[0], all_months[-1]

default_end = all_months[-1]
default_start = all_months[-3] if len(all_months) >= 3 else all_months[0]

st.sidebar.header("Filtrer par mois")
selected_range = st.sidebar.select_slider(
    "Choisir une période",
    options=all_months,
    value=(default_end, default_start),
)

start, end = selected_range
filtered_df = df_final[(df_final["year_month"] >= start) & (df_final["year_month"] <= end)]



########################################################################################################### AFFICHAGE
## Tabs
st.title("Analyse de mes transactions")
st.subheader(f"Données de {start} à {end}")
aggrid_interactive_table(filtered_df)

## Graphs
df_filtered_graph = filtered_df[filtered_df["Categorie perso"].isin(["Dépense fixe", "Restes"])]

df_graph = (
    df_filtered_graph
    .groupby(["year_month", "Categorie perso"])["Montant"]
    .sum()
    .abs()  # montants en positif
    .reset_index()
)

df_pivot = df_graph.pivot(index="year_month", columns="Categorie perso", values="Montant").fillna(0)
df_pivot["Total"] = df_pivot["Dépense fixe"] + df_pivot["Restes"]
df_pivot = df_pivot[["Dépense fixe", "Restes", "Total"]]

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot["Dépense fixe"], mode='lines+markers', name='Dépense fixe'))
fig.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot["Restes"], mode='lines+markers', name='Restes'))
fig.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot["Total"], mode='lines+markers', name='Total'))
fig.update_layout(
    title="Dépenses mensuelles (interactif)",
    xaxis_title="Mois",
    yaxis_title="Montant (€)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

## Pie
st.title("Analyse en detail")

categorie_perso_options = df_final["Categorie perso"].dropna().unique().tolist()
default_index = categorie_perso_options.index("Restes") if "Restes" in categorie_perso_options else 0

categorie_perso_choisie = st.selectbox(
    "Choisir une catégorie perso à analyser",
    options=categorie_perso_options,
    index=default_index,
)

st.subheader(f"Analyse detaillée de {categorie_perso_choisie}")



df_autre = filtered_df[filtered_df["Categorie perso"] == categorie_perso_choisie]

df_pie = (
    df_autre
    .groupby("Categorie Parente")["Montant"]
    .sum()
    .abs() 
    .reset_index()
)

fig_pie = px.pie(
    df_pie,
    names="Categorie Parente",
    values="Montant",
    hole=0.4  # pour un effet donut (optionnel)
)

st.plotly_chart(fig_pie, use_container_width=True)

## Graphs2
df_graph2 = (
    df_autre
    .groupby(["year_month", "Categorie Parente"])["Montant"]
    .sum()
    .abs() 
    .reset_index()
)
df_pivot = df_graph2.pivot(index="year_month", columns="Categorie Parente", values="Montant").fillna(0)
fig = go.Figure()

for col in df_pivot.columns:
    fig.add_trace(go.Scatter(
        x=df_pivot.index,
        y=df_pivot[col],
        mode='lines+markers',
        name=col
    ))

fig.update_layout(
    title=f"Évolution mensuelle – {categorie_perso_choisie} par catégorie parente",
    xaxis_title="Mois",
    yaxis_title="Montant (€)",
    hovermode="x unified"
)

st.subheader(f"Évolution dans le temps par catégorie parente – {categorie_perso_choisie}")
st.plotly_chart(fig, use_container_width=True)


aggrid_interactive_table(df_autre)
