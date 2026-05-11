import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import numpy as np

def get_data(query):
    conn = sqlite3.connect('apple_apps.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="AppStore Insights", layout="wide")
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

# Balken statt Torte für bessere Übersicht
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

# --- MODULE 5: APP-SUCHE (Erweitert & Sortiert) ---
st.divider()
st.subheader("🔍 Spezifische App-Details")

# Das Eingabefeld in der Sidebar
search_query = st.sidebar.text_input("App-Namen suchen", key="search_input")

if search_query:
    # 1. Suche im aktuellen DataFrame
    raw_search_df = df[df['App_Name'].str.contains(search_query, case=False, na=False)]
    
    if not raw_search_df.empty:
        # NEU: Wir sortieren die Suchergebnisse nach Reviews (absteigend)
        # So landet die populärste App (z.B. YouTube) immer auf Platz 1
        search_df = raw_search_df.sort_values(by='Reviews', ascending=False)
        
        # Detail-Ansicht für den populärsten Treffer
        target_app = search_df.iloc[0]
        st.markdown(f"### Top-Treffer (nach Popularität): {target_app['App_Name']}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Genre", target_app['Primary_Genre'])
        c2.metric("Rating", f"{target_app['Average_User_Rating']} ⭐")
        c3.metric("Größe", f"{target_app['Size_MB']:.1f} MB")
        c4.metric("Reviews", f"{int(target_app['Reviews']):,}") # Zeigt Beliebtheit statt Preis
        
        # 2. Liste aller weiteren Treffer
        if len(search_df) > 1:
            st.write(f"---")
            st.write(f"Alle gefundenen Treffer ({len(search_df)}), sortiert nach Reviews:")
            st.dataframe(
                search_df[['App_Name', 'Reviews', 'Primary_Genre', 'Size_MB', 'Average_User_Rating']], 
                use_container_width=True
            )
    else:
        st.error(f"Keine App gefunden, die '{search_query}' enthält.")


# --- MODULE 6: HIDDEN GEMS (Geheimtipps - Unabhängig vom Hauptfilter) ---
st.divider()
st.subheader("💎 Echte Geheimtipps")
st.write("Apps mit perfektem Rating, die noch nicht jeder kennt (unabhängig von den obigen Filtern).")

# Wir machen eine eigene kleine Abfrage für die Geheimtipps
gem_query = """
SELECT App_Name, Reviews, Average_User_Rating, Primary_Genre 
FROM apps 
WHERE Average_User_Rating = 5.0 
AND Reviews BETWEEN 500 AND 10000
ORDER BY Reviews DESC
LIMIT 10
"""
hidden_gems_df = get_data(gem_query)

if not hidden_gems_df.empty:
    st.table(hidden_gems_df[['App_Name', 'Reviews', 'Primary_Genre']])
    st.success(f"Diese Apps haben eine perfekte Bewertung, sind aber noch echte Entdeckungen.")
else:
    st.info("Momentan keine Apps mit exakt diesen Kriterien in der Datenbank.")


# --- MODULE 7: ML PROGNOSE (Entkoppelt vom Hauptfilter) ---
st.divider()
st.subheader("🤖 Professionelle Rating-Prognose")
st.write("Dieses Modell lernt aus dem *gesamten* Datensatz, um Trends objektiv vorherzusagen.")

# 1. Daten entkoppelt abfragen
# Wir holen uns alle Apps, um die volle Varianz des Marktes zu haben
@st.cache_data # Damit wir nicht bei jedem Klick die ganze DB laden
def get_ml_base_data():
    query_all = "SELECT Price, Size_MB, Average_User_Rating FROM apps"
    return get_data(query_all).dropna()

full_ml_data = get_ml_base_data()

if not full_ml_data.empty:
    # Benutzereingaben
    c_ml1, c_ml2 = st.columns(2)
    u_price = c_ml1.number_input("Dein Preis (€)", 0.0, 50.0, 0.0, step=0.99, key="ml_p_final")
    u_size = c_ml2.number_input("Deine Größe (MB)", 1.0, 3000.0, 150.0, step=10.0, key="ml_s_final")

    if st.button("Rating auf Basis des Gesamtmarkts berechnen"):
        # Pipeline Aufbau
        model_pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', LinearRegression())
        ])
        
        # Training auf dem VOLLSTÄNDIGEN Datensatz
        X_train = full_ml_data[['Price', 'Size_MB']]
        y_train = full_ml_data['Average_User_Rating']
        model_pipe.fit(X_train, y_train)
        
        # Vorhersage
        X_new = pd.DataFrame([[u_price, u_size]], columns=['Price', 'Size_MB'])
        prediction = model_pipe.predict(X_new)[0]
        
        # Clipping (0-5 Sterne)
        final_rating = max(0.0, min(5.0, prediction))
        
        st.write("---")
        st.metric("Prognostiziertes Rating", f"{final_rating:.2f} ⭐")
        
        # Analyse der Koeffizienten (Was hat das Modell gelernt?)
        coeffs = model_pipe.named_steps['regressor'].coef_
        st.write("**Statistischer Trend im Gesamtmarkt:**")
        
        # Erklärung der Trends
        p_trend = "sinkt" if coeffs[0] < 0 else "steigt"
        s_trend = "sinkt" if coeffs[1] < 0 else "steigt"
        
        st.write(f"* Mit höherem **Preis** {p_trend} das erwartete Rating tendenziell.")
        st.write(f"* Mit zunehmender **Größe** {s_trend} das erwartete Rating tendenziell.")
else:
    st.error("Datenbank konnte für das ML-Modell nicht geladen werden.")

# --- MODULE 8: MARKT-SEGMENTIERUNG (Boxplot) ---
st.divider()
st.subheader("📊 Qualitäts-Check pro Genre")
st.write("Wie stabil sind die Bewertungen in den verschiedenen Kategorien?")

# Wir nehmen die Top 10 Genres nach Anzahl der Apps, damit es übersichtlich bleibt
top_genres = df['Primary_Genre'].value_counts().nlargest(10).index
filtered_df = df[df['Primary_Genre'].isin(top_genres)]

fig_box = px.box(
    filtered_df, 
    x='Primary_Genre', 
    y='Average_User_Rating',
    color='Primary_Genre',
    title="Rating-Verteilung der Top 10 Genres",
    points="outliers" # Zeigt uns die besonders schlechten/guten Apps
)

st.plotly_chart(fig_box, use_container_width=True)

st.info("""
**Interpretationshilfe:** - Die Box zeigt, wo die mittleren 50% der Apps liegen. 
- Ein kurzer Kasten bedeutet: Die Nutzer sind sich einig. 
- Viele Punkte außerhalb (Outliers) bedeuten: Es gibt in diesem Genre extreme Qualitätsunterschiede.
""")