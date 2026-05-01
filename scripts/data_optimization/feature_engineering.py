"""
特征工程脚本 - 添加技术指标和时间特征
适配: AMD EPYC + 64GB内存
"""
import pandas as pd
import numpy as np
import os
import logging

# 配置日志
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/feature_engineering.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def calculate_technical_indicators(df):
    """计算技术指标"""
    
    logger.info("计算技术指标...")
    
    # 1. 移动平均线 (MA)
    for period in [5, 10, 20, 30, 60]:
        df[f'MA{period}'] = df['close'].rolling(window=period).mean()
        logger.info(f"  计算 MA{period}")
    
    # 2. 指数移动平均线 (EMA)
    for period in [12, 26]:
        df[f'EMA{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        logger.info(f"  计算 EMA{period}")
    
    # 3. MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    logger.info("  计算 MACD")
    
    # 4. RSI (相对强弱指标)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    logger.info("  计算 RSI")
    
    # 5. 布林带 (Bollinger Bands)
    ma20 = df['close'].rolling(window=20).mean()
    std20 = df['close'].rolling(window=20).std()
    df['BB_upper'] = ma20 + (std20 * 2)
    df['BB_lower'] = ma20 - (std20 * 2)
    df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / ma20
    logger.info("  计算 Bollinger Bands")
    
    # 6. ATR (平均真实波幅)
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = true_range.rolling(window=14).mean()
    logger.info("  计算 ATR")
    
    # 7. 成交量指标
    if 'volume' in df.columns:
        df['volume_MA5'] = df['volume'].rolling(window=5).mean()
        df['volume_MA20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_MA20']
        logger.info("  计算成交量指标")
    
    # 8. 价格变化率
    for period in [1, 5, 10, 20]:
        df[f'return_{period}'] = df['close'].pct_change(periods=period)
        logger.info(f"  计算 {period}期收益率")
    
    # 9. 波动率
    df['volatility_5'] = df['return_1'].rolling(window=5).std()
    df['volatility_20'] = df['return_1'].rolling(window=20).std()
    logger.info("  计算波动率")
    
    return df

def add_time_features(df):
    """添加时间特征"""
    
    logger.info("添加时间特征...")
    
    # 确保有时间列
    time_col = None
    if 'timestamp' in df.columns:
        time_col = 'timestamp'
    elif 'time' in df.columns:
        time_col = 'time'
    
    if time_col is None:
        logger.warning("未找到时间列，跳过时间特征")
        return df
    
    # 转换为datetime
    df[time_col] = pd.to_datetime(df[time_col])
    
    # 提取时间特征
    df['hour'] = df[time_col].dt.hour
    df['minute'] = df[time_col].dt.minute
    df['day_of_week'] = df[time_col].dt.dayofweek
    df['day_of_month'] = df[time_col].dt.day
    df['month'] = df[time_col].dt.month
    df['quarter'] = df[time_col].dt.quarter
    
    # 是否为交易日（周一到周五）
    df['is_trading_day'] = (df['day_of_week'] < 5).astype(int)
    
    # 时间段标记
    def get_time_period(hour):
        if 9 <= hour < 10:
            return 0  # 开盘
        elif 10 <= hour < 12:
            return 1  # 上午
        elif 13 <= hour < 14:
            return 2  # 下午开盘
        elif 14 <= hour < 15:
            return 3  # 尾盘
        else:
            return 4  # 其他
    
    df['time_period'] = df['hour'].apply(get_time_period)
    
    logger.info("  添加小时、分钟、星期、月份等特征")
    
    return df

def engineer_features(input_path='data/raw/futu/5min_300033_augmented.csv',
                      output_path='data/raw/futu/5min_300033_with_features.csv'):
    """
    完整的特征工程流程
    
    Args:
        input_path: 输入数据路径
        output_path: 输出数据路径
    """
    
    logger.info("=" * 80)
    logger.info("开始特征工程")
    logger.info("=" * 80)
    
    # 读取数据
    if not os.path.exists(input_path):
        logger.error(f"文件不存在: {input_path}")
        return False
    
    logger.info(f"读取数据: {input_path}")
    df = pd.read_csv(input_path)
    logger.info(f"原始数据量: {len(df)} 行, 列数: {len(df.columns)}")
    
    # 1. 计算技术指标
    df = calculate_technical_indicators(df)
    
    # 2. 添加时间特征
    df = add_time_features(df)
    
    # 3. 处理缺失值（技术指标计算会产生NaN）
    initial_rows = len(df)
    df = df.dropna()
    dropped_rows = initial_rows - len(df)
    
    logger.info(f"\n{'='*80}")
    logger.info("缺失值处理")
    logger.info(f"{'='*80}")
    logger.info(f"删除了 {dropped_rows} 行包含NaN的数据")
    logger.info(f"剩余数据量: {len(df)} 行")
    
    # 4. 保存结果
    df.to_csv(output_path, index=False)
    
    logger.info(f"\n{'='*80}")
    logger.info("特征工程完成")
    logger.info(f"{'='*80}")
    logger.info(f"最终列数: {len(df.columns)}")
    logger.info(f"新增特征数: {len(df.columns) - 6}")  # 假设原始有6列
    logger.info(f"数据已保存至: {output_path}")
    logger.info(f"\n新增特征列表:")
    
    # 列出新增的特征
    base_cols = ['open', 'high', 'low', 'close', 'volume', 'timestamp', 'time']
    new_features = [col for col in df.columns if col not in base_cols]
    for feat in new_features:
        logger.info(f"  - {feat}")
    
    logger.info("=" * 80)
    
    return True

if __name__ == '__main__':
    try:
        engineer_features()
    except Exception as e:
        logger.error(f"特征工程失败: {e}", exc_info=True)
        raise
