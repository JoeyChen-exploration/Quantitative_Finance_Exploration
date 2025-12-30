import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def run_pro_backtest(symbol, short_window=10, long_window=20, initial_capital=10000.0):
    file_path = f"data/{symbol}_prices.csv"
    df = pd.read_csv(file_path, index_col=0, parse_dates=True).tail(500)

    # --- 1. 计算均线 ---
    df['MA_Fast'] = df['Close'].rolling(window=short_window).mean()
    df['MA_Slow'] = df['Close'].rolling(window=long_window).mean()

    # --- 2. 计算 RSI (14日) ---
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # --- 3. 核心逻辑：带过滤器的信号 ---
    df['Signal'] = 0.0
    # 买入条件：金叉 且 RSI < 70 (不追高)
    df.loc[(df['MA_Fast'] > df['MA_Slow']) & (df['RSI'] < 70), 'Signal'] = 1.0
    
    # 卖出条件优化：除了死叉，RSI 极度超买 (>85) 也清仓保护利润
    # df.loc[df['RSI'] > 85, 'Signal'] = 0.0 

    df['Position'] = df['Signal'].diff()

    # --- 4. 计算收益 ---
    df['Market_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Market_Return']
    
    df['Equity_Market'] = initial_capital * (1 + df['Market_Return']).cumprod()
    df['Equity_Strategy'] = initial_capital * (1 + df['Strategy_Return']).cumprod()

    # --- 5. 输出分析 ---
    print(f"--- {symbol} Pro 策略报告 ---")
    print(f"最终策略价值: ${df['Equity_Strategy'].iloc[-1]:,.2f}")
    print(f"策略收益率: {((df['Equity_Strategy'].iloc[-1]/initial_capital)-1):.2%}")
    
    # 绘图逻辑同前...
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Equity_Strategy'], label='Pro Strategy (MA + RSI)', color='gold', linewidth=2)
    plt.plot(df.index, df['Equity_Market'], label='Market', color='gray', alpha=0.4)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    run_pro_backtest("AAPL")