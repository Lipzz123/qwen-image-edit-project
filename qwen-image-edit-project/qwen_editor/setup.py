import shutil
from .config import ROOT
from .comfy_manager import check_gpu, install_engine, start_comfyui, check_nodes
from .models import download_models


def setup():
    """One-time setup per Colab runtime. Fresh runtime downloads models again."""
    print('=== 1/5: Pemeriksaan GPU dan disk ===')
    check_gpu()
    ROOT.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage('/content')
    print(f'Disk kosong: {usage.free/1024**3:.2f} GiB')
    if usage.free < 20 * 1024**3:
        print('PERINGATAN: disk kosong kurang dari 20 GiB; unduhan model mungkin gagal.')
    print('\n=== 2/5: Instalasi ComfyUI dan custom node ===')
    install_engine()
    print('\n=== 3/5: Download model (redownload pada runtime baru) ===')
    download_models()
    print('\n=== 4/5: Menjalankan ComfyUI lokal ===')
    start_comfyui()
    print('\n=== 5/5: Validasi workflow ===')
    check_nodes()
    print('\nSETUP SELESAI. Jalankan launch_editor() pada cell berikutnya.')
