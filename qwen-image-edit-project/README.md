# Qwen Image Edit 2.1 — Colab Easy Mode + Website Starter

Starter project that separates the Colab AI runtime package from a Next.js website scaffold.

## Repository layout

```text
qwen-image-edit-project/
├── Qwen_Image_Edit_2_1_Easy_Mode.ipynb  # user-facing Colab notebook
├── qwen_editor/                         # public Python package used by notebook
├── pyproject.toml
├── website/                             # Next.js + Supabase website scaffold
└── README.md
```

## A. Publish this repository

1. Create a **public** GitHub repository, e.g. `qwen-image-edit-project`.
2. Upload the contents of this project to the repository root (not the containing folder as a nested folder).
3. In `Qwen_Image_Edit_2_1_Easy_Mode.ipynb`, set `GITHUB_REPO = "YOUR_GITHUB_USERNAME/qwen-image-edit-project"`.
4. Commit the notebook change.
5. Open the notebook in Colab using:
   `https://colab.research.google.com/github/YOUR_GITHUB_USERNAME/qwen-image-edit-project/blob/main/Qwen_Image_Edit_2_1_Easy_Mode.ipynb`
6. Share the notebook URL as **Viewer**. Users must use **File → Save a copy in Drive** to run their own copy.

Viewer mode protects the original notebook from edits, but it does not conceal source code or prevent copying. A public Python package is also public source code. Do not put secrets, private tokens, or credentials in this repository or notebook.

## B. Colab user flow

1. Open the notebook and save a personal Drive copy.
2. Select **Runtime → Change runtime type → GPU**.
3. Change `GITHUB_REPO` only if you changed the repository name.
4. Select **Runtime → Run all**.
5. Wait for ComfyUI, custom node, and model setup to finish.
6. Upload an image in the notebook widget, enter an edit prompt, choose steps/resolution, and press Generate.
7. Outputs are stored in `/content/qwen_image_2_1/outputs`.

The notebook uses a notebook-native `ipywidgets` UI and does not create a Gradio public tunnel. It does start a local ComfyUI process inside the Colab runtime. This is a technical prototype, not a guarantee that the workflow is permitted or continuously available on every Colab plan. Check current Google Colab terms and resource limits before public launch. Do not use multiple accounts to evade quotas or restrictions.

## C. Model setup notes

The package preserves the original notebook's model identifiers and workflow:

- Diffusion: `abenzerps/Qwen-Image-2.1-Uncensored-Quantized` — `qwen-image-2.1-UC-Q4_K_M.gguf`
- Text encoder: `text_encoders/qwen3vl_8b_int8_convrot.safetensors`
- VAE: `vae/qwen_image_2.1_vae_bf16.safetensors`
- Optional experimental LoRA: `ausboss/Qwen-Image-2.1-Consistency-LoRA`
- Engine: ComfyUI + `leejet/ComfyUI-GGUF`

Model repositories, file names, node APIs, and dependency versions may change. The notebook checks required ComfyUI nodes and file sizes, but a successful static check is not the same as a successful GPU inference. First test on the exact Colab GPU/runtime you intend to support. For a T4 16 GB, start at 768 resolution; 1024 may run out of memory depending on runtime state.

Check each model and dependency license and usage policy before commercial use. The word “uncensored” in a repository name is not a license grant or a safety guarantee.

## D. Website setup

See [`website/README.md`](website/README.md). The website scaffold includes:

- Next.js landing page
- Google OAuth sign-in through Supabase Auth
- notebook link configuration
- a fail-closed placeholder for rewarded-ad verification

The rewarded-ad provider is deliberately **not faked**. The access grant API returns an error until you choose a provider and implement its signed server-to-server callback verification. Never unlock access based only on a client-side button click or a JavaScript `onReward` event.

## E. Important access-gate limitation

A website cannot make a public Colab URL secret after giving it to a visitor. A user can bookmark or share that URL. The website gate is a monetization/onboarding flow, not strong access control. If the Colab notebook URL is public on GitHub, it can also be found without visiting the website. To enforce access technically, the inference must run behind infrastructure you control (e.g. authenticated backend/GPU), which is a different architecture and may incur compute costs.

## F. Local validation

From the repository root:

```bash
python -m compileall -q qwen_editor
```

The Colab GPU workflow must be tested in a live Colab runtime. This project was not executed against remote model repositories or a live GPU as part of packaging.
