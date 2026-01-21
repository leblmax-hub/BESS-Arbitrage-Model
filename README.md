# BESS-Arbitrage-Model
Python model optimizing battery storage revenue using Linear Programming.
# ⚡ BESS Energy Arbitrage Optimization Engine
<img width="1489" height="845" alt="Screenshot 2026-01-21 at 14 03 21" src="https://github.com/user-attachments/assets/9ff8e299-727f-493b-939c-c1ff7775cc0c" />

### Overview
This project models the operation of a **Battery Energy Storage System (BESS)** in volatile electricity markets. It uses **Mixed-Integer Linear Programming (MILP)** to generate optimal charging and discharging schedules that maximize revenue while accounting for physical system constraints.

**Business Goal:** Determine the economic viability of battery storage by simulating revenue against historical or stochastic price scenarios (e.g., the "Duck Curve" or grid crisis events).

### 📊 Key Features
* **Optimization Algorithm:** Uses `PuLP` to solve for the mathematically perfect trade schedule.
* **Physical Constraints:** Models round-trip efficiency (90%) and maximum power ratings.
* **Degradation Logic:** Includes a "Hurdle Rate" (Cycle Cost) to prevent micro-cycling and preserve battery lifespan.
* **Interactive Dashboard:** A `Streamlit` web app allowing users to test different battery sizes, volatility levels, and financial parameters in real-time.

### 🛠️ Technologies Used
* **Python 3.10+**
* **Streamlit** (Web Interface)
* **PuLP** (Linear Optimization Solver)
* **Pandas & NumPy** (Data Manipulation & Stochastic Simulation)
* **Matplotlib** (Financial Visualization)

### 🚀 How to Run
1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/BESS-Arbitrage-Model.git](https://github.com/YOUR_USERNAME/BESS-Arbitrage-Model.git)
    ```
2.  Install dependencies:
    ```bash
    pip install pandas pulp streamlit matplotlib
    ```
3.  Launch the Dashboard:
    ```bash
    streamlit run BESS_Full_Portfolio.py
    ```

### 📈 Sample Output
The model outputs a cumulative equity curve and a daily dispatch schedule, visualizing exactly when the battery buys (low prices) and sells (peak prices).
