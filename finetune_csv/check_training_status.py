"""
Check training status and optionally restart if stuck
"""

import os
import sys
from pathlib import Path
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("Training Status Check")
print("=" * 80)

# Check log files
log_dir = Path("outputs/finetuned_models/test_finetune_run/logs")

# Check tokenizer log
tokenizer_log = log_dir / "tokenizer_training_rank_0.log"
if tokenizer_log.exists():
    with open(tokenizer_log, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"\n✅ Tokenizer Log: {len(lines)} lines")
        if lines:
            print(f"   Last update: {lines[-1].strip()[:100]}")
else:
    print("\n❌ Tokenizer log not found")

# Check basemodel log
basemodel_log = log_dir / "basemodel_training_rank_0.log"
if basemodel_log.exists():
    with open(basemodel_log, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"\n📊 Predictor Log: {len(lines)} lines")
        if lines:
            print(f"   Last line: {lines[-1].strip()}")
        
        # Check if stuck
        if len(lines) <= 10:
            print("\n⚠️  WARNING: Predictor training appears to be stuck!")
            print("   Possible causes:")
            print("   1. Downloading pretrained model from Hugging Face (slow network)")
            print("   2. Model loading issue")
            print("   3. Network timeout")
            
            # Check how long ago the log was created
            log_age = time.time() - basemodel_log.stat().st_mtime
            print(f"\n   Log file age: {log_age/60:.1f} minutes")
            
            if log_age > 30 * 60:  # More than 30 minutes
                print("\n❌ Training has been stuck for >30 minutes")
                print("\n💡 Recommendation: Restart training with local model or use mirror")
            else:
                print(f"\n⏳ Still waiting... ({log_age/60:.1f} minutes elapsed)")
        else:
            print("\n✅ Predictor training is progressing")
else:
    print("\n❌ Predictor log not found")

# Check model files
print("\n" + "=" * 80)
print("Model Files Status")
print("=" * 80)

tokenizer_model = Path("outputs/finetuned_models/test_finetune_run/tokenizer/best_model/model.safetensors")
if tokenizer_model.exists():
    size_mb = tokenizer_model.stat().st_size / (1024 * 1024)
    print(f"\n✅ Tokenizer model: {size_mb:.2f} MB")
else:
    print("\n❌ Tokenizer model not found")

basemodel_dir = Path("outputs/finetuned_models/test_finetune_run/basemodel")
if basemodel_dir.exists():
    files = list(basemodel_dir.rglob("*"))
    print(f"\n📁 Predictor directory: {len(files)} files")
    if files:
        for f in files[:5]:
            print(f"   - {f.relative_to(basemodel_dir)}")
else:
    print("\n❌ Predictor directory not found or empty")

# Check GPU
print("\n" + "=" * 80)
print("GPU Status")
print("=" * 80)

try:
    import torch
    if torch.cuda.is_available():
        print(f"\n✅ CUDA Available: Yes")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory Allocated: {torch.cuda.memory_allocated(0) / 1024**2:.0f} MB")
        print(f"   Memory Cached: {torch.cuda.memory_reserved(0) / 1024**2:.0f} MB")
    else:
        print("\n❌ CUDA Not Available")
except Exception as e:
    print(f"\n❌ Error checking GPU: {e}")

print("\n" + "=" * 80)
print("Recommendations")
print("=" * 80)

if basemodel_log.exists() and len(open(basemodel_log, 'r', encoding='utf-8').readlines()) <= 10:
    print("\n⚠️  Predictor training appears stuck. Options:")
    print("\n1. Wait longer (model download may be slow)")
    print("2. Set Hugging Face mirror:")
    print("   $env:HF_ENDPOINT='https://hf-mirror.com'")
    print("3. Restart training manually")
    print("4. Download model manually first")
else:
    print("\n✅ Training appears to be running normally")

print("\n" + "=" * 80)
