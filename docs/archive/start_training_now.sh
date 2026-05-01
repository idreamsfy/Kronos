#!/bin/bash
# 立即开始训练

echo "======================================================================"
echo "🚀 开始 Kronos MPS GPU 训练"
echo "======================================================================"
echo ""

# 激活环境
source .venv/bin/activate

# 检查 MPS
echo "✅ 检查 MPS..."
python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
echo ""

# 清理旧日志
> outputs/logs/training_output.log

# 后台启动训练
echo "启动训练进程..."
nohup python -u finetune/train_tokenizer_mps.py > outputs/logs/training_output.log 2>&1 &
PID=$!

echo "✅ 训练已启动 (PID: $PID)"
echo ""
echo "等待 15 秒检查启动状态..."
sleep 15

# 检查进程
if pgrep -f "train_tokenizer_mps.py" > /dev/null; then
    echo "✅ 训练进程运行正常"
    echo ""
    echo "📊 最新输出:"
    tail -20 outputs/logs/training_output.log
else
    echo "❌ 训练启动失败"
    echo ""
    echo "错误日志:"
    cat outputs/logs/training_output.log
fi

echo ""
echo "======================================================================"
echo "监控命令: tail -f outputs/logs/training_output.log"
echo "停止命令: pkill -f train_tokenizer_mps.py"
echo "======================================================================"
