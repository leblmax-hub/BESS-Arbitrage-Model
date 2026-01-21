import streamlit as st
import pandas as pd
import pulp
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. SETUP & SIDEBAR
# ==========================================
st.set_page_config(page_title="BESS Arbitrage Pro", layout="wide")
st.title("⚡ Advanced Battery Arbitrage & Valuation Model")
st.markdown("""
This tool simulates a **Battery Energy Storage System (BESS)** trading in a volatile electricity market.
It uses **Linear Programming (MILP)** to optimize charging schedules while accounting for physical degradation costs.
""")

# --- Sidebar Controls ---
st.sidebar.header("🔋 Physical Assets")
BATTERY_CAPACITY = st.sidebar.slider("Battery Capacity (MWh)", 10, 200, 50)
MAX_POWER = st.sidebar.slider("Max Power (MW)", 1, 50, 10)
EFFICIENCY = st.sidebar.slider("Round-Trip Efficiency (%)", 50, 100, 90) / 100.0

st.sidebar.header("💰 Financial Constraints")
# OPTION 1 INTEGRATION: Cycle Costs (The "Hurdle Rate")
DEG_COST = st.sidebar.number_input("Degradation Cost ($/MWh)", min_value=0.0, max_value=50.0, value=10.0, step=0.5)
st.sidebar.caption(f"The battery will only trade if profit > ${DEG_COST}/MWh")

st.sidebar.header("📈 Market Simulation")
VOLATILITY = st.sidebar.selectbox("Market Volatility", ["Low", "Normal", "Extreme", "Crisis (Texas 2021)"])

# ==========================================
# 2. GENERATE MARKET DATA
# ==========================================
DAYS = 30
HOURS = DAYS * 24
np.random.seed(42)

# Volatility Config
vol_settings = {
    "Low": {"noise": 5, "spike_prob": 0.01, "spike_size": 50},
    "Normal": {"noise": 10, "spike_prob": 0.05, "spike_size": 200},
    "Extreme": {"noise": 25, "spike_prob": 0.10, "spike_size": 500},
    "Crisis (Texas 2021)": {"noise": 50, "spike_prob": 0.20, "spike_size": 2000}
}
settings = vol_settings[VOLATILITY]

# Create Prices
hour_of_day = np.tile(np.arange(24), DAYS)
base_price = 50 + 30 * np.sin((hour_of_day - 6) * np.pi / 12)
noise = np.random.normal(0, settings["noise"], HOURS)
# Random spikes
spikes = np.random.choice([0, settings["spike_size"]], size=HOURS, p=[1.0 - settings["spike_prob"], settings["spike_prob"]])

final_prices = np.maximum(base_price + noise + spikes, 0) # No negative prices for this sim
df = pd.DataFrame({'price': final_prices})

# ==========================================
# 3. OPTIMIZATION ENGINE (With Degradation)
# ==========================================
prob = pulp.LpProblem("Master_Optimization", pulp.LpMaximize)

# Variables
charge_vars = pulp.LpVariable.dicts("Charge", range(HOURS), 0, MAX_POWER)
discharge_vars = pulp.LpVariable.dicts("Discharge", range(HOURS), 0, MAX_POWER)
soc_vars = pulp.LpVariable.dicts("SoC", range(HOURS + 1), 0, BATTERY_CAPACITY)

# OBJECTIVE FUNCTION (Updated for Option 1)
# Profit = Revenue (Discharge * Price) - Cost (Charge * Price) - Wear&Tear (Discharge * DegCost)
prob += pulp.lpSum([
    (df['price'][t] * discharge_vars[t]) - 
    (df['price'][t] * charge_vars[t]) - 
    (discharge_vars[t] * DEG_COST) 
    for t in range(HOURS)
])

# Constraints
prob += soc_vars[0] == 0 
for t in range(HOURS):
    prob += soc_vars[t+1] == soc_vars[t] + (charge_vars[t] * EFFICIENCY) - (discharge_vars[t] / EFFICIENCY)

prob.solve()

# ==========================================
# 4. DASHBOARD VISUALIZATIONS
# ==========================================
if pulp.LpStatus[prob.status] == 'Optimal':
    
    # Process Results
    res_data = []
    cum_profit = 0
    profit_curve = []
    
    for t in range(HOURS):
        c = charge_vars[t].varValue
        d = discharge_vars[t].varValue
        # Realized profit for this hour
        pnl = (d * df['price'][t]) - (c * df['price'][t]) - (d * DEG_COST)
        cum_profit += pnl
        profit_curve.append(cum_profit)
        res_data.append({"Hour": t, "Price": df['price'][t], "Charge": c, "Discharge": d, "SoC": soc_vars[t+1].varValue})
    
    df_res = pd.DataFrame(res_data)
    df_res['Cumulative Profit'] = profit_curve
    
    # --- METRICS ROW ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Net Profit (30 Days)", f"${cum_profit:,.0f}")
    col2.metric("📉 Cycles Used", f"{int(df_res['Discharge'].sum() / BATTERY_CAPACITY)}")
    # ROI Calculation
    capex_est = BATTERY_CAPACITY * 150000 # Approx $150k per MWh cost
    col3.metric("Est. Monthly ROI", f"{(cum_profit / capex_est) * 100:.1f}%")
    col4.metric("Market Volatility", VOLATILITY)

    # --- TABBED VIEW FOR CHARTS ---
    tab1, tab2 = st.tabs(["Performance Overview", "Detailed Trading Activity"])
    
    with tab1:
        st.subheader("Equity Curve: Cumulative Profit")
        st.line_chart(df_res['Cumulative Profit'])
        
        st.info("Notice: If you increase the 'Degradation Cost' in the sidebar, the battery trades less often, but the curve becomes smoother (higher quality trades only).")

    with tab2:
        st.subheader("Zoom In: First 3 Days of Trading")
        # Custom Matplotlib Plot for detail
        fig, ax1 = plt.subplots(figsize=(10, 4))
        
        # Plot only first 72 hours
        subset = df_res.head(72)
        
        ax1.plot(subset['Hour'], subset['Price'], color='tab:gray', alpha=0.5, label='Price')
        ax1.set_ylabel('Price ($)', color='gray')
        
        ax2 = ax1.twinx()
        # Plot Net Action (Charge = Positive, Discharge = Negative)
        ax2.bar(subset['Hour'], subset['Charge'] - subset['Discharge'], color='tab:blue', alpha=0.6, label='Action')
        ax2.set_ylabel('Battery Action (MW)', color='blue')
        
        st.pyplot(fig)
        st.dataframe(df_res)

else:
    st.error("Optimization failed. Try adjusting constraints.")
