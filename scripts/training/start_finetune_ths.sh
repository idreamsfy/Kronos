#!/bin/bash
# 同花顺 (300033) 微调启动脚本

echo "======================================================================"
echo "🚀 开始同花顺 (300033) Kronos-base 微调"
echo "======================================================================"
echo ""

# 激活环境
source .venv/bin/activate

# 检查 MPS
echo "✅ 检查 MPS..."
python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
echo ""

# 清理旧日志
> outputs/logs/finetune_ths_300033.log

# 后台启动训练
echo "启动训练进程..."
nohup python -u finetune/finetune_ths_300033.py > outputs/logs/finetune_ths_300033.log 2>&1 &
PID=$!

echo "✅ 训练已启动 (PID: $PID)"
echo ""
echo "等待 15 秒检查启动状态..."
sleep 15

# 检查进程
if pgrep -f "finetune_ths_300033.py" > /dev/null; then
    echo "✅ 训练进程运行正常"
    echo ""
    echo "📊 最新输出:"
    tail -20 outputs/logs/finetune_ths_300033.log
else
    echo "❌ 训练启动失败"
    echo ""
    echo "错误日志:"
    cat outputs/logs/finetune_ths_300033.log
fi

echo ""
echo "======================================================================"
echo "监控命令: tail -f outputs/logs/finetune_ths_300033.log"
echo "停止命令: pkill -f finetune_ths_300033.py"
echo "======================================================================"
