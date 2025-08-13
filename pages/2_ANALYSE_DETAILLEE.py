import streamlit as st
from scripts.utils import *
import plotly.graph_objects as go
import plotly.express as px
from scripts.logging_config import logger

init_page()

## FILTERS
# --- Filtre time range ---
all_months = sorted(st.session_state.df_final["year_month"].unique())

st.sidebar.header("Filtres :")
st.session_state.date_range = st.sidebar.select_slider(
    "Time range",
    options=all_months,
    value=st.session_state.date_range
)

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

df_autre = filtered_df[filtered_df["Account ID"] == account_choisi]

# --- Filtre par catégorie perso ---
categorie_perso_options = df_autre["Categorie perso"].dropna().unique().tolist()
default_index = categorie_perso_options.index("Restes") if "Restes" in categorie_perso_options else 0

categorie_perso_choisie = st.sidebar.selectbox(
    "Catégorie perso",
    options=categorie_perso_options,
    index=default_index,
)

df_autre = df_autre[df_autre["Categorie perso"] == categorie_perso_choisie]

# --- Filtre par catégorie parente ---
all_categories = df_autre["Categorie Parente"].dropna().unique().tolist()
with st.sidebar.expander("Catégories parentes"):
    selected_categories = []
    for cat in all_categories:
        if st.checkbox(cat, value=True):
            selected_categories.append(cat)

df_autre = df_autre[df_autre["Categorie Parente"].isin(selected_categories)]


# --- Filtre par catégorie ---
all_achats = df_autre["Categorie"].dropna().unique().tolist()
with st.sidebar.expander("Catégories"):
    selected_categories = []
    for cat in all_achats:
        if st.checkbox(cat, value=True):
            selected_categories.append(cat)

df_autre = df_autre[df_autre["Categorie"].isin(selected_categories)]

################################################################# DISPLAY
st.title("ANALAYSE DETAILLEE")

### Tables
aggrid_interactive_table(df_autre)

### PIE + TOTAL
col1, col2 = st.columns([1, 3])  

with col1:
    total_montant = df_autre["Montant"].abs().sum()
    nb_transactions = len(df_autre)
    st.metric(label="Total", value=f"{total_montant:,.2f} €")
    st.metric(label="Transactions", value=nb_transactions)

with col2:
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
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

### Graphs2
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
    title="",
    xaxis_title="Mois",
    yaxis_title="Montant (€)",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
