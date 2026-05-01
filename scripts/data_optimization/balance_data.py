"""
数据平衡脚本 - 平衡涨跌样本
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
        logging.FileHandler('logs/data_balance.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def balance_data(input_path='data/raw/futu/5min_300033_updated.csv',
                 output_path='data/raw/futu/5min_300033_balanced.csv',
                 target_ratio=0.5):
    """
    平衡涨跌样本
    
    Args:
        input_path: 输入数据路径
        output_path: 输出数据路径
        target_ratio: 目标涨跌比例（默认0.5表示1:1）
    """
    
    logger.info("=" * 80)
    logger.info("开始数据平衡处理")
    logger.info("=" * 80)
    
    # 读取数据
    if not os.path.exists(input_path):
        logger.error(f"文件不存在: {input_path}")
        return False
    
    logger.info(f"读取数据: {input_path}")
    df = pd.read_csv(input_path)
    logger.info(f"原始数据量: {len(df)} 行")
    
    # 计算收益率
    if 'close' not in df.columns:
        logger.error("数据中缺少close列")
        return False
    
    df['returns'] = df['close'].pct_change()
    
    # 标记涨跌
    df['label'] = 0  # 0: 下跌或持平, 1: 上涨
    df.loc[df['returns'] > 0, 'label'] = 1
    
    # 统计涨跌分布
    positive_count = (df['label'] == 1).sum()
    negative_count = (df['label'] == 0).sum()
    total = len(df)
    
    logger.info(f"\n{'='*80}")
    logger.info("原始涨跌分布")
    logger.info(f"{'='*80}")
    logger.info(f"上涨样本: {positive_count} ({positive_count/total*100:.2f}%)")
    logger.info(f"下跌样本: {negative_count} ({negative_count/total*100:.2f}%)")
    
    # 判断是否需要平衡
    current_ratio = positive_count / total
    logger.info(f"\n当前上涨比例: {current_ratio:.4f}")
    logger.info(f"目标上涨比例: {target_ratio:.4f}")
    
    if abs(current_ratio - target_ratio) < 0.05:
        logger.info("涨跌分布已接近平衡，无需调整")
        df.to_csv(output_path, index=False)
        logger.info(f"数据已保存至: {output_path}")
        return True
    
    # 执行平衡策略
    logger.info("\n执行平衡策略...")
    
    positive_samples = df[df['label'] == 1]
    negative_samples = df[df['label'] == 0]
    
    if current_ratio < target_ratio:
        # 上涨样本不足，过采样上涨样本
        logger.info("上涨样本不足，进行过采样")
        
        oversample_count = int(negative_count * target_ratio / (1 - target_ratio)) - positive_count
        
        if oversample_count > 0:
            # 随机重复采样
            oversampled = positive_samples.sample(n=oversample_count, replace=True, random_state=42)
            df_balanced = pd.concat([df, oversampled], ignore_index=True)
            logger.info(f"添加了 {oversample_count} 个上涨样本")
        else:
            df_balanced = df.copy()
    
    else:
        # 下跌样本过多，欠采样下跌样本
        logger.info("下跌样本过多，进行欠采样")
        
        undersample_count = int(positive_count * (1 - target_ratio) / target_ratio)
        
        if undersample_count < negative_count:
            undersampled = negative_samples.sample(n=undersample_count, random_state=42)
            df_balanced = pd.concat([positive_samples, undersampled], ignore_index=True)
            logger.info(f"保留了 {undersample_count} 个下跌样本")
        else:
            df_balanced = df.copy()
    
    # 重新排序（按时间）
    if 'timestamp' in df_balanced.columns or 'time' in df_balanced.columns:
        time_col = 'timestamp' if 'timestamp' in df_balanced.columns else 'time'
        df_balanced = df_balanced.sort_values(time_col).reset_index(drop=True)
    
    # 删除临时列
    if 'returns' in df_balanced.columns:
        df_balanced = df_balanced.drop(columns=['returns'])
    if 'label' in df_balanced.columns:
        df_balanced = df_balanced.drop(columns=['label'])
    
    # 保存平衡后的数据
    df_balanced.to_csv(output_path, index=False)
    
    # 验证平衡效果
    logger.info(f"\n{'='*80}")
    logger.info("平衡后数据统计")
    logger.info(f"{'='*80}")
    logger.info(f"总行数: {len(df_balanced)}")
    logger.info(f"相比原始数据增加: {len(df_balanced) - len(df)} 行 ({(len(df_balanced)/len(df)-1)*100:.2f}%)")
    
    logger.info(f"\n数据已保存至: {output_path}")
    logger.info("=" * 80)
    logger.info("数据平衡完成")
    logger.info("=" * 80)
    
    return True

if __name__ == '__main__':
    try:
        balance_data()
    except Exception as e:
        logger.error(f"平衡失败: {e}", exc_info=True)
        raise
