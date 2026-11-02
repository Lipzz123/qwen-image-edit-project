import os, time, uuid, random, mimetypes, requests
from pathlib import Path
from PIL import Image
from .config import ROOT, COMFY_DIR, COMFY_URL, OUTPUT_DIR, LOG_PATH, MODEL, TEXT_ENCODER, VAE, LORA


def generate(image_path, prompt, steps=20, resolution=768, use_consistency_lora=False, status_callback=None):
    started = time.time()
    def status(msg):
        print(msg)
        if status_callback:
            status_callback(msg)
    if not image_path:
        raise ValueError('Unggah gambar terlebih dahulu.')
    if not prompt or not prompt.strip():
        raise ValueError('Instruksi edit tidak boleh kosong.')
    steps, resolution = int(steps), int(resolution)
    if not 12 <= steps <= 30:
        raise ValueError('Sampling steps harus antara 12 dan 30.')
    if resolution not in (768, 1024):
        raise ValueError('Resolusi yang didukung: 768 atau 1024.')
    paths = {
        MODEL: COMFY_DIR / 'models' / 'diffusion_models' / MODEL,
        TEXT_ENCODER: COMFY_DIR / 'models' / 'text_encoders' / TEXT_ENCODER,
        VAE: COMFY_DIR / 'models' / 'vae' / VAE,
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError('Model tidak ditemukan: ' + ', '.join(missing) + '. Jalankan ulang setup().')
    node_info = requests.get(f'{COMFY_URL}/object_info', timeout=60).json()
    if use_consistency_lora:
        if not (COMFY_DIR / 'models' / 'loras' / LORA).is_file():
            raise FileNotFoundError('Consistency LoRA tidak ditemukan. Jalankan setup() lagi.')
        if 'LoraLoaderModelOnly' not in node_info:
            raise RuntimeError('Node LoraLoaderModelOnly tidak tersedia. Matikan Consistency LoRA.')

    prompt = prompt.strip()
    if '<image1>' not in prompt:
        prompt = 'Edit <image1> according to these instructions:\n' + prompt
    seed = random.randint(1, 2**32 - 1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    upload_name = f'input_{uuid.uuid4().hex}_{Path(image_path).name}'
    status('Mengunggah gambar ke ComfyUI...')
    with open(image_path, 'rb') as f:
        up = requests.post(f'{COMFY_URL}/upload/image', files={'image': (upload_name, f, mimetypes.guess_type(image_path)[0] or 'application/octet-stream')}, data={'overwrite': 'false'}, timeout=180)
    up.raise_for_status()
    image_name = up.json().get('name')
    if not image_name:
        raise RuntimeError('ComfyUI tidak mengembalikan nama gambar input.')

    workflow = {
        '1': {'class_type': 'UnetLoaderGGUF', 'inputs': {'unet_name': MODEL}},
        '2': {'class_type': 'CLIPLoader', 'inputs': {'clip_name': TEXT_ENCODER, 'type': 'qwen_image', 'device': 'default'}},
        '3': {'class_type': 'VAELoader', 'inputs': {'vae_name': VAE}},
        '4': {'class_type': 'LoadImage', 'inputs': {'image': image_name}},
        '6': {'class_type': 'QwenImage21Cache', 'inputs': {'model': ['5', 0] if use_consistency_lora else ['1', 0], 'device': 'auto', 'dtype': 'default'}},
        '7': {'class_type': 'TextEncodeQwenImage21', 'inputs': {'clip': ['2', 0], 'vae': ['3', 0], 'images.image_1': ['4', 0], 'resolution': resolution, 'prompt': prompt, 'negative_prompt': ''}},
        '8': {'class_type': 'KSampler', 'inputs': {'model': ['6', 0], 'positive': ['7', 0], 'negative': ['7', 1], 'latent_image': ['7', 2], 'seed': seed, 'steps': steps, 'cfg': 1.0, 'sampler_name': 'euler', 'scheduler': 'simple', 'denoise': 1.0}},
        '9': {'class_type': 'VAEDecode', 'inputs': {'samples': ['8', 0], 'vae': ['3', 0]}},
        '10': {'class_type': 'SaveImage', 'inputs': {'images': ['9', 0], 'filename_prefix': 'qwen_edit'}},
    }
    if use_consistency_lora:
        workflow['5'] = {'class_type': 'LoraLoaderModelOnly', 'inputs': {'model': ['1', 0], 'lora_name': LORA, 'strength_model': 1.0}}

    status(f'Menjalankan workflow (steps={steps}, resolution={resolution}, seed={seed})...')
    submit = requests.post(f'{COMFY_URL}/prompt', json={'prompt': workflow}, timeout=120)
    try:
        data = submit.json()
    except Exception:
        raise RuntimeError('Respons ComfyUI tidak valid: ' + submit.text[:1200])
    if not submit.ok or data.get('node_errors'):
        raise RuntimeError('ComfyUI menolak workflow: ' + str(data)[:3000])
    prompt_id = data.get('prompt_id')
    if not prompt_id:
        raise RuntimeError('ComfyUI tidak mengembalikan prompt_id: ' + str(data))

    history_item = None
    while time.time() - started < 1800:
        time.sleep(2)
        h = requests.get(f'{COMFY_URL}/history/{prompt_id}', timeout=20)
        h.raise_for_status()
        history_item = h.json().get(prompt_id)
        if history_item:
            st = history_item.get('status', {})
            status_str = st.get('status_str', '')
            if status_str == 'error':
                raise RuntimeError('Workflow gagal: ' + str(st.get('messages', []))[-3000:])
            if st.get('completed') or status_str == 'success':
                break
        status(f'Memproses... {int(time.time()-started)} detik')
    else:
        raise TimeoutError('Generate melewati batas waktu 30 menit. Periksa log ComfyUI.')
    if not history_item:
        raise RuntimeError('Riwayat pekerjaan tidak ditemukan.')
    images = history_item.get('outputs', {}).get('10', {}).get('images', [])
    if not images:
        raise RuntimeError('Workflow selesai tetapi node SaveImage tidak menghasilkan gambar.')
    info = images[0]
    response = requests.get(f'{COMFY_URL}/view', params={'filename': info['filename'], 'subfolder': info.get('subfolder', ''), 'type': info.get('type', 'output')}, timeout=180)
    response.raise_for_status()
    if not response.content:
        raise RuntimeError('File output kosong.')
    output = OUTPUT_DIR / f'result_{uuid.uuid4().hex}.png'
    output.write_bytes(response.content)
    with Image.open(output) as im:
        im.verify()
    elapsed = round(time.time() - started, 1)
    status(f'Selesai dalam {elapsed} detik. Seed: {seed}. Prompt ID: {prompt_id}')
    return str(output)
