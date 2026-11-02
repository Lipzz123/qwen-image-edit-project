import os, sys, subprocess, time, requests
from .config import ROOT, COMFY_DIR, COMFY_URL, LOG_PATH


def _run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def install_engine():
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / 'cache' / 'pip').mkdir(parents=True, exist_ok=True)
    os.environ['PIP_CACHE_DIR'] = str(ROOT / 'cache' / 'pip')
    if not (COMFY_DIR / '.git').exists():
        _run(['git', 'clone', '--depth', '1', 'https://github.com/comfyanonymous/ComfyUI.git', str(COMFY_DIR)])
    _run([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'], cwd=str(COMFY_DIR))
    nodes = COMFY_DIR / 'custom_nodes' / 'ComfyUI-GGUF'
    if not (nodes / '.git').exists():
        _run(['git', 'clone', 'https://github.com/leejet/ComfyUI-GGUF.git', str(nodes)])
    req = nodes / 'requirements.txt'
    if req.exists():
        _run([sys.executable, '-m', 'pip', 'install', '-q', '-r', str(req)])
    _run([sys.executable, '-m', 'pip', 'install', '-q', 'huggingface_hub', 'hf_transfer', 'requests', 'pillow', 'ipywidgets'])


def check_gpu():
    try:
        import torch
    except Exception as e:
        raise RuntimeError(f'PyTorch tidak dapat diimpor: {e}')
    if not torch.cuda.is_available():
        raise RuntimeError('GPU CUDA tidak terdeteksi. Pilih Runtime > Change runtime type > GPU, lalu jalankan ulang.')
    print('GPU:', torch.cuda.get_device_name(0))
    print('CUDA:', torch.version.cuda)
    print('VRAM:', round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2), 'GiB')


def start_comfyui():
    def ready():
        try:
            return requests.get(f'{COMFY_URL}/system_stats', timeout=3).status_code == 200
        except Exception:
            return False
    if ready():
        print('ComfyUI sudah aktif.')
        return
    log = open(LOG_PATH, 'a', buffering=1)
    subprocess.Popen([sys.executable, 'main.py', '--listen', '127.0.0.1', '--port', '8188', '--lowvram'], cwd=str(COMFY_DIR), stdout=log, stderr=subprocess.STDOUT)
    for _ in range(90):
        if ready():
            print('ComfyUI aktif di localhost:8188')
            return
        time.sleep(2)
    tail = LOG_PATH.read_text(errors='ignore')[-5000:] if LOG_PATH.exists() else '(log kosong)'
    raise RuntimeError('ComfyUI gagal aktif. Log terakhir:\n' + tail)


def check_nodes():
    r = requests.get(f'{COMFY_URL}/object_info', timeout=60)
    r.raise_for_status()
    info = r.json()
    required = ['UnetLoaderGGUF', 'CLIPLoader', 'VAELoader', 'LoadImage', 'QwenImage21Cache', 'TextEncodeQwenImage21', 'KSampler', 'VAEDecode', 'SaveImage']
    missing = [x for x in required if x not in info]
    if missing:
        raise RuntimeError('Node workflow tidak ditemukan: ' + ', '.join(missing) + '. Periksa instalasi node dan restart runtime.')
    print('Semua custom node workflow tersedia.')
