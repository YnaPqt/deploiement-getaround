import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt

# Page configuration
st.set_page_config(
    page_title="GetAround Rental Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# --- Dashboard Header / Explanation ---
st.title("Getaround Rental Delay Dashboard")
st.markdown(f"""
In order to mitigate late checkout issues, GetAround wants to implement a **minimum delay between two rentals**.
            
Cars won't be shown in search results if the requested check-in or check-out time is too close to an existing rental.  
This can **solve operational issues**, but may also **reduce revenue** for Getaround and car owners.

""")

# --- Load and preprocess data ---
@st.cache_data
def load_data():
    df = pd.read_excel(r"C:\Users\ronal\DEPLOYMENT\jedha-getaround-project\data\get_around_delay_analysis.xlsx", sheet_name="rentals_data")
    df.dropna(subset=['car_id', 'checkin_type'], inplace=True)
    df = df[df['state'] == 'ended']
    df['delay_at_checkout_in_minutes'] = df['delay_at_checkout_in_minutes'].fillna(0)
    df['time_delta_with_previous_rental_in_minutes'] = df['time_delta_with_previous_rental_in_minutes'].fillna(np.inf)
    df['previous_delay'] = df['delay_at_checkout_in_minutes'].shift(1).fillna(0)

    def delay_category(delay):
        if delay <= 0:
            return 'on time'
        elif delay <= 30:
            return 'moderately late'
        elif delay <= 60:
            return 'very late'
        else:
            return 'extremely late'

    df['delay_category'] = df['delay_at_checkout_in_minutes'].apply(delay_category)
    return df

df_full = load_data()

# --- Sidebar filters ---
st.sidebar.title("🔧 Filters")
thresholds = [10, 20, 40, 60, 80, 100, 120, 140]
selected_checkin = st.sidebar.selectbox("🔄 Check-in Type", ["All", "mobile", "connect"])
selected_threshold = st.sidebar.selectbox("⏳ Minimum Delay Threshold (minutes)", thresholds)


# --- Apply check-in type filter ---
df = df_full.copy()
if selected_checkin != "All":
    df = df[df["checkin_type"] == selected_checkin]

# --- Apply dynamic revenue risk logic for selected threshold ---
df['revenue_risk'] = (
    (df['previous_delay'] > df['time_delta_with_previous_rental_in_minutes']) &
    (df['time_delta_with_previous_rental_in_minutes'] < selected_threshold)
)

# Blocked rentals: too soon after previous rental
blocked_df = df[df["time_delta_with_previous_rental_in_minutes"] < selected_threshold]
solved_cases_df = blocked_df[blocked_df["revenue_risk"]]

# Revenue risk percentage (filtered)
total_rentals = len(df)
revenue_risk_pct = (df["revenue_risk"].sum() / total_rentals * 100) if total_rentals > 0 else 0

# Total rentals after check-in filter
total_rentals = len(df)

# Blocked rentals: too soon after previous rental
blocked_rentals_current = (df['time_delta_with_previous_rental_in_minutes'] < selected_threshold).sum()

# Revenue Risk % = % of rentals blocked
revenue_risk_pct = (blocked_rentals_current / total_rentals) * 100 if total_rentals > 0 else 0

# Delta: how much more (or less) risk compared to previous threshold
prev_idx = thresholds.index(selected_threshold) - 1
if prev_idx >= 0:
    previous_threshold = thresholds[prev_idx]
    blocked_rentals_prev = (df['time_delta_with_previous_rental_in_minutes'] < previous_threshold).sum()
    revenue_risk_pct_prev = (blocked_rentals_prev / total_rentals) * 100 if total_rentals > 0 else 0
    revenue_risk_delta = revenue_risk_pct - revenue_risk_pct_prev
else:
    revenue_risk_delta = 0


##################################
st.subheader(f"📉 Impact for Threshold = {selected_threshold} min & {selected_checkin}")

# --- Prepare data ---
blocked_count = len(blocked_df)
not_blocked_count = total_rentals - blocked_count

solved_count = len(solved_cases_df)
unsolved_count = df["revenue_risk"].sum() - solved_count

# Total risky cases after filtering by check-in type
total_revenue_risk_cases = (
        (df['previous_delay'] > df['time_delta_with_previous_rental_in_minutes'])
        ).sum()

# Solved cases = risky rentals that were blocked by current threshold
solved_count = (
    (df['previous_delay'] > df['time_delta_with_previous_rental_in_minutes']) &
    (df['time_delta_with_previous_rental_in_minutes'] < selected_threshold)
).sum()

# Remaining risk = risky rentals not blocked
unsolved_count = total_revenue_risk_cases - solved_count

# --- Create subplot with 2 pies ---
fig_pies = make_subplots(
    rows=1, cols=2,
    specs=[[{"type": "domain"}, {"type": "domain"}]],

)

# Pie 1: Blocked Rentals
fig_pies.add_trace(
    go.Pie(
        labels=["Blocked", "Not Blocked"],
        values=[blocked_count, not_blocked_count],
        textinfo="percent+label",
        hole=0.4
    ),
    row=1, col=1
)

# Pie 2: Solved Cases
fig_pies.add_trace(
    go.Pie(
        labels=["Solved Cases", "Remaining Risk"],
        values=[solved_count, unsolved_count],
        textinfo="percent+label",
        hole=0.4
    ),
    row=1, col=2
    )

# Layout styling
fig_pies.update_layout(
    title_text="📊 Blocked Rentals & Risk Solved",
    paper_bgcolor="gray",
    margin=dict(t=80, b=20, l=20, r=20),
)

# Show chart inside Column 2
st.plotly_chart(fig_pies, use_container_width=True)


#############################################

# Line plot: Risk curve (still across thresholds)
def compute_metrics(df, thresholds):
    results = []
    for t in thresholds:
        df_temp = df.copy()
        df_temp['revenue_risk'] = (
            (df_temp['previous_delay'] > df_temp['time_delta_with_previous_rental_in_minutes']) &
            (df_temp['time_delta_with_previous_rental_in_minutes'] < t)
        )
        risk_pct = df_temp["revenue_risk"].sum() / len(df_temp) * 100 if len(df_temp) > 0 else 0
        results.append({"Threshold": t, "Revenue Risk %": risk_pct})
    return pd.DataFrame(results)

metrics_curve_df = compute_metrics(df, thresholds)
fig_curve = px.line(metrics_curve_df, x="Threshold", y="Revenue Risk %", markers=True,
                        title="📈 Revenue Risk")
fig_curve.update_layout(
    paper_bgcolor="gray", 
    plot_bgcolor="gray", 
)

st.plotly_chart(fig_curve)

#############################################

#KPI Metrics sidebar
st.sidebar.subheader("📊 Key Metrics")

st.sidebar.metric(
    label="🚫 Revenue Risk (% of Rentals Blocked)", 
    value=f"{revenue_risk_pct:.2f}%", 
    delta=f"{revenue_risk_delta:+.2f}%", 
    delta_color="inverse"
)

st.sidebar.metric("⛔ Blocked Rentals", value=len(blocked_df))
st.sidebar.metric("✅ Solved Cases", value=len(solved_cases_df))


