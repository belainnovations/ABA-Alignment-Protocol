
import torch
import sys

print(f"Python: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.version.cuda}")
print(f"Device Name: {torch.cuda.get_device_name(0)}")
print(f"BF16 Supported: {torch.cuda.is_bf16_supported()}")
