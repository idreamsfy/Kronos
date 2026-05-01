# 📊 方案一：数据层面优化 - 实施步骤说明书

**基于**: MODEL_OPTIMIZATION_PLAN.md - 方案一  
**制定时间**: 2026年5月1日  
**目标**: 通过数据扩充和增强提升模型预测准确性  
**优先级**: ⭐⭐⭐⭐⭐ (最高)  
**预计总耗时**: 3-5天  

---

## 📋 目录

1. [概述](#概述)
2. [前置准备](#前置准备)
3. [步骤1: 扩充训练数据集](#步骤1-扩充训练数据集)
4. [步骤2: 数据增强策略](#步骤2-数据增强策略)
5. [步骤3: 特征工程增强](#步骤3-特征工程增强)
6. [验证与测试](#验证与测试)
7. [常见问题](#常见问题)
8. [预期成果](#预期成果)

---

## 概述

### 核心问题

当前模型存在以下数据相关问题：
- ❌ 训练数据仅34,800条（3年历史），缺少最新市场模式
- ❌ 上涨行情样本不足，导致模型学习到悲观模式
- ❌ 仅使用基础OHLCV数据，缺少技术指标和市场情绪因子
- ❌ R²为负值(-3.76)，系统性看空偏差

### 解决方案

通过三个子方案解决数据层面问题：
1. **1.1 扩充训练数据集** - 合并新旧数据，增加最新市场模式
2. **1.2 数据增强策略** - 平衡涨跌样本，添加噪声增强
3. **1.3 特征工程增强** - 添加技术指标和时间特征

### 系统配置

- **CPU**: AMD EPYC 9T24 (16核/32线程)
- **内存**: 64 GB DDR5
- **GPU**: NVIDIA RTX 5880 Ada (12GB)
- **CUDA**: 12.8
- **优势**: 可快速处理大规模数据，支持并行计算

---

## 前置准备

### 1. 检查现有数据文件

```bash
# 检查数据文件是否存在
dir data\raw\futu\5min_300033.csv
dir data\raw\futu\5min_300033_2026-04-27_2026-04-30.csv
```

**预期结果**:
- ✅ `5min_300033.csv`: 34,802条历史数据
- ✅ `5min_300033_2026-04-27_2026-04-30.csv`: 194条新数据

### 2. 备份原始数据

```bash
# 创建备份目录
mkdir backups\data_backup_%date:~0,10%

# 备份原始数据文件
copy data\raw\futu\5min_300033.csv backups\data_backup_%date:~0,10%\
copy data\raw\futu\5min_300033_2026-04-27_2026-04-30.csv backups\data_backup_%date:~0,10%\
```

### 3. 创建脚本目录

```bash
mkdir scripts\data_optimization
```

---

## 步骤1: 扩充训练数据集

**优先级**: ⭐⭐⭐⭐⭐  
**难度**: ⭐ (简单)  
**预计耗时**: 2-4小时

### 1.1 创建数据合并脚本

创建文件: `scripts/data_optimization/merge_data.py`

```python
"""
数据合并脚本 - 合并历史数据和新数据
适配: AMD EPYC + 64GB内存 + RTX 5880 Ada
"""
import pandas as pd
import os
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_merge.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def merge_historical_and_new_data():
    """合并历史数据和新数据"""
    
    logger.info("=" * 80)
    logger.info("开始数据合并任务")
    logger.info("=" * 80)
    
    # 文件路径
    historical_path = 'data/raw/futu/5min_300033.csv'
    new_path = 'data/raw/futu/5min_300033_2026-04-27_2026-04-30.csv'
    output_path = 'data/raw/futu/5min_300033_updated.csv'
    
    # 检查文件是否存在
    if not os.path.exists(historical_path):
        raise FileNotFoundError(f"历史数据文件不存在: {historical_path}")
    
    if not os.path.exists(new_path):
        raise FileNotFoundError(f"新数据文件不存在: {new_path}")
    
    # 读取历史数据
    logger.info("\n1. 读取历史数据...")
    historical_df = pd.read_csv(historical_path)
    logger.info(f"   历史数据: {len(historical_df):,} 条")
    logger.info(f"   时间范围: {historical_df['timestamps'].iloc[0]} 到 {historical_df['timestamps'].iloc[-1]}")
    
    # 读取新数据
    logger.info("\n2. 读取新数据...")
    new_df = pd.read_csv(new_path)
    logger.info(f"   新数据: {len(new_df):,} 条")
    logger.info(f"   时间范围: {new_df['timestamps'].iloc[0]} 到 {new_df['timestamps'].iloc[-1]}")
    
    # 转换时间格式
    logger.info("\n3. 转换时间格式...")
    historical_df['timestamps'] = pd.to_datetime(historical_df['timestamps'])
    new_df['timestamps'] = pd.to_datetime(new_df['timestamps'])
    
    # 合并数据
    logger.info("\n4. 合并数据...")
    combined_df = pd.concat([historical_df, new_df], ignore_index=True)
    before_dedup = len(combined_df)
    logger.info(f"   合并后（去重前）: {before_dedup:,} 条")
    
    # 去重（基于时间戳）
    logger.info("\n5. 去除重复数据...")
    combined_df = combined_df.drop_duplicates(subset=['timestamps'], keep='last')
    after_dedup = len(combined_df)
    removed = before_dedup - after_dedup
    logger.info(f"   移除重复记录: {removed} 条")
    logger.info(f"   去重后: {after_dedup:,} 条")
    
    # 按时间排序
    logger.info("\n6. 按时间排序...")
    combined_df = combined_df.sort_values('timestamps').reset_index(drop=True)
    
    # 保存合并后的数据
    logger.info("\n7. 保存合并数据...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined_df.to_csv(output_path, index=False)
    logger.info(f"   ✅ 保存至: {output_path}")
    
    # 输出统计信息
    logger.info("\n" + "=" * 80)
    logger.info("合并完成统计")
    logger.info("=" * 80)
    logger.info(f"原始历史数据: {len(historical_df):,} 条")
    logger.info(f"新增数据: {len(new_df):,} 条")
    logger.info(f"移除重复: {removed} 条")
    logger.info(f"最终数据量: {len(combined_df):,} 条")
    logger.info(f"数据增长率: {(len(combined_df) - len(historical_df)) / len(historical_df) * 100:.2f}%")
    logger.info(f"时间范围: {combined_df['timestamps'].min()} 到 {combined_df['timestamps'].max()}")
    logger.info(f"总交易日数: {combined_df['timestamps'].dt.date.nunique()} 天")
    logger.info("=" * 80)
    
    return combined_df

if __name__ == "__main__":
    try:
        merged_data = merge_historical_and_new_data()
        logger.info("\n✅ 数据合并成功完成！")
    except Exception as e:
        logger.error(f"\n❌ 数据合并失败: {e}")
        raise
```

### 1.2 执行数据合并

```bash
# 创建日志目录
mkdir logs

# 运行合并脚本
python scripts/data_optimization/merge_data.py
```

**预期输出**:
```
================================================================================
开始数据合并任务
================================================================================

1. 读取历史数据...
   历史数据: 34,802 条
   时间范围: 2023-04-26 09:35:00 到 2026-04-25 15:00:00

2. 读取新数据...
   新数据: 194 条
   时间范围: 2026-04-27 09:35:00 到 2026-04-30 15:00:00

3. 转换时间格式...

4. 合并数据...
   合并后（去重前）: 34,996 条

5. 去除重复数据...
   移除重复记录: 0 条
   去重后: 34,996 条

6. 按时间排序...

7. 保存合并数据...
   ✅ 保存至: data/raw/futu/5min_300033_updated.csv

================================================================================
合并完成统计
================================================================================
原始历史数据: 34,802 条
新增数据: 194 条
移除重复: 0 条
最终数据量: 34,996 条
数据增长率: 0.56%
时间范围: 2023-04-26 09:35:00 到 2026-04-30 15:00:00
总交易日数: 730 天
================================================================================

✅ 数据合并成功完成！
```

### 1.3 验证合并结果

创建文件: `scripts/data_optimization/validate_merged_data.py`

```python
"""
验证合并后的数据质量
"""
import pandas as pd
import numpy as np
import json
import os

def validate_data_quality(df):
    """验证数据质量"""
    
    print("=" * 80)
    print("数据质量验证报告")
    print("=" * 80)
    
    # 基本统计
    print(f"\n📊 1. 基本统计:")
    print(f"   总记录数: {len(df):,}")
    print(f"   时间范围: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
    print(f"   总交易日数: {df['timestamps'].dt.date.nunique()} 天")
    
    # 缺失值统计
    print(f"\n⚠️  2. 缺失值统计:")
    has_missing = False
    for col in ['open', 'high', 'low', 'close', 'volume']:
        missing = df[col].isnull().sum()
        if missing > 0:
            has_missing = True
            print(f"   ❌ {col}: {missing} ({missing/len(df)*100:.2f}%)")
    if not has_missing:
        print(f"   ✅ 无缺失值")
    
    # OHLC逻辑验证
    print(f"\n🔍 3. OHLC逻辑验证:")
    invalid_ohlc = ((df['high'] < df['low']) | 
                   (df['high'] < df['open']) | 
                   (df['high'] < df['close']) |
                   (df['low'] > df['open']) | 
                   (df['low'] > df['close']))
    invalid_count = invalid_ohlc.sum()
    if invalid_count > 0:
        print(f"   ❌ 无效OHLC记录: {invalid_count} ({invalid_count/len(df)*100:.2f}%)")
    else:
        print(f"   ✅ 所有OHLC记录有效")
    
    # 价格异常检测
    print(f"\n📈 4. 价格异常检测:")
    price_changes = df['close'].pct_change()
    extreme_changes = (price_changes.abs() > 0.1).sum()
    if extreme_changes > 0:
        print(f"   ⚠️  极端价格变动 (>10%): {extreme_changes} 次")
    else:
        print(f"   ✅ 无极端价格变动")
    
    # 成交量异常检测
    print(f"\n📊 5. 成交量异常检测:")
    vol_mean = df['volume'].mean()
    vol_std = df['volume'].std()
    extreme_vol = (df['volume'] > vol_mean + 3 * vol_std).sum()
    if extreme_vol > 0:
        print(f"   ⚠️  极端成交量 (>3σ): {extreme_vol} 次")
    else:
        print(f"   ✅ 成交量分布正常")
    
    # 数据统计摘要
    print(f"\n📋 6. 价格统计摘要:")
    print(f"   收盘价均值: ¥{df['close'].mean():.2f}")
    print(f"   收盘价中位数: ¥{df['close'].median():.2f}")
    print(f"   最高价: ¥{df['high'].max():.2f}")
    print(f"   最低价: ¥{df['low'].min():.2f}")
    
    print("\n" + "=" * 80)
    
    # 生成验证报告
    report = {
        'total_records': int(len(df)),
        'date_range': f"{df['timestamps'].min()} to {df['timestamps'].max()}",
        'trading_days': int(df['timestamps'].dt.date.nunique()),
        'missing_values': {col: int(df[col].isnull().sum()) for col in ['open', 'high', 'low', 'close', 'volume']},
        'invalid_ohlc': int(invalid_count),
        'extreme_price_changes': int(extreme_changes),
        'extreme_volume': int(extreme_vol),
        'data_quality': 'PASS' if (invalid_count == 0) else 'WARNING'
    }
    
    return report

if __name__ == "__main__":
    data_path = 'data/raw/futu/5min_300033_updated.csv'
    print(f"加载数据: {data_path}")
    df = pd.read_csv(data_path)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    report = validate_data_quality(df)
    
    # 保存验证报告
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/data_validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ 验证报告已保存至: outputs/data_validation_report.json")
    print(f"数据质量评级: {report['data_quality']}")
```

执行验证：

```bash
python scripts/data_optimization/validate_merged_data.py
```

---

## 步骤2: 数据增强策略

**优先级**: ⭐⭐⭐⭐  
**难度**: ⭐⭐ (中等)  
**预计耗时**: 1-2天

### 2.1 创建数据平衡脚本

创建文件: `scripts/data_optimization/balance_data.py`

```python
"""
数据平衡脚本 - 平衡涨跌样本比例
"""
import pandas as pd
import numpy as np
import os

def balance_up_down_samples(df):
    """平衡涨跌样本"""
    
    print("=" * 80)
    print("数据平衡任务")
    print("=" * 80)
    
    # 标记涨跌
    df = df.copy()
    df['is_up'] = (df['close'] > df['open']).astype(int)
    
    up_samples = df[df['is_up'] == 1]
    down_samples = df[df['is_up'] == 0]
    
    print(f"\n📊 原始数据分布:")
    print(f"   上涨样本: {len(up_samples):,} ({len(up_samples)/len(df)*100:.1f}%)")
    print(f"   下跌样本: {len(down_samples):,} ({len(down_samples)/len(df)*100:.1f}%)")
    
    # 如果比例失衡，进行过采样
    ratio = len(down_samples) / len(up_samples) if len(up_samples) > 0 else float('inf')
    
    if ratio > 1.5 or ratio < 0.67:
        print(f"\n⚠️  样本不平衡 (比率: {ratio:.2f})，进行重采样...")
        
        if len(down_samples) > len(up_samples):
            # 过采样上涨样本
            print(f"   过采样上涨样本从 {len(up_samples):,} 到 {len(down_samples):,}")
            up_sampled = up_samples.sample(
                n=len(down_samples),
                replace=True,
                random_state=42
            )
            balanced_df = pd.concat([up_sampled, down_samples])
        else:
            # 过采样下跌样本
            print(f"   过采样下跌样本从 {len(down_samples):,} 到 {len(up_samples):,}")
            down_sampled = down_samples.sample(
                n=len(up_samples),
                replace=True,
                random_state=42
            )
            balanced_df = pd.concat([up_samples, down_sampled])
        
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"\n✅ 平衡后数据: {len(balanced_df):,} 条")
    else:
        balanced_df = df
        print(f"\n✅ 样本基本平衡，无需重采样")
    
    return balanced_df.drop(columns=['is_up'])

if __name__ == "__main__":
    # 加载数据
    data_path = 'data/raw/futu/5min_300033_updated.csv'
    print(f"加载数据: {data_path}")
    df = pd.read_csv(data_path)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    # 平衡数据
    balanced_df = balance_up_down_samples(df)
    
    # 保存
    output_path = 'data/raw/futu/5min_300033_balanced.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    balanced_df.to_csv(output_path, index=False)
    print(f"\n✅ 保存平衡数据至: {output_path}")
```

执行平衡：

```bash
python scripts/data_optimization/balance_data.py
```

### 2.2 创建噪声增强脚本

创建文件: `scripts/data_optimization/augment_data.py`

```python
"""
数据增强脚本 - 添加噪声增强
"""
import pandas as pd
import numpy as np
import os

def add_noise_augmentation(df, noise_levels=[0.005, 0.01]):
    """添加噪声增强"""
    
    print("=" * 80)
    print("数据噪声增强任务")
    print("=" * 80)
    
    augmented_dfs = [df]
    
    for noise_level in noise_levels:
        print(f"\n添加噪声级别: {noise_level*100:.1f}%")
        df_augmented = df.copy()
        
        # 对价格添加噪声
        for col in ['open', 'high', 'low', 'close']:
            noise = np.random.normal(0, noise_level, len(df))
            df_augmented[col] = df_augmented[col] * (1 + noise)
        
        # 确保OHLC逻辑正确
        df_augmented['high'] = df_augmented[['open', 'high', 'low', 'close']].max(axis=1)
        df_augmented['low'] = df_augmented[['open', 'high', 'low', 'close']].min(axis=1)
        
        augmented_dfs.append(df_augmented)
        print(f"   ✅ 生成增强数据: {len(df_augmented):,} 条")
    
    final_df = pd.concat(augmented_dfs, ignore_index=True)
    print(f"\n📊 增强后总数据: {len(final_df):,} 条 (原始{len(df):,}条 × {len(augmented_dfs)})")
    print(f"   数据增长: {(len(final_df) - len(df)) / len(df) * 100:.1f}%")
    
    return final_df

if __name__ == "__main__":
    # 加载平衡后的数据
    data_path = 'data/raw/futu/5min_300033_balanced.csv'
    print(f"加载数据: {data_path}")
    df = pd.read_csv(data_path)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    # 添加噪声增强
    augmented_df = add_noise_augmentation(df, noise_levels=[0.005, 0.01])
    
    # 保存
    output_path = 'data/raw/futu/5min_300033_augmented.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    augmented_df.to_csv(output_path, index=False)
    print(f"\n✅ 保存增强数据至: {output_path}")
```

执行增强：

```bash
python scripts/data_optimization/augment_data.py
```

---

## 步骤3: 特征工程增强

**优先级**: ⭐⭐⭐⭐⭐  
**难度**: ⭐⭐⭐ (较复杂)  
**预计耗时**: 1-2天

### 3.1 创建特征工程脚本

创建文件: `scripts/data_optimization/add_features.py`

```python
"""
特征工程脚本 - 添加技术指标和时间特征
"""
import pandas as pd
import numpy as np
import os

def add_technical_indicators(df):
    """添加技术指标"""
    df = df.copy()
    
    print("=" * 80)
    print("特征工程任务 - 添加技术指标")
    print("=" * 80)
    
    print("\n添加技术指标...")
    
    # 1. 移动平均线
    print("  - 移动平均线 (MA5, MA10, MA20)")
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    
    # 2. MACD
    print("  - MACD指标")
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # 3. RSI
    print("  - RSI指标")
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 4. 布林带
    print("  - 布林带")
    df['bb_middle'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * bb_std
    df['bb_lower'] = df['bb_middle'] - 2 * bb_std
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    
    # 5. 成交量指标
    print("  - 成交量指标")
    df['volume_ma'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    # 6. 价格变化率
    print("  - 价格变化率")
    df['price_change'] = df['close'].pct_change()
    df['price_range'] = (df['high'] - df['low']) / df['close']
    df['price_momentum'] = df['close'].pct_change(periods=5)
    
    # 7. 波动率
    print("  - 波动率")
    df['volatility'] = df['price_change'].rolling(10).std()
    
    # 8. 时间特征
    print("  - 时间特征")
    df['hour'] = df['timestamps'].dt.hour
    df['minute'] = df['timestamps'].dt.minute
    df['weekday'] = df['timestamps'].dt.dayofweek
    df['is_morning'] = (df['hour'] < 12).astype(int)
    df['is_afternoon'] = ((df['hour'] >= 13) & (df['hour'] < 15)).astype(int)
    
    # 删除NaN值
    df = df.dropna()
    
    print(f"\n📊 特征统计:")
    print(f"   原始特征数: 6 (OHLCV + timestamps)")
    print(f"   增强后特征数: {len(df.columns)}")
    print(f"   新增特征数: {len(df.columns) - 6}")
    print(f"   新增特征列表:")
    new_features = [col for col in df.columns if col not in ['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']]
    for feat in new_features:
        print(f"     - {feat}")
    
    return df

if __name__ == "__main__":
    # 加载增强后的数据
    data_path = 'data/raw/futu/5min_300033_augmented.csv'
    print(f"加载数据: {data_path}")
    df = pd.read_csv(data_path)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    # 添加特征
    enhanced_df = add_technical_indicators(df)
    
    # 保存
    output_path = 'data/raw/futu/5min_300033_enhanced.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    enhanced_df.to_csv(output_path, index=False)
    print(f"\n✅ 保存增强数据至: {output_path}")
    print(f"   最终数据量: {len(enhanced_df):,} 条")
    print(f"   特征数量: {len(enhanced_df.columns)}")
```

执行特征工程：

```bash
python scripts/data_optimization/add_features.py
```

---

## 验证与测试

### 验证最终数据

创建文件: `scripts/data_optimization/final_validation.py`

```python
"""
最终数据验证
"""
import pandas as pd
import json
import os

def final_validation():
    """验证最终处理后的数据"""
    
    print("=" * 80)
    print("最终数据验证")
    print("=" * 80)
    
    # 加载最终数据
    data_path = 'data/raw/futu/5min_300033_enhanced.csv'
    df = pd.read_csv(data_path)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    print(f"\n📊 数据概览:")
    print(f"   总记录数: {len(df):,}")
    print(f"   特征数量: {len(df.columns)}")
    print(f"   时间范围: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
    print(f"   交易日数: {df['timestamps'].dt.date.nunique()}")
    
    print(f"\n📋 特征列表:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    print(f"\n⚠️  缺失值检查:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print(f"   ✅ 无缺失值")
    else:
        print(f"   ❌ 发现缺失值:")
        for col, count in missing[missing > 0].items():
            print(f"      {col}: {count}")
    
    # 生成最终报告
    report = {
        'total_records': int(len(df)),
        'features': int(len(df.columns)),
        'feature_list': list(df.columns),
        'date_range': f"{df['timestamps'].min()} to {df['timestamps'].max()}",
        'trading_days': int(df['timestamps'].dt.date.nunique()),
        'missing_values': int(df.isnull().sum().sum()),
        'status': 'READY_FOR_TRAINING'
    }
    
    # 保存报告
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/final_data_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ 最终报告已保存至: outputs/final_data_report.json")
    print(f"   状态: {report['status']}")
    
    return report

if __name__ == "__main__":
    final_validation()
```

执行验证：

```bash
python scripts/data_optimization/final_validation.py
```

---

## 常见问题

### Q1: 数据合并后出现重复记录怎么办？

**A**: 脚本已自动处理，使用`drop_duplicates(subset=['timestamps'], keep='last')`去重。

### Q2: 数据增强后数据量太大怎么办？

**A**: 
- 可以减少噪声级别数量（从2个减为1个）
- 或者只对部分数据进行增强
- 64GB内存完全可以处理百万级数据

### Q3: 特征工程后出现NaN值怎么办？

**A**: 脚本已使用`dropna()`自动删除含NaN的行。这是正常的，因为某些指标（如MA20）需要足够的前置数据。

### Q4: 如何验证数据质量？

**A**: 运行验证脚本，检查：
- 缺失值数量为0
- OHLC逻辑正确
- 无极端异常值
- 数据质量评级为PASS

---

## 预期成果

### 数据层面改进

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| **数据量** | 34,802条 | 104,988条 (3x) | +200% |
| **特征数** | 6个 | 25+个 | +300% |
| **涨跌平衡** | 可能失衡 | 强制平衡 | ✅ |
| **最新数据** | 缺失 | 包含至2026-04-30 | ✅ |
| **技术指标** | 无 | MA/MACD/RSI/BB等 | ✅ |

### 模型性能预期

- **MAPE**: 1.70% → 1.3% (-0.4%)
- **R²**: -3.76 → -1.0 (+2.76)
- **方向准确率**: 66.7% → 70% (+3.3%)
- **消除系统性看空偏差**: ✅

### 下一步

数据优化完成后，可以继续进行：
- 方案二：模型架构优化
- 方案三：训练策略优化
- 或直接开始重新训练模型

---

## 附录：文件清单

### 📁 脚本目录结构

```
scripts/data_optimization/
├── merge_data.py              # 步骤1: 数据合并
├── validate_data.py           # 步骤2: 数据验证
├── balance_data.py            # 步骤3: 数据平衡
├── augment_data.py            # 步骤4: 数据增强
├── feature_engineering.py     # 步骤5: 特征工程
├── train_model.py             # 步骤6: 模型训练
├── run_all_steps.py           # 一键执行所有步骤
├── run_option1.bat            # Windows快速启动脚本
└── README.md                  # 详细使用说明
```

### 🚀 快速开始

#### 方法1: Windows批处理脚本（最简单）

```bash
# 双击运行或在命令行执行
scripts\data_optimization\run_option1.bat
```

#### 方法2: Python一键执行

```bash
python scripts\data_optimization\run_all_steps.py
```

#### 方法3: 分步执行

```bash
# 逐步执行每个优化步骤
python scripts\data_optimization\merge_data.py
python scripts\data_optimization\validate_data.py
python scripts\data_optimization\balance_data.py
python scripts\data_optimization\augment_data.py
python scripts\data_optimization\feature_engineering.py
python scripts\data_optimization\train_model.py
```

### 📄 生成的数据文件

| 文件名 | 说明 | 大小估计 |
|--------|------|----------|
| `data/raw/futu/5min_300033_updated.csv` | 合并后数据 | ~10 MB |
| `data/validation_report.txt` | 数据验证报告 | ~5 KB |
| `data/raw/futu/5min_300033_balanced.csv` | 平衡后数据 | ~10-15 MB |
| `data/raw/futu/5min_300033_augmented.csv` | 增强后数据 | ~10-15 MB |
| `data/raw/futu/5min_300033_with_features.csv` | 最终特征数据 (30+特征) | ~15-20 MB |

### 📊 日志文件

| 日志文件 | 记录内容 |
|----------|----------|
| `logs/data_merge.log` | 数据合并过程和统计 |
| `logs/data_validation.log` | 数据质量检查结果 |
| `logs/data_balance.log` | 涨跌样本平衡过程 |
| `logs/data_augmentation.log` | 噪声增强详情 |
| `logs/feature_engineering.log` | 特征计算和添加过程 |
| `logs/training.log` | 模型训练进度和结果 |

### 📈 输出模型

训练完成后，模型将保存在：
- `outputs/models/optimized_tokenizer/` - 优化后的Tokenizer
- `outputs/models/optimized_predictor/` - 优化后的Predictor
- `outputs/predictions/` - 预测结果

---

**文档版本**: 1.0  
**最后更新**: 2026年5月1日  
**适配配置**: AMD EPYC 9T24 + 64GB内存 + RTX 5880 Ada + CUDA 12.8  
**状态**: ✅ 准备就绪，可开始执行

**相关文档**:
- [MODEL_OPTIMIZATION_PLAN.md](MODEL_OPTIMIZATION_PLAN.md) - 完整优化方案
- [SYSTEM_CONFIG.md](SYSTEM_CONFIG.md) - 系统配置详情
- [scripts/data_optimization/README.md](scripts/data_optimization/README.md) - 脚本详细说明
