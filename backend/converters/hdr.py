"""Conversor de HDR (Radiance) e EXR via imageio + OpenCV."""
from pathlib import Path
import numpy as np


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    img_linear = _load_hdr(input_path, input_ext)

    if target_format == "exr":
        _save_exr(img_linear, output_path)
    else:
        # Tone mapping para LDR (Low Dynamic Range)
        img_ldr = _tonemap(img_linear)
        _save_ldr(img_ldr, output_path, target_format)


def _load_hdr(input_path: str, ext: str) -> np.ndarray:
    """Carrega arquivo HDR/EXR e retorna array float32 RGB."""
    if ext == "exr":
        return _load_exr(input_path)
    else:
        # HDR (Radiance RGBE)
        try:
            import imageio.v3 as iio
            img = iio.imread(input_path, plugin="opencv")
            return img.astype(np.float32)
        except Exception:
            import cv2
            img = cv2.imread(input_path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)
            if img is None:
                raise RuntimeError(f"Não foi possível abrir: {input_path}")
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32)


def _load_exr(input_path: str) -> np.ndarray:
    try:
        import cv2
        img = cv2.imread(input_path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)
        if img is None:
            raise RuntimeError("OpenCV não conseguiu abrir o EXR")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img_rgb.astype(np.float32)
    except ImportError:
        pass

    try:
        import imageio.v3 as iio
        img = iio.imread(input_path)
        return np.array(img, dtype=np.float32)
    except Exception as e:
        raise RuntimeError(
            f"EXR requer opencv-python ou imageio[freeimage]: {e}\n"
            "Instale com: pip install opencv-python"
        )


def _tonemap(img_linear: np.ndarray) -> np.ndarray:
    """Reinhard tone mapping simples: expõe para LDR 8-bit."""
    img = img_linear.copy()
    img = img / (img + 1.0)             # Reinhard
    img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
    return img


def _save_ldr(img: np.ndarray, output_path: str, target_format: str) -> None:
    from PIL import Image
    pil_img = Image.fromarray(img)

    fmt_map = {"png": "PNG", "jpg": "JPEG", "jpeg": "JPEG", "tiff": "TIFF"}
    pil_format = fmt_map.get(target_format)
    if pil_format is None:
        raise ValueError(f"Formato de saída não suportado: {target_format}")

    save_kwargs: dict = {}
    if pil_format == "JPEG":
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        save_kwargs["quality"] = 95

    pil_img.save(output_path, format=pil_format, **save_kwargs)


def _save_exr(img_linear: np.ndarray, output_path: str) -> None:
    try:
        import cv2
        img_bgr = cv2.cvtColor(img_linear, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, img_bgr)
        return
    except ImportError:
        pass

    try:
        import imageio.v3 as iio
        iio.imwrite(output_path, img_linear)
    except Exception as e:
        raise RuntimeError(f"EXR export requer opencv-python: {e}")
