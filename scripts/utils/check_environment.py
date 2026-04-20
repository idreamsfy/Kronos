"""
Verification script for Python environment setup
Tests that all components are working correctly
"""

import sys
import subprocess

print("=" * 80)
print("Python Environment Verification")
print("=" * 80)

# Check Python version
print(f"\n1. Python Version:")
print(f"   Version: {sys.version}")
print(f"   Executable: {sys.executable}")

if sys.version_info.major == 3 and sys.version_info.minor == 11:
    print("   ✅ Correct: Python 3.11.x")
else:
    print(f"   ⚠️  Warning: Expected Python 3.11.x, got {sys.version_info.major}.{sys.version_info.minor}")

# Check if in virtual environment
print(f"\n2. Virtual Environment:")
if '.venv' in sys.prefix:
    print(f"   ✅ Active: .venv environment")
    print(f"   Path: {sys.prefix}")
else:
    print(f"   ⚠️  Warning: Not in .venv environment")
    print(f"   Current prefix: {sys.prefix}")

# Check critical packages
print(f"\n3. Package Verification:")

packages_to_check = [
    'torch',
    'numpy',
    'pandas',
    'matplotlib',
    'huggingface_hub',
    'einops',
    'yaml',
]

for package_name in packages_to_check:
    try:
        module = __import__(package_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"   ✅ {package_name}: {version}")
    except ImportError as e:
        print(f"   ❌ {package_name}: NOT INSTALLED ({e})")

# Check CUDA/GPU
print(f"\n4. GPU/CUDA Verification:")

try:
    import torch
    
    cuda_available = torch.cuda.is_available()
    print(f"   CUDA Available: {cuda_available}")
    
    if cuda_available:
        print(f"   ✅ GPU Support: ENABLED")
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   GPU Count: {torch.cuda.device_count()}")
        print(f"   GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        
        # Test tensor on GPU
        x = torch.randn(3, 3).cuda()
        print(f"   ✅ GPU Tensor Test: SUCCESS")
        print(f"      Device: {x.device}")
        
    else:
        print(f"   ❌ GPU Support: NOT AVAILABLE")
        print(f"   ℹ️  Training will use CPU (slower)")
        
except Exception as e:
    print(f"   ❌ Error checking GPU: {e}")

# Check Kronos model imports
print(f"\n5. Kronos Model Verification:")

try:
    from model import Kronos, KronosTokenizer, KronosPredictor
    print(f"   ✅ Model imports: SUCCESS")
    print(f"      - Kronos")
    print(f"      - KronosTokenizer")
    print(f"      - KronosPredictor")
except Exception as e:
    print(f"   ⚠️  Model imports: FAILED ({e})")
    print(f"   ℹ️  This is OK if you haven't installed project dependencies yet")

# Summary
print(f"\n{'='*80}")
print("VERIFICATION SUMMARY")
print(f"{'='*80}")

checks_passed = 0
total_checks = 5

if sys.version_info.major == 3 and sys.version_info.minor == 11:
    checks_passed += 1

if '.venv' in sys.prefix:
    checks_passed += 1

try:
    import torch
    if torch.cuda.is_available():
        checks_passed += 1
except:
    pass

try:
    import numpy, pandas, matplotlib
    checks_passed += 1
except:
    pass

try:
    from model import Kronos, KronosTokenizer
    checks_passed += 1
except:
    pass

print(f"Checks Passed: {checks_passed}/5")

if checks_passed == 5:
    print("\n✅ ALL CHECKS PASSED!")
    print("🎉 Your environment is fully configured and ready for GPU training!")
elif checks_passed >= 3:
    print("\n✅ MOST CHECKS PASSED!")
    print("ℹ️  Your environment is functional. Some features may need attention.")
else:
    print("\n⚠️  SEVERAL CHECKS FAILED!")
    print("ℹ️  Please review the errors above and install missing components.")

print(f"\n{'='*80}")
print("Next Steps:")
print(f"{'='*80}")

if torch.cuda.is_available():
    print("1. Start GPU training:")
    print("   python train_sequential.py --config configs/config_step3_test.yaml")
    print()
    print("2. Monitor GPU usage during training:")
    print("   while ($true) { Clear-Host; nvidia-smi; Start-Sleep 2 }")
else:
    print("1. GPU not detected - training will use CPU")
    print("2. For faster training, consider installing CUDA-enabled PyTorch")

print(f"\n{'='*80}\n")
