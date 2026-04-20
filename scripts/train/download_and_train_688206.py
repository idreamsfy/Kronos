# coding=utf-8
"""
下载并训练科创板股票 688206
一步完成数据下载和模型训练
"""
from gm.api import *
import pandas as pd
import datetime
import os
import yaml
import subprocess
import sys

# 配置掘金量化Token
GM_TOKEN = 'cabb19a30fc311ec977252560acd7b8ecabb19a4'
set_token(GM_TOKEN)


def download_688206_data():
    """下载688206的历史数据"""
    print("=" * 80)
    print("  步骤1: 下载688206历史数据")
    print("=" * 80)
    
    symbol = 'SHSE.688206'
    code = '688206'
    
    # 计算时间范围（过去5年）
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=5*365)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"\n股票代码: {symbol}")
    print(f"时间范围: {start_date_str} 到 {end_date_str}")
    
    try:
        # 获取历史行情数据
        history_data = history(
            symbol=symbol,
            frequency='1d',
            start_time=start_date_str,
            end_time=end_date_str,
            fill_missing='last',
            df=True
        )
        
        if history_data is None or len(history_data) == 0:
            print(f"\n❌ 错误: 未获取到{symbol}的数据")
            print("   该股票可能尚未上市或已退市")
            return None
        
        print(f"✅ 成功获取 {len(history_data)} 条记录")
        
        # 转换为Kronos格式
        kronos_columns = {
            'eob': 'timestamps',
            'open': 'open',
            'close': 'close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume',
            'amount': 'amount',
        }
        
        available_columns = {k: v for k, v in kronos_columns.items() if k in history_data.columns}
        df_kronos = history_data.rename(columns=available_columns)
        
        required_columns = ['timestamps', 'open', 'close', 'high', 'low', 'volume', 'amount']
        missing_columns = [col for col in required_columns if col not in df_kronos.columns]
        
        if missing_columns:
            print(f"❌ 缺少列: {missing_columns}")
            return None
        
        df_kronos = df_kronos.sort_values('timestamps').reset_index(drop=True)
        df_kronos['timestamps'] = pd.to_datetime(df_kronos['timestamps'])
        
        # 保存文件
        output_dir = 'data/processed'
        os.makedirs(output_dir, exist_ok=True)
        
        start_str = df_kronos['timestamps'].iloc[0].strftime('%Y-%m-%d')
        end_str = df_kronos['timestamps'].iloc[-1].strftime('%Y-%m-%d')
        
        filename = f"kronos_SHSE_{code}_daily_{start_str}_{end_str}.csv"
        filepath = os.path.join(output_dir, filename)
        
        df_kronos.to_csv(filepath, index=False, encoding='utf-8')
        
        file_size = os.path.getsize(filepath) / 1024
        print(f"✅ 数据已保存: {filepath}")
        print(f"   记录数: {len(df_kronos)}, 大小: {file_size:.1f}KB")
        
        return filepath
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_config(data_path):
    """创建训练配置"""
    print("\n" + "=" * 80)
    print("  步骤2: 创建训练配置")
    print("=" * 80)
    
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
    
    config_dir = 'configs/training'
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, 'config_688206_daily.yaml')
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"✅ 配置文件已创建: {config_file}")
    return config_file


def train_model(config_file):
    """启动训练"""
    print("\n" + "=" * 80)
    print("  步骤3: 开始训练模型")
    print("=" * 80)
    print(f"\n配置文件: {config_file}")
    print(f"使用GPU: cuda:0")
    print("=" * 80 + "\n")
    
    cmd = [
        sys.executable,
        'src/finetuning/train_tokenizer_single.py',
        '--config', config_file
    ]
    
    print(f"执行命令: {' '.join(cmd)}\n")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            print("\n" + "=" * 80)
            print("  ✅ 训练成功完成！")
            print("=" * 80)
            print(f"\n模型保存在: outputs/finetuned_models/688206_daily_finetune/")
            return True
        else:
            print(f"\n❌ 训练失败，退出码: {process.returncode}")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断训练")
        process.terminate()
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  科创板股票 688206 下载与训练工具")
    print("=" * 80)
    print(f"运行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    # 步骤1: 下载数据
    data_path = download_688206_data()
    
    if data_path is None:
        print("\n❌ 数据下载失败，无法继续")
        return
    
    # 步骤2: 创建配置
    config_file = create_config(data_path)
    
    if config_file is None:
        print("\n❌ 配置创建失败，无法继续")
        return
    
    # 询问是否开始训练
    print("\n是否开始训练？(y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        # 步骤3: 训练模型
        success = train_model(config_file)
        
        if success:
            print("\n🎉 全部完成！")
        else:
            print("\n⚠️  训练未完成")
    else:
        print("\n已取消训练")
        print(f"数据文件: {data_path}")
        print(f"配置文件: {config_file}")
        print(f"可以稍后手动运行训练")


if __name__ == '__main__':
    main()
