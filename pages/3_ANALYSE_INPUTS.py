import streamlit as st
from scripts.utils import *
import plotly.graph_objects as go


## DF
if "df_accounts_clean" not in st.session_state:
    st.session_state.df_accounts_clean = load_accounts()
    logger.info(f"Accounts load")

get_accounts_button()

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


all_accounts = filtered_df["Account ID"].dropna().unique().tolist()
all_accounts_str = [str(a) for a in all_accounts]
with st.sidebar.expander("Account ID"):
    selected_account = []
    for accounts in all_accounts_str:
        if st.checkbox(accounts, value=True):
            selected_account.append(accounts)

filtered_df = filtered_df[filtered_df["Account ID"].astype(str).isin(selected_account)]


st.title("ANALAYSE INPUTS")

### Tables

st.write(st.session_state.df_accounts_clean)
aggrid_interactive_table(filtered_df)


total_montant = filtered_df["Montant"].sum()
nb_transactions = len(filtered_df)
st.metric(label="Total", value=f"{total_montant:,.2f} €")
st.metric(label="Transactions", value=nb_transactions)


### Graphs
df_graph = (
    filtered_df
    .groupby(["year_month", "Account ID"])["Montant"]
    .sum()
    .reset_index()
)
df_pivot = df_graph.pivot(index="year_month", columns="Account ID", values="Montant").fillna(0)

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
