from pathlib import Path
from IPython.display import display
import ipywidgets as widgets
from PIL import Image as PILImage
from .inference import generate


def launch_editor():
    """Notebook-native UI; no public Gradio tunnel or externally exposed web server."""
    title = widgets.HTML('<h2>Qwen Image Edit 2.1</h2><p>Upload gambar, tulis instruksi, lalu tekan Generate.</p>')
    upload = widgets.FileUpload(accept='image/*', multiple=False, description='Upload image')
    prompt = widgets.Textarea(value='', placeholder='Example: Change the background to a bright green studio. Keep the person unchanged.', description='Prompt:', layout=widgets.Layout(width='100%', height='110px'))
    steps = widgets.IntSlider(value=20, min=12, max=30, step=1, description='Steps:', continuous_update=False)
    resolution = widgets.Dropdown(options=[('768 (recommended for T4)', 768), ('1024', 1024)], value=768, description='Resolution:')
    lora = widgets.Checkbox(value=False, description='Consistency LoRA (experimental)')
    button = widgets.Button(description='Generate Image', button_style='success', icon='magic')
    status = widgets.HTML('<i>Ready. Setup must finish before generating.</i>')
    output = widgets.Output()

    def on_generate(_):
        button.disabled = True
        output.clear_output()
        status.value = '<b>Starting...</b>'
        try:
            value = upload.value
            if not value:
                raise ValueError('Pilih gambar terlebih dahulu.')
            # ipywidgets 7 (Colab legacy) returns dict; ipywidgets 8 returns tuple/list.
            if isinstance(value, dict):
                item = next(iter(value.values()))
                content = item['content']
                filename = item.get('metadata', {}).get('name', 'input_image')
            else:
                item = value[0]
                content = item['content']
                filename = item.get('name', 'input_image')
            suffix = Path(filename).suffix.lower() or '.png'
            if suffix not in ('.png', '.jpg', '.jpeg', '.webp', '.bmp'):
                suffix = '.png'
            from .config import ROOT
            input_dir = ROOT / 'inputs'
            input_dir.mkdir(parents=True, exist_ok=True)
            image_path = input_dir / ('upload_' + __import__('uuid').uuid4().hex + suffix)
            image_path.write_bytes(bytes(content))
            with PILImage.open(image_path) as im:
                im.verify()
            result = generate(str(image_path), prompt.value, steps.value, resolution.value, lora.value, lambda msg: setattr(status, 'value', '<b>' + msg.replace('&','&amp;').replace('<','&lt;') + '</b>'))
            status.value = '<b>Completed successfully.</b>'
            with output:
                display(PILImage.open(result))
                print('Output file:', result)
                display(widgets.HTML('<p>Gunakan ikon file di panel Files Colab untuk mengunduh hasil dari folder <code>/content/qwen_image_2_1/outputs</code>.</p>'))
        except Exception as exc:
            status.value = '<b style="color:#b91c1c">Error: ' + str(exc).replace('&','&amp;').replace('<','&lt;') + '</b>'
            with output:
                print(type(exc).__name__ + ':', exc)
                print('Jika masalah berlanjut, periksa /content/qwen_image_2_1/comfyui.log')
        finally:
            button.disabled = False

    button.on_click(on_generate)
    display(widgets.VBox([title, upload, prompt, steps, resolution, lora, button, status, output]))
