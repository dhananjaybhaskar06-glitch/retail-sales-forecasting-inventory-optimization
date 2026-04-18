import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Retail AI Dashboard", layout="wide")

# =========================
# SIMPLE LOGIN SYSTEM
# =========================
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("outputs/final_output.csv")
future = pd.read_csv("outputs/future_forecast.csv")

df['Date'] = pd.to_datetime(df['Date'])
future['Date'] = pd.to_datetime(future['Date'])

# =========================
# SIDEBAR NAVIGATION
# =========================
with st.sidebar:
    selected = option_menu(
        "Retail AI",
        ["Dashboard", "Forecast", "Inventory", "KPIs"],
        icons=["speedometer", "graph-up", "boxes", "cash-stack"]
    )

    st.markdown("---")
    store = st.selectbox("Store", df['Store'].unique())
    product = st.selectbox("Product", df['Product'].unique())

    date_range = st.date_input(
        "Date Range",
        [df['Date'].min(), df['Date'].max()]
    )

# =========================
# FILTER DATA
# =========================
filtered = df[
    (df['Store']==store) &
    (df['Product']==product) &
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1]))
]

future_filtered = future[
    (future['Store']==store) &
    (future['Product']==product)
]

# =========================
# DASHBOARD
# =========================
if selected == "Dashboard":
    st.title("📊 Retail Performance")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Sales", int(filtered['Sales'].sum()))
    col2.metric("Revenue", int(filtered['Revenue'].sum()))
    col3.metric("Profit", int(filtered['Profit'].sum()))
    col4.metric("Avg Sales", int(filtered['Sales'].mean()))

    fig = px.line(filtered, x='Date', y=['Sales','Predicted'],
                  title="Sales vs Forecast", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# FORECAST
# =========================
elif selected == "Forecast":
    st.title("📈 Future Forecast")

    fig = px.line(future_filtered, x='Date', y='Predicted',
                  title="Next 7 Days", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Download Forecast CSV",
        future_filtered.to_csv(index=False),
        file_name="forecast.csv"
    )

# =========================
# INVENTORY
# =========================
elif selected == "Inventory":
    st.title("📦 Inventory Insights")

    fig = px.scatter(filtered, x='Sales', y='Reorder_Point',
                     color='Inventory_Status',
                     title="Inventory Health")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(filtered.tail(20))

# =========================
# KPIs
# =========================
elif selected == "KPIs":
    st.title("💰 Business KPIs")

    col1, col2 = st.columns(2)

    col1.metric("Total Revenue", int(filtered['Revenue'].sum()))
    col2.metric("Total Profit", int(filtered['Profit'].sum()))

    fig = px.histogram(filtered, x="Sales", nbins=25,
                       title="Sales Distribution")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚠️ Anomalies")
    st.dataframe(filtered[filtered['Anomaly']=="YES"])

# =========================
# LOGOUT BUTTON
# =========================
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.experimental_rerun()