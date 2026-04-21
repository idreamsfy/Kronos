"""
同花顺 (300033) 专用微调配置
使用 Kronos-base 模型进行微调
"""

import os

class ThsConfig:
    """同花顺股票微调配置"""
    
    def __init__(self):
        # =================================================================
        # 数据配置
        # =================================================================
        self.stock_code = '300033'
        self.stock_name = '同花顺'
        self.data_file = f"./data/raw/akshare/daily_{self.stock_code}.csv"
        
        # 时间范围
        self.train_ratio = 0.7  # 70% 训练
        self.val_ratio = 0.15   # 15% 验证
        self.test_ratio = 0.15  # 15% 测试
        
        # 滑动窗口参数
        self.lookback_window = 100  # 历史窗口长度
        self.predict_window = 20    # 预测长度
        self.max_context = 512      # 最大上下文长度
        
        # 特征列
        self.feature_list = ['open', 'high', 'low', 'close', 'volume', 'amount']
        
        # =================================================================
        # 模型配置 - 使用 Kronos-base
        # =================================================================
        self.pretrained_model_path = "./model/pretrained_models/Kronos-base"
        self.pretrained_tokenizer_path = "./model/pretrained_models/Kronos-Tokenizer-base"
        
        # =================================================================
        # 训练超参数
        # =================================================================
        self.epochs = 30
        self.batch_size = 32  # Kronos-base 较大，减小批次
        self.learning_rate = 2e-4
        self.weight_decay = 0.01
        self.warmup_ratio = 0.1
        self.clip = 5.0
        
        # =================================================================
        # 设备配置
        # =================================================================
        import torch
        if torch.backends.mps.is_available():
            self.device = 'mps'
        elif torch.cuda.is_available():
            self.device = 'cuda'
        else:
            self.device = 'cpu'
        
        print(f"✅ 使用设备: {self.device}")
        
        # =================================================================
        # 保存路径
        # =================================================================
        self.output_dir = f"./outputs/models/finetune_{self.stock_code}_base_mps"
        self.log_dir = "./outputs/logs"
        
        # 创建目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        print(f"📁 输出目录: {self.output_dir}")
        print(f"📊 数据文件: {self.data_file}")
        print(f"🎯 模型: Kronos-base (102M params)")
        print(f"⚙️  批次大小: {self.batch_size}")
        print(f"📈 学习率: {self.learning_rate}")
        print(f"🔄 Epochs: {self.epochs}")


# 创建全局配置实例
config = ThsConfig()
