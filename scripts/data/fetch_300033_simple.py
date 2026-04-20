"""
简单测试：获取股票 300033 数据
"""
import akshare as ak
import pandas as pd
import time

print("尝试获取股票 300033（东方财富）的数据...")
print("=" * 70)

# 增加等待时间
time.sleep(5)

try:
    # 尝试获取数据
    df = ak.stock_zh_a_hist(
        symbol="300033",
        period="daily",
        start_date="20150101",
        end_date="20260419",
        adjust="qfq"
    )
    
    print(f"✅ 成功获取 {len(df)} 条记录")
    print(f"\n数据预览:")
    print(df.head())
    print(f"\n数据列: {list(df.columns)}")
    print(f"时间范围: {df['日期'].min()} 至 {df['日期'].max()}")
    
    # 保存为 CSV
    output_file = "./akshare_data/daily_300033.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✅ 数据已保存至: {output_file}")
    
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    print("\n建议:")
    print("1. 检查网络连接")
    print("2. 稍后重试（可能是临时网络问题）")
    print("3. 尝试其他股票代码")
