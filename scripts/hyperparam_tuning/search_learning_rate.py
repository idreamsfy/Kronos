#!/usr/bin/env python
"""
学习率搜索实验
测试不同的学习率配置，找到最优值

测试的学习率:
- 1e-5 (保守)
- 2e-5 (当前使用)
- 5e-5 (中等)
- 1e-4 (激进)
"""

import os
import sys
import yaml
import subprocess
from datetime import datetime


def create_config_for_lr(base_lr, exp_suffix):
    """为特定学习率创建配置文件"""
    
    # 读取基础配置
    base_config_path = "finetune_csv/configs/config_cuda_optimized.yaml"
    
    with open(base_config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 修改学习率
    config['training']['learning_rate'] = base_lr
    
    # 修改实验名称
    config['model_paths']['exp_name'] = f"lr_search_{base_lr:.0e}_{exp_suffix}"
    
    # 保存新配置
    output_dir = "finetune_csv/configs/lr_search"
    os.makedirs(output_dir, exist_ok=True)
    
    config_filename = f"config_lr_{base_lr:.0e}.yaml"
    config_path = os.path.join(output_dir, config_filename)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    return config_path


def run_training(config_path, lr_value):
    """运行训练"""
    
    print(f"\n{'='*80}")
    print(f"🚀 开始训练 - 学习率: {lr_value:.0e}")
    print(f"{'='*80}")
    print(f"配置文件: {config_path}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 构建命令
    cmd = [
        sys.executable,
        "finetune_csv/train_sequential.py",
        "--config", config_path,
        "--skip-tokenizer"  # 跳过tokenizer训练
    ]
    
    try:
        # 运行训练
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            capture_output=False,
            check=True
        )
        
        print(f"\n✅ 训练完成 - 学习率: {lr_value:.0e}")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 训练失败 - 学习率: {lr_value:.0e}")
        print(f"错误代码: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ 训练异常 - 学习率: {lr_value:.0e}")
        print(f"错误: {str(e)}")
        return False


def main():
    """主函数"""
    
    print("=" * 80)
    print("🔬 学习率搜索实验")
    print("=" * 80)
    print()
    
    # 定义要测试的学习率
    learning_rates = [
        1e-5,   # 保守
        2e-5,   # 当前使用
        5e-5,   # 中等
        1e-4,   # 激进
    ]
    
    print("将要测试的学习率:")
    for i, lr in enumerate(learning_rates, 1):
        print(f"  {i}. {lr:.0e}")
    print()
    
    print("⚠️  警告:")
    print("  - 每个学习率需要训练约140分钟")
    print(f"  - 总共需要约 {len(learning_rates) * 140 / 60:.1f} 小时")
    print("  - 建议按顺序运行，或并行运行多个实验")
    print()
    
    response = input("是否继续？(y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return
    
    results = []
    
    for lr in learning_rates:
        # 创建配置文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_path = create_config_for_lr(lr, timestamp)
        
        print(f"\n📝 已创建配置文件: {config_path}")
        
        # 运行训练
        success = run_training(config_path, lr)
        
        results.append({
            'lr': lr,
            'config': config_path,
            'success': success,
            'timestamp': timestamp
        })
        
        if not success:
            print(f"\n⚠️  学习率 {lr:.0e} 的训练失败，但将继续下一个实验")
    
    # 保存实验记录
    output_dir = "outputs/hyperparam_tuning"
    os.makedirs(output_dir, exist_ok=True)
    
    import pandas as pd
    results_df = pd.DataFrame(results)
    
    results_file = f"{output_dir}/lr_search_experiments.csv"
    results_df.to_csv(results_file, index=False)
    
    print("\n" + "=" * 80)
    print("📊 实验记录")
    print("=" * 80)
    print(results_df.to_string(index=False))
    print(f"\n💾 实验记录已保存到: {results_file}")
    
    print("\n✅ 所有实验已完成！")
    print("\n下一步:")
    print("  1. 检查 outputs/models/ 目录中的模型")
    print("  2. 比较不同学习率的验证Loss")
    print("  3. 选择最佳学习率进行后续实验")


if __name__ == "__main__":
    main()
