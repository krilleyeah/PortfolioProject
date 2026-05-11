import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

def get_data(query):
    conn = sqlite3.connect('apple_apps.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Chris' App Insights", layout="wide")
st.title("App Store Analytics Dashboard")

# --- SIDEBAR ---
st.sidebar.header("Filter & Steuerung")
min_rating = st.sidebar.slider("Mindest-Rating", 0.0, 5.0, 4.0)
min_reviews = st.sidebar.number_input("Mindestanzahl Reviews", 0, 1000000, 1000)

# --- DATEN HOLEN ---
query = f"""
SELECT App_Name, Average_User_Rating, Reviews, Price, Size_MB, Primary_Genre 
FROM apps 
WHERE Average_User_Rating >= {min_rating} AND Reviews >= {min_reviews}
"""
df = get_data(query)
df['Size_MB'] = pd.to_numeric(df['Size_MB'], errors='coerce').fillna(0)
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce').fillna(0)

# --- MODULE 1: METRIKEN ---
col1, col2, col3 = st.columns(3)
col1.metric("Apps im Fokus", len(df))
col2.metric("Ø Rating", f"{df['Average_User_Rating'].mean():.2f}")
col3.metric("Ø Preis", f"{df['Price'].mean():.2f} €")

# --- MODULE 2: DER CLUSTER (SCATTER) ---
st.subheader("Markt-Übersicht: Rating vs. Popularität")
fig_scatter = px.scatter(
    df, x="Reviews", y="Average_User_Rating", 
    size="Size_MB", color="Primary_Genre",
    hover_name="App_Name", log_x=True,
    template="plotly_dark", size_max=30
)
st.plotly_chart(fig_scatter, use_container_width=True)

# --- MODULE 3: DIE TRUE GIANTS (Top Apps nach Reviews) ---
st.subheader("🏆 Die True Giants (Meistbewertet)")
top_apps = df.nlargest(10, 'Reviews')[['App_Name', 'Reviews', 'Average_User_Rating']]
st.table(top_apps)

# --- MODULE 4: GENRE VERTEILUNG (BALKENDIAGRAMM STATT PIE) ---
st.subheader("📊 Genre-Verteilung")
genre_counts = df['Primary_Genre'].value_counts().reset_index()
genre_counts.columns = ['Genre', 'Anzahl']

# Hier ist die Änderung: Balken statt Torte für bessere Übersicht
fig_bar = px.bar(
    genre_counts.head(15), 
    x='Anzahl', 
    y='Genre', 
    orientation='h',
    color='Anzahl',
    color_continuous_scale='Viridis',
    template="plotly_dark"
)
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar, use_container_width=True)

st.info("💡 Alle Daten werden live aus der SQL-Datenbank gefiltert.")