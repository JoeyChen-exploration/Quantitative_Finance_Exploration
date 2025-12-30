import pandas as pd
import os
import matplotlib.pyplot as plt

def run_ma_crossover_backtest(symbol, short_window=20, long_window=50, initial_capital=10000.0):
    """
    Backtest the Dual Moving Average Crossover Strategy.
    Strategy: 
    - Buy (Long) when MA20 crosses above MA50.
    - Sell (Exit) when MA20 crosses below MA50.
    """
    file_path = f"data/{symbol}_prices.csv"
    if not os.path.exists(file_path):
        print(f"❌ Data file not found for {symbol}. Please run data_fetcher.py first.")
        return

    # Load data
    df = pd.read_csv(file_path)
    date_col = 'Date' if 'Date' in df.columns else 'date'
    df[date_col] = pd.to_datetime(df[date_col])
    df.set_index(date_col, inplace=True)
    
    # Slice data for the recent 2 years (500 trading days) for clarity
    df = df.tail(500).copy()

    # --- Step 1: Calculate Indicators ---
    df['MA_Fast'] = df['Close'].rolling(window=short_window).mean()
    df['MA_Slow'] = df['Close'].rolling(window=long_window).mean()

    # --- Step 2: Generate Signals ---
    # 1.0 = MA_Fast > MA_Slow (Bullish), 0.0 = Otherwise
    df['Signal'] = 0.0
    df.loc[df['MA_Fast'] > df['MA_Slow'], 'Signal'] = 1.0
    
    # Position: Detect the moment of crossing
    # 1.0 = Golden Cross (Buy), -1.0 = Death Cross (Sell)
    df['Position'] = df['Signal'].diff()

    # --- Step 3: Calculate Returns ---
    # Daily Market Return
    df['Market_Return'] = df['Close'].pct_change()
    
    # Strategy Return: Use yesterday's signal for today's price action
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Market_Return']

    # --- Step 4: Portfolio Value (Equity Curve) ---
    df['Equity_Market'] = initial_capital * (1 + df['Market_Return']).fillna(0).add(1).cumprod() / (1 + df['Market_Return'].iloc[0] if not pd.isna(df['Market_Return'].iloc[0]) else 1)
    # Simpler way to calculate cumulative growth:
    df['Equity_Market'] = initial_capital * (1 + df['Market_Return']).cumprod()
    df['Equity_Strategy'] = initial_capital * (1 + df['Strategy_Return']).cumprod()

    # Handle the first row NaN
    df.iloc[0, df.columns.get_loc('Equity_Market')] = initial_capital
    df.iloc[0, df.columns.get_loc('Equity_Strategy')] = initial_capital

    # --- Step 5: Performance Metrics ---
    total_market_ret = (df['Equity_Market'].iloc[-1] / initial_capital) - 1
    total_strat_ret = (df['Equity_Strategy'].iloc[-1] / initial_capital) - 1
    
    print(f"--- Backtest Results for {symbol} ---")
    print(f"Initial Investment: ${initial_capital:,.2f}")
    print(f"Market Return (Buy & Hold): {total_market_ret:.2%}")
    print(f"Strategy Return (MA Crossover): {total_strat_ret:.2%}")

    # --- Step 6: Visualization ---
    plt.figure(figsize=(12, 7))
    plt.plot(df.index, df['Equity_Market'], label='Market (Buy & Hold)', color='gray', alpha=0.6)
    plt.plot(df.index, df['Equity_Strategy'], label='Strategy (MA Crossover)', color='teal', linewidth=2)
    
    # Mark Buy/Sell points on the chart
    buy_signals = df[df['Position'] == 1.0]
    sell_signals = df[df['Position'] == -1.0]
    plt.scatter(buy_signals.index, df.loc[buy_signals.index, 'Equity_Strategy'], marker='^', color='green', s=100, label='Buy Signal')
    plt.scatter(sell_signals.index, df.loc[sell_signals.index, 'Equity_Strategy'], marker='v', color='red', s=100, label='Sell Signal')

    plt.title(f'Equity Curve: {symbol} MA Crossover', fontsize=14)
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig(f"data/MA/{symbol}_ma_backtest_result_InitialTry.png")
    plt.show()

if __name__ == "__main__":
    run_ma_crossover_backtest("AAPL")