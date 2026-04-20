# coding=utf-8
"""
训练科创板股票 688206
使用Kronos模型进行微调训练
"""
import os
import sys
import yaml
import subprocess


def create_config_688206():
    """为688206创建训练配置"""
    
    # 查找688206的数据文件
    data_files = []
    for root, dirs, files in os.walk('data/processed'):
        for file in files:
            if '688206' in file and file.endswith('.csv'):
                data_files.append(os.path.join(root, file))
    
    if not data_files:
        print("❌ 错误: 未找到688206的数据文件")
        print("   请先运行: python scripts/data/batch_download_star_market.py 下载数据")
        return None
    
    data_path = data_files[0]
    print(f"✅ 找到数据文件: {data_path}")
    
    # 创建配置
    config = {
        'data': {
            'data_path': data_path.replace('\\', '/'),
            'lookback_window': 60,
            'predict_window': 10,
            'max_context': 512,
            'clip': 5.0,
            'train_ratio': 0.9,
            'val_ratio': 0.1,
            'test_ratio': 0.0
        },
        'training': {
            'tokenizer_epochs': 15,
            'basemodel_epochs': 10,
            'batch_size': 8,
            'log_interval': 50,
            'num_workers': 4,
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
            'exp_name': '688206_daily_finetune',
            'base_path': 'outputs/finetuned_models',
            'base_save_path': '',
            'finetuned_tokenizer': '',
            'tokenizer_save_name': 'tokenizer',
            'basemodel_save_name': 'basemodel'
        },
        'experiment': {
            'name': '688206_daily_prediction',
            'description': '对科创板股票688206进行日K线数据微调训练',
            'use_comet': False,
            'train_tokenizer': True,
            'train_basemodel': True,
            'skip_existing': False
        },
        'device': {
            'use_cuda': True,
            'device_id': 0
        }
    }
    
    # 保存配置文件
    config_dir = 'configs/training'
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, 'config_688206_daily.yaml')
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"✅ 配置文件已创建: {config_file}")
    return config_file


def train_688206(config_file):
    """启动688206的训练"""
    
    print("\n" + "=" * 80)
    print("  开始训练科创板股票 688206")
    print("=" * 80)
    print(f"\n配置文件: {config_file}")
    print(f"使用GPU: cuda:0")
    print("=" * 80 + "\n")
    
    # 构建训练命令
    cmd = [
        sys.executable,
        'src/finetuning/train_tokenizer_single.py',
        '--config', config_file
    ]
    
    print(f"执行命令: {' '.join(cmd)}\n")
    
    try:
        # 启动训练
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 实时输出训练日志
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            print("\n" + "=" * 80)
            print("  ✅ 训练成功完成！")
            print("=" * 80)
            print(f"\n模型保存在: outputs/finetuned_models/688206_daily_finetune/")
        else:
            print(f"\n❌ 训练失败，退出码: {process.returncode}")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断训练")
        process.terminate()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  科创板股票 688206 训练工具")
    print("=" * 80)
    print(f"运行时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    # 创建配置
    config_file = create_config_688206()
    
    if config_file is None:
        print("\n❌ 无法继续：配置创建失败")
        return
    
    # 询问是否开始训练
    print("\n是否开始训练？(y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        train_688206(config_file)
    else:
        print("\n已取消训练")
        print(f"配置文件已保存: {config_file}")
        print(f"可以稍后手动运行训练")


if __name__ == '__main__':
    main()
