"""
数据验证脚本 - 验证合并后的数据质量
适配: AMD EPYC + 64GB内存
"""
import pandas as pd
import numpy as np
import os
import logging
from pathlib import Path

# 配置日志
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_validation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_data_quality(data_path='data/raw/futu/5min_300033_updated.csv'):
    """验证数据质量"""
    
    logger.info("=" * 80)
    logger.info("开始数据质量验证")
    logger.info("=" * 80)
    
    # 检查文件是否存在
    if not os.path.exists(data_path):
        logger.error(f"文件不存在: {data_path}")
        return False
    
    # 读取数据
    logger.info(f"读取数据: {data_path}")
    df = pd.read_csv(data_path)
    
    logger.info(f"\n{'='*80}")
    logger.info("基本统计信息")
    logger.info(f"{'='*80}")
    logger.info(f"总行数: {len(df)}")
    logger.info(f"列数: {len(df.columns)}")
    logger.info(f"列名: {list(df.columns)}")
    
    # 检查缺失值
    logger.info(f"\n{'='*80}")
    logger.info("缺失值检查")
    logger.info(f"{'='*80}")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    for col in df.columns:
        if missing[col] > 0:
            logger.warning(f"{col}: {missing[col]} ({missing_pct[col]}%)")
        else:
            logger.info(f"{col}: 无缺失值 ✓")
    
    # 检查重复值
    logger.info(f"\n{'='*80}")
    logger.info("重复值检查")
    logger.info(f"{'='*80}")
    duplicates = df.duplicated().sum()
    logger.info(f"重复行数: {duplicates} ({duplicates/len(df)*100:.2f}%)")
    
    # 检查数据类型
    logger.info(f"\n{'='*80}")
    logger.info("数据类型检查")
    logger.info(f"{'='*80}")
    for col in df.columns:
        logger.info(f"{col}: {df[col].dtype}")
    
    # 检查数值范围
    logger.info(f"\n{'='*80}")
    logger.info("数值范围检查")
    logger.info(f"{'='*80}")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        logger.info(f"{col}:")
        logger.info(f"  最小值: {df[col].min():.4f}")
        logger.info(f"  最大值: {df[col].max():.4f}")
        logger.info(f"  平均值: {df[col].mean():.4f}")
        logger.info(f"  标准差: {df[col].std():.4f}")
    
    # 检查时间序列连续性
    if 'timestamp' in df.columns or 'time' in df.columns:
        time_col = 'timestamp' if 'timestamp' in df.columns else 'time'
        logger.info(f"\n{'='*80}")
        logger.info("时间序列连续性检查")
        logger.info(f"{'='*80}")
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(time_col).reset_index(drop=True)
        
        time_diffs = df[time_col].diff()
        median_diff = time_diffs.median()
        logger.info(f"时间间隔中位数: {median_diff}")
        logger.info(f"时间间隔标准差: {time_diffs.std()}")
        
        # 检测异常时间间隔
        abnormal = time_diffs[time_diffs > median_diff * 2]
        if len(abnormal) > 0:
            logger.warning(f"发现 {len(abnormal)} 个异常时间间隔")
        else:
            logger.info("时间序列连续性良好 ✓")
    
    # 检查价格合理性
    price_cols = ['open', 'high', 'low', 'close']
    existing_price_cols = [col for col in price_cols if col in df.columns]
    
    if existing_price_cols:
        logger.info(f"\n{'='*80}")
        logger.info("价格合理性检查")
        logger.info(f"{'='*80}")
        
        for idx in range(len(df)):
            row = df.iloc[idx]
            if 'high' in df.columns and 'low' in df.columns:
                if row['high'] < row['low']:
                    logger.warning(f"行 {idx}: high < low (high={row['high']}, low={row['low']})")
            
            if 'open' in df.columns and 'close' in df.columns:
                if 'high' in df.columns:
                    if row['open'] > row['high'] or row['close'] > row['high']:
                        logger.warning(f"行 {idx}: open/close > high")
                if 'low' in df.columns:
                    if row['open'] < row['low'] or row['close'] < row['low']:
                        logger.warning(f"行 {idx}: open/close < low")
    
    # 检查收益率分布
    if 'close' in df.columns:
        logger.info(f"\n{'='*80}")
        logger.info("收益率分布检查")
        logger.info(f"{'='*80}")
        
        returns = df['close'].pct_change().dropna()
        logger.info(f"平均收益率: {returns.mean():.6f}")
        logger.info(f"收益率标准差: {returns.std():.6f}")
        logger.info(f"最大单日涨幅: {returns.max():.4f} ({returns.max()*100:.2f}%)")
        logger.info(f"最大单日跌幅: {returns.min():.4f} ({returns.min()*100:.2f}%)")
        
        # 涨跌分布
        positive = (returns > 0).sum()
        negative = (returns < 0).sum()
        zero = (returns == 0).sum()
        total = len(returns)
        
        logger.info(f"\n涨跌分布:")
        logger.info(f"  上涨: {positive} ({positive/total*100:.2f}%)")
        logger.info(f"  下跌: {negative} ({negative/total*100:.2f}%)")
        logger.info(f"  持平: {zero} ({zero/total*100:.2f}%)")
    
    # 保存验证报告
    report_path = 'data/validation_report.txt'
    os.makedirs('data', exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"数据验证报告\n")
        f.write(f"生成时间: {pd.Timestamp.now()}\n")
        f.write(f"数据文件: {data_path}\n")
        f.write(f"总行数: {len(df)}\n")
        f.write(f"缺失值总数: {df.isnull().sum().sum()}\n")
        f.write(f"重复行数: {duplicates}\n")
    
    logger.info(f"\n验证报告已保存至: {report_path}")
    logger.info("=" * 80)
    logger.info("数据验证完成")
    logger.info("=" * 80)
    
    return True

if __name__ == '__main__':
    try:
        validate_data_quality()
    except Exception as e:
        logger.error(f"验证失败: {e}", exc_info=True)
        raise
