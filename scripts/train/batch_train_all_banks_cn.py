# coding=utf-8
"""
批量训练所有银行股票的Kronos模型（中文版）
自动遍历data目录下的所有kronos格式CSV文件
为每只股票创建配置文件并启动GPU训练
"""
import os
import glob
import yaml
import subprocess
import datetime
import time
import sys


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text):
    """打印章节"""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)


def get_stock_info(csv_file):
    """
    从CSV文件名提取股票信息
    
    Args:
        csv_file: CSV文件路径
    
    Returns:
        dict: 股票信息字典
    """
    filename = os.path.basename(csv_file)
    parts = filename.replace('.csv', '').split('_')
    
    if len(parts) >= 5:
        exchange = parts[1]  # SHSE or SZSE
        code = parts[2]      # 股票代码
        
        # 获取股票名称映射
        stock_names = {
            '600000': '浦发银行',
            '600015': '华夏银行',
            '600016': '民生银行',
            '600036': '招商银行',
            '600926': '杭州银行',
            '601009': '南京银行',
            '601128': '常熟银行',
            '601162': '天风证券',
            '601166': '兴业银行',
            '601169': '北京银行',
            '601187': '厦门银行',
            '601288': '农业银行',
            '601328': '交通银行',
            '601398': '工商银行',
            '601528': '瑞丰银行',
            '601577': '长沙银行',
            '601658': '邮储银行',
            '601818': '光大银行',
            '601838': '成都银行',
            '601860': '紫金银行',
            '601939': '建设银行',
            '601963': '重庆银行',
            '601988': '中国银行',
            '601997': '贵阳银行',
            '601998': '中信银行',
            '000001': '平安银行',
            '002142': '宁波银行',
            '002807': '江阴银行',
            '002839': '张家港行',
            '002936': '郑州银行',
            '002948': '青岛银行',
            '002958': '青农商行',
            '002966': '苏州银行',
        }
        
        stock_name = stock_names.get(code, f'股票{code}')
        
        return {
            'exchange': exchange,
            'code': code,
            'name': stock_name,
            'full_name': f'{stock_name}({code})',
            'file': csv_file
        }
    
    return None


def create_config_for_stock(stock_info, exp_name=None):
    """
    为单只股票创建训练配置文件
    
    Args:
        stock_info: 股票信息字典
        exp_name: 实验名称（可选）
    
    Returns:
        str: 配置文件路径
    """
    code = stock_info['code']
    name = stock_info['name']
    csv_file = stock_info['file']
    
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
            'num_workers': 0,
            'seed': 42,
            'tokenizer_learning_rate': 0.0002,
            'predictor_learning_rate': 0.000001
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
            'description': f'对{name}({code})进行日K线数据微调训练',
            'use_comet': False
        },
        'device': {
            'use_cuda': True,
            'device_id': 0
        },
        'experiment_description': f'对{name}({code})进行日K线数据微调训练'
    }
    
    # 保存配置文件
    config_dir = 'finetune_csv/configs'
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, f'config_{code.lower()}_daily.yaml')
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    return config_file


def check_if_trained(stock_code):
    """
    检查股票是否已经训练过
    
    Args:
        stock_code: 股票代码
    
    Returns:
        bool: 是否已训练
    """
    model_dir = f'outputs/finetuned_models/{stock_code.lower()}_daily_finetune'
    tokenizer_model = os.path.join(model_dir, 'tokenizer', 'best_model', 'model.safetensors')
    predictor_model = os.path.join(model_dir, 'basemodel', 'best_model', 'model.safetensors')
    
    return os.path.exists(tokenizer_model) and os.path.exists(predictor_model)


def train_single_stock(config_file, stock_info, gpu_id=0):
    """
    训练单只股票
    
    Args:
        config_file: 配置文件路径
        stock_info: 股票信息
        gpu_id: GPU ID
    
    Returns:
        bool: 是否成功
    """
    code = stock_info['code']
    name = stock_info['name']
    
    print_section(f"开始训练: {name}({code})")
    print(f"配置文件: {config_file}")
    print(f"数据文件: {stock_info['file']}")
    print(f"使用GPU: {gpu_id}")
    print(f"开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 构建命令
        cmd = [
            sys.executable,
            'finetune_csv/train_sequential.py',
            '--config', config_file
        ]
        
        # 设置环境变量指定GPU
        env = os.environ.copy()
        env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
        
        # 执行训练
        process = subprocess.run(
            cmd,
            env=env,
            cwd=os.getcwd()
        )
        
        if process.returncode == 0:
            print(f"\n✅ {name}({code}) 训练完成！")
            end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"结束时间: {end_time}")
            return True
        else:
            print(f"\n❌ {name}({code}) 训练失败，返回码: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ {name}({code}) 训练出错: {str(e)}")
        return False


def batch_train_all_stocks(start_index=0, end_index=None, gpu_id=0, skip_trained=True):
    """
    批量训练所有股票
    
    Args:
        start_index: 起始索引
        end_index: 结束索引（None表示全部）
        gpu_id: GPU ID
        skip_trained: 是否跳过已训练的
    """
    print_header("Kronos 银行股票批量训练系统（GPU加速版）")
    
    # 查找所有kronos格式的CSV文件
    csv_files = sorted(glob.glob('data/kronos_*_daily_*.csv'))
    
    if not csv_files:
        print("❌ 错误: 未找到任何kronos格式的CSV文件")
        print("请先运行数据下载脚本")
        return
    
    print(f"📊 找到 {len(csv_files)} 个股票数据文件")
    print()
    
    # 解析股票信息
    stocks = []
    for csv_file in csv_files:
        info = get_stock_info(csv_file)
        if info:
            stocks.append(info)
    
    if not stocks:
        print("❌ 错误: 无法解析股票信息")
        return
    
    # 过滤已训练的股票
    if skip_trained:
        original_count = len(stocks)
        stocks = [s for s in stocks if not check_if_trained(s['code'])]
        skipped_count = original_count - len(stocks)
        
        if skipped_count > 0:
            print(f"⏭️  跳过 {skipped_count} 个已训练的股票")
    
    if not stocks:
        print("✅ 所有股票都已训练完成！")
        return
    
    # 限制范围
    if end_index is None:
        end_index = len(stocks)
    
    stocks_to_train = stocks[start_index:end_index]
    
    print(f"\n📋 待训练股票列表 ({len(stocks_to_train)} 只):")
    print("-" * 80)
    for i, stock in enumerate(stocks_to_train, 1):
        status = "✅ 已训练" if check_if_trained(stock['code']) else "⏳ 待训练"
        print(f"  {i:2d}. {stock['full_name']:20s} - {status}")
    print("-" * 80)
    
    # 开始训练
    print_header("开始批量训练")
    
    success_count = 0
    fail_count = 0
    total_start_time = time.time()
    
    for i, stock in enumerate(stocks_to_train, 1):
        print(f"\n{'='*80}")
        print(f"进度: [{i}/{len(stocks_to_train)}]")
        print(f"{'='*80}")
        
        # 创建配置文件
        config_file = create_config_for_stock(stock)
        
        # 训练
        success = train_single_stock(config_file, stock, gpu_id)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # 显示统计
        elapsed = time.time() - total_start_time
        avg_time = elapsed / i if i > 0 else 0
        remaining = avg_time * (len(stocks_to_train) - i)
        
        print(f"\n📊 当前统计:")
        print(f"  成功: {success_count} ✅")
        print(f"  失败: {fail_count} ❌")
        print(f"  已用时: {elapsed/60:.1f} 分钟")
        print(f"  预计剩余: {remaining/60:.1f} 分钟")
        
        # 短暂暂停
        if i < len(stocks_to_train):
            print("\n⏸️  等待5秒后继续下一只股票...")
            time.sleep(5)
    
    # 最终统计
    total_time = time.time() - total_start_time
    
    print_header("训练完成总结")
    print(f"总股票数: {len(stocks_to_train)}")
    print(f"成功: {success_count} ✅")
    print(f"失败: {fail_count} ❌")
    print(f"成功率: {success_count/len(stocks_to_train)*100:.1f}%")
    print(f"总用时: {total_time/60:.1f} 分钟 ({total_time/3600:.2f} 小时)")
    print(f"平均每只: {total_time/len(stocks_to_train)/60:.1f} 分钟")
    print()
    
    if fail_count > 0:
        print("⚠️  以下股票训练失败，请检查日志:")
        print("-" * 80)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='批量训练银行股票Kronos模型')
    parser.add_argument('--start', type=int, default=0, help='起始索引（默认: 0）')
    parser.add_argument('--end', type=int, default=None, help='结束索引（默认: 全部）')
    parser.add_argument('--gpu', type=int, default=0, help='GPU ID（默认: 0）')
    parser.add_argument('--no-skip', action='store_true', help='不跳过已训练的股票')
    
    args = parser.parse_args()
    
    batch_train_all_stocks(
        start_index=args.start,
        end_index=args.end,
        gpu_id=args.gpu,
        skip_trained=not args.no_skip
    )
