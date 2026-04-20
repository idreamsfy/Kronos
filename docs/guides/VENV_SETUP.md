# Kronos Project - Python Environment Setup

## Virtual Environment

This project uses a Python virtual environment located in `.venv/`.

### Activating the Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Installed Dependencies

All required dependencies have been installed from `requirements.txt`:

- **numpy**: Numerical computing library
- **torch>=2.0.0**: PyTorch deep learning framework (currently v2.11.0)
- **einops==0.8.1**: Tensor operations library
- **huggingface_hub==0.33.1**: Hugging Face model hub client
- **matplotlib==3.9.3**: Plotting and visualization
- **pandas**: Data manipulation and analysis (currently v3.0.2)
- **tqdm==4.67.1**: Progress bar library
- **safetensors==0.6.2**: Safe tensor serialization

### Python Version

The virtual environment is using **Python 3.11.9**.

### Verifying Installation

To verify that all packages are correctly installed, run:

```python
python -c "import torch; import pandas; import numpy; import matplotlib; print('All packages OK!')"
```

### Deactivating the Virtual Environment

When you're done working on the project, you can deactivate the virtual environment:

```powershell
deactivate
```
