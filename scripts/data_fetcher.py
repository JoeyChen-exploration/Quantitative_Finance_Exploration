import akshare as ak
import os

def fetch_data_ak():
    symbol = "AAPL"
    print(f"--- 使用 AkShare 下载 {symbol} 数据 ---")
    
    # get_us_stock_daily 是 AkShare 获取美股的接口
    # 注意：AkShare 返回的列名可能是中文，我们可以手动改回英文
    df = ak.stock_us_daily(symbol=symbol, adjust="qfq")
    
    if df.empty:
        print("❌ 数据为空")
        return

    # 统一列名，方便后续分析脚本
    df.rename(columns={'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

    if not os.path.exists('data'): os.makedirs('data')
    df.to_csv(f"data/{symbol}_prices.csv", index=False)
    print("✅ AkShare 抓取成功")

if __name__ == "__main__":
    fetch_data_ak()