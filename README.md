# Flora AI стиль в ComfyUI — фото по референсу + Wan 2.1 видео

Этот проект воспроизводит функциональность Flora AI прямо в ComfyUI:
1. **Фото по референсу** — загружаешь своё фото, IP-Adapter переносит твой облик/стиль на новое изображение
2. **Видео из фото** — сгенерированное фото оживает через Wan 2.1 (Image-to-Video)

---

## Быстрый старт

### 1. Установи кастомные ноды

```bash
chmod +x install_custom_nodes.sh
./install_custom_nodes.sh /путь/до/ComfyUI
```

### 2. Скачай модели

```bash
chmod +x download_models.sh
./download_models.sh /путь/до/ComfyUI
```

Или скачай вручную — список в `models_required.txt`

### 3. Загрузи воркфлоу в ComfyUI

**Шаг 1 — Генерация фото:**
- Открой ComfyUI в браузере (`http://localhost:8188`)
- Нажми `Load` → выбери `workflows/01_image_from_reference.json`
- В ноде `LoadImage` загрузи своё референс-фото
- Напиши промпт в `CLIPTextEncode` (позитивный)
- Нажми `Queue Prompt`

**Шаг 2 — Генерация видео:**
- Загрузи `workflows/02_image_to_video_wan21.json`
- В ноде `LoadImage` загрузи фото из шага 1
- Напиши промпт для движения (например: "плавно идёт по парку")
- Нажми `Queue Prompt`

---

## Или через Python API

```bash
# Установи зависимости
pip install huggingface_hub

# Запустить ComfyUI
cd /путь/до/ComfyUI && python main.py

# Из другого терминала — генерируй и фото и видео сразу:
python api_client.py \
  --mode both \
  --reference ./моё_фото.jpg \
  --prompt "professional portrait, beautiful lighting, 8k" \
  --video-prompt "walking gracefully in a garden, cinematic motion" \
  --frames 81
```

---

## Структура файлов

```
workflows/
  01_image_from_reference.json  — IP-Adapter SDXL (как Flora AI)
  02_image_to_video_wan21.json  — Wan 2.1 I2V (видео из фото)

install_custom_nodes.sh         — установщик нодов
download_models.sh              — загрузчик моделей
models_required.txt             — список всех нужных моделей
api_client.py                   — Python клиент для автоматизации
```

---

## Настройки воркфлоу

### Workflow 01 — IP-Adapter (фото по референсу)

| Нод | Настройка | Описание |
|-----|-----------|----------|
| `CheckpointLoaderSimple` | имя файла | Модель SDXL (JuggernautXL рекомендуется) |
| `LoadImage` | файл | Твоё референс-фото |
| `IPAdapterAdvanced` | weight | Сила влияния референса (0.7–1.2) |
| `CLIPTextEncode` (первый) | текст | Описание желаемого изображения |
| `CLIPTextEncode` (второй) | текст | Что не хочешь видеть |
| `EmptyLatentImage` | width/height | Размер (1024×1024 для SDXL) |
| `KSampler` | steps | Кол-во шагов (20–40) |
| `KSampler` | cfg | Следование промпту (6–8) |

### Workflow 02 — Wan 2.1 (видео)

| Нод | Настройка | Описание |
|-----|-----------|----------|
| `WanVideoModelLoader` | модель | 14B = качество, 1.3B = скорость |
| `LoadImage` | файл | Фото из шага 1 |
| `WanVideoTextEncode` | текст | Описание движения |
| `WanVideoImageToVideoLatent` | frames | Кол-во кадров (81 = ~3.4 сек) |
| `WanVideoSampler` | steps | 30–50 шагов |
| `WanVideoSampler` | cfg | 5–7 |
| `VHS_VideoCombine` | fps | Частота кадров (24) |

---

## Советы для лучшего результата

**Для фото (как Flora AI):**
- `ip_adapter_weight = 0.8–1.0` — хорошо сохраняет облик
- Используй `ip-adapter-faceid-plusv2_sdxl` если важно точное лицо
- Промпт: описывай свет, окружение, не внешность (она берётся с референса)

**Для видео (Wan 2.1):**
- Описывай **движение**, не внешность: "walks slowly", "hair swaying in wind"
- 81 кадр @ 24fps = ~3.4 секунды — оптимально
- Для больше вариантов попробуй разные сиды (--seed 123, 456...)
- Если мало VRAM — переключись на модель 1.3B

---

## Требования

- Python 3.10+
- ComfyUI (последняя версия)
- GPU с 10+ GB VRAM (24 GB для 14B модели Wan 2.1)
