import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def run_vcp_tuned_backtest(symbol, initial_capital=10000.0):
    file_path = f"data/{symbol}_prices.csv"
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found. Please run data_fetcher.py first.")
        return

    # 1. 加载数据并截取最近 500 个交易日
    df = pd.read_csv(file_path, index_col=0, parse_dates=True).tail(500)
    
    # --- Step 2: 核心指标计算 (微调版) ---
    
    # 趋势过滤：确保处于大牛市趋势中
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    # 波动率收缩 (VCP 的 'C' - Contraction)
    # 计算 ATR (真实波幅) 的移动平均
    df['ATR'] = df['High'] - df['Low']
    df['ATR_MA'] = df['ATR'].rolling(window=20).mean()
    # 调参：从 0.8 放宽到 0.95，只要波动稍有收敛即认为“紧凑”
    df['Is_Tight'] = df['ATR'] < (df['ATR_MA'] * 0.95)
    
    # 价格位置：距离 52周最高点 15% 以内 (从 10% 放宽)
    df['52W_High'] = df['Close'].rolling(window=252).max()
    df['Near_High'] = df['Close'] > (df['52W_High'] * 0.85)
    
    # 成交量确认：调参从 1.5倍 降低到 1.2倍
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    df['Vol_Spike'] = df['Volume'] > (df['Vol_MA20'] * 1.2)
    
    # 价格动能：当日必须是实质性上涨 (涨幅 > 1%)
    df['Market_Return'] = df['Close'].pct_change()
    df['Price_Surge'] = df['Market_Return'] > 0.01

    # --- Step 3: 复合信号生成 ---
    df['Signal'] = 0.0
    # 条件组合：长线趋势向上 + 接近高位 + 昨天波动收缩 + 今天放量大涨
    df.loc[(df['Close'] > df['MA200']) & 
           (df['Near_High']) & 
           (df['Is_Tight'].shift(1)) & 
           (df['Vol_Spike']) & 
           (df['Price_Surge']), 'Signal'] = 1.0

    # --- Step 4: 收益计算与止损 (5% 硬止损) ---
    # 简化模拟：持仓直到下一次信号或止损（这里演示基础逻辑）
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Market_Return']
    
    # 计算累计净值
    df['Equity_Market'] = initial_capital * (1 + df['Market_Return']).cumprod()
    df['Equity_Strategy'] = initial_capital * (1 + df['Strategy_Return']).cumprod()

    # --- Step 5: 结果分析 ---
    trade_count = int(df['Signal'].sum())
    final_equity = df['Equity_Strategy'].iloc[-1]
    total_return = (final_equity / initial_capital) - 1
    
    print(f"--- {symbol} Tuned VCP Strategy Report ---")
    print(f"Total Buy Signals: {trade_count}")
    print(f"Strategy Final Value: ${final_equity:,.2f}")
    print(f"Total Strategy Return: {total_return:.2%}")
    print(f"Market Return: {((df['Equity_Market'].iloc[-1]/initial_capital)-1):.2%}")

    # --- Step 6: 绘图 ---
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Equity_Market'], label='Market (Buy & Hold)', color='silver', alpha=0.6)
    plt.plot(df.index, df['Equity_Strategy'], label='Tuned VCP Strategy', color='royalblue', linewidth=2)
    
    # 用金星标记买入点
    buy_dates = df[df['Signal'] == 1.0].index
    if not buy_dates.empty:
        plt.scatter(buy_dates, df.loc[buy_dates, 'Equity_Strategy'], 
                    marker='*', color='gold', s=150, edgecolors='black', label='VCP Signal', zorder=5)

    plt.title(f'VCP Momentum: {symbol} (Tuned Parameters)', fontsize=14)
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_vcp_tuned_backtest("NVDA")