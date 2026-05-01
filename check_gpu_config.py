import torch
import psutil
import platform

print("=" * 80)
print("系统配置信息")
print("=" * 80)

# 基本信息
print(f"\n操作系统: {platform.system()} {platform.release()}")
print(f"处理器: {platform.processor()}")
print(f"CPU核心: {psutil.cpu_count(logical=False)}物理 / {psutil.cpu_count(logical=True)}逻辑")

# 内存
mem = psutil.virtual_memory()
print(f"总内存: {mem.total/(1024**3):.2f} GB")
print(f"可用内存: {mem.available/(1024**3):.2f} GB")
print(f"内存使用率: {mem.percent}%")

# GPU/CUDA
print(f"\nPyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA版本: {torch.version.cuda}")
    print(f"GPU数量: {torch.cuda.device_count()}")
    
    for i in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(i)
        props = torch.cuda.get_device_properties(i)
        total_mem = props.total_memory / (1024**3)
        
        print(f"\nGPU {i}: {name}")
        print(f"  显存总量: {total_mem:.2f} GB")
        print(f"  计算能力: {props.major}.{props.minor}")
        print(f"  多处理器数量: {props.multi_processor_count}")
        
        # 当前使用情况
        allocated = torch.cuda.memory_allocated(i) / (1024**3)
        reserved = torch.cuda.memory_reserved(i) / (1024**3)
        print(f"  已分配显存: {allocated:.2f} GB")
        print(f"  已缓存显存: {reserved:.2f} GB")
else:
    print("\n❌ CUDA不可用")
    # 检查MPS
    if hasattr(torch.backends, 'mps'):
        print(f"MPS可用: {torch.backends.mps.is_available()}")

print("\n" + "=" * 80)
