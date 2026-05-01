"""
方案一完整执行脚本 - 一键执行所有数据优化步骤
"""
import subprocess
import sys
import os

def run_script(script_name, description):
    """运行单个脚本"""
    print(f"\n{'='*80}")
    print(f"执行: {description}")
    print(f"脚本: {script_name}")
    print(f"{'='*80}\n")
    
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ {description} 失败!")
        return False
    
    print(f"\n✅ {description} 完成!")
    return True

def main():
    """主函数"""
    print("="*80)
    print("方案一：数据层面优化 - 完整执行流程")
    print("="*80)
    print("\n本脚本将依次执行以下步骤:")
    print("1. 数据合并 - 合并历史数据和新数据")
    print("2. 数据验证 - 验证数据质量和完整性")
    print("3. 数据平衡 - 平衡涨跌样本比例")
    print("4. 数据增强 - 添加噪声增强样本多样性")
    print("5. 特征工程 - 添加技术指标和时间特征")
    print("6. 模型训练 - 使用优化数据训练模型")
    print("\n系统配置: AMD EPYC 9T24 + 64GB + RTX 5880 Ada + CUDA 12.8")
    print("预计总耗时: 20-40分钟")
    print("\n" + "="*80)
    
    # 确认开始
    response = input("\n是否开始执行? (yes/no): ")
    if response.lower() != 'yes':
        print("已取消执行")
        return
    
    steps = [
        ("scripts/data_optimization/merge_data.py", "步骤1: 数据合并"),
        ("scripts/data_optimization/validate_data.py", "步骤2: 数据验证"),
        ("scripts/data_optimization/balance_data.py", "步骤3: 数据平衡"),
        ("scripts/data_optimization/augment_data.py", "步骤4: 数据增强"),
        ("scripts/data_optimization/feature_engineering.py", "步骤5: 特征工程"),
        ("scripts/data_optimization/train_model.py", "步骤6: 模型训练"),
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for script, description in steps:
        if os.path.exists(script):
            if run_script(script, description):
                success_count += 1
            else:
                print(f"\n⚠️  {description} 失败，是否继续? (yes/no): ")
                response = input()
                if response.lower() != 'yes':
                    break
        else:
            print(f"\n⚠️  脚本不存在: {script}，跳过")
    
    # 总结
    print("\n" + "="*80)
    print("执行完成总结")
    print("="*80)
    print(f"成功: {success_count}/{total_steps} 个步骤")
    
    if success_count == total_steps:
        print("\n🎉 所有步骤成功完成！")
        print("\n生成的文件:")
        print("  - data/raw/futu/5min_300033_updated.csv (合并后)")
        print("  - data/validation_report.txt (验证报告)")
        print("  - data/raw/futu/5min_300033_balanced.csv (平衡后)")
        print("  - data/raw/futu/5min_300033_augmented.csv (增强后)")
        print("  - data/raw/futu/5min_300033_with_features.csv (最终特征增强, 30+特征)")
        print("  - outputs/models/ (训练好的模型)")
        print("\n日志文件:")
        print("  - logs/data_merge.log")
        print("  - logs/data_validation.log")
        print("  - logs/data_balance.log")
        print("  - logs/data_augmentation.log")
        print("  - logs/feature_engineering.log")
        print("  - logs/training.log")
        print("\n下一步:")
        print("  检查 outputs/models/ 目录查看训练结果和预测性能！")
    else:
        print(f"\n⚠️  部分步骤未完成，请检查日志")
    
    print("="*80)

if __name__ == "__main__":
    main()
