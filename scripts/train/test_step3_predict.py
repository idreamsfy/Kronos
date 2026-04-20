"""
Step 3: Instantiate Predictor and Generate Forecasts
Based on README section: Getting Started -> Making Forecasts -> Steps 4-5

This script demonstrates how to use the prepared data to generate predictions.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("STEP 3: Generating Predictions with Kronos")
print("=" * 60)

try:
    # Step 1: Load Model and Tokenizer
    print("\n[Step 1] Loading Tokenizer and Model from Hugging Face...")
    from model import Kronos, KronosTokenizer, KronosPredictor
    
    tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
    print("   ✅ Tokenizer loaded: NeoQuasar/Kronos-Tokenizer-base")
    
    model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
    print("   ✅ Model loaded: NeoQuasar/Kronos-small")
    
    # Step 2: Instantiate Predictor
    print("\n[Step 2] Creating Predictor instance...")
    predictor = KronosPredictor(model, tokenizer, max_context=512)
    print("   ✅ Predictor initialized with max_context=512")
    
    # Step 3: Load Prepared Data
    print("\n[Step 3] Loading prepared dataset...")
    prepared_dir = Path("prepared_data")
    
    x_df = pd.read_csv(prepared_dir / "input_data.csv")
    x_timestamp = pd.read_csv(prepared_dir / "x_timestamps.csv", parse_dates=['timestamps'])['timestamps']
    y_timestamp = pd.read_csv(prepared_dir / "y_timestamps.csv", parse_dates=['timestamps'])['timestamps']
    
    print(f"   ✅ Loaded input data: {x_df.shape}")
    print(f"   ✅ Loaded {len(x_timestamp)} historical timestamps")
    print(f"   ✅ Loaded {len(y_timestamp)} future timestamps")
    
    # Step 4: Generate Forecasts
    print("\n[Step 4] Generating forecasts...")
    print("   This may take 30-60 seconds depending on your hardware...")
    
    pred_df = predictor.predict(
        df=x_df,
        x_timestamp=x_timestamp,
        y_timestamp=y_timestamp,
        pred_len=120,
        T=1.0,          # Temperature for sampling
        top_p=0.9,      # Nucleus sampling probability
        sample_count=1, # Number of forecast paths
        verbose=True
    )
    
    print("   ✅ Prediction completed!")
    
    # Step 5: Display Results
    print("\n[Step 5] Forecast Results:")
    print("\n   Predicted Values (first 5 rows):")
    print(pred_df.head())
    
    print(f"\n   Prediction Statistics:")
    print(pred_df.describe())
    
    # Step 6: Save Results
    print("\n[Step 6] Saving prediction results...")
    output_dir = Path("prediction_results")
    output_dir.mkdir(exist_ok=True)
    
    result_path = output_dir / "predictions.csv"
    pred_df.to_csv(result_path, index=True)
    print(f"   ✅ Saved predictions to: {result_path}")
    
    # Step 7: Quick Analysis
    print("\n[Step 7] Quick Analysis:")
    print(f"   - Prediction shape: {pred_df.shape}")
    print(f"   - Columns: {list(pred_df.columns)}")
    print(f"   - Date range: {pred_df.index.min()} to {pred_df.index.max()}")
    
    if 'close' in pred_df.columns:
        first_close = pred_df['close'].iloc[0]
        last_close = pred_df['close'].iloc[-1]
        change_pct = ((last_close - first_close) / first_close) * 100
        print(f"   - First predicted close: ${first_close:.2f}")
        print(f"   - Last predicted close: ${last_close:.2f}")
        print(f"   - Predicted change: {change_pct:+.2f}%")
    
    print("\n" + "=" * 60)
    print("✅ STEP 3 COMPLETE - Predictions Generated!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. View results: prediction_results/predictions.csv")
    print("   2. Run full example: python examples/prediction_example.py")
    print("   3. Try batch prediction: python examples/prediction_batch_example.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
