"""
数据增强脚本 - 添加噪声和数据增强
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
        logging.FileHandler('logs/data_augmentation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def add_noise_to_data(input_path='data/raw/futu/5min_300033_balanced.csv',
                      output_path='data/raw/futu/5min_300033_augmented.csv',
                      noise_level=0.01):
    """
    添加高斯噪声进行数据增强
    
    Args:
        input_path: 输入数据路径
        output_path: 输出数据路径
        noise_level: 噪声水平（相对于价格的标准差比例）
    """
    
    logger.info("=" * 80)
    logger.info("开始数据增强处理")
    logger.info("=" * 80)
    
    # 读取数据
    if not os.path.exists(input_path):
        logger.error(f"文件不存在: {input_path}")
        return False
    
    logger.info(f"读取数据: {input_path}")
    df = pd.read_csv(input_path)
    logger.info(f"原始数据量: {len(df)} 行")
    
    # 复制数据用于增强
    df_augmented = df.copy()
    
    # 对价格列添加噪声
    price_cols = ['open', 'high', 'low', 'close']
    existing_price_cols = [col for col in price_cols if col in df.columns]
    
    logger.info(f"\n对以下价格列添加噪声: {existing_price_cols}")
    
    for col in existing_price_cols:
        # 计算噪声标准差
        std = df[col].std() * noise_level
        
        # 生成高斯噪声
        noise = np.random.normal(0, std, len(df))
        
        # 添加噪声
        df_augmented[col] = df[col] + noise
        
        logger.info(f"{col}: 标准差={std:.6f}, 噪声范围=[{noise.min():.6f}, {noise.max():.6f}]")
    
    # 确保high >= low, high >= open/close, low <= open/close
    if all(col in df_augmented.columns for col in ['high', 'low']):
        # 修正high和low
        df_augmented['high'] = df_augmented[['open', 'high', 'low', 'close']].max(axis=1)
        df_augmented['low'] = df_augmented[['open', 'high', 'low', 'close']].min(axis=1)
        logger.info("已修正high和low的合理性")
    
    # 保存增强后的数据
    df_augmented.to_csv(output_path, index=False)
    
    logger.info(f"\n{'='*80}")
    logger.info("数据增强完成")
    logger.info(f"{'='*80}")
    logger.info(f"增强后数据量: {len(df_augmented)} 行")
    logger.info(f"噪声水平: {noise_level}")
    logger.info(f"数据已保存至: {output_path}")
    logger.info("=" * 80)
    
    return True

def augment_by_sliding_window(input_path='data/raw/futu/5min_300033_balanced.csv',
                              output_path='data/raw/futu/5min_300033_window_augmented.csv',
                              window_size=100,
                              step_size=50):
    """
    通过滑动窗口创建重叠样本进行增强
    
    Args:
        input_path: 输入数据路径
        output_path: 输出数据路径
        window_size: 窗口大小
        step_size: 步长
    """
    
    logger.info("=" * 80)
    logger.info("开始滑动窗口数据增强")
    logger.info("=" * 80)
    
    # 读取数据
    if not os.path.exists(input_path):
        logger.error(f"文件不存在: {input_path}")
        return False
    
    logger.info(f"读取数据: {input_path}")
    df = pd.read_csv(input_path)
    logger.info(f"原始数据量: {len(df)} 行")
    
    # 创建滑动窗口样本
    augmented_samples = []
    
    for start_idx in range(0, len(df) - window_size + 1, step_size):
        end_idx = start_idx + window_size
        window_data = df.iloc[start_idx:end_idx].copy()
        augmented_samples.append(window_data)
    
    # 合并所有窗口样本
    df_augmented = pd.concat(augmented_samples, ignore_index=True)
    
    logger.info(f"\n{'='*80}")
    logger.info("滑动窗口增强完成")
    logger.info(f"{'='*80}")
    logger.info(f"窗口大小: {window_size}")
    logger.info(f"步长: {step_size}")
    logger.info(f"创建窗口数: {len(augmented_samples)}")
    logger.info(f"增强后数据量: {len(df_augmented)} 行")
    logger.info(f"相比原始数据增加: {len(df_augmented) - len(df)} 行 ({(len(df_augmented)/len(df)-1)*100:.2f}%)")
    logger.info(f"数据已保存至: {output_path}")
    logger.info("=" * 80)
    
    df_augmented.to_csv(output_path, index=False)
    
    return True

if __name__ == '__main__':
    try:
        # 先执行噪声增强
        add_noise_to_data()
        
        # 再执行滑动窗口增强（可选）
        # augment_by_sliding_window()
        
    except Exception as e:
        logger.error(f"增强失败: {e}", exc_info=True)
        raise
