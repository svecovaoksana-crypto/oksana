"""
ComfyUI API Client — Flora AI стиль + Wan 2.1 видео
Позволяет запускать воркфлоу через Python без браузера.

Использование:
  python api_client.py --mode image --reference ./моё_фото.jpg --prompt "красивая женщина в парке"
  python api_client.py --mode video --input ./generated_photo.png --prompt "плавно идёт по саду"
"""

import json
import time
import argparse
import base64
import urllib.request
import urllib.parse
from pathlib import Path


COMFYUI_URL = "http://127.0.0.1:8188"


def load_workflow(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def upload_image(image_path: str) -> str:
    """Загружает изображение в ComfyUI и возвращает имя файла."""
    url = f"{COMFYUI_URL}/upload/image"
    image_path = Path(image_path)

    with open(image_path, "rb") as f:
        image_data = f.read()

    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{image_path.name}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + image_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    print(f"  Загружено: {result['name']}")
    return result["name"]


def queue_prompt(workflow: dict) -> str:
    """Отправляет воркфлоу в очередь и возвращает prompt_id."""
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: int = 600) -> dict:
    """Ждёт завершения генерации."""
    print("  Генерация идёт", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            print(" готово!")
            return history[prompt_id]
        print(".", end="", flush=True)
        time.sleep(2)
    raise TimeoutError("Генерация заняла слишком много времени")


def get_output_images(history_entry: dict) -> list[str]:
    """Извлекает пути к готовым файлам."""
    outputs = history_entry.get("outputs", {})
    files = []
    for node_output in outputs.values():
        for key in ("images", "gifs"):
            for item in node_output.get(key, []):
                files.append(item["filename"])
    return files


def set_node_widget(workflow: dict, node_type: str, widget_index: int, value):
    """Меняет значение виджета в ноде по типу."""
    for node in workflow.get("nodes", []):
        if node.get("type") == node_type:
            widgets = node.get("widgets_values", [])
            if widget_index < len(widgets):
                widgets[widget_index] = value
    return workflow


def find_node_by_type(workflow: dict, node_type: str) -> dict | None:
    for node in workflow.get("nodes", []):
        if node.get("type") == node_type:
            return node
    return None


def run_image_generation(
    reference_path: str,
    prompt: str,
    negative_prompt: str = "",
    output_name: str = "flora_style_output",
    width: int = 1024,
    height: int = 1024,
    steps: int = 30,
    cfg: float = 7.0,
    ip_adapter_strength: float = 1.0,
    seed: int = 42,
):
    """Шаг 1: Генерация фото по референсу (Flora AI стиль)"""
    print("\n=== Генерация фото по референсу ===")
    print(f"  Референс: {reference_path}")
    print(f"  Промпт: {prompt[:60]}...")

    workflow = load_workflow("workflows/01_image_from_reference.json")

    # Загружаем референс в ComfyUI
    ref_filename = upload_image(reference_path)

    # Настраиваем референс
    ref_node = find_node_by_type(workflow, "LoadImage")
    if ref_node:
        ref_node["widgets_values"][0] = ref_filename

    # Настраиваем промпты
    text_nodes = [n for n in workflow["nodes"] if n["type"] == "CLIPTextEncode"]
    if len(text_nodes) >= 1 and prompt:
        text_nodes[0]["widgets_values"][0] = prompt
    if len(text_nodes) >= 2 and negative_prompt:
        text_nodes[1]["widgets_values"][0] = negative_prompt

    # IP-Adapter сила
    ipa_node = find_node_by_type(workflow, "IPAdapterAdvanced")
    if ipa_node:
        ipa_node["widgets_values"][0] = ip_adapter_strength

    # Размер
    size_node = find_node_by_type(workflow, "EmptyLatentImage")
    if size_node:
        size_node["widgets_values"][0] = width
        size_node["widgets_values"][1] = height

    # Сэмплер
    sampler_node = find_node_by_type(workflow, "KSampler")
    if sampler_node:
        sampler_node["widgets_values"][0] = seed
        sampler_node["widgets_values"][2] = steps
        sampler_node["widgets_values"][3] = cfg

    # Имя выходного файла
    save_node = find_node_by_type(workflow, "SaveImage")
    if save_node:
        save_node["widgets_values"][0] = output_name

    prompt_id = queue_prompt(workflow)
    print(f"  ID задачи: {prompt_id}")

    history = wait_for_completion(prompt_id)
    files = get_output_images(history)
    print(f"  Готово! Файлы: {files}")
    return files


def run_image_to_video(
    image_path: str,
    prompt: str,
    negative_prompt: str = "blurry, distorted, low quality",
    output_name: str = "wan21_video_output",
    frames: int = 81,
    width: int = 512,
    height: int = 512,
    steps: int = 50,
    cfg: float = 6.0,
    seed: int = 42,
):
    """Шаг 2: Генерация видео из фото (Wan 2.1)"""
    print("\n=== Генерация видео (Wan 2.1) ===")
    print(f"  Входное фото: {image_path}")
    print(f"  Промпт: {prompt[:60]}...")
    print(f"  Кадров: {frames} ({frames/24:.1f} сек при 24fps)")

    workflow = load_workflow("workflows/02_image_to_video_wan21.json")

    # Загружаем входное фото
    img_filename = upload_image(image_path)

    # Настраиваем входное фото
    load_node = find_node_by_type(workflow, "LoadImage")
    if load_node:
        load_node["widgets_values"][0] = img_filename

    # Настраиваем промпты
    text_node = find_node_by_type(workflow, "WanVideoTextEncode")
    if text_node:
        text_node["widgets_values"][0] = prompt
        text_node["widgets_values"][1] = negative_prompt

    # Размер и кадры
    latent_node = find_node_by_type(workflow, "WanVideoImageToVideoLatent")
    if latent_node:
        latent_node["widgets_values"][0] = frames
        latent_node["widgets_values"][1] = width
        latent_node["widgets_values"][2] = height

    # Сэмплер
    sampler_node = find_node_by_type(workflow, "WanVideoSampler")
    if sampler_node:
        sampler_node["widgets_values"][0] = seed
        sampler_node["widgets_values"][2] = steps
        sampler_node["widgets_values"][3] = cfg

    # Видео вывод
    video_node = find_node_by_type(workflow, "VHS_VideoCombine")
    if video_node:
        video_node["widgets_values"][2] = output_name

    prompt_id = queue_prompt(workflow)
    print(f"  ID задачи: {prompt_id}")

    history = wait_for_completion(prompt_id, timeout=900)
    files = get_output_images(history)
    print(f"  Готово! Файлы: {files}")
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Flora AI стиль в ComfyUI: референс-фото → генерация → видео"
    )
    parser.add_argument(
        "--mode",
        choices=["image", "video", "both"],
        default="both",
        help="Что делать: image (фото), video (видео), both (всё сразу)",
    )
    parser.add_argument("--reference", help="Путь к референс-фото (для режима image/both)")
    parser.add_argument("--input", help="Путь к фото для видео (для режима video)")
    parser.add_argument(
        "--prompt",
        default="professional portrait photo, beautiful woman, perfect lighting, sharp focus, 8k uhd, photorealistic",
        help="Текстовый промпт",
    )
    parser.add_argument(
        "--video-prompt",
        default="A beautiful woman walking gracefully, smooth camera movement, cinematic",
        help="Промпт для видео",
    )
    parser.add_argument("--seed", type=int, default=42, help="Сид генерации")
    parser.add_argument("--steps", type=int, default=30, help="Шаги для изображения")
    parser.add_argument("--video-steps", type=int, default=50, help="Шаги для видео")
    parser.add_argument("--width", type=int, default=1024, help="Ширина изображения")
    parser.add_argument("--height", type=int, default=1024, help="Высота изображения")
    parser.add_argument("--frames", type=int, default=81, help="Количество кадров видео (81=~3.4 сек)")
    parser.add_argument("--strength", type=float, default=1.0, help="Сила IP-Adapter (0.0-1.5)")
    parser.add_argument("--url", default="http://127.0.0.1:8188", help="URL ComfyUI сервера")

    args = parser.parse_args()

    global COMFYUI_URL
    COMFYUI_URL = args.url

    generated_image = None

    if args.mode in ("image", "both"):
        if not args.reference:
            print("ОШИБКА: укажи --reference путь_к_фото")
            return
        files = run_image_generation(
            reference_path=args.reference,
            prompt=args.prompt,
            width=args.width,
            height=args.height,
            steps=args.steps,
            seed=args.seed,
            ip_adapter_strength=args.strength,
        )
        if files:
            generated_image = files[0]
            print(f"\nФото сохранено: {generated_image}")

    if args.mode == "video":
        input_image = args.input
        if not input_image:
            print("ОШИБКА: укажи --input путь_к_фото")
            return
        files = run_image_to_video(
            image_path=input_image,
            prompt=args.video_prompt,
            frames=args.frames,
            steps=args.video_steps,
            seed=args.seed,
        )
        if files:
            print(f"\nВидео сохранено: {files[0]}")

    elif args.mode == "both" and generated_image:
        # Используем сгенерированное фото как вход для видео
        comfyui_output_dir = Path(COMFYUI_URL.replace("http://", "").split(":")[0])
        files = run_image_to_video(
            image_path=generated_image,
            prompt=args.video_prompt,
            frames=args.frames,
            steps=args.video_steps,
            seed=args.seed,
        )
        if files:
            print(f"\nВидео сохранено: {files[0]}")

    print("\n=== Готово! ===")


if __name__ == "__main__":
    main()
