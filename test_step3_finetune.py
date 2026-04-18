"""
Step 3: Run the Fine-tuning
Based on README section: Finetuning -> Step 3: Model Finetuning

This script runs sequential fine-tuning (tokenizer + predictor) using CSV data.
"""

import sys
from pathlib import Path
import subprocess
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("STEP 3: Running Fine-tuning Process")
print("=" * 80)

try:
    # Change to finetune_csv directory
    finetune_dir = Path("finetune_csv")
    os.chdir(finetune_dir)
    
    print("\n[Step 3.1] Checking prerequisites...")
    print(f"   Working directory: {Path.cwd()}")
    
    # Check if config exists
    config_path = Path("configs/config_step3_test.yaml")
    if not config_path.exists():
        print(f"   ❌ Config file not found at {config_path}")
        sys.exit(1)
    print(f"   ✅ Config found: {config_path}")
    
    # Check if data exists
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    data_path = Path(config['data']['data_path'])
    if not data_path.exists():
        print(f"   ❌ Data file not found at {data_path}")
        sys.exit(1)
    print(f"   ✅ Data found: {data_path}")
    
    # Count lines in data file
    with open(data_path, 'r', encoding='utf-8') as f:
        line_count = sum(1 for line in f)
    print(f"   📊 Data size: {line_count:,} rows")
    
    print("\n[Step 3.2] Starting Sequential Fine-tuning...")
    print("   This will train both tokenizer and predictor models.")
    print("   ⏱️  Estimated time: 5-15 minutes depending on hardware\n")
    
    # Run sequential training
    cmd = [
        sys.executable,
        "train_sequential.py",
        "--config", "configs/config_step3_test.yaml"
    ]
    
    print(f"   🚀 Command: {' '.join(cmd)}")
    print(f"   📝 Log output will be displayed below:\n")
    print("-" * 80)
    
    # Run with live output
    process = subprocess.run(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        cwd=str(Path.cwd())
    )
    
    print("-" * 80)
    
    if process.returncode == 0:
        print("\n✅ Fine-tuning completed successfully!")
        
        # Check for saved models
        exp_name = config['model_paths']['exp_name']
        base_path = Path(config['model_paths']['base_path']) / exp_name
        
        tokenizer_path = base_path / "tokenizer" / "best_model"
        predictor_path = base_path / "basemodel" / "best_model"
        
        print(f"\n📂 Model checkpoints saved to:")
        if tokenizer_path.exists():
            print(f"   ✅ Tokenizer: {tokenizer_path}")
        else:
            print(f"   ⚠️  Tokenizer path created but no checkpoint yet")
            
        if predictor_path.exists():
            print(f"   ✅ Predictor: {predictor_path}")
        else:
            print(f"   ⚠️  Predictor path created but no checkpoint yet")
        
        print("\n" + "=" * 80)
        print("✅ STEP 3 COMPLETE - Models Fine-tuned!")
        print("=" * 80)
        print("\n💡 Next steps:")
        print("   1. Use fine-tuned models for prediction")
        print("   2. Run backtesting: python ../finetune/qlib_test.py")
        print("   3. Compare with original pre-trained models")
        
    else:
        print(f"\n❌ Fine-tuning failed with exit code {process.returncode}")
        print("   Check the error messages above for details.")
        sys.exit(process.returncode)
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    # Return to original directory
    os.chdir(project_root)
