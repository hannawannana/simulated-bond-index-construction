"""
Simulated Bond Index vs Market Benchmark (S&P 500)
Author: Nudrat Hanna Ahona

This project uses real-world data from the FRED API to build and compare bond index strategies.
It prices bonds from yield data, applies monthly rebalancing with cost simulation, and benchmarks
against the S&P 500 index from 2018 to 2023.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fredapi import Fred
from datetime import datetime

# ---------------------------
# STEP 1: Connect to FRED API
# ---------------------------
FRED_API_KEY = 'b9a4903923b9fcb6db345239517e5'  # Replace with your FRED key
fred = Fred(api_key=FRED_API_KEY)

start_date = '2018-01-01'
end_date = '2023-12-31'
initial_investment = 1000

# ---------------------------
# STEP 2: Download Treasury Yields and S&P 500
# ---------------------------
# Treasury yields: 1Y, 5Y, 10Y
yields = {
    'GS1': '1Y',
    'GS5': '5Y',
    'GS10': '10Y'
}

yields_df = pd.DataFrame()
for code, label in yields.items():
    yields_df[label] = fred.get_series(code, observation_start=start_date, observation_end=end_date)

# Benchmark: S&P 500 index (daily closing value)
sp500 = fred.get_series('SP500', observation_start=start_date, observation_end=end_date)

# ---------------------------
# STEP 3: Resample to monthly data and align
# ---------------------------
yields_df = yields_df.resample('M').mean().dropna()
sp500 = sp500.resample('M').last()
sp500 = sp500.loc[yields_df.index]  # align with yield data

# ---------------------------
# STEP 4: Estimate bond prices from yields
# ---------------------------
# Assume all bonds are $100 face value, fixed duration
def bond_price(yield_percent, duration_years):
    return 100 / ((1 + yield_percent / 100) ** duration_years)

durations = {'1Y': 1, '5Y': 5, '10Y': 10}
prices_df = pd.DataFrame(index=yields_df.index)

for col in yields_df.columns:
    prices_df[col] = yields_df[col].apply(lambda y: bond_price(y, durations[col]))

# ---------------------------
# STEP 5: Simulate monthly rebalanced bond index
# ---------------------------
def simulate_bond_index(prices, weights, transaction_cost=0.001):
    value = initial_investment
    portfolio_values = []
    holdings = {}

    for i in range(1, len(prices)):
        prev = prices.iloc[i - 1]
        curr = prices.iloc[i]

        # First time: buy according to initial weights
        if not holdings:
            holdings = {bond: (value * weights[bond]) / prev[bond] for bond in weights}

        # Update value
        value = sum(holdings[bond] * curr[bond] for bond in holdings)

        # Desired holdings for rebalancing
        desired_value = {bond: value * weights[bond] for bond in weights}
        new_holdings = {bond: desired_value[bond] / curr[bond] for bond in weights}

        # Calculate turnover cost
        turnover = sum(abs(new_holdings[bond] - holdings[bond]) * curr[bond] for bond in weights)
        cost = turnover * transaction_cost
        value -= cost  # Deduct cost

        # Update holdings
        holdings = new_holdings
        portfolio_values.append(value)

    return portfolio_values

# Original and adjusted weight strategies
weights_original = {'1Y': 0.3, '5Y': 0.4, '10Y': 0.3}
weights_adjusted = {'1Y': 0.5, '5Y': 0.3, '10Y': 0.2}

# Simulate both strategies
original_index = simulate_bond_index(prices_df, weights_original)
adjusted_index = simulate_bond_index(prices_df, weights_adjusted)

# ---------------------------
# STEP 6: Simulate S&P 500 Index
# ---------------------------
sp500_returns = sp500.pct_change().dropna()
sp500_index = (1 + sp500_returns).cumprod() * initial_investment
sp500_index = sp500_index.loc[prices_df.index[1:]]

# ---------------------------
# STEP 7: Combine results into one DataFrame
# ---------------------------
results_df = pd.DataFrame({
    'Bond Index (Original)': original_index,
    'Bond Index (Adjusted)': adjusted_index,
    'S&P 500 Index': sp500_index
}, index=prices_df.index[1:])

# ---------------------------
# STEP 8: Plot the results
# ---------------------------
plt.figure(figsize=(11, 6))
plt.plot(results_df.index, results_df['Bond Index (Original)'], label='Bond Index (0.3/0.4/0.3)', color='blue')
plt.plot(results_df.index, results_df['Bond Index (Adjusted)'], label='Bond Index (0.5/0.3/0.2)', linestyle='--', color='green')
plt.plot(results_df.index, results_df['S&P 500 Index'], label='S&P 500 Index', linestyle=':', color='gray')
plt.title('Bond Index Strategies vs S&P 500 (2018–2023)')
plt.xlabel('Date')
plt.ylabel('Portfolio Value ($)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("bond_vs_sp500.png")
plt.show()

# ---------------------------
# STEP 9: Save results to file
# ---------------------------
results_df.to_csv("bond_vs_sp500_data.csv")
