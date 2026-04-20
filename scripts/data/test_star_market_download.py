# coding=utf-8
"""
测试科创板数据下载功能
只下载前3只股票作为测试
使用掘金量化API
"""
from batch_download_star_market import batch_download_star_stocks

if __name__ == '__main__':
    print("=" * 80)
    print("测试科创板数据下载（前3只股票）")
    print("=" * 80)
    
    # 测试模式：只下载前3只股票
    batch_download_star_stocks(
        years=5,        # 5年数据
        delay=2,        # 2秒间隔
        max_stocks=3    # 只下载3只
    )
    
    print("\n✅ 测试完成！")
    print("\n如果测试成功，可以修改 main() 函数中的 max_stocks=None 来下载全部股票")
