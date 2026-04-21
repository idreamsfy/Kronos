#!/usr/bin/env python
"""
同花顺 (300033) Kronos-base 真正微调脚本
使用 Tokenizer 编码数据，然后微调模型
"""

import os
import sys
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from model.kronos import Kronos, KronosTokenizer


class ThsFinetuneDataset(Dataset):
    """同花顺微调数据集 - 简化版"""
    
    def __init__(self, df, lookback=100, pred_len=20):
        """
        Args:
            df: DataFrame with OHLCV data
            lookback: Historical window size
            pred_len: Prediction length
        """
        self.lookback = lookback
        self.pred_len = pred_len
        
        # 准备特征
        feature_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
        self.features = df[feature_cols].values.astype(np.float32)
        
        # 归一化
        self.mean = np.mean(self.features, axis=0)
        self.std = np.std(self.features, axis=0) + 1e-8
        self.normalized = (self.features - self.mean) / self.std
        
        print(f"✅ 数据集创建完成: {len(self)} 个样本")
    
    def __len__(self):
        return max(0, len(self.normalized) - self.lookback - self.pred_len)
    
    def __getitem__(self, idx):
        # 输入序列
        x_data = self.normalized[idx:idx+self.lookback]
        
        # 目标序列
        y_data = self.normalized[idx+self.lookback:idx+self.lookback+self.pred_len]
        
        return {
            'x': torch.FloatTensor(x_data),
            'y': torch.FloatTensor(y_data)
        }


def collate_fn(batch):
    """自定义 collate 函数，过滤 None 值"""
    batch = [b for b in batch if b is not None]
    if len(batch) == 0:
        return None
    
    return {
        key: torch.stack([item[key] for item in batch])
        for key in batch[0].keys()
    }


def finetune_kronos():
    """主微调函数"""
    
    print("=" * 70)
    print("🚀 开始同花顺 (300033) Kronos-base 真正微调")
    print("=" * 70)
    print()
    
    # ==================== 配置参数 ====================
    STOCK_CODE = '300033'
    DATA_FILE = f"./data/raw/akshare/daily_{STOCK_CODE}.csv"
    MODEL_PATH = "./model/pretrained_models/Kronos-base"
    TOKENIZER_PATH = "./model/pretrained_models/Kronos-Tokenizer-base"
    
    LOOKBACK = 100
    PRED_LEN = 20
    BATCH_SIZE = 8  # 更小的批次
    EPOCHS = 5  # 减少 epochs 以快速测试
    LEARNING_RATE = 1e-5  # 较小的学习率用于微调
    WEIGHT_DECAY = 0.01
    DEVICE = 'cpu'  # 强制使用 CPU（后台进程MPS不可用）
    
    OUTPUT_DIR = f"./outputs/models/finetune_{STOCK_CODE}_base_real"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"📊 数据文件: {DATA_FILE}")
    print(f"🤖 模型: Kronos-base (102M)")
    print(f"⚙️  设备: {DEVICE}")
    print(f"📈 学习率: {LEARNING_RATE}")
    print(f"🔄 Epochs: {EPOCHS}")
    print(f"📦 Batch Size: {BATCH_SIZE}")
    print()
    
    # ==================== 1. 加载数据 ====================
    print("1. 加载数据...")
    if not os.path.exists(DATA_FILE):
        print(f"❌ 文件不存在: {DATA_FILE}")
        return
    
    df = pd.read_csv(DATA_FILE)
    if 'timestamps' not in df.columns and 'date' in df.columns:
        df['timestamps'] = pd.to_datetime(df['date'])
    elif 'timestamps' in df.columns:
        df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    df = df.sort_values('timestamps').reset_index(drop=True)
    print(f"   ✅ 数据加载: {len(df)} 行")
    print(f"   范围: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
    print()
    
    # ==================== 2. 加载模型和 Tokenizer ====================
    print("2. 加载预训练模型...")
    try:
        tokenizer = KronosTokenizer.from_pretrained(TOKENIZER_PATH)
        model = Kronos.from_pretrained(MODEL_PATH)
        model.to(DEVICE)
        tokenizer.to(DEVICE)
        
        print(f"   ✅ 模型加载成功")
        print(f"   参数量: {sum(p.numel() for p in model.parameters()):,}")
        print(f"   可训练参数: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
        
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # ==================== 3. 创建数据集 ====================
    print("3. 创建数据集...")
    dataset = ThsFinetuneDataset(df, LOOKBACK, PRED_LEN)
    
    if len(dataset) == 0:
        print("   ❌ 数据集为空")
        return
    
    # 预编码数据（加速训练）
    print("   预编码数据... (这可能需要几分钟)")
    encoded_data = []
    for i in tqdm(range(len(dataset)), desc="编码"):
        sample = dataset[i]
        x_raw = sample['x'].unsqueeze(0).to(DEVICE)
        y_raw = sample['y'].unsqueeze(0).to(DEVICE)
        
        # 拼接并编码
        xy_raw = torch.cat([x_raw, y_raw], dim=1)
        with torch.no_grad():
            tokens = tokenizer.encode(xy_raw, half=True)
        
        # Shifted sequence
        encoded_data.append({
            'input_s1': tokens[0][:, :-1].cpu(),
            'input_s2': tokens[1][:, :-1].cpu(),
            'target_s1': tokens[0][:, 1:].cpu(),
            'target_s2': tokens[1][:, 1:].cpu()
        })
    
    print(f"   ✅ 预编码完成: {len(encoded_data)} 个样本")
    
    # 创建简单的 DataLoader
    from torch.utils.data import TensorDataset
    
    input_s1_tensor = torch.cat([d['input_s1'] for d in encoded_data])
    input_s2_tensor = torch.cat([d['input_s2'] for d in encoded_data])
    target_s1_tensor = torch.cat([d['target_s1'] for d in encoded_data])
    target_s2_tensor = torch.cat([d['target_s2'] for d in encoded_data])
    
    tensor_dataset = TensorDataset(input_s1_tensor, input_s2_tensor, target_s1_tensor, target_s2_tensor)
    
    dataloader = DataLoader(
        tensor_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )
    
    print(f"   ✅ DataLoader 创建: {len(dataloader)} batches")
    print()
    
    # ==================== 4. 设置优化器 ====================
    print("4. 设置优化器...")
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )
    
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=EPOCHS,
        eta_min=1e-6
    )
    
    criterion = nn.CrossEntropyLoss()
    
    print(f"   ✅ AdamW (lr={LEARNING_RATE})")
    print(f"   ✅ CosineAnnealingLR")
    print()
    
    # ==================== 5. 训练循环 ====================
    print("5. 开始微调训练...")
    print("=" * 70)
    
    best_loss = float('inf')
    training_start = time.time()
    
    for epoch in range(1, EPOCHS + 1):
        epoch_start = time.time()
        model.train()
        
        total_loss = 0
        total_s1_loss = 0
        total_s2_loss = 0
        num_batches = 0
        
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch}/{EPOCHS}")
        
        for batch_idx, batch in enumerate(progress_bar):
            try:
                # 获取预编码的数据
                input_s1 = batch[0].to(DEVICE)
                input_s2 = batch[1].to(DEVICE)
                target_s1 = batch[2].to(DEVICE)
                target_s2 = batch[3].to(DEVICE)
                
                # 前向传播
                optimizer.zero_grad()
                
                s1_logits, s2_logits = model(
                    s1_ids=input_s1,
                    s2_ids=input_s2,
                    use_teacher_forcing=False
                )
                
                # 计算损失
                s1_loss = criterion(
                    s1_logits.reshape(-1, s1_logits.size(-1)),
                    target_s1.reshape(-1)
                )
                
                s2_loss = criterion(
                    s2_logits.reshape(-1, s2_logits.size(-1)),
                    target_s2.reshape(-1)
                )
                
                loss = s1_loss + s2_loss
                
                # 反向传播
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                
                total_loss += loss.item()
                total_s1_loss += s1_loss.item()
                total_s2_loss += s2_loss.item()
                num_batches += 1
                
                # 更新进度条
                avg_loss = total_loss / num_batches
                progress_bar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'avg_loss': f'{avg_loss:.4f}'
                })
                
            except Exception as e:
                if batch_idx < 3:
                    print(f"\n❌ Batch {batch_idx} 错误: {e}")
                    import traceback
                    traceback.print_exc()
                continue
        
        # Epoch 结束
        avg_loss = total_loss / max(num_batches, 1)
        avg_s1_loss = total_s1_loss / max(num_batches, 1)
        avg_s2_loss = total_s2_loss / max(num_batches, 1)
        epoch_time = time.time() - epoch_start
        
        scheduler.step()
        
        print(f"\nEpoch [{epoch}/{EPOCHS}] "
              f"Loss: {avg_loss:.4f} "
              f"(S1: {avg_s1_loss:.4f}, S2: {avg_s2_loss:.4f}) | "
              f"Time: {epoch_time:.1f}s | "
              f"LR: {scheduler.get_last_lr()[0]:.6f}")
        
        # 保存最佳模型
        if avg_loss < best_loss:
            best_loss = avg_loss
            save_path = os.path.join(OUTPUT_DIR, 'best_model')
            os.makedirs(save_path, exist_ok=True)
            
            model.save_pretrained(save_path)
            tokenizer.save_pretrained(save_path)
            
            print(f"   ✅ 保存最佳模型 (Loss: {best_loss:.4f})")
        
        # 定期保存检查点
        if epoch % 2 == 0:
            checkpoint_path = os.path.join(OUTPUT_DIR, f'checkpoint_epoch_{epoch}')
            os.makedirs(checkpoint_path, exist_ok=True)
            model.save_pretrained(checkpoint_path)
            tokenizer.save_pretrained(checkpoint_path)
            print(f"   💾 保存检查点: Epoch {epoch}")
        
        print("-" * 70)
    
    # ==================== 6. 训练完成 ====================
    total_time = time.time() - training_start
    
    print()
    print("=" * 70)
    print("🎉 微调完成！")
    print("=" * 70)
    print(f"总耗时: {total_time/3600:.2f} 小时")
    print(f"最佳损失: {best_loss:.4f}")
    print(f"模型保存至: {OUTPUT_DIR}")
    print("=" * 70)
    print()
    print("📝 使用说明:")
    print(f"   从本地加载微调后的模型:")
    print(f"   model = Kronos.from_pretrained('{OUTPUT_DIR}/best_model')")
    print()


if __name__ == "__main__":
    finetune_kronos()
