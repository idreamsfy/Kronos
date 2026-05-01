"""检查系统配置"""
import torch
import psutil
import platform

print("=" * 80)
print("系统配置信息")
print("=" * 80)

# CPU和内存
print(f"\nCPU: {platform.processor()}")
print(f"CPU核心数: {psutil.cpu_count(logical=False)} 物理 / {psutil.cpu_count(logical=True)} 逻辑")
memory = psutil.virtual_memory()
print(f"内存: {memory.total / (1024**3):.2f} GB (可用: {memory.available / (1024**3):.2f} GB)")

# GPU
print(f"\nPyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA版本: {torch.version.cuda}")
    print(f"GPU数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(i)
        props = torch.cuda.get_device_properties(i)
        total_mem = props.total_memory / (1024**3)
        print(f"GPU {i}: {name}")
        print(f"  显存: {total_mem:.2f} GB")
        print(f"  计算能力: {props.major}.{props.minor}")
else:
    print("未检测到CUDA GPU，将使用CPU训练")

print("\n" + "=" * 80)
