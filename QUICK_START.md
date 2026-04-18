# 🚀 Kronos Quick Start Guide

## ✅ Step 1: Environment Setup - COMPLETE

Your Kronos debug environment is fully configured and ready to use!

### What's Been Set Up:

✅ **All Dependencies Installed**
- numpy, pandas, torch, einops, huggingface_hub, matplotlib, tqdm, safetensors

✅ **Debug Configuration Created**
- VS Code launch configurations (`.vscode/launch.json`)
- Editor settings (`.vscode/settings.json`)
- Environment test script (`debug_setup.py`)

✅ **Documentation Ready**
- Main README with usage examples
- Debug setup guide (Chinese)
- This quick start guide

---

## 🎯 How to Get Started

### Option 1: Verify Your Setup (Recommended First Time)

Open VS Code terminal and run:

```powershell
python debug_setup.py
```

This will:
- ✅ Check all Python packages are installed
- 📥 Attempt to download models from Hugging Face (requires internet)
- 🔮 Test the prediction pipeline with sample data
- 📊 Report any issues

**Note:** If you see network errors when downloading models, this is normal if you're behind a firewall. The models will download successfully once you have a stable connection to Hugging Face Hub.

---

### Option 2: Run Your First Prediction

The fastest way to see Kronos in action:

```powershell
python examples/prediction_example.py
```

This script will:
1. Load the Kronos-small model from Hugging Face
2. Read sample K-line data from `examples/data/`
3. Generate a 120-step forecast
4. Display a visualization comparing predictions vs actual values

**Expected Runtime:** ~30-60 seconds (depends on internet speed for model download)

---

### Option 3: Use VS Code Debugger

For interactive debugging:

1. **Open VS Code** → Press `F5`
2. **Select configuration:** Choose "🐛 Debug Setup Script"
3. **Click Run** (green play button)
4. **Set breakpoints** by clicking left margin of any file
5. **Inspect variables** as code executes

**Available Debug Configurations:**
- 🐛 Debug Setup Script - Test environment
- 📈 Run Prediction Example - Basic forecasting
- 📊 Run Batch Prediction - Multiple time series
- 🌐 WebUI App - Interactive web interface
- 🔧 Finetune Tokenizer - Custom training
- 🎯 Finetune Predictor - Model fine-tuning
- 🧪 Run Tests - Regression tests

---

## 📋 Quick Reference

### Basic Prediction Code

```python
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd

# 1. Load model
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, max_context=512)

# 2. Prepare your data
df = pd.read_csv("your_data.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

lookback = 400  # historical window
pred_len = 120  # forecast length

x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume']]
x_timestamp = df.loc[:lookback-1, 'timestamps']
y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']

# 3. Generate forecast
pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=pred_len,
    T=1.0,        # temperature
    top_p=0.9,    # nucleus sampling
    sample_count=1
)

print(pred_df.head())
```

---

## 🛠️ Troubleshooting

### Network Issues (Most Common)

**Problem:** Can't connect to Hugging Face

**Quick Fix:**
```powershell
# Use mirror site
$env:HF_ENDPOINT="https://hf-mirror.com"
python examples/prediction_example.py
```

**Alternative:** Download models manually and cache locally

---

### GPU/CUDA Issues

**Check if GPU is available:**
```python
import torch
print(f"CUDA: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
```

**If no GPU detected:**
- CPU mode works fine for testing (just slower)
- To enable GPU: Install CUDA-enabled PyTorch
  ```bash
  pip uninstall torch
  pip install torch --index-url https://download.pytorch.org/whl/cu118
  ```

---

### Memory Issues

**Reduce memory usage:**
```python
# Use smaller parameters
lookback = 200      # instead of 400
pred_len = 50       # instead of 120
sample_count = 1    # keep at 1 for testing

# Or use smaller model
model = Kronos.from_pretrained("NeoQuasar/Kronos-mini")
```

---

## 📚 Next Steps

Once your setup is verified:

1. **Explore Examples**
   ```powershell
   python examples/prediction_batch_example.py
   python examples/prediction_cn_markets_day.py
   ```

2. **Try Fine-tuning**
   - See `finetune/README.md` for detailed guide
   - Install Qlib: `pip install pyqlib`
   - Configure paths in `finetune/config.py`

3. **Launch Web UI**
   ```powershell
   python webui/app.py
   # Open browser to http://127.0.0.1:7860
   ```

4. **Read Documentation**
   - Main README.md - Full documentation
   - DEBUG_SETUP_GUIDE.md - Detailed Chinese guide
   - Paper: https://arxiv.org/abs/2508.02739

---

## ✨ Success Checklist

Run this checklist to confirm everything works:

```powershell
# 1. Check Python version (should be 3.10+)
python --version

# 2. Check installed packages
python -c "import numpy, pandas, torch; print('✅ Core packages OK')"

# 3. Test model import
python -c "from model import Kronos, KronosTokenizer; print('✅ Model imports OK')"

# 4. Run full diagnostic
python debug_setup.py
```

If all checks pass, you're ready to go! 🎉

---

## 📞 Need Help?

- Check error messages in VS Code terminal
- Review DEBUG_SETUP_GUIDE.md for detailed troubleshooting
- Ensure you're running from project root: `d:\GitHub\Kronos`
- Verify internet connection for model downloads

---

**You're all set!** Start with `python debug_setup.py` to verify your environment.
