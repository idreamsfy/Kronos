#!/usr/bin/env python
"""
使用 Apple Silicon MPS (GPU) 微调 Kronos Tokenizer
适用于 macOS M1/M2/M3 芯片
"""
import os
import sys
import time
from time import gmtime, strftime
import datetime
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import yaml

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from dataset import QlibDataset
from model.kronos import KronosTokenizer


def set_seed(seed: int):
    """设置随机种子以确保可重复性"""
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(seed)


def format_time(seconds: float) -> str:
    """格式化时间为 H:M:S 字符串"""
    return str(datetime.timedelta(seconds=int(seconds)))


def train_model_mps(model, device, config, save_dir):
    """使用 MPS 设备的训练循环"""
    print(f"开始在设备上训练: {device}")
    
    # 创建数据加载器
    print("加载数据集...")
    train_dataset = QlibDataset('train')
    valid_dataset = QlibDataset('val')
    print(f"训练集大小: {len(train_dataset)}, 验证集大小: {len(valid_dataset)}")
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=config['batch_size'], 
        shuffle=True,
        num_workers=0,
        pin_memory=False  # MPS doesn't support pinned memory
    )
    
    val_loader = DataLoader(
        valid_dataset, 
        batch_size=config['batch_size'], 
        shuffle=False,
        num_workers=0,
        pin_memory=False  # MPS doesn't support pinned memory
    )
    
    # 优化器和学习率调度器
    optimizer = torch.optim.AdamW(
        model.parameters(), 
        lr=config['learning_rate'],
        weight_decay=config.get('weight_decay', 0.01)
    )
    
    total_steps = len(train_loader) * config['epochs']
    warmup_steps = int(total_steps * config.get('warmup_ratio', 0.1))
    
    from transformers import get_cosine_schedule_with_warmup
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps
    )
    
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 训练循环
    print(f"\n开始训练，共 {config['epochs']} 个 epoch")
    print(f"批次大小: {config['batch_size']}")
    print(f"学习率: {config['learning_rate']}")
    print(f"总步数: {total_steps}")
    print("=" * 70)
    
    global_step = 0
    best_loss = float('inf')
    
    for epoch in range(config['epochs']):
        epoch_start_time = time.time()
        
        # 训练阶段
        model.train()
        train_loss = 0.0
        train_count = 0
        
        for i, (ori_batch_x, _) in enumerate(train_loader):
            # 移动数据到 MPS 设备
            ori_batch_x = ori_batch_x.to(device, non_blocking=True)
            
            # 前向传播
            zs, bsq_loss, _, _ = model(ori_batch_x)
            z_pre, z = zs
            
            # 计算损失
            recon_loss_pre = F.mse_loss(z_pre, ori_batch_x)
            recon_loss_all = F.mse_loss(z, ori_batch_x)
            recon_loss = recon_loss_pre + recon_loss_all
            loss = (recon_loss + bsq_loss) / 2
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()
            
            # 统计
            train_loss += loss.item()
            train_count += 1
            global_step += 1
            
            # 打印日志
            if (i + 1) % config.get('logging_steps', 10) == 0:
                avg_loss = train_loss / train_count
                current_lr = scheduler.get_last_lr()[0]
                print(f"Epoch [{epoch+1}/{config['epochs']}] Step [{i+1}/{len(train_loader)}] "
                      f"Loss: {avg_loss:.6f} LR: {current_lr:.6f}")
        
        # 计算平均训练损失
        avg_train_loss = train_loss / train_count
        
        # 验证阶段
        model.eval()
        val_loss = 0.0
        val_count = 0
        
        with torch.no_grad():
            for ori_batch_x, _ in val_loader:
                ori_batch_x = ori_batch_x.to(device, non_blocking=True)
                
                zs, bsq_loss, _, _ = model(ori_batch_x)
                z_pre, z = zs
                
                recon_loss_pre = F.mse_loss(z_pre, ori_batch_x)
                recon_loss_all = F.mse_loss(z, ori_batch_x)
                recon_loss = recon_loss_pre + recon_loss_all
                loss = (recon_loss + bsq_loss) / 2
                
                val_loss += loss.item()
                val_count += 1
        
        avg_val_loss = val_loss / val_count if val_count > 0 else 0
        
        epoch_time = time.time() - epoch_start_time
        
        print(f"\nEpoch [{epoch+1}/{config['epochs']}] 完成!")
        print(f"  训练损失: {avg_train_loss:.6f}")
        print(f"  验证损失: {avg_val_loss:.6f}")
        print(f"  耗时: {format_time(epoch_time)}")
        print("-" * 70)
        
        # 保存最佳模型
        if avg_val_loss < best_loss:
            best_loss = avg_val_loss
            checkpoint_path = os.path.join(save_dir, 'best_model')
            os.makedirs(checkpoint_path, exist_ok=True)
            
            # 保存模型
            model.save_pretrained(checkpoint_path)
            
            # 保存配置
            with open(os.path.join(checkpoint_path, 'config.json'), 'w') as f:
                json.dump({
                    'model_type': 'kronos_tokenizer',
                    'best_val_loss': best_loss,
                    'epoch': epoch + 1,
                    'timestamp': datetime.datetime.now().isoformat()
                }, f, indent=2)
            
            print(f"✅ 保存最佳模型 (验证损失: {best_loss:.6f})")
        
        # 定期保存检查点
        if (epoch + 1) % config.get('save_steps', 5) == 0:
            checkpoint_path = os.path.join(save_dir, f'checkpoint_epoch_{epoch+1}')
            os.makedirs(checkpoint_path, exist_ok=True)
            model.save_pretrained(checkpoint_path)
            print(f"💾 保存检查点: epoch {epoch+1}")
    
    print("\n" + "=" * 70)
    print("训练完成!")
    print(f"最佳验证损失: {best_loss:.6f}")
    print(f"模型保存至: {save_dir}")
    print("=" * 70)


def main():
    """主函数"""
    print("=" * 70)
    print("Kronos Tokenizer 微调 - Apple Silicon MPS (GPU)")
    print("=" * 70)
    
    # 检查 MPS 可用性
    if not torch.backends.mps.is_available():
        print("❌ 错误: MPS 不可用")
        print("请确保:")
        print("1. 使用 macOS 系统")
        print("2. 使用 Apple Silicon (M1/M2/M3) 芯片")
        print("3. PyTorch 版本 >= 1.12")
        return
    
    print(f"✅ MPS 可用")
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"设备: Apple Silicon MPS\n")
    
    # 加载配置
    config_file = os.path.join(os.path.dirname(__file__), 'config_300033_mps.yaml')
    
    if os.path.exists(config_file):
        print(f"加载配置文件: {config_file}")
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        print(f"配置文件不存在，使用默认配置")
        config = {
            'pretrained_tokenizer_path': 'NeoQuasar/Kronos-Tokenizer-base',
            'batch_size': 50,
            'epochs': 30,
            'learning_rate': 0.0002,
            'weight_decay': 0.01,
            'warmup_ratio': 0.1,
            'save_steps': 5,
            'logging_steps': 10,
        }
    
    # 设置随机种子
    set_seed(config.get('seed', 42))
    
    # 设置设备
    device = torch.device('mps')
    print(f"使用设备: {device}\n")
    
    # 加载预训练模型
    print(f"加载预训练 tokenizer: {config['pretrained_tokenizer_path']}")
    model = KronosTokenizer.from_pretrained(config['pretrained_tokenizer_path'])
    model.to(device)
    print("✅ 模型加载成功\n")
    
    # 开始训练
    save_dir = config.get('save_dir', './outputs/models/finetune_tokenizer_300033_mps')
    train_model_mps(model, device, config, save_dir)


if __name__ == "__main__":
    import json
    main()
