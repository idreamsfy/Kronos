"""测试 mootdx 是否能获取数据"""
from mootdx.quotes import Quotes

print("测试 mootdx 数据获取...")
client = Quotes.factory(market='std')

test_stocks = [
    ('600519', 0, '贵州茅台'),
    ('000001', 1, '平安银行'),
    ('300059', 1, '东方财富'),
]

for code, market, name in test_stocks:
    try:
        klines = client.bars(symbol=code, market=market, frequency=9, offset=0, limit=5)
        if klines is not None and len(klines) > 0:
            print(f"✅ {code} ({name}): {len(klines)} 条记录")
            print(f"   列名: {list(klines.columns)}")
            print(f"   最新数据:\n{klines.head(1)}")
        else:
            print(f"❌ {code} ({name}): 无数据")
    except Exception as e:
        print(f"❌ {code} ({name}): {e}")
