"""
Single-GPU/CPU training script for Kronos Tokenizer finetuning.
This is a simplified version that doesn't require torchrun/DDP.
"""
import os
import sys
import json
import time
from time import gmtime, strftime
import datetime
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from dataset import QlibDataset
from model.kronos import KronosTokenizer


def set_seed(seed: int):
    """Sets random seed for reproducibility."""
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def format_time(seconds: float) -> str:
    """Formats duration in seconds into H:M:S string."""
    return str(datetime.timedelta(seconds=int(seconds)))


def train_model(model, device, config, save_dir):
    """
    Training loop for the tokenizer.
    
    Args:
        model: The KronosTokenizer model
        device: Training device (CPU or CUDA)
        config: Configuration dictionary
        save_dir: Directory to save checkpoints
    
    Returns:
        tuple: (trained_model, results_dict)
    """
    print(f"Starting training on device: {device}")
    
    # Create dataloaders
    print("Loading datasets...")
    train_dataset = QlibDataset('train')
    valid_dataset = QlibDataset('val')
    print(f"Train dataset size: {len(train_dataset)}, Validation dataset size: {len(valid_dataset)}")
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=config['batch_size'], 
        shuffle=True,
        num_workers=0,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    val_loader = DataLoader(
        valid_dataset, 
        batch_size=config['batch_size'], 
        shuffle=False,
        num_workers=0,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    # Optimizer and scheduler
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config['tokenizer_learning_rate'],
        betas=(config['adam_beta1'], config['adam_beta2']),
        weight_decay=config['adam_weight_decay']
    )
    
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer=optimizer,
        max_lr=config['tokenizer_learning_rate'],
        steps_per_epoch=len(train_loader),
        epochs=config['epochs'],
        pct_start=0.03,
        div_factor=10
    )
    
    best_val_loss = float('inf')
    dt_result = {}
    start_time = time.time()
    
    print(f"\n{'='*70}")
    print(f"Training started with {config['epochs']} epochs")
    print(f"Batch size: {config['batch_size']}, Learning rate: {config['tokenizer_learning_rate']}")
    print(f"{'='*70}\n")
    
    for epoch_idx in range(config['epochs']):
        epoch_start_time = time.time()
        model.train()
        epoch_loss = 0.0
        n_batches = 0
        
        # Training loop
        for i, (ori_batch_x, _) in enumerate(train_loader):
            # ori_batch_x shape: [batch_size, window_len, n_features]
            ori_batch_x = ori_batch_x.to(device, non_blocking=True)
            
            # Forward pass
            zs, bsq_loss, _, _ = model(ori_batch_x)
            z_pre, z = zs
            
            # Loss calculation (model output already has batch dimension)
            recon_loss_pre = F.mse_loss(z_pre, ori_batch_x)
            recon_loss_all = F.mse_loss(z, ori_batch_x)
            recon_loss = recon_loss_pre + recon_loss_all
            loss = (recon_loss + bsq_loss) / 2
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            
            # Optimizer step
            optimizer.step()
            scheduler.step()
            
            epoch_loss += loss.item()
            n_batches += 1
            
            # Log progress
            if (i + 1) % config['log_interval'] == 0:
                avg_loss = epoch_loss / n_batches
                print(
                    f"[Epoch {epoch_idx + 1}/{config['epochs']}, Step {i + 1}/{len(train_loader)}] "
                    f"LR {optimizer.param_groups[0]['lr']:.6f}, Loss: {avg_loss:.4f}"
                )
        
        # Calculate average training loss
        avg_train_loss = epoch_loss / len(train_loader)
        
        # Validation loop
        model.eval()
        val_loss_sum = 0.0
        val_sample_count = 0
        
        with torch.no_grad():
            for ori_batch_x, _ in val_loader:
                # ori_batch_x shape: [batch_size, window_len, n_features]
                ori_batch_x = ori_batch_x.to(device)
                
                zs, _, _, _ = model(ori_batch_x)
                _, z = zs
                val_loss_item = F.mse_loss(z, ori_batch_x)
                
                val_loss_sum += val_loss_item.item() * ori_batch_x.size(0)
                val_sample_count += ori_batch_x.size(0)
        
        avg_val_loss = val_loss_sum / val_sample_count if val_sample_count > 0 else 0
        
        # Print epoch summary
        print(f"\n{'-'*70}")
        print(f"--- Epoch {epoch_idx + 1}/{config['epochs']} Summary ---")
        print(f"Average Training Loss: {avg_train_loss:.4f}")
        print(f"Validation Loss: {avg_val_loss:.4f}")
        print(f"Time This Epoch: {format_time(time.time() - epoch_start_time)}")
        print(f"Total Time Elapsed: {format_time(time.time() - start_time)}")
        print(f"{'-'*70}\n")
        
        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            save_path = os.path.join(save_dir, 'checkpoints', 'best_model')
            os.makedirs(save_path, exist_ok=True)
            model.save_pretrained(save_path)
            print(f"✓ Best model saved to {save_path} (Val Loss: {best_val_loss:.4f})\n")
    
    dt_result['best_val_loss'] = best_val_loss
    return model, dt_result


def main():
    """Main function for single GPU/CPU training."""
    # Load configuration
    config_obj = Config()
    config = {
        'batch_size': config_obj.batch_size,
        'epochs': config_obj.epochs,
        'log_interval': config_obj.log_interval,
        'tokenizer_learning_rate': config_obj.tokenizer_learning_rate,
        'adam_beta1': config_obj.adam_beta1,
        'adam_beta2': config_obj.adam_beta2,
        'adam_weight_decay': config_obj.adam_weight_decay,
        'seed': config_obj.seed,
        'pretrained_tokenizer_path': config_obj.pretrained_tokenizer_path,
        'save_path': config_obj.save_path,
        'tokenizer_save_folder_name': config_obj.tokenizer_save_folder_name,
    }
    
    # Set seed
    set_seed(config['seed'])
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("Note: Running on CPU. Training will be slower than GPU.")
    
    # Setup save directory
    save_dir = os.path.join(config['save_path'], config['tokenizer_save_folder_name'])
    os.makedirs(os.path.join(save_dir, 'checkpoints'), exist_ok=True)
    print(f"Models will be saved to: {save_dir}")
    
    # Load pretrained model
    print(f"\nLoading pretrained tokenizer from: {config['pretrained_tokenizer_path']}")
    model = KronosTokenizer.from_pretrained(config['pretrained_tokenizer_path'])
    model.to(device)
    print("Model loaded successfully!\n")
    
    # Start training
    print("Starting training...\n")
    trained_model, results = train_model(model, device, config, save_dir)
    
    # Final summary
    print(f"\n{'='*70}")
    print("Training completed!")
    print(f"Best validation loss: {results['best_val_loss']:.4f}")
    print(f"Model saved to: {save_dir}/checkpoints/best_model")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
