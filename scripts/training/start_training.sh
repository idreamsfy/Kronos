#!/bin/bash
# Kronos MPS GPU 训练启动脚本
# 用于 macOS Apple Silicon (M1/M2/M3)

echo "======================================================================"
echo "Kronos Tokenizer 训练 - Apple Silicon MPS GPU"
echo "======================================================================"
echo ""

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 检查 MPS 可用性
echo "检查 MPS 可用性..."
python -c "import torch; print(f'MPS可用: {torch.backends.mps.is_available()}')"
echo ""

# 开始训练
echo "开始训练..."
echo "配置文件: finetune/config_300033_mps.yaml"
echo "输出目录: ./outputs/models/finetune_tokenizer_300033_mps"
echo ""
echo "按 Ctrl+C 可以随时停止训练"
echo "======================================================================"
echo ""

python finetune/train_tokenizer_mps.py

echo ""
echo "======================================================================"
echo "训练完成！"
echo "======================================================================"
