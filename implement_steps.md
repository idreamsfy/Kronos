# 🚀 Kronos 模型优化实施步骤指南

**基于**: MODEL_OPTIMIZATION_PLAN.md  
**制定时间**: 2026年5月1日  
**目标**: 系统化执行模型优化方案，提升预测准确性

---

## 📋 实施前准备

### 1. 环境检查

```bash
# 检查Python环境
python --version

# 检查PyTorch和CUDA
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"

# 检查GPU信息
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"No GPU\"}')"

# 检查依赖包
pip list | findstr "pandas numpy matplotlib scikit-learn"
```

### 2. 备份当前模型和数据

```bash
# 创建备份目录
mkdir backups
mkdir backups\models
mkdir backups\data

# 备份当前模型
xcopy outputs\models\* backups\models\ /E /I

# 备份当前数据
xcopy data\raw\* backups\data\ /E /I
```

### 3. 创建工作目录

```bash
mkdir optimization_work
cd optimization_work
mkdir data
mkdir models
mkdir logs
mkdir scripts
```

---

## 🎯 第1周：快速改进实施步骤

### Day 1-2: 数据扩充

#### 步骤1.1: 获取最新数据

```python
# scripts/fetch_latest_data.py
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def fetch_latest_300033_data():
    """获取最新的300033股票5分钟数据"""
    
    # 获取最近5个交易日的数据
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')
    
    # 使用akshare获取数据
    df = ak.stock_zh_a_hist_min_em(
        symbol="300033",
        period="5",
        start_date=start_date,
        end_date=end_date,
        adjust=""
    )
    
    # 重命名列以匹配现有格式
    df.rename(columns={
        '时间': 'timestamps',
        '开盘': 'open',
        '最高': 'high',
        '最低': 'low',
        '收盘': 'close',
        '成交量': 'volume',
        '成交额': 'amount'
    }, inplace=True)
    
    # 转换时间格式
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    return df

if __name__ == "__main__":
    print("获取最新数据...")
    new_data = fetch_latest_300033_data()
    new_data.to_csv('data/raw/futu/5min_300033_latest.csv', index=False)
    print(f"获取到 {len(new_data)} 条新数据")
    print(f"时间范围: {new_data['timestamps'].min()} 到 {new_data['timestamps'].max()}")
```

#### 步骤1.2: 合并历史数据和新数据

```python
# scripts/merge_data.py
import pandas as pd
import os

def merge_historical_and_new_data():
    """合并历史数据和新数据"""
    
    # 读取历史数据
    historical_path = 'data/raw/futu/5min_300033.csv'
    if os.path.exists(historical_path):
        historical_df = pd.read_csv(historical_path)
        print(f"历史数据: {len(historical_df)} 条")
    else:
        raise FileNotFoundError(f"历史数据文件不存在: {historical_path}")
    
    # 读取新数据
    new_path = 'data/raw/futu/5min_300033_latest.csv'
    if os.path.exists(new_path):
        new_df = pd.read_csv(new_path)
        print(f"新数据: {len(new_df)} 条")
    else:
        raise FileNotFoundError(f"新数据文件不存在: {new_path}")
    
    # 转换时间格式
    historical_df['timestamps'] = pd.to_datetime(historical_df['timestamps'])
    new_df['timestamps'] = pd.to_datetime(new_df['timestamps'])
    
    # 合并数据
    combined_df = pd.concat([historical_df, new_df], ignore_index=True)
    
    # 去重（基于时间戳）
    combined_df = combined_df.drop_duplicates(subset=['timestamps'], keep='last')
    
    # 按时间排序
    combined_df = combined_df.sort_values('timestamps').reset_index(drop=True)
    
    # 保存合并后的数据
    output_path = 'data/raw/futu/5min_300033_updated.csv'
    combined_df.to_csv(output_path, index=False)
    
    print(f"\n合并完成!")
    print(f"总数据量: {len(combined_df)} 条")
    print(f"时间范围: {combined_df['timestamps'].min()} 到 {combined_df['timestamps'].max()}")
    print(f"保存至: {output_path}")
    
    return combined_df

if __name__ == "__main__":
    merged_data = merge_historical_and_new_data()
```

#### 步骤1.3: 数据质量验证

```python
# scripts/validate_data.py
import pandas as pd
import numpy as np

def validate_data_quality(df):
    """验证数据质量"""
    
    print("=" * 60)
    print("数据质量验证报告")
    print("=" * 60)
    
    # 基本统计
    print(f"\n1. 基本统计:")
    print(f"   总记录数: {len(df):,}")
    print(f"   时间范围: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
    print(f"   缺失值统计:")
    for col in ['open', 'high', 'low', 'close', 'volume']:
        missing = df[col].isnull().sum()
        print(f"     {col}: {missing} ({missing/len(df)*100:.2f}%)")
    
    # OHLC逻辑验证
    print(f"\n2. OHLC逻辑验证:")
    invalid_ohlc = ((df['high'] < df['low']) | 
                   (df['high'] < df['open']) | 
                   (df['high'] < df['close']) |
                   (df['low'] > df['open']) | 
                   (df['low'] > df['close']))
    print(f"   无效OHLC记录: {invalid_ohlc.sum()} ({invalid_ohlc.sum()/len(df)*100:.2f}%)")
    
    # 价格异常检测
    print(f"\n3. 价格异常检测:")
    price_changes = df['close'].pct_change()
    extreme_changes = (price_changes.abs() > 0.1).sum()  # 超过10%的变动
    print(f"   极端价格变动 (>10%): {extreme_changes} 次")
    
    # 成交量异常检测
    print(f"\n4. 成交量异常检测:")
    vol_mean = df['volume'].mean()
    vol_std = df['volume'].std()
    extreme_vol = (df['volume'] > vol_mean + 3 * vol_std).sum()
    print(f"   极端成交量 (>3σ): {extreme_vol} 次")
    
    # 数据连续性检查
    print(f"\n5. 数据连续性检查:")
    time_diffs = df['timestamps'].diff()
    median_diff = time_diffs.median()
    print(f"   中位数时间间隔: {median_diff}")
    irregular_intervals = (time_diffs != median_diff).sum() - 1  # 减去第一个NaT
    print(f"   不规则时间间隔: {irregular_intervals} 次")
    
    print("\n" + "=" * 60)
    
    return {
        'total_records': len(df),
        'missing_values': df[['open', 'high', 'low', 'close', 'volume']].isnull().sum().to_dict(),
        'invalid_ohlc': invalid_ohlc.sum(),
        'extreme_price_changes': extreme_changes,
        'extreme_volume': extreme_vol,
        'irregular_intervals': irregular_intervals
    }

if __name__ == "__main__":
    df = pd.read_csv('data/raw/futu/5min_300033_updated.csv')
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    report = validate_data_quality(df)
```

**执行命令**:
```bash
python scripts/fetch_latest_data.py
python scripts/merge_data.py
python scripts/validate_data.py
```

---

### Day 3-4: 缩短预测窗口

#### 步骤2.1: 修改数据集配置

```python
# finetune/dataset_updated.py
import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np

class FiveMinFinetuneDataset(Dataset):
    """5分钟数据微调数据集 - 优化版本"""
    
    def __init__(self, df, lookback=100, pred_len=48):
        """
        Args:
            df: 包含OHLCV数据的DataFrame
            lookback: 回看窗口长度
            pred_len: 预测窗口长度（改为48，即1天）
        """
        self.df = df
        self.lookback = lookback
        self.pred_len = pred_len  # 从144改为48
        
        # 归一化参数
        self.price_scaler = df['close'].mean()
        self.volume_scaler = df['volume'].mean()
        
        # 生成样本索引
        self.valid_indices = []
        for i in range(len(df) - lookback - pred_len + 1):
            self.valid_indices.append(i)
        
        print(f"数据集初始化完成:")
        print(f"  总样本数: {len(self.valid_indices)}")
        print(f"  回看窗口: {lookback}")
        print(f"  预测窗口: {pred_len} (1天)")
    
    def __len__(self):
        return len(self.valid_indices)
    
    def __getitem__(self, idx):
        start_idx = self.valid_indices[idx]
        end_idx = start_idx + self.lookback
        pred_end_idx = end_idx + self.pred_len
        
        # 提取输入序列
        input_seq = self.df.iloc[start_idx:end_idx]
        target_seq = self.df.iloc[end_idx:pred_end_idx]
        
        # 归一化
        input_normalized = self._normalize(input_seq)
        target_normalized = self._normalize(target_seq)
        
        return {
            'input': torch.FloatTensor(input_normalized.values),
            'target': torch.FloatTensor(target_normalized.values),
            'input_timestamps': input_seq['timestamps'].values,
            'target_timestamps': target_seq['timestamps'].values
        }
    
    def _normalize(self, df):
        """归一化数据"""
        normalized = df.copy()
        normalized['open'] = normalized['open'] / self.price_scaler
        normalized['high'] = normalized['high'] / self.price_scaler
        normalized['low'] = normalized['low'] / self.price_scaler
        normalized['close'] = normalized['close'] / self.price_scaler
        normalized['volume'] = normalized['volume'] / self.volume_scaler
        return normalized[['open', 'high', 'low', 'close', 'volume']]
```

#### 步骤2.2: 更新训练配置

```yaml
# finetune/config_updated.yaml
data:
  data_path: "data/raw/futu/5min_300033_updated.csv"
  lookback_window: 100
  predict_window: 48  # 从144改为48
  max_context: 512
  clip: 5.0
  train_ratio: 0.8
  val_ratio: 0.15
  test_ratio: 0.05

training:
  tokenizer_epochs: 20
  basemodel_epochs: 15
  batch_size: 32
  log_interval: 50
  num_workers: 6
  seed: 42
  
  tokenizer_learning_rate: 0.0002
  predictor_learning_rate: 0.00001  # 调整学习率
  
  adam_beta1: 0.9
  adam_beta2: 0.95
  adam_weight_decay: 0.1
  accumulation_steps: 1

model_paths:
  pretrained_tokenizer: "model/pretrained_models/Kronos-Tokenizer-base"
  pretrained_predictor: "model/pretrained_models/Kronos-base"
  exp_name: "optimized_300033_pred48"
  base_path: "outputs/models"

device:
  use_cuda: true
  device_id: 0
```

#### 步骤2.3: 重新训练模型

```python
# finetune/train_optimized.py
import torch
from torch.utils.data import DataLoader
from dataset_updated import FiveMinFinetuneDataset
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd
import yaml

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def train_optimized_model():
    """训练优化后的模型"""
    
    # 加载配置
    config = load_config('finetune/config_updated.yaml')
    
    # 加载数据
    print("加载数据...")
    df = pd.read_csv(config['data']['data_path'])
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    # 创建数据集
    dataset = FiveMinFinetuneDataset(
        df=df,
        lookback=config['data']['lookback_window'],
        pred_len=config['data']['predict_window']
    )
    
    # 划分训练集和验证集
    train_size = int(len(dataset) * config['data']['train_ratio'])
    val_size = int(len(dataset) * config['data']['val_ratio'])
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=True,
        num_workers=config['training']['num_workers'],
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False,
        num_workers=config['training']['num_workers'],
        pin_memory=True
    )
    
    # 初始化模型
    print("初始化模型...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    tokenizer = KronosTokenizer.from_pretrained(
        config['model_paths']['pretrained_tokenizer']
    ).to(device)
    
    predictor = KronosPredictor.from_pretrained(
        config['model_paths']['pretrained_predictor'],
        tokenizer=tokenizer
    ).to(device)
    
    # 设置优化器
    optimizer = torch.optim.AdamW(
        predictor.parameters(),
        lr=config['training']['predictor_learning_rate'],
        betas=(config['training']['adam_beta1'], config['training']['adam_beta2']),
        weight_decay=config['training']['adam_weight_decay']
    )
    
    # 训练循环
    print("开始训练...")
    best_val_loss = float('inf')
    
    for epoch in range(config['training']['basemodel_epochs']):
        # 训练阶段
        predictor.train()
        total_train_loss = 0
        
        for batch_idx, batch in enumerate(train_loader):
            optimizer.zero_grad()
            
            # 前向传播
            input_data = batch['input'].to(device)
            target_data = batch['target'].to(device)
            
            # 这里需要根据实际模型接口调整
            loss = predictor.compute_loss(input_data, target_data)
            
            # 反向传播
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                predictor.parameters(), 
                config['data']['clip']
            )
            optimizer.step()
            
            total_train_loss += loss.item()
            
            if batch_idx % config['training']['log_interval'] == 0:
                print(f"Epoch [{epoch+1}/{config['training']['basemodel_epochs']}] "
                      f"Batch [{batch_idx}/{len(train_loader)}] "
                      f"Loss: {loss.item():.4f}")
        
        avg_train_loss = total_train_loss / len(train_loader)
        
        # 验证阶段
        predictor.eval()
        total_val_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                input_data = batch['input'].to(device)
                target_data = batch['target'].to(device)
                
                loss = predictor.compute_loss(input_data, target_data)
                total_val_loss += loss.item()
        
        avg_val_loss = total_val_loss / len(val_loader)
        
        print(f"\nEpoch [{epoch+1}/{config['training']['basemodel_epochs']}] "
              f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
        
        # 保存最佳模型
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            save_path = f"outputs/models/{config['model_paths']['exp_name']}/best_model"
            predictor.save_pretrained(save_path)
            print(f"✅ 保存最佳模型到: {save_path}")
    
    print("\n训练完成!")
    print(f"最佳验证损失: {best_val_loss:.4f}")

if __name__ == "__main__":
    train_optimized_model()
```

**执行命令**:
```bash
python finetune/train_optimized.py
```

---

### Day 5-7: 超参数调优

#### 步骤3.1: 创建超参数搜索脚本

```python
# scripts/hyperparameter_search.py
import torch
import itertools
from model import KronosPredictor
import pandas as pd
import numpy as np

def hyperparameter_search():
    """超参数搜索"""
    
    # 定义搜索空间
    param_grid = {
        'temperature': [0.8, 1.0, 1.2],
        'top_p': [0.9, 0.95, 1.0],
        'learning_rate': [5e-6, 1e-5, 2e-5]
    }
    
    # 加载测试数据
    test_df = pd.read_csv('data/raw/futu/5min_300033_updated.csv')
    test_df['timestamps'] = pd.to_datetime(test_df['timestamps'])
    
    # 加载模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    predictor = KronosPredictor.from_pretrained(
        'outputs/models/optimized_300033_pred48/best_model'
    ).to(device)
    
    results = []
    
    # 遍历所有参数组合
    for temp, top_p, lr in itertools.product(
        param_grid['temperature'],
        param_grid['top_p'],
        param_grid['learning_rate']
    ):
        print(f"\n测试参数组合: T={temp}, top_p={top_p}, lr={lr}")
        
        # 这里需要根据实际预测接口调整
        try:
            # 进行预测并计算指标
            mape, r2, direction_acc = evaluate_prediction(
                predictor, test_df, temp, top_p
            )
            
            results.append({
                'temperature': temp,
                'top_p': top_p,
                'learning_rate': lr,
                'mape': mape,
                'r2': r2,
                'direction_accuracy': direction_acc
            })
            
            print(f"  MAPE: {mape:.2f}%, R²: {r2:.4f}, Dir Acc: {direction_acc:.2f}%")
            
        except Exception as e:
            print(f"  错误: {e}")
            continue
    
    # 保存结果
    results_df = pd.DataFrame(results)
    results_df.to_csv('outputs/hyperparameter_search_results.csv', index=False)
    
    # 找出最佳参数组合
    best_idx = results_df['mape'].idxmin()
    best_params = results_df.loc[best_idx]
    
    print("\n" + "=" * 60)
    print("最佳参数组合:")
    print(f"  Temperature: {best_params['temperature']}")
    print(f"  Top-p: {best_params['top_p']}")
    print(f"  Learning Rate: {best_params['learning_rate']}")
    print(f"  MAPE: {best_params['mape']:.2f}%")
    print(f"  R²: {best_params['r2']:.4f}")
    print("=" * 60)

def evaluate_prediction(predictor, test_df, temperature, top_p):
    """评估预测性能"""
    # 这里需要根据实际的预测接口实现
    # 返回 MAPE, R², 方向准确率
    pass

if __name__ == "__main__":
    hyperparameter_search()
```

**执行命令**:
```bash
python scripts/hyperparameter_search.py
```

---

## 🎯 第2周：中级优化实施步骤

### Day 8-10: 特征工程

#### 步骤4.1: 添加技术指标

```python
# scripts/feature_engineering.py
import pandas as pd
import numpy as np

def add_technical_indicators(df):
    """添加技术指标"""
    df = df.copy()
    
    print("添加技术指标...")
    
    # 1. 移动平均线
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    
    # 2. MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # 3. RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 4. 布林带
    df['bb_middle'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * bb_std
    df['bb_lower'] = df['bb_middle'] - 2 * bb_std
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    
    # 5. 成交量指标
    df['volume_ma'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    # 6. 价格变化率
    df['price_change'] = df['close'].pct_change()
    df['price_range'] = (df['high'] - df['low']) / df['close']
    df['price_momentum'] = df['close'].pct_change(periods=5)
    
    # 7. 波动率
    df['volatility'] = df['price_change'].rolling(10).std()
    
    # 8. 时间特征
    df['hour'] = df['timestamps'].dt.hour
    df['minute'] = df['timestamps'].dt.minute
    df['weekday'] = df['timestamps'].dt.dayofweek
    df['is_morning'] = (df['hour'] < 12).astype(int)
    df['is_afternoon'] = ((df['hour'] >= 13) & (df['hour'] < 15)).astype(int)
    
    # 删除NaN值
    df = df.dropna()
    
    print(f"原始特征数: 6")
    print(f"增强后特征数: {len(df.columns) - 1}")
    print(f"新增特征: {[col for col in df.columns if col not in ['timestamps', 'open', 'high', 'low', 'close', 'volume']]}")
    
    return df

if __name__ == "__main__":
    df = pd.read_csv('data/raw/futu/5min_300033_updated.csv')
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    enhanced_df = add_technical_indicators(df)
    enhanced_df.to_csv('data/raw/futu/5min_300033_enhanced.csv', index=False)
    print(f"\n保存增强数据到: data/raw/futu/5min_300033_enhanced.csv")
```

**执行命令**:
```bash
python scripts/feature_engineering.py
```

---

### Day 11-12: 早停机制

#### 步骤5.1: 实现早停回调

```python
# finetune/utils/early_stopping.py
import torch
import os

class EarlyStopping:
    """早停机制"""
    
    def __init__(self, patience=5, min_delta=0.001, save_path=None):
        """
        Args:
            patience: 容忍的epoch数
            min_delta: 最小改进阈值
            save_path: 最佳模型保存路径
        """
        self.patience = patience
        self.min_delta = min_delta
        self.save_path = save_path
        self.counter = 0
        self.best_loss = float('inf')
        self.early_stop = False
        self.best_model_state = None
    
    def __call__(self, val_loss, model):
        """
        Args:
            val_loss: 验证损失
            model: 当前模型
        """
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            # 保存最佳模型状态
            self.best_model_state = {
                k: v.cpu().clone() for k, v in model.state_dict().items()
            }
            
            if self.save_path:
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                torch.save(self.best_model_state, self.save_path)
                print(f"  ✅ 保存最佳模型 (Val Loss: {val_loss:.4f})")
        else:
            self.counter += 1
            print(f"  ⚠️  未改进 ({self.counter}/{self.patience})")
            
            if self.counter >= self.patience:
                self.early_stop = True
                print(f"  🛑 早停触发! 最佳验证损失: {self.best_loss:.4f}")
    
    def load_best_model(self, model):
        """加载最佳模型"""
        if self.best_model_state:
            model.load_state_dict(self.best_model_state)
            print("已加载最佳模型")
```

#### 步骤5.2: 集成到训练流程

```python
# 在 train_optimized.py 中添加早停
from utils.early_stopping import EarlyStopping

# 初始化早停
early_stopping = EarlyStopping(
    patience=5,
    min_delta=0.001,
    save_path=f"outputs/models/{config['model_paths']['exp_name']}/best_model.pt"
)

for epoch in range(max_epochs):
    # ... 训练代码 ...
    
    # 验证
    avg_val_loss = validate(...)
    
    # 早停检查
    early_stopping(avg_val_loss, predictor)
    
    if early_stopping.early_stop:
        print("早停触发，结束训练")
        break

# 加载最佳模型
early_stopping.load_best_model(predictor)
```

---

### Day 13-14: 数据增强

#### 步骤6.1: 实现数据增强

```python
# scripts/data_augmentation.py
import pandas as pd
import numpy as np

def balance_up_down_samples(df):
    """平衡涨跌样本"""
    
    # 标记涨跌
    df['is_up'] = (df['close'] > df['open']).astype(int)
    
    up_samples = df[df['is_up'] == 1]
    down_samples = df[df['is_up'] == 0]
    
    print(f"上涨样本: {len(up_samples)} ({len(up_samples)/len(df)*100:.1f}%)")
    print(f"下跌样本: {len(down_samples)} ({len(down_samples)/len(df)*100:.1f}%)")
    
    # 如果比例失衡，进行过采样
    ratio = len(down_samples) / len(up_samples)
    if ratio > 1.5 or ratio < 0.67:
        print(f"样本不平衡，进行重采样...")
        
        if len(down_samples) > len(up_samples):
            # 过采样上涨样本
            up_sampled = up_samples.sample(
                n=len(down_samples),
                replace=True,
                random_state=42
            )
            balanced_df = pd.concat([up_sampled, down_samples])
        else:
            # 过采样下跌样本
            down_sampled = down_samples.sample(
                n=len(up_samples),
                replace=True,
                random_state=42
            )
            balanced_df = pd.concat([up_samples, down_sampled])
        
        balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"平衡后数据: {len(balanced_df)} 条")
    else:
        balanced_df = df
        print("样本基本平衡，无需重采样")
    
    return balanced_df.drop(columns=['is_up'])

def add_noise_augmentation(df, noise_levels=[0.005, 0.01]):
    """添加噪声增强"""
    
    augmented_dfs = [df]
    
    for noise_level in noise_levels:
        df_augmented = df.copy()
        
        # 对价格添加噪声
        for col in ['open', 'high', 'low', 'close']:
            noise = np.random.normal(0, noise_level, len(df))
            df_augmented[col] = df_augmented[col] * (1 + noise)
        
        # 确保OHLC逻辑正确
        df_augmented['high'] = df_augmented[['open', 'high', 'low', 'close']].max(axis=1)
        df_augmented['low'] = df_augmented[['open', 'high', 'low', 'close']].min(axis=1)
        
        augmented_dfs.append(df_augmented)
    
    final_df = pd.concat(augmented_dfs, ignore_index=True)
    print(f"噪声增强后数据: {len(final_df)} 条 (原始{len(df)}条 × {len(augmented_dfs)})")
    
    return final_df

if __name__ == "__main__":
    df = pd.read_csv('data/raw/futu/5min_300033_enhanced.csv')
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    # 平衡样本
    balanced_df = balance_up_down_samples(df)
    
    # 添加噪声
    augmented_df = add_noise_augmentation(balanced_df)
    
    # 保存
    augmented_df.to_csv('data/raw/futu/5min_300033_augmented.csv', index=False)
    print(f"\n保存增强数据到: data/raw/futu/5min_300033_augmented.csv")
```

**执行命令**:
```bash
python scripts/data_augmentation.py
```

---

## 📊 每周验证和监控

### 验证脚本

```python
# scripts/weekly_validation.py
import pandas as pd
import numpy as np
from model import KronosPredictor
import torch

def weekly_validation(model_path, test_data_path):
    """每周验证模型性能"""
    
    print("=" * 60)
    print("每周模型验证")
    print("=" * 60)
    
    # 加载模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    predictor = KronosPredictor.from_pretrained(model_path).to(device)
    
    # 加载测试数据
    test_df = pd.read_csv(test_data_path)
    test_df['timestamps'] = pd.to_datetime(test_df['timestamps'])
    
    # 进行预测
    predictions = predictor.predict(
        df=test_df,
        pred_len=48,
        T=1.0,
        top_p=0.95
    )
    
    # 计算指标
    actual = test_df.iloc[-48:]
    
    mape = calculate_mape(actual, predictions)
    r2 = calculate_r2(actual, predictions)
    direction_acc = calculate_direction_accuracy(actual, predictions)
    
    print(f"\n验证结果:")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  R²: {r2:.4f}")
    print(f"  方向准确率: {direction_acc:.2f}%")
    
    # 保存验证结果
    validation_report = {
        'date': pd.Timestamp.now(),
        'model_path': model_path,
        'mape': mape,
        'r2': r2,
        'direction_accuracy': direction_acc
    }
    
    report_df = pd.DataFrame([validation_report])
    report_file = 'outputs/validation_reports.csv'
    
    if pd.io.common.file_exists(report_file):
        existing = pd.read_csv(report_file)
        report_df = pd.concat([existing, report_df], ignore_index=True)
    
    report_df.to_csv(report_file, index=False)
    print(f"\n验证报告已保存至: {report_file}")
    
    return validation_report

def calculate_mape(actual, predicted):
    """计算MAPE"""
    return np.mean(np.abs((actual['close'] - predicted['close']) / actual['close'])) * 100

def calculate_r2(actual, predicted):
    """计算R²"""
    ss_res = np.sum((actual['close'] - predicted['close']) ** 2)
    ss_tot = np.sum((actual['close'] - np.mean(actual['close'])) ** 2)
    return 1 - (ss_res / ss_tot)

def calculate_direction_accuracy(actual, predicted):
    """计算方向准确率"""
    actual_direction = np.sign(actual['close'].diff().iloc[1:])
    predicted_direction = np.sign(predicted['close'].diff().iloc[1:])
    return np.mean(actual_direction == predicted_direction) * 100

if __name__ == "__main__":
    weekly_validation(
        model_path='outputs/models/optimized_300033_pred48/best_model',
        test_data_path='data/raw/futu/5min_300033_updated.csv'
    )
```

---

## 🎯 关键里程碑检查点

### Week 1 结束检查

```bash
# 检查点1: 数据扩充完成
python scripts/validate_data.py

# 检查点2: 新模型训练完成
ls -la outputs/models/optimized_300033_pred48/best_model

# 检查点3: 超参数搜索结果
cat outputs/hyperparameter_search_results.csv
```

**预期成果**:
- ✅ 数据量增加至少10%
- ✅ 预测窗口缩短至48
- ✅ MAPE降至1.3%以下
- ✅ R²提升至-1.0以上

### Week 2 结束检查

```bash
# 检查点4: 特征工程完成
python scripts/feature_engineering.py

# 检查点5: 早停机制生效
grep "早停触发" outputs/logs/training.log

# 检查点6: 数据增强完成
wc -l data/raw/futu/5min_300033_augmented.csv
```

**预期成果**:
- ✅ 特征数量增加至20+
- ✅ 自动选择最佳模型
- ✅ MAPE降至1.1%以下
- ✅ R²转正 (>0)

---

## 📝 实施注意事项

### 1. 资源管理

```bash
# 监控GPU使用情况
while ($true) { Clear-Host; nvidia-smi; Start-Sleep 5 }

# 清理缓存
python -c "import torch; torch.cuda.empty_cache()"
```

### 2. 版本控制

```bash
# 每次重要更新后提交
git add .
git commit -m "优化阶段X完成: [具体改进]"
git tag -a "optimization-phase-X" -m "优化阶段X完成"
```

### 3. 日志记录

```python
# 使用logging模块
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/optimization.log'),
        logging.StreamHandler()
    ]
)
```

### 4. 备份策略

```bash
# 每日备份
robocopy outputs\models backups\models_daily_%date:~0,10% /E

# 每周完整备份
robocopy . backups\weekly_%date:~0,10% /E /XD .git backups
```

---

## 🚨 故障排除

### 常见问题1: CUDA内存不足

```python
# 解决方案: 减小batch size
config['training']['batch_size'] = 16  # 从32降到16

# 或使用梯度累积
config['training']['accumulation_steps'] = 2
```

### 常见问题2: 训练不收敛

```python
# 解决方案: 降低学习率
config['training']['predictor_learning_rate'] = 5e-6

# 或增加warmup
scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=10, T_mult=2
)
```

### 常见问题3: 过拟合

```python
# 解决方案: 增加正则化
config['training']['adam_weight_decay'] = 0.2

# 或使用dropout
model.dropout_rate = 0.3
```

---

## 📈 进度追踪表

| 任务 | 计划时间 | 实际完成 | 状态 | 备注 |
|------|---------|---------|------|------|
| 数据扩充 | Day 1-2 | | ⏳ | |
| 缩短预测窗口 | Day 3-4 | | ⏳ | |
| 超参数调优 | Day 5-7 | | ⏳ | |
| 特征工程 | Day 8-10 | | ⏳ | |
| 早停机制 | Day 11-12 | | ⏳ | |
| 数据增强 | Day 13-14 | | ⏳ | |

---

**最后更新**: 2026年5月1日  
**下一步**: 开始执行Day 1-2的数据扩充任务
