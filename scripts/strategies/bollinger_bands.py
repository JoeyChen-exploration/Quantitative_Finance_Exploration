import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def run_bollinger_backtest(symbol, initial_capital=200.0): # 默认200美金
    file_path = f"data/{symbol}_prices.csv"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    df = pd.read_csv(file_path, index_col=0, parse_dates=True).tail(500)

    # 1. 计算布林带
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['Std'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['MA20'] + (df['Std'] * 2)
    df['Lower'] = df['MA20'] - (df['Std'] * 2)

    # 2. 计算 RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))

    # 3. 生成信号 (循环逻辑确保持仓状态正确)
    holding = 0.0
    signals = []
    for i in range(len(df)):
        if holding == 0.0:
            # 买入：跌破下轨 + RSI低位
            if (df['Close'].iloc[i] < df['Lower'].iloc[i]) and (df['RSI'].iloc[i] < 35):
                holding = 1.0
        elif holding == 1.0:
            # 卖出：触碰上轨
            if df['Close'].iloc[i] > df['Upper'].iloc[i]:
                holding = 0.0
        signals.append(holding)
    df['Signal'] = signals

    # 4. 收益计算 (已修复 BUG)
    df['Market_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Market_Return']
    
    # !!! 核心修复在这里 !!!
    df['Equity_Strategy'] = initial_capital * (1 + df['Strategy_Return'].fillna(0)).cumprod()

    print(f"--- {symbol} Bollinger Band Strategy ---")
    if not df['Equity_Strategy'].empty:
        print(f"Final Value: ${df['Equity_Strategy'].iloc[-1]:,.2f}")
        print(f"Return Rate: {(df['Equity_Strategy'].iloc[-1]/initial_capital - 1):.2%}")
    
    # 绘图
    plt.figure(figsize=(12, 6))
    plt.fill_between(df.index, df['Upper'], df['Lower'], color='blue', alpha=0.1, label='Bollinger Bands')
    plt.plot(df.index, df['Upper'], color='blue', alpha=0.2, linestyle='--')
    plt.plot(df.index, df['Lower'], color='blue', alpha=0.2, linestyle='--')
    plt.plot(df.index, df['Close'], label='Close Price', color='black', alpha=0.7, linewidth=1.5)
    
    buy_signals = df[df['Signal'].diff() == 1]
    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', s=100, label='Buy', zorder=5)
    
    sell_signals = df[df['Signal'].diff() == -1]
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', s=100, label='Sell', zorder=5)

    plt.title(f"{symbol} Bollinger Band Strategy: Buy & Sell Timing", fontsize=14)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    run_bollinger_backtest("NVDA")