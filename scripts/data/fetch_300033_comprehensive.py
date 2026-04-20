"""
综合数据获取脚本 - 尝试多种数据源获取股票 300033 数据
按优先级尝试:
1. AkShare (免费，无需 Token)
2. Tushare Pro (需要 Token 和积分)
3. yfinance (Yahoo Finance，可能受限)
4. 手动下载提示
"""
import akshare as ak
import tushare as ts
import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime

print("=" * 70)
print("综合数据获取工具 - 股票 300033（东方财富）")
print("=" * 70)

stock_code = "300033"
output_dir = "./akshare_data"
output_file = os.path.join(output_dir, f"daily_{stock_code}.csv")

os.makedirs(output_dir, exist_ok=True)

# ==================== 方案 1: AkShare ====================
print("\n【方案 1】尝试使用 AkShare...")
print("-" * 70)

try:
    print("正在连接东方财富数据源...")
    time.sleep(2)  # 等待
    
    df_ak = ak.stock_zh_a_hist(
        symbol=stock_code,
        period="daily",
        start_date="20160101",
        end_date="20260419",
        adjust="qfq"
    )
    
    if not df_ak.empty:
        print(f"✅ AkShare 成功！获取到 {len(df_ak)} 条记录")
        
        # 转换格式
        df_ak.rename(columns={
            '日期': 'timestamps',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount'
        }, inplace=True)
        
        df_ak = df_ak[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        df_ak['timestamps'] = pd.to_datetime(df_ak['timestamps'])
        df_ak = df_ak.sort_values('timestamps').reset_index(drop=True)
        
        # 保存
        df_ak.to_csv(output_file, index=False)
        print(f"✅ 数据已保存至: {output_file}")
        print(f"\n数据统计:")
        print(f"  - 记录数: {len(df_ak)}")
        print(f"  - 时间范围: {df_ak['timestamps'].min()} 至 {df_ak['timestamps'].max()}")
        print(f"  - 收盘价范围: ¥{df_ak['close'].min():.2f} - ¥{df_ak['close'].max():.2f}")
        
        print("\n" + "=" * 70)
        print("✅ 完成！使用 AkShare 成功获取数据")
        print("=" * 70)
        exit(0)
    else:
        print("❌ AkShare 返回空数据")
        
except Exception as e:
    print(f"❌ AkShare 失败: {e}")


# ==================== 方案 2: Tushare Pro ====================
print("\n【方案 2】尝试使用 Tushare Pro...")
print("-" * 70)

try:
    # Tushare Token - 请替换为您的实际 Token
    TUSHARE_TOKEN = "YOUR_TUSHARE_TOKEN_HERE"
    
    if TUSHARE_TOKEN != "YOUR_TUSHARE_TOKEN_HERE":
        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
        
        print("正在获取数据...")
        df_ts = pro.daily(ts_code=f"{stock_code}.SZ", 
                         start_date='20160101', 
                         end_date='20260419')
        
        if not df_ts.empty:
            print(f"✅ Tushare 成功！获取到 {len(df_ts)} 条记录")
            
            # 转换格式
            df_ts.rename(columns={
                'trade_date': 'timestamps',
                'vol': 'volume'
            }, inplace=True)
            
            df_ts = df_ts[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']]
            df_ts['timestamps'] = pd.to_datetime(df_ts['timestamps'])
            df_ts = df_ts.sort_values('timestamps').reset_index(drop=True)
            
            # 保存
            df_ts.to_csv(output_file, index=False)
            print(f"✅ 数据已保存至: {output_file}")
            
            print("\n" + "=" * 70)
            print("✅ 完成！使用 Tushare 成功获取数据")
            print("=" * 70)
            exit(0)
        else:
            print("❌ Tushare 返回空数据（可能是积分不足）")
    else:
        print("⚠️  Tushare Token 未配置，跳过")
        
except Exception as e:
    print(f"❌ Tushare 失败: {e}")


# ==================== 方案 3: yfinance ====================
print("\n【方案 3】尝试使用 yfinance (Yahoo Finance)...")
print("-" * 70)

try:
    print("正在连接 Yahoo Finance...")
    time.sleep(2)
    
    df_yf = yf.download(
        f"{stock_code}.SZ",
        start="2016-01-01",
        end="2026-04-19",
        interval="1d",
        progress=False
    )
    
    if not df_yf.empty:
        print(f"✅ yfinance 成功！获取到 {len(df_yf)} 条记录")
        
        # 转换格式
        df_yf.reset_index(inplace=True)
        df_yf.rename(columns={
            'Date': 'timestamps',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        df_yf['amount'] = df_yf['close'] * df_yf['volume']
        df_yf = df_yf[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        df_yf['timestamps'] = pd.to_datetime(df_yf['timestamps'])
        df_yf = df_yf.sort_values('timestamps').reset_index(drop=True)
        
        # 保存
        df_yf.to_csv(output_file, index=False)
        print(f"✅ 数据已保存至: {output_file}")
        
        print("\n" + "=" * 70)
        print("✅ 完成！使用 yfinance 成功获取数据")
        print("=" * 70)
        exit(0)
    else:
        print("❌ yfinance 返回空数据")
        
except Exception as e:
    print(f"❌ yfinance 失败: {e}")


# ==================== 所有方案都失败 ====================
print("\n" + "=" * 70)
print("❌ 所有在线数据源均失败")
print("=" * 70)

print("\n建议的解决方案:")
print("\n1️⃣  稍后重试（推荐）")
print("   - 网络问题通常是暂时的")
print("   - 等待 30 分钟后再次运行此脚本")
print("   - 命令: python tests/fetch_300033_comprehensive.py")

print("\n2️⃣  使用已有数据")
print("   - 您已有 5 只股票的完整数据:")
print("     * daily_000001.csv (平安银行)")
print("     * daily_000858.csv (五粮液)")
print("     * daily_600000.csv (浦发银行)")
print("     * daily_600519.csv (贵州茅台)")
print("     * daily_600977.csv (中国电影)")

print("\n3️⃣  手动下载数据")
print("   - 访问: https://quote.eastmoney.com/sz300033.html")
print("   - 点击'历史行情'")
print("   - 选择时间范围: 2016-01-01 至 2026-04-19")
print("   - 导出为 Excel/CSV")
print("   - 转换为 Kronos 格式")

print("\n4️⃣  检查网络设置")
print("   - 检查代理设置: echo $http_proxy")
print("   - 禁用代理: unset http_proxy https_proxy")
print("   - 测试连接: ping www.eastmoney.com")

print("\n" + "=" * 70)
