"""
Step 1: Load the Tokenizer and Model
Based on README section: Getting Started -> Making Forecasts -> Step 1
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("STEP 1: Loading Tokenizer and Model")
print("=" * 60)

try:
    # Import the model classes
    print("\n1. Importing model classes...")
    from model import Kronos, KronosTokenizer, KronosPredictor
    print("   ✅ Successfully imported:")
    print("      - Kronos")
    print("      - KronosTokenizer")
    print("      - KronosPredictor")
    
    # Load tokenizer from Hugging Face Hub
    print("\n2. Loading tokenizer from Hugging Face Hub...")
    print("   📥 Downloading: NeoQuasar/Kronos-Tokenizer-base")
    tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
    print("   ✅ Tokenizer loaded successfully!")
    
    # Load model from Hugging Face Hub
    print("\n3. Loading model from Hugging Face Hub...")
    print("   📥 Downloading: NeoQuasar/Kronos-small")
    model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
    print("   ✅ Model loaded successfully!")
    
    # Display model information
    print("\n4. Model Information:")
    print(f"   - Model type: {type(model).__name__}")
    print(f"   - Max sequence length: {model.max_seq_len}")
    print(f"   - Device: {next(model.parameters()).device}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   - Total parameters: {total_params:,}")
    
    # Create predictor instance
    print("\n5. Creating Predictor instance...")
    predictor = KronosPredictor(model, tokenizer, max_context=512)
    print("   ✅ Predictor initialized with max_context=512")
    
    print("\n" + "=" * 60)
    print("✅ STEP 1 COMPLETE - Model and Tokenizer Ready!")
    print("=" * 60)
    print("\n💡 Next step: Prepare your data (README Step 3)")
    print("   See: examples/prediction_example.py for usage")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check internet connection (required for Hugging Face)")
    print("2. If behind firewall, use mirror:")
    print("   $env:HF_ENDPOINT='https://hf-mirror.com'")
    print("3. Verify Hugging Face login if using private models")
    import traceback
    traceback.print_exc()
