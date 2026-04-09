#!/bin/bash

# ============================================================
# Установщик кастомных нодов для Flora AI style + Wan 2.1
# Запускать из папки ComfyUI/custom_nodes/
# ============================================================

set -e

COMFYUI_DIR="${1:-$HOME/ComfyUI}"
CUSTOM_NODES_DIR="$COMFYUI_DIR/custom_nodes"

echo "======================================="
echo " Установка ComfyUI нодов для Wan 2.1"
echo " + IP-Adapter (Flora AI стиль)"
echo "======================================="
echo "ComfyUI папка: $COMFYUI_DIR"
echo ""

if [ ! -d "$COMFYUI_DIR" ]; then
    echo "ОШИБКА: ComfyUI не найден в $COMFYUI_DIR"
    echo "Укажи путь: ./install_custom_nodes.sh /путь/до/ComfyUI"
    exit 1
fi

cd "$CUSTOM_NODES_DIR"

# -------------------------------------------------------
# 1. ComfyUI-WanVideoWrapper (kijai) — Wan 2.1 видео
# -------------------------------------------------------
echo "[1/5] Установка ComfyUI-WanVideoWrapper..."
if [ -d "ComfyUI-WanVideoWrapper" ]; then
    echo "  Уже установлен. Обновляем..."
    cd ComfyUI-WanVideoWrapper && git pull && cd ..
else
    git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git
    cd ComfyUI-WanVideoWrapper
    pip install -r requirements.txt
    cd ..
fi

# -------------------------------------------------------
# 2. ComfyUI_IPAdapter_plus — IP-Adapter (референс фото)
# -------------------------------------------------------
echo "[2/5] Установка ComfyUI_IPAdapter_plus..."
if [ -d "ComfyUI_IPAdapter_plus" ]; then
    echo "  Уже установлен. Обновляем..."
    cd ComfyUI_IPAdapter_plus && git pull && cd ..
else
    git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
fi

# -------------------------------------------------------
# 3. ComfyUI-VideoHelperSuite — VHS_VideoCombine
# -------------------------------------------------------
echo "[3/5] Установка ComfyUI-VideoHelperSuite..."
if [ -d "ComfyUI-VideoHelperSuite" ]; then
    echo "  Уже установлен. Обновляем..."
    cd ComfyUI-VideoHelperSuite && git pull && cd ..
else
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
    cd ComfyUI-VideoHelperSuite
    pip install -r requirements.txt
    cd ..
fi

# -------------------------------------------------------
# 4. ComfyUI-Manager (удобное управление нодами)
# -------------------------------------------------------
echo "[4/5] Установка ComfyUI-Manager..."
if [ -d "ComfyUI-Manager" ]; then
    echo "  Уже установлен."
else
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
fi

# -------------------------------------------------------
# 5. ComfyUI_essentials — полезные утилиты
# -------------------------------------------------------
echo "[5/5] Установка ComfyUI_essentials..."
if [ -d "ComfyUI_essentials" ]; then
    echo "  Уже установлен. Обновляем..."
    cd ComfyUI_essentials && git pull && cd ..
else
    git clone https://github.com/cubiq/ComfyUI_essentials.git
    cd ComfyUI_essentials
    pip install -r requirements.txt
    cd ..
fi

echo ""
echo "======================================="
echo " Все ноды установлены!"
echo "======================================="
echo ""
echo "Теперь нужно скачать модели:"
echo "  ./download_models.sh $COMFYUI_DIR"
echo ""
echo "Или скачай вручную (см. models_required.txt)"
