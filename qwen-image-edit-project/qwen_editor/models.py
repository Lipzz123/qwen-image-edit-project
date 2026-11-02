import os, shutil
from pathlib import Path
from huggingface_hub import hf_hub_download
from .config import ROOT, COMFY_DIR, MODEL_REPO, MODEL, TEXT_ENCODER, VAE, LORA


def download_models():
    """Download required files to ComfyUI model folders; redownload on fresh Colab runtime."""
    models_dir = COMFY_DIR / 'models'
    cache = ROOT / 'cache' / 'huggingface'
    os.environ['HF_HOME'] = str(cache)
    os.environ['HUGGINGFACE_HUB_CACHE'] = str(cache / 'hub')
    os.environ['TMPDIR'] = str(ROOT / 'tmp')
    cache.mkdir(parents=True, exist_ok=True)
    (ROOT / 'tmp').mkdir(parents=True, exist_ok=True)

    items = [
        (MODEL_REPO, MODEL, 'diffusion_models', 3 * 1024**3),
        (MODEL_REPO, 'text_encoders/' + TEXT_ENCODER, 'text_encoders', 6 * 1024**3),
        (MODEL_REPO, 'vae/' + VAE, 'vae', 300 * 1024**2),
        ('ausboss/Qwen-Image-2.1-Consistency-LoRA', LORA, 'loras', 100 * 1024**2),
    ]
    missing_estimate = 0
    for repo, filename, folder, minimum in items:
        dest = models_dir / folder / Path(filename).name
        if not (dest.is_file() and dest.stat().st_size >= minimum):
            missing_estimate += {'diffusion_models': 4.60, 'text_encoders': 9.35, 'vae': 0.63, 'loras': 0.16}[folder] * 1024**3
    free = shutil.disk_usage(ROOT).free
    if free < missing_estimate + 512 * 1024**2:
        raise RuntimeError(f'Ruang disk tidak cukup. Kosong {free/1024**3:.1f} GiB; estimasi kebutuhan unduhan {missing_estimate/1024**3:.1f} GiB. Estimasi konservatif; periksa kapasitas Colab.')

    for repo, filename, folder, minimum in items:
        dest_dir = models_dir / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / Path(filename).name
        if dest.is_file() and dest.stat().st_size >= minimum:
            print(f'[OK] Sudah ada: {dest.name}')
            continue
        print(f'\n[DOWNLOAD] {repo} / {filename}')
        downloaded = hf_hub_download(repo_id=repo, filename=filename, local_dir=str(ROOT / 'hf_downloads'))
        source = Path(downloaded)
        if source.resolve() != dest.resolve():
            shutil.copy2(source, dest)
        if not dest.is_file() or dest.stat().st_size < minimum:
            raise RuntimeError(f'File model tidak lengkap/ukurannya tidak sesuai: {dest}')
        print(f'[OK] {dest.name}: {dest.stat().st_size/1024**3:.2f} GiB')

    print('\nSemua file model berhasil diverifikasi.')
