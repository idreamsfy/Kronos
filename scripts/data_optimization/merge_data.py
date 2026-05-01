"""
数据合并脚本 - 合并历史数据和新数据
适配: AMD EPYC + 64GB内存 + RTX 5880 Ada
"""
import pandas as pd
import os
from pathlib import Path
import logging

# 配置日志
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_merge.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def merge_historical_and_new_data():
    """合并历史数据和新数据"""
    
    logger.info("=" * 80)
    logger.info("开始数据合并任务")
    logger.info("=" * 80)
    
    # 文件路径
    historical_path = 'data/raw/futu/5min_300033.csv'
    new_path = 'data/raw/futu/5min_300033_2026-04-27_2026-04-30.csv'
    output_path = 'data/raw/futu/5min_300033_updated.csv'
    
    # 检查文件是否存在
    if not os.path.exists(historical_path):
        raise FileNotFoundError(f"历史数据文件不存在: {historical_path}")
    
    if not os.path.exists(new_path):
        raise FileNotFoundError(f"新数据文件不存在: {new_path}")
    
    # 读取历史数据
    logger.info("\n1. 读取历史数据...")
    historical_df = pd.read_csv(historical_path)
    logger.info(f"   历史数据: {len(historical_df):,} 条")
    logger.info(f"   时间范围: {historical_df['timestamps'].iloc[0]} 到 {historical_df['timestamps'].iloc[-1]}")
    
    # 读取新数据
    logger.info("\n2. 读取新数据...")
    new_df = pd.read_csv(new_path)
    logger.info(f"   新数据: {len(new_df):,} 条")
    logger.info(f"   时间范围: {new_df['timestamps'].iloc[0]} 到 {new_df['timestamps'].iloc[-1]}")
    
    # 转换时间格式
    logger.info("\n3. 转换时间格式...")
    historical_df['timestamps'] = pd.to_datetime(historical_df['timestamps'])
    new_df['timestamps'] = pd.to_datetime(new_df['timestamps'])
    
    # 合并数据
    logger.info("\n4. 合并数据...")
    combined_df = pd.concat([historical_df, new_df], ignore_index=True)
    before_dedup = len(combined_df)
    logger.info(f"   合并后（去重前）: {before_dedup:,} 条")
    
    # 去重（基于时间戳）
    logger.info("\n5. 去除重复数据...")
    combined_df = combined_df.drop_duplicates(subset=['timestamps'], keep='last')
    after_dedup = len(combined_df)
    removed = before_dedup - after_dedup
    logger.info(f"   移除重复记录: {removed} 条")
    logger.info(f"   去重后: {after_dedup:,} 条")
    
    # 按时间排序
    logger.info("\n6. 按时间排序...")
    combined_df = combined_df.sort_values('timestamps').reset_index(drop=True)
    
    # 保存合并后的数据
    logger.info("\n7. 保存合并数据...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined_df.to_csv(output_path, index=False)
    logger.info(f"   ✅ 保存至: {output_path}")
    
    # 输出统计信息
    logger.info("\n" + "=" * 80)
    logger.info("合并完成统计")
    logger.info("=" * 80)
    logger.info(f"原始历史数据: {len(historical_df):,} 条")
    logger.info(f"新增数据: {len(new_df):,} 条")
    logger.info(f"移除重复: {removed} 条")
    logger.info(f"最终数据量: {len(combined_df):,} 条")
    logger.info(f"数据增长率: {(len(combined_df) - len(historical_df)) / len(historical_df) * 100:.2f}%")
    logger.info(f"时间范围: {combined_df['timestamps'].min()} 到 {combined_df['timestamps'].max()}")
    logger.info(f"总交易日数: {combined_df['timestamps'].dt.date.nunique()} 天")
    logger.info("=" * 80)
    
    return combined_df

if __name__ == "__main__":
    try:
        merged_data = merge_historical_and_new_data()
        logger.info("\n✅ 数据合并成功完成！")
    except Exception as e:
        logger.error(f"\n❌ 数据合并失败: {e}")
        raise
