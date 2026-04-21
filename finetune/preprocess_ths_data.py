"""
同花顺 (300033) 数据预处理脚本
将 CSV 数据转换为训练所需的格式
"""

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# 导入配置
import importlib.util
spec = importlib.util.spec_from_file_location("ths_config", os.path.join(project_root, "config", "ths_300033_config.py"))
ths_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ths_config)
config = ths_config.config


class ThsDataset(Dataset):
    """同花顺数据集"""
    
    def __init__(self, data_df, lookback=100, predict_len=20, mode='train'):
        """
        Args:
            data_df: DataFrame with columns ['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']
            lookback: Number of historical time steps
            predict_len: Number of future time steps to predict
            mode: 'train', 'val', or 'test'
        """
        self.lookback = lookback
        self.predict_len = predict_len
        self.mode = mode
        
        # 提取特征
        self.features = data_df[config.feature_list].values.astype(np.float32)
        self.timestamps = data_df['timestamps'].values
        
        # 归一化
        self.mean = np.mean(self.features, axis=0)
        self.std = np.std(self.features, axis=0) + 1e-8
        self.normalized_features = (self.features - self.mean) / self.std
        
        # 生成样本索引
        self.sample_indices = []
        total_len = len(self.normalized_features)
        
        for i in range(total_len - lookback - predict_len + 1):
            self.sample_indices.append(i)
        
        print(f"[{mode.upper()}] Created {len(self.sample_indices)} samples")
    
    def __len__(self):
        return len(self.sample_indices)
    
    def __getitem__(self, idx):
        start_idx = self.sample_indices[idx]
        end_idx = start_idx + self.lookback
        pred_end_idx = end_idx + self.predict_len
        
        # 输入序列
        x = self.normalized_features[start_idx:end_idx]
        
        # 目标序列
        y = self.normalized_features[end_idx:pred_end_idx]
        
        return {
            'x': torch.FloatTensor(x),
            'y': torch.FloatTensor(y)
        }


def load_and_split_data():
    """加载并分割数据"""
    
    print("=" * 70)
    print("加载同花顺 (300033) 数据")
    print("=" * 70)
    print()
    
    # 检查文件是否存在
    if not os.path.exists(config.data_file):
        print(f"❌ 错误: 数据文件不存在: {config.data_file}")
        return None, None, None
    
    # 加载数据
    print(f"📂 加载数据: {config.data_file}")
    df = pd.read_csv(config.data_file)
    
    # 处理时间戳
    if 'timestamps' not in df.columns and 'date' in df.columns:
        df['timestamps'] = pd.to_datetime(df['date'])
    elif 'timestamps' in df.columns:
        df['timestamps'] = pd.to_datetime(df['timestamps'])
    else:
        print("❌ 错误: 找不到时间戳列")
        return None, None, None
    
    # 排序
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    print(f"✅ 数据加载成功")
    print(f"   总行数: {len(df)}")
    print(f"   时间范围: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
    print(f"   特征列: {config.feature_list}")
    print()
    
    # 分割数据
    total_len = len(df)
    train_end = int(total_len * config.train_ratio)
    val_end = int(total_len * (config.train_ratio + config.val_ratio))
    
    train_df = df[:train_end]
    val_df = df[train_end:val_end]
    test_df = df[val_end:]
    
    print(f"📊 数据分割:")
    print(f"   训练集: {len(train_df)} 行 ({config.train_ratio*100:.0f}%)")
    print(f"   验证集: {len(val_df)} 行 ({config.val_ratio*100:.0f}%)")
    print(f"   测试集: {len(test_df)} 行 ({config.test_ratio*100:.0f}%)")
    print()
    
    # 创建数据集
    print("创建数据集...")
    train_dataset = ThsDataset(train_df, config.lookback_window, config.predict_window, 'train')
    val_dataset = ThsDataset(val_df, config.lookback_window, config.predict_window, 'val')
    test_dataset = ThsDataset(test_df, config.lookback_window, config.predict_window, 'test')
    
    print()
    print("=" * 70)
    print("✅ 数据预处理完成！")
    print("=" * 70)
    
    return train_dataset, val_dataset, test_dataset


if __name__ == "__main__":
    train_dataset, val_dataset, test_dataset = load_and_split_data()
    
    if train_dataset is not None:
        print(f"\n测试数据加载...")
        sample = train_dataset[0]
        print(f"样本形状:")
        print(f"  x: {sample['x'].shape}")
        print(f"  y: {sample['y'].shape}")
        print(f"  x_timestamp: {len(sample['x_timestamp'])}")
        print(f"  y_timestamp: {len(sample['y_timestamp'])}")
