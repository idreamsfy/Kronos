#!/usr/bin/env python
"""
同花顺 (300033) 5分钟K线数据 Kronos-base 微调脚本
使用 Futu API 获取的5分钟数据进行模型微调
"""

import os
import sys
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, TensorDataset
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm
import safetensors.torch

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from model.kronos import Kronos, KronosTokenizer


class FiveMinFinetuneDataset(Dataset):
    """5分钟K线微调数据集"""
    
    def __init__(self, df, lookback=100, pred_len=20):
        """
        Args:
            df: DataFrame with OHLCV data (5分钟K线)
            lookback: 历史窗口大小 (默认100个5分钟 ≈ 8小时)
            pred_len: 预测长度 (默认20个5分钟 ≈ 1.5小时)
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
        
        print(f"✅ 5分钟数据集创建完成:")
        print(f"   - 总记录数: {len(df):,}")
        print(f"   - 样本数: {len(self):,}")
        print(f"   - Lookback: {lookback} 个5分钟 (约{lookback/48*2:.1f}天)")
        print(f"   - Pred_len: {pred_len} 个5分钟 (约{pred_len/48*2:.1f}天)")
    
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


def finetune_kronos_5min():
    """主微调函数"""
    
    print("=" * 70)
    print("🚀 开始同花顺 (300033) 5分钟K线 Kronos-base 微调")
    print("=" * 70)
    print()
    
    # ==================== 配置参数 ====================
    STOCK_CODE = '300033'
    DATA_FILE = "./data/raw/futu/5min_300033.csv"  # 5分钟数据
    MODEL_PATH = "./model/pretrained_models/Kronos-base"
    TOKENIZER_PATH = "./model/pretrained_models/Kronos-Tokenizer-base"
    
    LOOKBACK = 100      # 100个5分钟 ≈ 8小时交易数据
    PRED_LEN = 20       # 预测20个5分钟 ≈ 1.5小时
    BATCH_SIZE = 8      # 批次大小
    EPOCHS = 5          # 训练轮数
    LEARNING_RATE = 1e-5  # 学习率
    WEIGHT_DECAY = 0.01
    DEVICE = 'mps' if torch.backends.mps.is_available() else 'cpu'
    
    OUTPUT_DIR = f"./outputs/models/finetune_{STOCK_CODE}_5min_base"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    LOG_FILE = f"./outputs/logs/finetune_5min_{STOCK_CODE}.log"
    os.makedirs("./outputs/logs", exist_ok=True)
    
    print(f"📋 配置信息:")
    print(f"   - 数据文件: {DATA_FILE}")
    print(f"   - 模型路径: {MODEL_PATH}")
    print(f"   - Tokenizer: {TOKENIZER_PATH}")
    print(f"   - Lookback: {LOOKBACK} 个5分钟")
    print(f"   - Pred_len: {PRED_LEN} 个5分钟")
    print(f"   - Batch size: {BATCH_SIZE}")
    print(f"   - Epochs: {EPOCHS}")
    print(f"   - Learning rate: {LEARNING_RATE}")
    print(f"   - Device: {DEVICE}")
    print(f"   - 输出目录: {OUTPUT_DIR}")
    print()
    
    # ==================== 1. 加载数据 ====================
    print("1. 加载5分钟K线数据...")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ 数据文件不存在: {DATA_FILE}")
        print("请先运行: python scripts/data/fetch_300033_futu.py")
        return
    
    df = pd.read_csv(DATA_FILE)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    print(f"   ✅ 数据加载成功: {len(df):,} 条记录")
    print(f"   时间范围: {df['timestamps'].min()} 至 {df['timestamps'].max()}")
    print(f"   收盘价范围: ¥{df['close'].min():.2f} - ¥{df['close'].max():.2f}")
    print()
    
    # ==================== 2. 创建数据集 ====================
    print("2. 创建数据集...")
    
    dataset = FiveMinFinetuneDataset(df, lookback=LOOKBACK, pred_len=PRED_LEN)
    
    if len(dataset) == 0:
        print("❌ 数据集为空，请检查数据量是否足够")
        return
    
    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,  # macOS 必须为 0
        collate_fn=collate_fn,
        pin_memory=False
    )
    
    print(f"   ✅ DataLoader 创建完成: {len(dataloader)} 个批次")
    print()
    
    # ==================== 3. 加载模型和 Tokenizer ====================
    print("3. 加载预训练模型和 Tokenizer...")
    
    try:
        tokenizer = KronosTokenizer.from_pretrained(TOKENIZER_PATH)
        model = Kronos.from_pretrained(MODEL_PATH)
        
        # 将 tokenizer 也移动到设备上
        tokenizer.to(DEVICE)
        model.to(DEVICE)
        
        print(f"   ✅ 模型加载成功")
        print(f"   参数量: {sum(p.numel() for p in model.parameters()):,}")
        print(f"   设备: {DEVICE}")
    except Exception as e:
        print(f"   ❌ 模型加载失败: {e}")
        return
    
    print()
    
    # ==================== 4. 设置优化器 ====================
    print("4. 设置优化器和学习率调度器...")
    
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )
    
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=EPOCHS * len(dataloader),
        eta_min=LEARNING_RATE * 0.01
    )
    
    criterion = nn.CrossEntropyLoss()
    
    print(f"   ✅ 优化器: AdamW (lr={LEARNING_RATE}, weight_decay={WEIGHT_DECAY})")
    print(f"   ✅ 调度器: CosineAnnealingLR")
    print(f"   ✅ 损失函数: CrossEntropyLoss")
    print()
    
    # ==================== 5. 预编码数据（加速训练）====================
    print("5. 预编码数据... (这可能需要几分钟)")
    print("   提示: 将原始数据转换为 token 序列，避免重复编码")
    
    encoded_data = []
    for i in tqdm(range(len(dataset)), desc="编码进度"):
        sample = dataset[i]
        x_raw = sample['x'].unsqueeze(0).to(DEVICE)
        y_raw = sample['y'].unsqueeze(0).to(DEVICE)
        
        # 拼接输入和目标用于自回归训练
        xy_raw = torch.cat([x_raw, y_raw], dim=1)
        
        # 使用 tokenizer 编码（half=True 返回 [s1, s2]）
        with torch.no_grad():
            tokens = tokenizer.encode(xy_raw, half=True)
        
        # 准备输入和目标（shifted by 1 for next token prediction）
        input_s1 = tokens[0][:, :-1].cpu()
        input_s2 = tokens[1][:, :-1].cpu()
        target_s1 = tokens[0][:, 1:].cpu()
        target_s2 = tokens[1][:, 1:].cpu()
        
        encoded_data.append({
            'input_s1': input_s1,
            'input_s2': input_s2,
            'target_s1': target_s1,
            'target_s2': target_s2
        })
    
    # 创建 TensorDataset
    input_s1_tensor = torch.cat([d['input_s1'] for d in encoded_data])
    input_s2_tensor = torch.cat([d['input_s2'] for d in encoded_data])
    target_s1_tensor = torch.cat([d['target_s1'] for d in encoded_data])
    target_s2_tensor = torch.cat([d['target_s2'] for d in encoded_data])
    
    tensor_dataset = TensorDataset(input_s1_tensor, input_s2_tensor, target_s1_tensor, target_s2_tensor)
    encoded_dataloader = DataLoader(tensor_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    
    print(f"   ✅ 预编码完成: {len(tensor_dataset)} 个样本")
    print()
    
    # ==================== 6. 开始训练 ====================
    print("6. 开始微调训练...")
    print("-" * 70)
    
    best_loss = float('inf')
    start_time = time.time()
    
    # 打开日志文件
    log_file = open(LOG_FILE, 'w', encoding='utf-8')
    
    for epoch in range(EPOCHS):
        epoch_start = time.time()
        model.train()
        total_loss = 0
        total_s1_loss = 0
        total_s2_loss = 0
        num_batches = 0
        
        progress_bar = tqdm(encoded_dataloader, desc=f"Epoch {epoch+1}/{EPOCHS}")
        
        for batch_idx, (input_s1_batch, input_s2_batch, target_s1_batch, target_s2_batch) in enumerate(progress_bar):
            # 移动到设备
            input_s1_batch = input_s1_batch.to(DEVICE)
            input_s2_batch = input_s2_batch.to(DEVICE)
            target_s1_batch = target_s1_batch.to(DEVICE)
            target_s2_batch = target_s2_batch.to(DEVICE)
            
            # 前向传播
            s1_logits, s2_logits = model(
                s1_ids=input_s1_batch,
                s2_ids=input_s2_batch,
                use_teacher_forcing=False
            )
            
            # 计算损失
            s1_loss = criterion(s1_logits.reshape(-1, s1_logits.size(-1)), target_s1_batch.reshape(-1))
            s2_loss = criterion(s2_logits.reshape(-1, s2_logits.size(-1)), target_s2_batch.reshape(-1))
            loss = s1_loss + s2_loss
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            scheduler.step()
            
            # 统计
            total_loss += loss.item()
            total_s1_loss += s1_loss.item()
            total_s2_loss += s2_loss.item()
            num_batches += 1
            
            # 更新进度条
            avg_loss = total_loss / num_batches
            progress_bar.set_postfix({
                'loss': f"{loss.item():.4f}",
                'avg_loss': f"{avg_loss:.4f}"
            })
        
        # Epoch 结束
        epoch_time = time.time() - epoch_start
        avg_loss = total_loss / num_batches
        avg_s1_loss = total_s1_loss / num_batches
        avg_s2_loss = total_s2_loss / num_batches
        current_lr = optimizer.param_groups[0]['lr']
        
        log_msg = f"Epoch [{epoch+1}/{EPOCHS}] Loss: {avg_loss:.4f} (S1: {avg_s1_loss:.4f}, S2: {avg_s2_loss:.4f}) | Time: {epoch_time:.1f}s | LR: {current_lr:.6f}"
        print(log_msg)
        log_file.write(log_msg + "\n")
        log_file.flush()
        
        # 保存最佳模型
        if avg_loss < best_loss:
            best_loss = avg_loss
            save_path = f"{OUTPUT_DIR}/best_model"
            os.makedirs(save_path, exist_ok=True)
            
            # 保存模型
            model.save_pretrained(save_path)
            tokenizer.save_pretrained(save_path)
            
            print(f"   ✅ 保存最佳模型 (Loss: {best_loss:.4f})")
            log_file.write(f"   ✅ 保存最佳模型 (Loss: {best_loss:.4f})\n")
            log_file.flush()
        
        # 每2个epoch保存检查点
        if (epoch + 1) % 2 == 0:
            checkpoint_path = f"{OUTPUT_DIR}/checkpoint_epoch_{epoch+1}"
            os.makedirs(checkpoint_path, exist_ok=True)
            model.save_pretrained(checkpoint_path)
            tokenizer.save_pretrained(checkpoint_path)
            print(f"   💾 保存检查点: {checkpoint_path}")
    
    log_file.close()
    
    # ==================== 7. 训练总结 ====================
    total_time = time.time() - start_time
    
    print()
    print("=" * 70)
    print("🎉 微调完成！")
    print("=" * 70)
    print()
    print(f"📊 训练总结:")
    print(f"   - 总耗时: {total_time/3600:.2f} 小时 ({total_time/60:.1f} 分钟)")
    print(f"   - 最佳损失: {best_loss:.4f}")
    print(f"   - 模型保存至: {OUTPUT_DIR}/best_model")
    print()
    print(f"📁 输出文件:")
    print(f"   - 最佳模型: {OUTPUT_DIR}/best_model/")
    print(f"   - 检查点: {OUTPUT_DIR}/checkpoint_epoch_*/")
    print(f"   - 训练日志: {LOG_FILE}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        finetune_kronos_5min()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断训练")
    except Exception as e:
        print(f"\n\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
