#!/bin/bash

# ============================================================
# Скачивает модели для Wan 2.1 + IP-Adapter
# Нужен huggingface-cli: pip install huggingface_hub
# ============================================================

set -e

COMFYUI_DIR="${1:-$HOME/ComfyUI}"

echo "Скачиваю модели в: $COMFYUI_DIR"
echo ""

# Проверяем наличие huggingface_hub
if ! python3 -c "import huggingface_hub" 2>/dev/null; then
    echo "Устанавливаем huggingface_hub..."
    pip install huggingface_hub
fi

HF_DL="python3 -c \"from huggingface_hub import hf_hub_download; "

mkdir -p "$COMFYUI_DIR/models/checkpoints"
mkdir -p "$COMFYUI_DIR/models/ipadapter"
mkdir -p "$COMFYUI_DIR/models/clip_vision"
mkdir -p "$COMFYUI_DIR/models/clip"
mkdir -p "$COMFYUI_DIR/models/vae"
mkdir -p "$COMFYUI_DIR/models/wanvideo"

# -------------------------------------------------------
# SDXL чекпоинт — JuggernautXL (фотореализм как Flora AI)
# -------------------------------------------------------
echo "[1/7] Скачиваю JuggernautXL..."
CKPT="$COMFYUI_DIR/models/checkpoints/juggernautXL_v9Rdphoto2Lightning.safetensors"
if [ ! -f "$CKPT" ]; then
    python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='RunDiffusion/Juggernaut-XL-v9',
    filename='Juggernaut-XL_rdphoto2-lightning_4S.safetensors',
    local_dir='$COMFYUI_DIR/models/checkpoints'
)
"
    mv "$COMFYUI_DIR/models/checkpoints/Juggernaut-XL_rdphoto2-lightning_4S.safetensors" "$CKPT" 2>/dev/null || true
else
    echo "  Уже скачан."
fi

# -------------------------------------------------------
# IP-Adapter SDXL Plus (для стиля/референса)
# -------------------------------------------------------
echo "[2/7] Скачиваю IP-Adapter Plus SDXL..."
IPA="$COMFYUI_DIR/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors"
if [ ! -f "$IPA" ]; then
    python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='h94/IP-Adapter',
    filename='sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors',
    local_dir='/tmp/ipa_download'
)
import shutil
shutil.move('/tmp/ipa_download/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors', '$IPA')
"
else
    echo "  Уже скачан."
fi

# -------------------------------------------------------
# CLIP Vision ViT-H (для IP-Adapter)
# -------------------------------------------------------
echo "[3/7] Скачиваю CLIP Vision ViT-H..."
CV="$COMFYUI_DIR/models/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"
if [ ! -f "$CV" ]; then
    python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='h94/IP-Adapter',
    filename='models/image_encoder/model.safetensors',
    local_dir='/tmp/cv_download'
)
import shutil
shutil.move('/tmp/cv_download/models/image_encoder/model.safetensors', '$CV')
"
else
    echo "  Уже скачан."
fi

# -------------------------------------------------------
# Wan 2.1 I2V 480p 14B (Image-to-Video)
# -------------------------------------------------------
echo "[4/7] Скачиваю Wan 2.1 I2V 480p 14B (большой файл ~29GB)..."
WAN_MODEL="$COMFYUI_DIR/models/wanvideo/wan2.1_i2v_480p_14B_bf16.safetensors"
if [ ! -f "$WAN_MODEL" ]; then
    python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='kijai/WanVideo-safetensors',
    filename='wan2.1_i2v_480p_14B_bf16.safetensors',
    local_dir='$COMFYUI_DIR/models/wanvideo'
)
"
else
    echo "  Уже скачан."
fi

# -------------------------------------------------------
# Wan 2.1 VAE
# -------------------------------------------------------
echo "[5/7] Скачиваю Wan 2.1 VAE..."
WAN_VAE="$COMFYUI_DIR/models/vae/wan_2.1_vae.safetensors"
if [ ! -f "$WAN_VAE" ]; then
    python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='kijai/WanVideo-safetensors',
    filename='wan_2.1_vae.safetensors',
    local_dir='$COMFYUI_DIR/models/vae'
)
"
else
    echo "  Уже скачан."
fi

# -------------------------------------------------------
# UMT5-XXL text encoder (для Wan 2.1)
# -------------------------------------------------------
echo "[6/7] Скачиваю UMT5-XXL text encoder..."
T5="$COMFYUI_DIR/models/clip/umt5-xxl-enc-bf16.safetensors"
if [ ! -f "$T5" ]; then
    python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='kijai/WanVideo-safetensors',
    filename='umt5-xxl-enc-bf16.safetensors',
    local_dir='$COMFYUI_DIR/models/clip'
)
"
else
    echo "  Уже скачан."
fi

# -------------------------------------------------------
# CLIP Vision для Wan 2.1
# -------------------------------------------------------
echo "[7/7] Скачиваю CLIP Vision для Wan 2.1..."
CV2="$COMFYUI_DIR/models/clip_vision/clip_vision_h.safetensors"
if [ ! -f "$CV2" ]; then
    python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='kijai/WanVideo-safetensors',
    filename='clip_vision_h.safetensors',
    local_dir='$COMFYUI_DIR/models/clip_vision'
)
"
else
    echo "  Уже скачан."
fi

echo ""
echo "======================================="
echo " Все модели скачаны!"
echo "======================================="
echo ""
echo "Теперь:"
echo "1. Запусти ComfyUI"
echo "2. Загрузи workflow 01 для генерации фото"
echo "3. Загрузи workflow 02 для создания видео"
