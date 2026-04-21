#!/bin/bash
# 同花顺 (300033) Kronos-base 真正微调启动脚本

echo "======================================================================"
echo "🚀 开始同花顺 (300033) Kronos-base 真正微调"
echo "======================================================================"
echo ""

# 激活环境
source .venv/bin/activate

# 检查 MPS
echo "✅ 检查 MPS..."
python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
echo ""

# 清理旧日志
mkdir -p outputs/logs
> outputs/logs/finetune_ths_real.log

# 后台启动训练
echo "启动训练进程..."
nohup python -u finetune/finetune_ths_real.py > outputs/logs/finetune_ths_real.log 2>&1 &
PID=$!

echo "✅ 训练已启动 (PID: $PID)"
echo ""
echo "等待 20 秒检查启动状态..."
sleep 20

# 检查进程
if pgrep -f "finetune_ths_real.py" > /dev/null; then
    echo "✅ 训练进程运行正常"
    echo ""
    echo "📊 最新输出:"
    tail -30 outputs/logs/finetune_ths_real.log
else
    echo "❌ 训练启动失败"
    echo ""
    echo "错误日志:"
    cat outputs/logs/finetune_ths_real.log
fi

echo ""
echo "======================================================================"
echo "监控命令: tail -f outputs/logs/finetune_ths_real.log"
echo "停止命令: pkill -f finetune_ths_real.py"
echo "======================================================================"
