#!/usr/bin/env python
"""
使用本地预训练模型示例

演示如何从本地路径加载 Kronos 模型和 Tokenizer
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import torch
import pandas as pd
from model.kronos import Kronos, KronosTokenizer, KronosPredictor


def load_local_models():
    """从本地路径加载模型"""
    
    print("=" * 70)
    print("加载本地预训练模型")
    print("=" * 70)
    print()
    
    # 定义本地模型路径
    model_path = "./model/pretrained_models/Kronos-base"
    tokenizer_path = "./model/pretrained_models/Kronos-Tokenizer-base"
    
    # 检查文件是否存在
    if not os.path.exists(model_path):
        print(f"❌ 错误: 模型路径不存在: {model_path}")
        print("请先下载模型:")
        print("  export HF_ENDPOINT=https://hf-mirror.com")
        print("  python -c \"from huggingface_hub import snapshot_download; snapshot_download('NeoQuasar/Kronos-base', local_dir='./model/pretrained_models/Kronos-base')\"")
        return None, None
    
    if not os.path.exists(tokenizer_path):
        print(f"❌ 错误: Tokenizer 路径不存在: {tokenizer_path}")
        return None, None
    
    # 加载 Tokenizer
    print(f"1. 加载 Tokenizer from: {tokenizer_path}")
    try:
        tokenizer = KronosTokenizer.from_pretrained(tokenizer_path)
        print(f"   ✅ Tokenizer 加载成功")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return None, None
    
    print()
    
    # 加载模型
    print(f"2. 加载 Kronos-base from: {model_path}")
    try:
        model = Kronos.from_pretrained(model_path)
        print(f"   ✅ 模型加载成功")
        
        # 显示模型信息
        total_params = sum(p.numel() for p in model.parameters())
        print(f"   参数量: {total_params:,}")
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return None, None
    
    print()
    
    # 设置设备
    if torch.backends.mps.is_available():
        device = torch.device('mps')
        model.to(device)
        print(f"3. 设备: Apple Silicon MPS (GPU) ✅")
    elif torch.cuda.is_available():
        device = torch.device('cuda')
        model.to(device)
        print(f"3. 设备: NVIDIA CUDA (GPU) ✅")
    else:
        device = torch.device('cpu')
        print(f"3. 设备: CPU ⚠️")
    
    print()
    print("=" * 70)
    print("✅ 所有模型加载成功！")
    print("=" * 70)
    
    return model, tokenizer


def test_prediction(model, tokenizer):
    """测试预测功能"""
    
    print()
    print("=" * 70)
    print("测试预测功能")
    print("=" * 70)
    print()
    
    # 创建预测器
    predictor = KronosPredictor(
        model=model,
        tokenizer=tokenizer,
        max_context=512
    )
    print("✅ Predictor 创建成功")
    print()
    
    # 检查是否有测试数据
    data_file = "./data/raw/akshare/daily_300033.csv"
    if not os.path.exists(data_file):
        print(f"⚠️  测试数据不存在: {data_file}")
        print("跳过预测测试")
        return
    
    # 加载数据
    print(f"加载测试数据: {data_file}")
    df = pd.read_csv(data_file)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    print(f"   数据行数: {len(df)}")
    print()
    
    # 准备输入
    lookback = 100
    pred_len = 20
    
    x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
    x_timestamp = df.loc[:lookback-1, 'timestamps']
    y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']
    
    print(f"进行预测...")
    print(f"   历史数据: {lookback} 条")
    print(f"   预测长度: {pred_len} 条")
    print()
    
    # 预测
    try:
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_len,
            T=1.0,
            top_p=0.9,
            sample_count=1
        )
        
        print("✅ 预测完成！")
        print()
        print("预测结果:")
        print(pred_df.to_string())
        
    except Exception as e:
        print(f"❌ 预测失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    
    # 加载模型
    model, tokenizer = load_local_models()
    
    if model is None or tokenizer is None:
        print("\n❌ 模型加载失败，退出")
        sys.exit(1)
    
    # 测试预测
    test_prediction(model, tokenizer)
    
    print()
    print("=" * 70)
    print("🎉 测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
