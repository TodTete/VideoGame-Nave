import pygame
try:
    from PIL import Image
    PIL_OK = True
except Exception as e:
    print("[AVISO] Pillow no disponible, los GIF se verán estáticos:", e)
    PIL_OK = False

def load_gif_frames(path, size):
    frames, durations = [], []
    if not PIL_OK:
        try:
            img = pygame.image.load(path).convert_alpha()
            if size: img = pygame.transform.smoothscale(img, size)
            return [img], [120]
        except Exception as e:
            print(f"[AVISO] No se pudo cargar '{path}': {e}")
            surf = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill((5,5,15,255))
            return [surf], [120]

    try:
        im = Image.open(path)
        frame_count = getattr(im, "n_frames", 1)
        canvas_size = im.size
        prev = Image.new("RGBA", canvas_size, (0,0,0,0))

        for i in range(frame_count):
            im.seek(i)
            dur = max(20, int(im.info.get("duration", 100)))
            curr = im.convert("RGBA")
            composed = prev.copy()
            composed.alpha_composite(curr, dest=(0,0))

            disposal = getattr(im, "disposal", im.info.get("disposal", 0))
            next_prev = Image.new("RGBA", canvas_size, (0,0,0,0)) if disposal == 2 else composed

            out_img = composed if not size or size==canvas_size else composed.resize(size, Image.LANCZOS)
            data = out_img.tobytes()
            py_img = pygame.image.fromstring(data, out_img.size, "RGBA").convert_alpha()
            frames.append(py_img); durations.append(dur)
            prev = next_prev

        if not frames:
            raise ValueError("GIF sin frames")
        return frames, durations
    except Exception as e:
        print(f"[AVISO] Error cargando GIF '{path}': {e}")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((5,5,15,255))
        return [surf],[120]
