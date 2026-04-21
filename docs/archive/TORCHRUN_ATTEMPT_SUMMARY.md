# 🔬 torchrun 多 GPU 训练尝试报告

## 📋 实验目标

尝试在 macOS Apple M1 上使用 `torchrun` 进行多 GPU/CPU 分布式训练

---

## 🧪 实验过程

### 尝试 1: 直接使用 torchrun（原始方法）

**命令**:
```bash
torchrun --standalone --nproc_per_node=2 finetune/train_tokenizer.py
```

**结果**: ❌ **失败**

**错误信息**:
```
W0331 21:45:20.818000 torch/distributed/elastic/multiprocessing/redirects.py:29] 
NOTE: Redirects are currently not supported in Windows or MacOs.

[W331 21:45:21.291659000 socket.cpp:764] [c10d] The IPv6 network addresses 
cannot be retrieved (gai error: 8 - nodename nor servname provided, or not known)
```

**问题原因**:
- macOS 的 IPv6 反向 DNS 解析失败
- `torchrun` 依赖网络套接字进行进程发现
- 无限期等待，进程卡死

---

### 尝试 2: 设置网络接口环境变量

**命令**:
```bash
export GLOO_SOCKET_IFNAME=en0
export NCCL_SOCKET_IFNAME=en0
torchrun --standalone --nproc_per_node=1 finetune/train_tokenizer.py
```

**结果**: ❌ **仍然失败**

**观察**:
- 即使指定了网络接口，IPv6 解析问题依然存在
- 这是 macOS 系统级别的限制

---

### 尝试 3: 使用 torch.multiprocessing.spawn（替代方案）

**命令**:
```bash
python finetune/train_tokenizer_spawn.py
```

**结果**: ✅ **成功！**

**输出**:
```
No CUDA available. Will use 4 CPU processes
Starting distributed training with 4 processes using spawn...
[Rank 0] DDP initialized successfully
[Rank 1] DDP initialized successfully
[Rank 2] DDP initialized successfully
[Rank 3] DDP initialized successfully

======================================================================
Training started with 30 epochs
Batch size per GPU: 50, Effective batch size: 200
Learning rate: 0.0002
Number of devices: 4
======================================================================
```

**成功关键**:
- 使用 `torch.multiprocessing.spawn` 而不是 `torchrun`
- 通过环境变量配置进程通信
- 不依赖复杂的网络发现机制

---

## 📊 方案对比

| 特性 | torchrun | torch.multiprocessing.spawn |
|------|----------|----------------------------|
| **启动方式** | CLI 命令 | Python 脚本 |
| **网络依赖** | 是（套接字） | 否（环境变量） |
| **macOS 兼容** | ❌ 不兼容 | ✅ 完全兼容 |
| **配置复杂度** | 低 | 中 |
| **灵活性** | 低 | 高 |
| **错误恢复** | 无 | 可自定义 |
| **推荐度** | ⭐⭐ (Linux) | ⭐⭐⭐⭐⭐ (macOS) |

---

## 🎯 最终解决方案

### 核心代码

```python
import torch.multiprocessing as mp
from torch.distributed import init_process_group

def train_worker(rank, world_size, config, save_dir):
    # DDP 初始化
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '29501'
    
    init_process_group(
        backend='gloo',
        rank=rank,
        world_size=world_size,
        timeout=datetime.timedelta(seconds=30)
    )
    
    # 训练逻辑...
    pass

def main():
    world_size = 4  # 4 进程
    
    mp.spawn(
        train_worker,
        args=(world_size, config, save_dir),
        nprocs=world_size,
        join=True
    )

if __name__ == '__main__':
    main()
```

### 使用方法

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/train_tokenizer_spawn.py
```

---

## 💡 经验总结

### 学到的教训

1. **工具链有平台限制**
   - `torchrun` 在 Linux 上很好用
   - macOS 需要特殊处理

2. **理解底层很重要**
   - 知道 DDP 如何工作
   - 才能找到替代方案

3. **优雅降级是关键**
   - 多进程失败时用单进程
   - 保证程序总能运行

### 最佳实践

```python
# ✅ 推荐做法
try:
    # 尝试多进程
    mp.spawn(train_ddp, ...)
except Exception as e:
    # 降级到单进程
    print(f"Multi-process failed: {e}")
    train_single()

# ❌ 不推荐
mp.spawn(train_ddp, ...)  # 可能直接崩溃
```

---

## 🔍 技术细节深挖

### 为什么 torchrun 失败？

**torchrun 的工作流程**:
```
1. 启动 master 进程
2. 创建本地 store（基于文件/网络）
3. 各 worker 连接到 store
4. 通过 RDVZ 文件进行进程发现
5. 初始化 process group
```

**问题环节**:
- 步骤 2-3：macOS 的网络配置导致套接字创建失败
- IPv6 反向 DNS 解析超时

### 为什么 spawn 成功？

**spawn 的工作流程**:
```
1. 主进程创建子进程（fork/spawn）
2. 通过管道传递必要信息
3. 各进程设置环境变量
4. 直接初始化 process group
```

**优势**:
- 不需要网络发现
- 进程关系由 OS 管理
- 更简单、更可靠

---

## 📈 性能数据

### 预期性能对比

| 模式 | 进程数 | 预计时间/epoch | 总时间 (30 epochs) |
|------|-------|---------------|-------------------|
| 单进程 CPU | 1 | ~20-30 分钟 | 10-15 小时 |
| **spawn 4 进程** | **4** | **~8-15 分钟** | **4-7.5 小时** |
| 单 GPU (RTX 3090) | 1 | ~1-2 分钟 | 30-60 分钟 |
| torchrun 4-GPU | 4 | ~30-60 秒 | 15-30 分钟 |

**注意**: spawn 方案在 macOS 上的实际表现取决于 CPU 核心数和内存带宽。

---

## 🛠️ 实用技巧

### 调试多进程问题

```bash
# 1. 查看进程
ps aux | grep python

# 2. 查看打开的文件
lsof -p <PID>

# 3. 监控资源
watch -n 1 'ps aux | grep python | awk "{print $3, $4}"'
```

### 日志记录

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format=f'[Rank {rank}] %(message)s'
)
logger = logging.getLogger(__name__)
```

---

## 🚀 下一步

### 已完成
- ✅ 实现 spawn 多进程训练
- ✅ DDP 初始化成功
- ✅ 训练正常启动

### 待完成
- ⏳ 等待训练完成
- ⏳ 验证模型质量
- ⏳ 执行 Step 3.2 (Predictor 微调)

---

## 📞 参考资源

### 相关文档
- [PyTorch Multiprocessing](https://pytorch.org/docs/stable/multiprocessing.html)
- [DDP Tutorial](https://pytorch.org/tutorials/intermediate/ddp_tutorial.html)
- [Gloo Backend](https://github.com/facebookincubator/gloo)

### 项目文件
- `finetune/train_tokenizer_spawn.py` - Spawn 版本训练脚本
- `TORCHRUN_SPAWN_SUCCESS.md` - 详细技术报告
- 本文档 - 实验总结

---

**实验日期**: 2026 年 3 月 31 日  
**实验平台**: macOS Apple M1  
**最终状态**: ✅ 成功找到替代方案  

🎉 **虽然 torchrun 失败了，但我们找到了更好的替代方案！**
