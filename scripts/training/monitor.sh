#!/bin/bash
# 实时监控 Kronos 训练进度

echo "======================================================================"
echo "Kronos 训练进度监控"
echo "======================================================================"
echo ""

LOG_FILE="training_output.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 错误: 日志文件 $LOG_FILE 不存在"
    echo "请先启动训练: ./train_mps.sh"
    exit 1
fi

# 检查进程是否在运行
if ! pgrep -f "train_tokenizer_mps.py" > /dev/null; then
    echo "⚠️  警告: 训练进程未运行"
    echo ""
fi

# 显示最后 20 行
echo "📊 最新训练进度:"
echo "----------------------------------------------------------------------"
tail -20 "$LOG_FILE"
echo "----------------------------------------------------------------------"
echo ""

# 统计信息
TOTAL_LINES=$(wc -l < "$LOG_FILE")
EPOCH_COMPLETED=$(grep -c "Epoch \[.*\] 完成!" "$LOG_FILE" || echo 0)
BEST_MODEL_SAVED=$(grep -c "保存最佳模型" "$LOG_FILE" || echo 0)

echo "📈 统计信息:"
echo "  - 日志总行数: $TOTAL_LINES"
echo "  - 已完成 Epoch: $EPOCH_COMPLETED / 30"
echo "  - 最佳模型保存次数: $BEST_MODEL_SAVED"
echo ""

# 检查是否有输出文件
if [ -d "outputs/models/finetune_tokenizer_300033_mps" ]; then
    CHECKPOINTS=$(ls -d outputs/models/finetune_tokenizer_300033_mps/checkpoint_* 2>/dev/null | wc -l)
    BEST_MODEL=$(ls -d outputs/models/finetune_tokenizer_300033_mps/best_model 2>/dev/null | wc -l)
    
    echo "💾 模型文件:"
    echo "  - 检查点数量: $CHECKPOINTS"
    echo "  - 最佳模型: $([ $BEST_MODEL -gt 0 ] && echo '✅ 已保存' || echo '❌ 未保存')"
    echo ""
fi

echo "💡 提示:"
echo "  - 实时查看: tail -f $LOG_FILE"
echo "  - 停止训练: pkill -f train_tokenizer_mps.py"
echo "  - 再次监控: ./monitor_training.sh"
echo "======================================================================"
