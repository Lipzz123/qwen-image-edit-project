from pathlib import Path

ROOT = Path('/content/qwen_image_2_1')
COMFY_DIR = ROOT / 'ComfyUI'
OUTPUT_DIR = ROOT / 'outputs'
LOG_PATH = ROOT / 'comfyui.log'
COMFY_URL = 'http://127.0.0.1:8188'
MODEL_REPO = 'abenzerps/Qwen-Image-2.1-Uncensored-Quantized'
MODEL = 'qwen-image-2.1-UC-Q4_K_M.gguf'
TEXT_ENCODER = 'qwen3vl_8b_int8_convrot.safetensors'
VAE = 'qwen_image_2.1_vae_bf16.safetensors'
LORA = 'qwen-image-2.1-consistency.safetensors'
