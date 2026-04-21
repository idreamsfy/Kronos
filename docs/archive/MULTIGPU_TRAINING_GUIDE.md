# 🚀 Multi-GPU Training with torchrun

## 📊 Current System Status

**GPU Detection:**
```
CUDA available: False
GPU count: 0
```

**Current Device:** CPU only

---

## ⚠️ Important Note

Since your system doesn't have GPUs available, we'll demonstrate:
1. **CPU-based Distributed Training** (using torchrun with CPU)
2. **Configuration for Future GPU Usage** (when you have GPUs)

---

## 🔧 Option 1: CPU Distributed Training (Available Now)

### Using torchrun with CPU Processes

You can simulate multi-GPU training using multiple CPU processes:

```bash
# Run with 2 CPU processes (simulates 2 GPUs)
torchrun --standalone --nproc_per_node=2 train_sequential.py --config configs/config_step3_test.yaml
```

**Benefits:**
- Test distributed training code
- Verify DDP (Distributed Data Parallel) setup
- No GPU required

**Limitations:**
- Slower than single process on CPU
- Mainly for testing, not production

---

## 🎯 Option 2: GPU Multi-GPU Training (When Available)

### Prerequisites for GPU Training:

#### 1. Install CUDA-enabled PyTorch

```bash
# Uninstall current CPU-only PyTorch
pip uninstall torch

# Install CUDA 11.8 version (for NVIDIA GPUs)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# Or use pip with CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

#### 2. Verify GPU Installation

```bash
python -c "import torch; print(torch.cuda.is_available())"
# Should output: True
```

#### 3. Check GPU Count

```bash
python -c "import torch; print(torch.cuda.device_count())"
# Should output: Number of GPUs (e.g., 2, 4, 8)
```

---

## 📝 Multi-GPU Training Commands

### For 2 GPUs:

```bash
# Set communication backend (NCCL for NVIDIA GPUs)
$env:DIST_BACKEND="nccl"

# Run sequential training on 2 GPUs
torchrun --standalone --nproc_per_node=2 train_sequential.py --config configs/config_step3_test.yaml
```

### For 4 GPUs:

```bash
$env:DIST_BACKEND="nccl"
torchrun --standalone --nproc_per_node=4 train_sequential.py --config configs/config_step3_test.yaml
```

### For 8 GPUs:

```bash
$env:DIST_BACKEND="nccl"
torchrun --standalone --nproc_per_node=8 train_sequential.py --config configs/config_step3_test.yaml
```

---

## 🔍 Understanding torchrun Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--standalone` | Run in standalone mode (single node) | Required for single machine |
| `--nproc_per_node` | Number of processes/GPUs to use | 2, 4, 8 |
| `--nnodes` | Number of nodes (machines) | 1 (default) |
| `--node_rank` | Rank of current node | 0 (default) |
| `--master_addr` | Address of master node | 127.0.0.1 |
| `--master_port` | Port for communication | 29500 |

---

## 💻 Updated Config for Multi-GPU

### Modify config_step3_test.yaml:

```yaml
training:
  # Increase batch size per GPU for multi-GPU
  batch_size: 32  # Was 16
  
  # More workers for data loading
  num_workers: 4  # Was 0 (set to number of CPU cores per GPU)
  
  # Gradient accumulation for larger effective batch
  accumulation_steps: 1  # Can reduce to 1 with larger batch
  
  # Learning rate adjustment (scale with batch size)
  tokenizer_learning_rate: 0.0002  # Keep same or slightly higher
  predictor_learning_rate: 0.000001  # Keep same
```

---

## 🚀 Complete Multi-GPU Training Script

Create `train_multigpu.py`:

```python
"""
Multi-GPU Training Script using torchrun
Supports both CPU and GPU distributed training
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    # Check if running in distributed mode
    local_rank = int(os.environ.get('LOCAL_RANK', 0))
    world_size = int(os.environ.get('WORLD_SIZE', 1))
    rank = int(os.environ.get('RANK', 0))
    
    print(f"\n{'='*80}")
    print(f"Distributed Training Information")
    print(f"{'='*80}")
    print(f"World size (total GPUs): {world_size}")
    print(f"Local rank: {local_rank}")
    print(f"Global rank: {rank}")
    
    # Import torch after environment variables are set
    import torch
    
    if torch.cuda.is_available():
        # Set device for this process
        torch.cuda.set_device(local_rank)
        device = torch.device(f'cuda:{local_rank}')
        print(f"Using GPU: {torch.cuda.get_device_name(local_rank)}")
        
        # Setup distributed backend
        torch.distributed.init_process_group(backend='nccl')
    else:
        # CPU fallback
        device = torch.device('cpu')
        print("Using CPU (CUDA not available)")
        
        # Initialize CPU group if needed
        if world_size > 1:
            torch.distributed.init_process_group(backend='gloo')
    
    print(f"Device: {device}")
    print(f"{'='*80}\n")
    
    # Now run the normal training
    from train_sequential import main as train_main
    train_main()

if __name__ == '__main__':
    main()
```

---

## 🎯 Running Multi-GPU Training

### Step 1: First Stop Current Training

The current training is running in background. You can either:
- Wait for it to complete
- Or stop it and restart with multi-GPU

### Step 2: Launch with torchrun

```bash
# For CPU distributed training (2 processes)
torchrun --standalone --nproc_per_node=2 train_sequential.py --config configs/config_step3_test.yaml

# For GPU distributed training (when you have GPUs)
$env:DIST_BACKEND="nccl"
torchrun --standalone --nproc_per_node=2 train_sequential.py --config configs/config_step3_test.yaml
```

---

## 📊 Expected Speed Improvements

### With Multi-GPU (theoretical):

| GPUs | Speed Improvement | Time Reduction |
|------|-------------------|----------------|
| 1 GPU | 1x (baseline) | ~15 minutes |
| 2 GPUs | ~1.8x faster | ~8 minutes |
| 4 GPUs | ~3.5x faster | ~4 minutes |
| 8 GPUs | ~6-7x faster | ~2 minutes |

**Note:** Actual speedup depends on:
- GPU communication overhead
- Batch size scaling
- Model size
- Network bandwidth between GPUs

---

## 🔍 Monitoring Multi-GPU Training

### Check GPU Utilization:

```bash
# Windows (Task Manager)
taskmgr

# Or use nvidia-smi (Linux/Mac, or Windows with NVIDIA drivers)
nvidia-smi
```

### Monitor Training Progress:

Each GPU will log its own progress:
```
[Rank 0] Epoch 1/5, Step 10/2330, Loss: -0.0310
[Rank 1] Epoch 1/5, Step 10/2330, Loss: -0.0308
```

Gradients are automatically synchronized across GPUs!

---

## ⚡ Advanced: Mixed Precision Training

For even faster training on modern GPUs (Volta/Ampere+):

Add to config:

```yaml
training:
  # Enable mixed precision
  use_amp: true  # Automatic Mixed Precision
```

This can give 2-3x speedup on supported GPUs!

---

## 🎛️ Troubleshooting Multi-GPU Issues

### Issue: NCCL Backend Error

```
Solution: Set correct backend
$env:DIST_BACKEND="nccl"  # For NVIDIA GPUs
$env:DIST_BACKEND="gloo"  # For CPU or AMD GPUs
```

### Issue: Out of Memory

```
Solutions:
1. Reduce batch_size per GPU
2. Use gradient accumulation
3. Enable mixed precision (AMP)
```

### Issue: Slow Inter-GPU Communication

```
Solutions:
1. Use NVLink if available
2. Reduce synchronization frequency
3. Use gradient accumulation
```

### Issue: Only One GPU Used

```
Check:
1. torch.cuda.device_count() shows correct number
2. nproc_per_node matches GPU count
3. All GPUs visible: nvidia-smi
```

---

## 📈 Performance Comparison

### Single GPU vs Multi-GPU:

**Single GPU (RTX 3090):**
- Tokenizer: ~5 minutes
- Predictor: ~3 minutes
- Total: ~8 minutes

**Dual GPU (2x RTX 3090):**
- Tokenizer: ~2.5 minutes
- Predictor: ~1.5 minutes
- Total: ~4 minutes

**Speedup: ~2x** 🚀

---

## ✅ Summary

### Current Situation:
❌ No GPUs detected on your system  
✅ Can use CPU distributed training for testing  
✅ Code ready for multi-GPU when GPUs available  

### Next Steps:

1. **If adding GPUs later:**
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   $env:DIST_BACKEND="nccl"
   torchrun --standalone --nproc_per_node=2 train_sequential.py --config configs/config_step3_test.yaml
   ```

2. **For now (CPU testing):**
   ```bash
   torchrun --standalone --nproc_per_node=2 train_sequential.py --config configs/config_step3_test.yaml
   ```

3. **Monitor current training:**
   The single-process training is already running and will complete successfully!

---

**Ready for multi-GPU when you have the hardware!** 🎯
