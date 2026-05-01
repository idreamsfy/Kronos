#!/bin/bash
# 明天继续训练的便捷脚本

echo "======================================================================"
echo "🚀 Kronos 训练 - 明日继续"
echo "======================================================================"
echo ""

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 错误: 虚拟环境不存在"
    exit 1
fi

# 激活环境
echo "✅ 激活虚拟环境..."
source .venv/bin/activate

# 检查 MPS
echo "✅ 检查 MPS 可用性..."
python -c "import torch; print(f'   MPS可用: {torch.backends.mps.is_available()}')"
echo ""

# 检查模型目录
if [ -d "outputs/models/finetune_tokenizer_300033_mps/best_model" ]; then
    echo "⚠️  检测到已存在的模型:"
    ls -lh outputs/models/finetune_tokenizer_300033_mps/best_model/ | grep -E "model.safetensors|config.json"
    echo ""
    read -p "是否覆盖现有模型？(y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消训练"
        exit 0
    fi
fi

# 开始训练
echo "======================================================================"
echo "开始训练..."
echo "配置文件: finetune/config_300033_mps.yaml"
echo "输出目录: outputs/models/finetune_tokenizer_300033_mps/"
echo ""
echo "💡 提示:"
echo "  - 实时监控: ./monitor_training.sh"
echo "  - 停止训练: pkill -f train_tokenizer_mps.py"
echo "  - 查看日志: tail -f training_output.log"
echo "======================================================================"
echo ""

# 后台运行
nohup python -u finetune/train_tokenizer_mps.py > training_output.log 2>&1 &
TRAIN_PID=$!

echo "✅ 训练已在后台启动 (PID: $TRAIN_PID)"
echo ""
echo "等待 5 秒检查启动状态..."
sleep 5

if pgrep -f "train_tokenizer_mps.py" > /dev/null; then
    echo "✅ 训练进程运行正常"
    echo ""
    echo "📊 初始输出:"
    head -20 training_output.log
else
    echo "❌ 训练启动失败，请检查日志:"
    cat training_output.log
fi

echo ""
echo "======================================================================"
echo "祝训练顺利！"
echo "======================================================================"
