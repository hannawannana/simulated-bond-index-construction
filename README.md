# Bond Index Simulation vs S&P 500 Benchmark 

This project simulates a custom bond index using real Treasury yield data from the [FRED API](https://fred.stlouisfed.org/). It prices bonds using duration-based formulas, rebalances monthly with transaction cost simulation, and compares performance to the S&P 500 from 2018–2023.

## What It Does

- Pulls historical 1Y, 5Y, and 10Y Treasury yields
- Prices bonds using:
  \[ P = \frac{100}{(1 + y)^\text{duration}} \]
- Rebalances two bond portfolios monthly with cost simulation
- Benchmarks against the S&P 500 Index
- Outputs chart + CSV of results

## Files

| File                     | Description                       |
|--------------------------|-----------------------------------|
| `bond_index.py`          | Main simulation code              |
| `bond_vs_sp500.png`      | Chart: Bond strategies vs S&P 500 |
| `bond_vs_sp500_data.csv` | Portfolio values export           |

## How to Run

1. Clone the repo
2. Install requirements: pip install pandas matplotlib numpy fredapi
3. Add your FRED API key in the script
4. Run: python bond_index_realistic.py


