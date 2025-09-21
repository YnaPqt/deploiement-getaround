
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt



# Page setup
st.set_page_config(
    page_title="GetAround Rental Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

#PAGE SET UP

# Side bar 
st.sidebar.markdown("<h2 style='font-size: 24px;'>📋 Main </h2>", unsafe_allow_html=True)
page = st.sidebar.radio("", options=["Home", "Rental Overview","Price Prediction"])



# --- Header ---

def screen_Home():

    st.title("🚗 Welcome to the Getaround Dashboard")
    st.image(
        "https://d1011j0lbv5k1u.cloudfront.net/assets/store-430338/430338-logo-1571068302.jpg"
    )
    st.subheader("Explore the world of peer-to-peer car rentals")
    st.markdown("""
Getaround is planning to **hide cars from search results** if they are **too close to another rental**.

This helps prevent issues like **late returns**, but might reduce availability and owner revenue.

### 🔍 Use this Dashboard to:
- Analyze how **thresholds** and **check-in types** affect:
    - 🚨 Revenue risk
    - ⛔ Rentals that get blocked
    - ✅ Conflicts that are resolved
- Visualize real rental patterns by check-in type and delay severity
""")


#######################################################################################################################""
# --- Data Loader ---
@st.cache_data
def load_data():
    df = pd.read_excel(
        r"https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx", 
        sheet_name="rentals_data"
    )
    df = df.dropna(subset=['car_id', 'checkin_type'])
    df = df[df['state'] == 'ended']

    df['delay_at_checkout_in_minutes'] = df['delay_at_checkout_in_minutes'].fillna(0)
    df['time_delta_with_previous_rental_in_minutes'] = df['time_delta_with_previous_rental_in_minutes'].fillna(np.inf)
    df['previous_delay'] = df['delay_at_checkout_in_minutes'].shift(1).fillna(0)

    return df


df_full = load_data()

###############################################################################""
def screen_RentalOverview():
    st.title("Rental Overview")
    # --- Sidebar Filters ---
    st.sidebar.title("🔧 Filters")
    thresholds = [10, 20, 40, 60, 80, 100, 120, 140]
    selected_checkin = st.sidebar.selectbox("🔄 Check-in Type", ["All", "mobile", "connect"])
    selected_threshold = st.sidebar.selectbox("⏳ Minimum Delay Threshold (minutes)", thresholds)

    # --- Filter Data ---
    df = df_full if selected_checkin == "All" else df_full[df_full["checkin_type"] == selected_checkin]
    df = df.copy()

    # --- Revenue Risk Logic ---
    df['revenue_risk'] = (
        (df['previous_delay'] > df['time_delta_with_previous_rental_in_minutes']) &
        (df['time_delta_with_previous_rental_in_minutes'] < selected_threshold)
    )

    # Metrics
    total_rentals = len(df)
    blocked_df = df[df['time_delta_with_previous_rental_in_minutes'] < selected_threshold]
    solved_cases_df = blocked_df[blocked_df["revenue_risk"]]

    blocked_count = len(blocked_df)
    solved_count = len(solved_cases_df)
    revenue_risk_pct = (blocked_count / total_rentals * 100) if total_rentals > 0 else 0

    # --- Compute Delta ---
    prev_idx = thresholds.index(selected_threshold) - 1
    if prev_idx >= 0:
        prev_thresh = thresholds[prev_idx]
        prev_blocked = (df['time_delta_with_previous_rental_in_minutes'] < prev_thresh).sum()
        revenue_risk_delta = revenue_risk_pct - (prev_blocked / total_rentals * 100)
    else:
        revenue_risk_delta = 0

    # --- KPIs ---
    st.subheader("📊 Key Metrics")
    st.metric("🚫 Revenue Risk (% of Rentals Blocked)", f"{revenue_risk_pct:.2f}%", f"{revenue_risk_delta:+.2f}%", delta_color="inverse")
    st.metric("⛔ Blocked Rentals", blocked_count)
    st.metric("✅ Solved Cases", solved_count)

    # --- Pie Chart Section ---
    st.subheader(f"📉 Impact for Threshold = {selected_threshold} min & {selected_checkin}")
    not_blocked_count = total_rentals - blocked_count
    total_revenue_risk_cases = ((df['previous_delay'] > df['time_delta_with_previous_rental_in_minutes'])).sum()
    unsolved_count = total_revenue_risk_cases - solved_count

    fig_pies = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]])
    fig_pies.add_trace(go.Pie(labels=["Blocked", "Not Blocked"], values=[blocked_count, not_blocked_count], hole=0.4), 1, 1)
    fig_pies.add_trace(go.Pie(labels=["Solved Cases", "Remaining Risk"], values=[solved_count, unsolved_count], hole=0.4), 1, 2)
    fig_pies.update_layout(title_text="📊 Blocked Rentals & Risk Solved", paper_bgcolor="gray")
    st.plotly_chart(fig_pies, use_container_width=True)

    # --- Line Plot ---
    def compute_metrics(df, thresholds):
        results = []
        for t in thresholds:
            risky = (
                (df['previous_delay'] > df['time_delta_with_previous_rental_in_minutes']) &
                (df['time_delta_with_previous_rental_in_minutes'] < t)
            ).sum()
            pct = (risky / len(df) * 100) if len(df) > 0 else 0
            results.append({"Threshold": t, "Revenue Risk %": pct})
        return pd.DataFrame(results)

    metrics_curve_df = compute_metrics(df, thresholds)
    fig_curve = px.line(metrics_curve_df, x="Threshold", y="Revenue Risk %", markers=True, title="📈 Revenue Risk")
    fig_curve.update_layout(paper_bgcolor="gray", plot_bgcolor="gray")
    st.plotly_chart(fig_curve)

##################################################################################################

#Price Prediction 
def get_price_prediction(features: dict):
    # API function
    API_URL = "https://yona-p-getaround-api.hf.space/predict"
    try:
        response = requests.post(API_URL, json=features)
        response.raise_for_status()
        return response.json().get("prediction")
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def screen_PricePrediction(): 
    #st.set_page_config(
    #page_title="Getaround Rental Delay Dashboard",
    #layout="wide",
    #page_icon="🚗"
    #)
    st.title("💸 Price Prediction")
    st.markdown("---")
    st.markdown("""
    <p style="font-size:20px;">
    Use this form to enter car features and get a predicted rental price.
    </p>
    """, unsafe_allow_html=True)

    with st.form("price_form"):
        st.subheader("Car Features")
        col1, col2 = st.columns(2)
        with col1:
            model_key = st.selectbox("Model",[""] + ['Audi', 'BMW', 'Citroën', 'Mercedes', 'Mitsubishi', 'Nissan', 'Peugeot', 'Renault', 'Toyota', 'Volkswagen', 'Others'])
            mileage = st.number_input("Mileage (km)", min_value=0, value=50000)
            engine_power = st.number_input("Engine Power (hp)", min_value=10, value=120)
            fuel = st.selectbox("Fuel Type",[""] + ['diesel', 'petrol', 'other'])
            auto = st.checkbox("Automatic", value=False)
            gps = st.checkbox("GPS", value=False)
        with col2:
            ac = st.checkbox("Air Conditioning", value=False)
            speed_reg = st.checkbox("Speed Regulator", value=False)
            winter_tires = st.checkbox("Winter Tires", value=False)
            private_parking = st.checkbox("Private Parking", value=False)
            connect = st.checkbox("Getaround Connect", value=False)
            car_type = st.selectbox("Car Type",[""] + ['convertible', 'coupe', 'estate', 'hatchback', 'sedan','subcompact', 'suv', 'van'])
            paint_color = st.selectbox("Paint Color", [""] + ['black','grey','white','red','silver','blue','beige','brown','green','orange'])

        submitted = st.form_submit_button("Compute Predicted Price")

    if submitted:
        payload = {
            "model_key": model_key,
            "mileage": mileage,
            "engine_power": engine_power,
            "fuel": fuel,
            "automatic_car": 1 if auto else 0,
            "has_gps": 1 if gps else 0,
            "has_air_conditioning": 1 if ac else 0,
            "has_speed_regulator": 1 if speed_reg else 0,
            "winter_tires": 1 if winter_tires else 0,
            "private_parking_available": 1 if private_parking else 0,
            "has_getaround_connect": 1 if connect else 0,
            "car_type": car_type,
            "paint_color": paint_color
        }
        prediction = get_price_prediction(payload)
        if prediction is not None:
            st.success(f"Estimated rental price: **{prediction:.2f}€** per day")



if page=="Home":
    screen_Home()
elif page == "Rental Overview" :
    screen_RentalOverview()
elif page=="Price Prediction" :
    screen_PricePrediction()
