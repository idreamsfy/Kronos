"""
Test script for the finetuned Kronos Tokenizer.
This script loads the finetuned tokenizer and tests its encoding/decoding capabilities.
"""
import torch
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from model.kronos import KronosTokenizer


def test_tokenizer():
    """Test the finetuned tokenizer with random data."""
    
    print("="*70)
    print("Kronos Tokenizer 微调后测试")
    print("="*70)
    
    # Load finetuned tokenizer
    tokenizer_path = "./outputs/models/finetune_tokenizer_demo/checkpoints/best_model"
    
    print(f"\n正在从以下路径加载 tokenizer:\n{tokenizer_path}")
    
    try:
        tokenizer = KronosTokenizer.from_pretrained(tokenizer_path)
        print("✅ Tokenizer 加载成功!\n")
    except Exception as e:
        print(f"❌ 加载失败：{e}")
        print("\n尝试使用预训练 tokenizer...")
        tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
        print("✅ 预训练 Tokenizer 加载成功!\n")
    
    # Print model info
    print("模型信息:")
    print(f"  - 输入维度 (d_in): {tokenizer.d_in}")
    print(f"  - 模型维度 (d_model): {tokenizer.d_model}")
    print(f"  - 注意力头数 (n_heads): {tokenizer.n_heads}")
    print(f"  - 编码层层数 (enc_layers): {tokenizer.enc_layers}")
    print(f"  - 解码层层数 (dec_layers): {tokenizer.dec_layers}")
    print(f"  - S1 量化位数 (s1_bits): {tokenizer.s1_bits}")
    print(f"  - S2 量化位数 (s2_bits): {tokenizer.s2_bits}")
    print()
    
    # Test with synthetic data
    print("生成测试数据...")
    batch_size = 2
    seq_len = 100
    n_features = 6  # OHLCV + amount
    
    # Create synthetic OHLCV data
    torch.manual_seed(42)
    test_data = torch.randn(batch_size, seq_len, n_features)
    
    # Scale to realistic price ranges
    test_data[:, :, 0] *= 10 + 100  # Open
    test_data[:, :, 1] *= 10 + 100  # High
    test_data[:, :, 2] *= 10 + 100  # Low
    test_data[:, :, 3] *= 10 + 100  # Close
    test_data[:, :, 4] *= 1000 + 5000  # Volume
    test_data[:, :, 5] *= 1000 + 5000  # Amount
    
    print(f"测试数据形状：{test_data.shape}")
    print(f"Close price 范围：[{test_data[:, :, 3].min():.2f}, {test_data[:, :, 3].max():.2f}]")
    print()
    
    # Test encoding
    print("测试编码功能...")
    try:
        with torch.no_grad():
            tokens = tokenizer.encode(test_data)
        print(f"✅ 编码成功!")
        print(f"   Tokens 形状：{tokens.shape}")
        print(f"   Tokens 范围：[{tokens.min()}, {tokens.max()}]")
        print()
    except Exception as e:
        print(f"❌ 编码失败：{e}")
        return False
    
    # Test decoding
    print("测试解码功能...")
    try:
        with torch.no_grad():
            reconstructed = tokenizer.decode(tokens)
        print(f"✅ 解码成功!")
        print(f"   重构数据形状：{reconstructed.shape}")
        print()
    except Exception as e:
        print(f"❌ 解码失败：{e}")
        return False
    
    # Calculate reconstruction error
    print("计算重构误差...")
    mse_loss = torch.nn.MSELoss()
    reconstruction_mse = mse_loss(reconstructed, test_data).item()
    print(f"   重构 MSE: {reconstruction_mse:.6f}")
    
    # Calculate per-feature MSE
    feature_names = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount']
    print("\n各特征重构误差:")
    for i, name in enumerate(feature_names):
        feature_mse = mse_loss(reconstructed[:, :, i], test_data[:, :, i]).item()
        print(f"   {name:8s}: MSE = {feature_mse:.6f}")
    
    # Visualization (optional)
    try:
        import matplotlib.pyplot as plt
        
        print("\n生成可视化图表...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Plot Close price comparison
        ax1 = axes[0, 0]
        ax1.plot(test_data[0, :, 3].numpy(), label='Original', linewidth=2)
        ax1.plot(reconstructed[0, :, 3].numpy(), label='Reconstructed', alpha=0.7, linestyle='--')
        ax1.set_title('Close Price: Original vs Reconstructed', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot reconstruction error over time
        ax2 = axes[0, 1]
        close_error = (test_data[0, :, 3] - reconstructed[0, :, 3]).abs().numpy()
        ax2.fill_between(range(seq_len), 0, close_error, alpha=0.5, color='red')
        ax2.set_title('Absolute Reconstruction Error (Close)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Absolute Error')
        ax2.grid(True, alpha=0.3)
        
        # Plot all features for first few time steps
        ax3 = axes[1, 0]
        x = range(min(20, seq_len))
        width = 0.35
        orig_close = test_data[0, :20, 3].numpy()
        recon_close = reconstructed[0, :20, 3].numpy()
        ax3.bar([i - width/2 for i in x], orig_close, width, label='Original', alpha=0.7)
        ax3.bar([i + width/2 for i in x], recon_close, width, label='Reconstructed', alpha=0.7)
        ax3.set_title('Close Price Comparison (First 20 Steps)', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Time Step')
        ax3.set_ylabel('Price')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot volume comparison
        ax4 = axes[1, 1]
        ax4.plot(test_data[0, :, 4].numpy(), label='Original Volume', linewidth=2)
        ax4.plot(reconstructed[0, :, 4].numpy(), label='Reconstructed Volume', alpha=0.7, linestyle='--')
        ax4.set_title('Volume: Original vs Reconstructed', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Time Step')
        ax4.set_ylabel('Volume')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save figure
        save_path = "./figures/tokenizer_reconstruction_test.png"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 可视化图表已保存到：{save_path}")
        
        plt.close()
        
    except ImportError:
        print("\n⚠️  Matplotlib 未安装，跳过可视化")
    except Exception as e:
        print(f"\n⚠️  可视化生成失败：{e}")
    
    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)
    
    return True


if __name__ == '__main__':
    success = test_tokenizer()
    sys.exit(0 if success else 1)
