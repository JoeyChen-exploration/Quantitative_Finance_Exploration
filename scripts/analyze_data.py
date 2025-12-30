import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

def run_analysis(symbol):
    file_path = f"data/{symbol}_prices.csv"
    if not os.path.exists(file_path):
        print(f"❌ 错误：找不到文件 {file_path}")
        return

    # 1. 加载数据
    df = pd.read_csv(file_path)
    date_col = 'Date' if 'Date' in df.columns else 'date'
    df[date_col] = pd.to_datetime(df[date_col])
    df.set_index(date_col, inplace=True)

    # 2. 数据切片：只看最近 500 个交易日（约2年）
    df = df.tail(500).copy()

    # 3. 计算指标
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['Return'] = df['Close'].pct_change()

    # 4. 打印分析文字
    print(f"--- {symbol} 深度分析报告 ---")
    print(f"分析周期: {df.index.min().date()} 至 {df.index.max().date()}")
    print(f"当前价格: {df['Close'].iloc[-1]:.2f}")
    print(f"MA20 (短期趋势): {df['MA20'].iloc[-1]:.2f}")
    print(f"MA50 (长期趋势): {df['MA50'].iloc[-1]:.2f}")
    
    # 计算年化波动率（基于最近2年）
    volatility = df['Return'].std() * (252**0.5)
    print(f"最近两年年化波动率: {volatility:.2%}")

    # 5. 绘图
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Price', color='#1f77b4', linewidth=1.5, alpha=0.8)
    plt.plot(df.index, df['MA20'], label='MA20 (1-Month)', color='#ff7f0e', linestyle='--')
    plt.plot(df.index, df['MA50'], label='MA50 (Quarterly)', color='#d62728', linestyle=':')

    plt.title(f'{symbol} Trend Analysis (Recent 500 Days)', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend(loc='best')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # --- 重要修复：先保存，后显示 ---
    # 确保 data 文件夹存在
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 也可以用时间戳命名：f"data/{symbol}_chart_{datetime.now().strftime('%Y%m%d')}.png"
    output_image = f"data/{symbol}_recent_trend.png"
    
    # 增加 dpi 参数让图片更清晰
    plt.savefig(output_image, dpi=300) 
    print(f"✅ 图片已成功保存至: {output_image}")

    # 最后再显示
    plt.show()

if __name__ == "__main__":
    run_analysis("AAPL")