#!/bin/bash
# 监控 Kronos 微调进度

echo "======================================================================"
echo "📊 Kronos-base 微调监控"
echo "======================================================================"
echo ""

LOG_FILE="outputs/logs/finetune_ths_optimized.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 日志文件不存在: $LOG_FILE"
    exit 1
fi

echo "实时输出 (Ctrl+C 退出):"
echo "----------------------------------------------------------------------"
tail -f "$LOG_FILE" | grep --line-buffered -E "(Epoch|Loss|保存|完成)"
