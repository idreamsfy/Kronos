"""
Step 2: Prepare the Dataset (For Making Predictions)
Based on README section: Getting Started -> Making Forecasts -> Step 3

This script prepares your K-line data for prediction using Kronos.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("STEP 2: Preparing Dataset for Prediction")
print("=" * 60)

try:
    # Load the example data
    print("\n1. Loading K-line data...")
    data_path = Path("examples/data/XSHG_5min_600977.csv")
    
    if not data_path.exists():
        print(f"   ❌ Error: Data file not found at {data_path}")
        print("   Please ensure you have CSV data with K-line information.")
        sys.exit(1)
    
    df = pd.read_csv(data_path)
    print(f"   ✅ Loaded {len(df)} rows from {data_path.name}")
    
    # Convert timestamps to datetime
    print("\n2. Processing timestamps...")
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    print(f"   ✅ Timestamps converted to datetime format")
    print(f"      Range: {df['timestamps'].min()} to {df['timestamps'].max()}")
    
    # Define prediction parameters
    print("\n3. Setting prediction parameters...")
    lookback = 400  # Historical window size
    pred_len = 120  # Prediction length
    
    print(f"   - Lookback window: {lookback} time steps")
    print(f"   - Prediction length: {pred_len} time steps")
    
    # Prepare input data (X) and target timestamps (y)
    print("\n4. Preparing input features and timestamps...")
    
    # Select required columns
    required_columns = ['open', 'high', 'low', 'close', 'volume', 'amount']
    x_df = df.loc[:lookback-1, required_columns].copy()
    
    print(f"   ✅ Input data shape: {x_df.shape}")
    print(f"      Columns: {list(x_df.columns)}")
    
    # Prepare timestamps
    x_timestamp = df.loc[:lookback-1, 'timestamps'].copy()
    y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps'].copy()
    
    print(f"   ✅ Historical timestamps: {len(x_timestamp)} points")
    print(f"   ✅ Future timestamps: {len(y_timestamp)} points")
    
    # Display sample data
    print("\n5. Sample Data Preview:")
    print("\n   Historical Input (last 5 rows):")
    print(x_df.tail())
    
    print("\n   Target Timestamps (first 5):")
    print(y_timestamp.head())
    
    # Verify data quality
    print("\n6. Data Quality Check:")
    print(f"   - Missing values in x_df: {x_df.isnull().sum().sum()}")
    print(f"   - Missing values in timestamps: {x_timestamp.isnull().sum() + y_timestamp.isnull().sum()}")
    
    if x_df.isnull().sum().sum() > 0:
        print("   ⚠️  Warning: Missing values detected!")
        print("   Consider filling or removing missing data.")
    else:
        print("   ✅ No missing values detected")
    
    # Save prepared data (optional)
    print("\n7. Saving prepared data...")
    output_dir = Path("prepared_data")
    output_dir.mkdir(exist_ok=True)
    
    x_df.to_csv(output_dir / "input_data.csv", index=False)
    x_timestamp.to_csv(output_dir / "x_timestamps.csv", index=False)
    y_timestamp.to_csv(output_dir / "y_timestamps.csv", index=False)
    
    print(f"   ✅ Saved to {output_dir}/")
    print(f"      - input_data.csv")
    print(f"      - x_timestamps.csv")
    print(f"      - y_timestamps.csv")
    
    print("\n" + "=" * 60)
    print("✅ STEP 2 COMPLETE - Dataset Ready!")
    print("=" * 60)
    print("\n💡 Next step: Instantiate Predictor and Generate Forecasts")
    print("   See: test_step3_predict.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
