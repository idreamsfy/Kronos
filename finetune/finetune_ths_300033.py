#!/usr/bin/env python
"""
同花顺 (300033) 微调脚本
使用 Kronos-base 模型进行微调
"""

import os
import sys
import time
import torch
from torch.utils.data import DataLoader
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from model.kronos import Kronos, KronosTokenizer, KronosPredictor
from finetune.preprocess_ths_data import load_and_split_data

# 导入配置
import importlib.util
spec = importlib.util.spec_from_file_location("ths_config", os.path.join(project_root, "config", "ths_300033_config.py"))
ths_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ths_config)
config = ths_config.config


def train_epoch(model, tokenizer, dataloader, optimizer, device, epoch):
    """训练一个 epoch"""
    
    model.train()
    total_loss = 0
    num_batches = 0
    
    for batch_idx, batch in enumerate(dataloader):
        # 移动数据到设备
        x = batch['x'].to(device)
        y = batch['y'].to(device)
        
        # 前向传播
        optimizer.zero_grad()
        
        try:
            # 使用模型的 forward 方法
            outputs = model(x)
            
            # 计算损失 (MSE)
            loss = torch.nn.functional.mse_loss(outputs, y)
            
            # 反向传播
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
            # 打印进度
            if (batch_idx + 1) % config.log_interval == 0:
                avg_loss = total_loss / num_batches
                print(f"Epoch [{epoch}] Step [{batch_idx + 1}/{len(dataloader)}] "
                      f"Loss: {loss.item():.6f} Avg Loss: {avg_loss:.6f}")
        
        except Exception as e:
            print(f"❌ 训练错误: {e}")
            continue
    
    return total_loss / max(num_batches, 1)


def validate(model, tokenizer, dataloader, device):
    """验证模型"""
    
    model.eval()
    total_loss = 0
    num_batches = 0
    
    with torch.no_grad():
        for batch in dataloader:
            x = batch['x'].to(device)
            y = batch['y'].to(device)
            
            try:
                outputs = model(x)
                loss = torch.nn.functional.mse_loss(outputs, y)
                total_loss += loss.item()
                num_batches += 1
            except Exception as e:
                continue
    
    return total_loss / max(num_batches, 1)


def finetune_model():
    """主微调函数"""
    
    print("=" * 70)
    print("🚀 开始同花顺 (300033) 模型微调")
    print("=" * 70)
    print()
    
    # 1. 加载数据
    print("1. 加载数据...")
    train_dataset, val_dataset, test_dataset = load_and_split_data()
    
    if train_dataset is None:
        print("❌ 数据加载失败")
        return
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=0,  # macOS 兼容性
        pin_memory=False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=False
    )
    
    print()
    
    # 2. 加载模型
    print("2. 加载预训练模型...")
    try:
        # 加载 tokenizer
        tokenizer = KronosTokenizer.from_pretrained(config.pretrained_tokenizer_path)
        print(f"   ✅ Tokenizer 加载成功")
        
        # 加载模型
        model = Kronos.from_pretrained(config.pretrained_model_path)
        print(f"   ✅ Kronos-base 加载成功")
        
        # 移动到设备
        device = torch.device(config.device)
        model.to(device)
        print(f"   ✅ 模型已移动到 {device}")
        
    except Exception as e:
        print(f"   ❌ 模型加载失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # 3. 设置优化器
    print("3. 设置优化器...")
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    
    # 学习率调度器
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=config.epochs,
        eta_min=1e-6
    )
    
    print(f"   ✅ 优化器: AdamW (lr={config.learning_rate})")
    print(f"   ✅ 调度器: CosineAnnealingLR")
    print()
    
    # 4. 训练循环
    print("4. 开始训练...")
    print("=" * 70)
    
    best_val_loss = float('inf')
    training_start_time = time.time()
    
    for epoch in range(1, config.epochs + 1):
        epoch_start_time = time.time()
        
        # 训练
        train_loss = train_epoch(model, tokenizer, train_loader, optimizer, device, epoch)
        
        # 验证
        val_loss = validate(model, tokenizer, val_loader, device)
        
        # 更新学习率
        scheduler.step()
        
        # 计算时间
        epoch_time = time.time() - epoch_start_time
        
        # 打印结果
        print(f"\nEpoch [{epoch}/{config.epochs}] "
              f"Train Loss: {train_loss:.6f} | "
              f"Val Loss: {val_loss:.6f} | "
              f"Time: {epoch_time:.1f}s | "
              f"LR: {scheduler.get_last_lr()[0]:.6f}")
        
        # 保存最佳模型
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            save_path = os.path.join(config.output_dir, 'best_model')
            os.makedirs(save_path, exist_ok=True)
            
            # 保存模型
            model.save_pretrained(save_path)
            tokenizer.save_pretrained(save_path)
            
            print(f"   ✅ 保存最佳模型 (Val Loss: {val_loss:.6f})")
        
        # 定期保存检查点
        if epoch % 5 == 0:
            checkpoint_path = os.path.join(config.output_dir, f'checkpoint_epoch_{epoch}')
            os.makedirs(checkpoint_path, exist_ok=True)
            model.save_pretrained(checkpoint_path)
            tokenizer.save_pretrained(checkpoint_path)
            print(f"   💾 保存检查点: Epoch {epoch}")
        
        print("-" * 70)
    
    # 5. 训练完成
    total_time = time.time() - training_start_time
    
    print()
    print("=" * 70)
    print("🎉 训练完成！")
    print("=" * 70)
    print(f"总耗时: {total_time/3600:.2f} 小时")
    print(f"最佳验证损失: {best_val_loss:.6f}")
    print(f"模型保存至: {config.output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    finetune_model()
