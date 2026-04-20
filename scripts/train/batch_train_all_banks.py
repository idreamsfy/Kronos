# coding=utf-8
"""
批量训练所有银行股票的Kronos模型
自动遍历data目录下的所有kronos格式CSV文件
为每只股票创建配置文件并启动训练
"""
import os
import glob
import yaml
import subprocess
import datetime
import time


def create_config_for_stock(csv_file, exp_name=None):
    """
    为单只股票创建训练配置文件
    
    Args:
        csv_file: CSV文件路径
        exp_name: 实验名称（可选）
    
    Returns:
        str: 配置文件路径
    """
    # 从文件名提取信息
    filename = os.path.basename(csv_file)
    parts = filename.replace('.csv', '').split('_')
    
    if len(parts) >= 5:
        exchange = parts[1]  # SHSE or SZSE
        code = parts[2]      # 股票代码
        start_date = parts[4]
        end_date = parts[5] if len(parts) > 5 else "unknown"
        
        # 生成实验名称
        if exp_name is None:
            exp_name = f"{code.lower()}_daily_finetune"
        
        # 创建配置
        config = {
            'data': {
                'data_path': csv_file,
                'lookback_window': 60,
                'predict_window': 10,
                'max_context': 512,
                'clip': 5.0,
                'train_ratio': 0.8,
                'val_ratio': 0.15,
                'test_ratio': 0.05
            },
            'training': {
                'tokenizer_epochs': 15,
                'basemodel_epochs': 10,
                'batch_size': 8,
                'log_interval': 10,
                'num_workers': 0,
                'seed': 42,
                'tokenizer_learning_rate': 0.0002,
                'predictor_learning_rate': 0.000001,
                'adam_beta1': 0.9,
                'adam_beta2': 0.95,
                'adam_weight_decay': 0.1,
                'accumulation_steps': 1
            },
            'model_paths': {
                'pretrained_tokenizer': 'NeoQuasar/Kronos-Tokenizer-base',
                'pretrained_predictor': 'NeoQuasar/Kronos-base',
                'exp_name': exp_name,
                'base_path': 'outputs/finetuned_models',
                'base_save_path': '',
                'finetuned_tokenizer': '',
                'tokenizer_save_name': 'tokenizer',
                'basemodel_save_name': 'basemodel'
            },
            'experiment': {
                'name': f'{code.lower()}_daily_prediction',
                'description': f'Fine-tuning on stock {code} daily data',
                'use_comet': False
            }
        }
        
        # 保存配置文件
        config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'finetune_csv', 'configs')
        os.makedirs(config_dir, exist_ok=True)
        
        config_file = os.path.join(config_dir, f'config_{code.lower()}_daily.yaml')
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        return config_file
    else:
        print(f"⚠️  无法解析文件名: {filename}")
        return None


def train_single_stock(config_file, gpu_id=0):
    """
    训练单只股票
    
    Args:
        config_file: 配置文件路径
        gpu_id: GPU ID（-1表示CPU）
    
    Returns:
        bool: 是否成功
    """
    try:
        print(f"\n{'='*80}")
        print(f"开始训练: {os.path.basename(config_file)}")
        print(f"{'='*80}")
        
        # 构建命令
        cmd = [
            'python',
            'finetune_csv/train_sequential.py',
            '--config', config_file
        ]
        
        # 设置环境变量指定GPU
        env = os.environ.copy()
        if gpu_id >= 0:
            env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
        
        # 执行训练
        result = subprocess.run(cmd, env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print(f"✅ 训练成功完成")
            return True
        else:
            print(f"❌ 训练失败，返回码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ 训练出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def batch_train_all_stocks(start_index=0, end_index=None, gpu_id=0):
    """
    批量训练所有股票
    
    Args:
        start_index: 起始索引
        end_index: 结束索引（None表示全部）
        gpu_id: GPU ID
    """
    print("=" * 80)
    print("批量训练A股银行股票 Kronos 模型")
    print("=" * 80)
    print(f"运行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取所有Kronos格式的CSV文件
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    pattern = os.path.join(data_dir, 'kronos_*_daily_*.csv')
    csv_files = sorted(glob.glob(pattern))
    
    if not csv_files:
        print("❌ 错误: 未找到Kronos格式的CSV文件")
        print(f"   请先运行: python tests/batch_download_bank_stocks.py")
        return
    
    print(f"\n找到 {len(csv_files)} 个数据文件")
    
    # 限制范围
    if end_index is None:
        end_index = len(csv_files)
    
    csv_files = csv_files[start_index:end_index]
    
    print(f"将训练 {len(csv_files)} 只股票 (索引 {start_index}-{end_index-1})")
    print(f"使用GPU: {gpu_id if gpu_id >= 0 else 'CPU'}")
    print("=" * 80)
    
    # 统计
    total = len(csv_files)
    success_count = 0
    failed_count = 0
    
    for idx, csv_file in enumerate(csv_files, start=start_index):
        filename = os.path.basename(csv_file)
        print(f"\n[{idx+1}/{total}] 处理: {filename}")
        
        # 检查是否已经训练过
        parts = filename.replace('.csv', '').split('_')
        if len(parts) >= 3:
            code = parts[2]
            model_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'outputs', 'finetuned_models',
                f'{code.lower()}_daily_finetune'
            )
            
            if os.path.exists(model_dir):
                print(f"   ⏭️  模型已存在，跳过")
                continue
        
        # 创建配置文件
        config_file = create_config_for_stock(csv_file)
        
        if config_file is None:
            print(f"   ❌ 创建配置文件失败")
            failed_count += 1
            continue
        
        print(f"   📝 配置文件: {os.path.basename(config_file)}")
        
        # 开始训练
        success = train_single_stock(config_file, gpu_id=gpu_id)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
        
        # 短暂延迟，避免资源占用过高
        time.sleep(2)
    
    # 打印总结
    print("\n" + "=" * 80)
    print("批量训练完成！")
    print("=" * 80)
    print(f"\n统计信息:")
    print(f"  - 总计: {total} 只")
    print(f"  - 成功: {success_count} 只 ✅")
    print(f"  - 失败: {failed_count} 只 ❌")
    print(f"  - 跳过: {total - success_count - failed_count} 只 ⏭️")
    
    if total > 0:
        print(f"\n成功率: {success_count/total*100:.1f}%")
    
    print("=" * 80)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量训练银行股票Kronos模型')
    parser.add_argument('--start', type=int, default=0, help='起始索引')
    parser.add_argument('--end', type=int, default=None, help='结束索引')
    parser.add_argument('--gpu', type=int, default=0, help='GPU ID (-1 for CPU)')
    parser.add_argument('--stock', type=str, default=None, help='单个股票代码（如601398）')
    
    args = parser.parse_args()
    
    if args.stock:
        # 训练单只股票
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        pattern = os.path.join(data_dir, f'kronos_*_{args.stock}_daily_*.csv')
        csv_files = glob.glob(pattern)
        
        if not csv_files:
            print(f"❌ 未找到股票 {args.stock} 的数据文件")
            return
        
        csv_file = csv_files[0]
        print(f"找到文件: {csv_file}")
        
        config_file = create_config_for_stock(csv_file)
        if config_file:
            train_single_stock(config_file, gpu_id=args.gpu)
    else:
        # 批量训练
        batch_train_all_stocks(
            start_index=args.start,
            end_index=args.end,
            gpu_id=args.gpu
        )


if __name__ == '__main__':
    main()
