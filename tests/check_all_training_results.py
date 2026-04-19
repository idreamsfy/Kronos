# coding=utf-8
"""
检查所有已训练模型的状态和结果
显示训练摘要、模型质量和性能指标
"""
import os
import glob
import json
from pathlib import Path


def check_training_results():
    """检查所有训练结果"""
    print("=" * 80)
    print("Kronos 银行股票训练结果检查")
    print("=" * 80)
    
    # 查找所有训练目录
    models_dir = Path("outputs/finetuned_models")
    
    if not models_dir.exists():
        print("❌ 错误: 未找到训练模型目录")
        return
    
    train_dirs = [d for d in models_dir.iterdir() if d.is_dir()]
    
    if not train_dirs:
        print("⚠️  暂无训练完成的模型")
        return
    
    print(f"\n找到 {len(train_dirs)} 个训练项目\n")
    
    results = []
    
    for train_dir in sorted(train_dirs):
        experiment_name = train_dir.name
        print(f"📊 检查: {experiment_name}")
        print("-" * 80)
        
        result = {
            'name': experiment_name,
            'tokenizer_loss': None,
            'predictor_loss': None,
            'tokenizer_time': None,
            'predictor_time': None,
            'status': 'Unknown'
        }
        
        # 检查Tokenizer
        tokenizer_log = train_dir / "logs" / "tokenizer_training_rank_0.log"
        if tokenizer_log.exists():
            with open(tokenizer_log, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 提取最佳Loss
                if "Best validation loss:" in content:
                    for line in content.split('\n'):
                        if "Best validation loss:" in line:
                            try:
                                loss = float(line.split(":")[-1].strip())
                                result['tokenizer_loss'] = loss
                            except:
                                pass
                
                # 提取训练时间
                if "Training time:" in content:
                    for line in content.split('\n'):
                        if "Training time:" in line and "minutes" in line:
                            try:
                                time_str = line.split(":")[-1].strip()
                                result['tokenizer_time'] = time_str
                            except:
                                pass
        
        # 检查Predictor
        basemodel_log = train_dir / "logs" / "basemodel_training_rank_0.log"
        if basemodel_log.exists():
            with open(basemodel_log, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 提取最佳Loss
                if "Best validation loss:" in content:
                    for line in content.split('\n'):
                        if "Best validation loss:" in content.split('\n')[content.split('\n').index(line)]:
                            try:
                                loss = float(line.split(":")[-1].strip())
                                result['predictor_loss'] = loss
                            except:
                                pass
                
                # 提取训练时间
                if "Training time:" in content:
                    for line in content.split('\n'):
                        if "Training time:" in line and "minutes" in line:
                            try:
                                time_str = line.split(":")[-1].strip()
                                result['predictor_time'] = time_str
                            except:
                                pass
        
        # 检查模型文件
        tokenizer_model = train_dir / "tokenizer" / "best_model" / "model.safetensors"
        predictor_model = train_dir / "basemodel" / "best_model" / "model.safetensors"
        
        tokenizer_exists = tokenizer_model.exists()
        predictor_exists = predictor_model.exists()
        
        if tokenizer_exists and predictor_exists:
            result['status'] = '✅ Complete'
            tokenizer_size = tokenizer_model.stat().st_size / (1024 * 1024)  # MB
            predictor_size = predictor_model.stat().st_size / (1024 * 1024)  # MB
            result['tokenizer_size'] = tokenizer_size
            result['predictor_size'] = predictor_size
        elif tokenizer_exists:
            result['status'] = '⚠️  Tokenizer Only'
        elif predictor_exists:
            result['status'] = '⚠️  Predictor Only'
        else:
            result['status'] = '❌ Incomplete'
        
        results.append(result)
        
        # 打印结果
        print(f"  状态: {result['status']}")
        
        if result['tokenizer_loss']:
            print(f"  Tokenizer:")
            print(f"    - Best Loss: {result['tokenizer_loss']:.4f}")
            if result['tokenizer_time']:
                print(f"    - Training Time: {result['tokenizer_time']}")
            if 'tokenizer_size' in result:
                print(f"    - Model Size: {result['tokenizer_size']:.1f} MB")
        
        if result['predictor_loss']:
            print(f"  Predictor:")
            print(f"    - Best Loss: {result['predictor_loss']:.4f}")
            if result['predictor_time']:
                print(f"    - Training Time: {result['predictor_time']}")
            if 'predictor_size' in result:
                print(f"    - Model Size: {result['predictor_size']:.1f} MB")
        
        print()
    
    # 打印总结
    print("=" * 80)
    print("训练总结")
    print("=" * 80)
    
    complete_count = sum(1 for r in results if r['status'] == '✅ Complete')
    incomplete_count = len(results) - complete_count
    
    print(f"\n总训练项目: {len(results)}")
    print(f"已完成: {complete_count} ✅")
    print(f"未完成: {incomplete_count} ⚠️")
    
    if complete_count > 0:
        print(f"\n完成率: {complete_count/len(results)*100:.1f}%")
        
        # 计算平均Loss
        tokenizer_losses = [r['tokenizer_loss'] for r in results if r['tokenizer_loss']]
        predictor_losses = [r['predictor_loss'] for r in results if r['predictor_loss']]
        
        if tokenizer_losses:
            avg_tokenizer_loss = sum(tokenizer_losses) / len(tokenizer_losses)
            print(f"\n平均 Tokenizer Loss: {avg_tokenizer_loss:.4f}")
        
        if predictor_losses:
            avg_predictor_loss = sum(predictor_losses) / len(predictor_losses)
            print(f"平均 Predictor Loss: {avg_predictor_loss:.4f}")
    
    print("\n" + "=" * 80)
    
    # 质量评级
    print("\n模型质量评级:")
    print("-" * 80)
    
    for result in results:
        if result['status'] != '✅ Complete':
            continue
        
        name = result['name']
        t_loss = result.get('tokenizer_loss', 999)
        p_loss = result.get('predictor_loss', 999)
        
        # 简单评级逻辑
        if t_loss < 0.02 and p_loss < 4.5:
            rating = "⭐⭐⭐⭐⭐ 优秀"
        elif t_loss < 0.03 and p_loss < 5.5:
            rating = "⭐⭐⭐⭐ 良好"
        elif t_loss < 0.05 and p_loss < 6.5:
            rating = "⭐⭐⭐ 中等"
        else:
            rating = "⭐⭐ 需改进"
        
        print(f"{name:<40} {rating}")
    
    print("=" * 80)


if __name__ == '__main__':
    check_training_results()
