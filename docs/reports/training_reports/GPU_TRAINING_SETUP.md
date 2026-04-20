# 🚀 GPU Training Setup Guide

## ⚠️ Current Issue: Python 3.14 Incompatibility

### Your System Configuration:
```
✅ GPU: NVIDIA GeForce RTX 2080 Ti (11GB VRAM)
✅ Driver: 560.94 (CUDA 12.6 capable)
❌ PyTorch: Only CPU version available for Python 3.14
❌ CUDA Support: Not available for Python 3.14
```

### The Problem:
PyTorch **does not yet release CUDA-enabled wheels** for Python 3.14 because it's too new.

---

## ✅ Solution Options

### Option 1: Install Python 3.10/3.11 (RECOMMENDED)

#### Step 1: Download Python 3.10 or 3.11
- Visit: https://www.python.org/downloads/
- Download Python 3.10.x or 3.11.x installer
- Install to: `C:\Python310\` or `C:\Python311\`

#### Step 2: Create Virtual Environment with Python 3.10/3.11
```powershell
# Using Python 3.10
C:\Python310\python.exe -m venv venv_gpu

# Activate environment
.\venv_gpu\Scripts\Activate.ps1
```

#### Step 3: Install Dependencies
```powershell
pip install --upgrade pip
pip install numpy pandas matplotlib tqdm einops huggingface_hub safetensors pyyaml

# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### Step 4: Verify GPU Support
```powershell
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

Expected output:
```
CUDA: True
GPU: NVIDIA GeForce RTX 2080 Ti
```

#### Step 5: Start GPU Training!
```powershell
# Single GPU training (your RTX 2080 Ti)
python train_sequential.py --config configs/config_step3_test.yaml

# Or use torchrun (even though single GPU, good for testing)
torchrun --standalone --nproc_per_node=1 train_sequential.py --config configs/config_step3_test.yaml
```

---

### Option 2: Continue CPU Training (Current Setup)

Your current training is progressing well and will complete successfully!

**Pros:**
- ✅ Already running
- ✅ No setup changes needed
- ✅ Will produce same quality models

**Cons:**
- ❌ Slower (~5-10x slower than GPU)
- ❌ Takes hours instead of minutes

**Current Status:** Tokenizer training ~40% complete

---

## 🎯 GPU Training Commands (After Python Downgrade)

### Single GPU (RTX 2080 Ti):

```powershell
# Simple single-GPU training
python train_sequential.py --config configs/config_step3_test.yaml

# With torchrun (recommended even for single GPU)
torchrun --standalone --nproc_per_node=1 train_sequential.py --config configs/config_step3_test.yaml
```

### Expected Performance on RTX 2080 Ti:

| Phase | CPU Time | GPU Time | Speedup |
|-------|----------|----------|---------|
| Tokenizer (5 epochs) | ~8 hours | ~45 minutes | 10x faster |
| Predictor (3 epochs) | ~5 hours | ~30 minutes | 10x faster |
| **Total** | **~13 hours** | **~1.25 hours** | **10x faster** |

---

## 🔧 Updated Config for GPU Training

Modify `configs/config_step3_test.yaml`:

```yaml
training:
  # Increase batch size for GPU (was 16 for CPU)
  batch_size: 32  # RTX 2080 Ti can handle this
  
  # More workers for faster data loading
  num_workers: 4  # Utilize multiple CPU cores
  
  # Keep learning rates same
  tokenizer_learning_rate: 0.0002
  predictor_learning_rate: 0.000001
  
  # Reduce epochs for faster testing (optional)
  tokenizer_epochs: 5
  basemodel_epochs: 3
```

---

## 📊 Complete GPU Training Script

Create `train_gpu.py`:

```python
"""
GPU-Accelerated Training Script
Optimized for single GPU (RTX 2080 Ti)
"""

import sys
from pathlib import Path
import torch

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("GPU Training Setup")
print("=" * 80)

# Check GPU
if not torch.cuda.is_available():
    print("❌ ERROR: CUDA not available!")
    print("Please install CUDA-enabled PyTorch:")
    print("  pip install torch --index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)

print(f"✅ GPU Detected: {torch.cuda.get_device_name(0)}")
print(f"   CUDA Version: {torch.version.cuda}")
print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

# Set device
device = torch.device('cuda:0')
print(f"\n🚀 Starting training on GPU...")
print("=" * 80)

# Import and run training
from train_sequential import main as train_main
train_main()
```

Then run:
```powershell
python train_gpu.py --config configs/config_step3_test.yaml
```

---

## 🎛️ Mixed Precision Training (Optional Speed Boost)

For even faster training on RTX 2080 Ti (Tensor Cores):

Add to config:
```yaml
training:
  # Enable automatic mixed precision
  use_amp: true
```

This can give **2-3x additional speedup** with no loss in accuracy!

---

## 📈 Monitoring GPU Training

### Check GPU Utilization:
```powershell
# Watch GPU usage in real-time
watch -n 1 nvidia-smi

# Or on Windows PowerShell
while ($true) { 
    Clear-Host
    nvidia-smi
    Start-Sleep -Seconds 2
}
```

### Expected GPU Usage:
```
GPU Utilization: 80-100%
Memory Usage: ~8-10 GB / 11 GB
Temperature: 60-75°C
Power: 180-220W
```

---

## ⚡ Quick Start Summary

### If You Have Python 3.10/3.11 Installed:

```powershell
# 1. Create and activate venv
python -m venv venv_gpu
.\venv_gpu\Scripts\Activate.ps1

# 2. Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Install other dependencies
pip install -r requirements.txt

# 4. Start GPU training
python train_sequential.py --config configs/config_step3_test.yaml
```

**Training will complete in ~1-2 hours instead of 13+ hours!**

---

## 🎯 Recommendation

### Best Approach:

**Option A: Wait for Current Training**
- Let CPU training finish (~5-7 more hours)
- Get your fine-tuned models
- Test and validate results
- Later set up Python 3.10 environment for production

**Option B: Setup Python 3.10 Now**
- Install Python 3.10 alongside 3.14
- Create GPU training environment
- Restart training (will finish in ~1.5 hours)
- Much faster for future experiments

---

## 📝 Key Takeaways

### Current Situation:
- ✅ You have a powerful GPU (RTX 2080 Ti)
- ❌ Python 3.14 doesn't support CUDA PyTorch yet
- ✅ CPU training working but slow

### For GPU Training:
1. Install Python 3.10 or 3.11
2. Create separate virtual environment
3. Install CUDA PyTorch
4. Run training (10x faster!)

### Worth the Setup?
- **Yes!** if you plan to do multiple training runs
- **No** if this is a one-time experiment (CPU is fine)

---

## 🔗 Resources

- PyTorch Compatibility: https://pytorch.org/get-started/locally/
- Python 3.10 Download: https://www.python.org/downloads/release/python-31011/
- Python 3.11 Download: https://www.python.org/downloads/release/python-3119/
- CUDA Installation Guide: https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/

---

**Your GPU is ready - just needs Python 3.10/3.11 to unlock 10x speed!** 🚀
