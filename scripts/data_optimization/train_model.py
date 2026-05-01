"""
使用优化后的数据进行模型训练
适配: AMD EPYC + RTX 5880 Ada + CUDA 12.8
"""
import subprocess
import sys
import os
import logging

# 配置日志
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def train_with_optimized_data(data_path='data/raw/futu/5min_300033_with_features.csv',
                              config_path='finetune_csv/configs/config_cuda_optimized.yaml'):
    """
    使用优化后的数据训练模型
    
    Args:
        data_path: 优化后的数据路径
        config_path: 训练配置文件路径
    """
    
    logger.info("=" * 80)
    logger.info("开始使用优化数据训练模型")
    logger.info("=" * 80)
    
    # 检查文件是否存在
    if not os.path.exists(data_path):
        logger.error(f"数据文件不存在: {data_path}")
        return False
    
    if not os.path.exists(config_path):
        logger.error(f"配置文件不存在: {config_path}")
        return False
    
    logger.info(f"数据文件: {data_path}")
    logger.info(f"配置文件: {config_path}")
    
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 构建训练命令
    train_script = 'finetune_csv/train_sequential.py'
    
    if not os.path.exists(train_script):
        logger.error(f"训练脚本不存在: {train_script}")
        return False
    
    command = [
        sys.executable,
        train_script,
        '--config', config_path
    ]
    
    logger.info(f"\n执行训练命令:")
    logger.info(f"{' '.join(command)}")
    logger.info("\n" + "=" * 80)
    
    try:
        # 执行训练
        result = subprocess.run(
            command,
            cwd=os.getcwd(),
            capture_output=False,
            check=True
        )
        
        logger.info("\n" + "=" * 80)
        logger.info("训练完成！")
        logger.info("=" * 80)
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"训练失败: {e}")
        return False
    except Exception as e:
        logger.error(f"训练异常: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    try:
        success = train_with_optimized_data()
        
        if success:
            logger.info("\n✅ 训练成功完成！")
            logger.info("请检查 outputs/models/ 目录查看训练结果")
        else:
            logger.error("\n❌ 训练失败，请检查日志")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)
        sys.exit(1)
