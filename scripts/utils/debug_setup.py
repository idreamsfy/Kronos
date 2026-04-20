# 🔍 Kronos Debug Environment Test Script
"""
This script helps you verify your Kronos environment is properly set up
and provides a simple debugging entry point.
"""

import sys
import os
from pathlib import Path


def check_environment():
    """Check if all required packages are installed"""
    print("=" * 60)
    print("🔍 Checking Kronos Environment")
    print("=" * 60)
    
    required_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'torch': 'torch',
        'einops': 'einops',
        'huggingface_hub': 'huggingface_hub',
        'matplotlib': 'matplotlib',
        'tqdm': 'tqdm',
        'safetensors': 'safetensors'
    }
    
    missing = []
    for package_name, import_name in required_packages.items():
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {package_name}: {version}")
        except ImportError:
            print(f"❌ {package_name}: NOT INSTALLED")
            missing.append(package_name)
    
    if missing:
        print("\n⚠️  Missing packages detected!")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required packages installed!")
    return True


def test_model_loading():
    """Test loading the Kronos model and tokenizer"""
    print("\n" + "=" * 60)
    print("🤖 Testing Model Loading")
    print("=" * 60)
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from model import Kronos, KronosTokenizer, KronosPredictor
        
        print("✅ Model imports successful")
        
        # Test loading from Hugging Face
        print("\n📥 Loading tokenizer from Hugging Face Hub...")
        tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
        print("✅ Tokenizer loaded successfully")
        
        print("\n📥 Loading model from Hugging Face Hub...")
        model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
        print("✅ Model loaded successfully")
        
        print(f"\n📊 Model Info:")
        print(f"   - Context length: {model.max_seq_len}")
        print(f"   - Device: {next(model.parameters()).device}")
        
        # Create predictor
        predictor = KronosPredictor(model, tokenizer, max_context=512)
        print("✅ Predictor initialized successfully")
        
        return True, model, tokenizer, predictor
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None, None, None


def test_prediction():
    """Test a simple prediction with debug output"""
    print("\n" + "=" * 60)
    print("📈 Testing Prediction (Debug Mode)")
    print("=" * 60)
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from model import Kronos, KronosTokenizer, KronosPredictor
        import pandas as pd
        
        # Load test data
        example_data_path = Path("examples/data/XSHG_5min_600977.csv")
        if not example_data_path.exists():
            print(f"⚠️  Example data not found at {example_data_path}")
            print("Skipping prediction test...")
            return True
        
        print(f"📂 Loading data from: {example_data_path}")
        df = pd.read_csv(example_data_path)
        df['timestamps'] = pd.to_datetime(df['timestamps'])
        print(f"✅ Data loaded: {len(df)} rows")
        
        # Setup parameters
        lookback = 100  # Smaller for faster testing
        pred_len = 20
        
        print(f"\n📊 Configuration:")
        print(f"   - Lookback: {lookback}")
        print(f"   - Prediction length: {pred_len}")
        
        x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
        x_timestamp = df.loc[:lookback-1, 'timestamps']
        y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']
        
        # Load model
        tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
        model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
        predictor = KronosPredictor(model, tokenizer, max_context=512)
        
        print("\n🔮 Generating prediction...")
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_len,
            T=1.0,
            top_p=0.9,
            sample_count=1,
            verbose=True
        )
        
        print("\n✅ Prediction successful!")
        print(f"\n📊 Forecast Results:")
        print(pred_df.head())
        print(f"\n📈 Prediction shape: {pred_df.shape}")
        print(f"   Columns: {list(pred_df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Prediction test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main debug function"""
    print("\n🚀 Kronos Debug Environment Setup\n")
    
    # Step 1: Check environment
    if not check_environment():
        print("\n⚠️  Please install missing dependencies first!")
        print("   Run: pip install -r requirements.txt")
        return
    
    # Step 2: Test model loading
    success, model, tokenizer, predictor = test_model_loading()
    if not success:
        print("\n⚠️  Model loading failed. Check your internet connection and credentials.")
        return
    
    # Step 3: Test prediction
    test_prediction()
    
    print("\n" + "=" * 60)
    print("✅ Debug environment setup complete!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Run examples/prediction_example.py for full demo")
    print("   2. Run examples/prediction_batch_example.py for batch prediction")
    print("   3. Check finetune/ directory for fine-tuning scripts")
    print("   4. Run webui/app.py for web interface")


if __name__ == "__main__":
    main()
