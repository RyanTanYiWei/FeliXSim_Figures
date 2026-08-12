from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "Raw_Sources"
OUTPUT_DIR = BASE_DIR / "Final_Figures"


def natural_key(path: Path):
    parts = []
    current = ""
    for char in path.stem:
        if char.isdigit():
            current += char
        else:
            if current:
                parts.append(int(current))
                current = ""
            parts.append(char.lower())
    if current:
        parts.append(int(current))
    return parts


def build_figure(input_folder: Path, output_name: str) -> None:
    files = sorted(
        [
            p for p in input_folder.iterdir()
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
        ],
        key=natural_key,
    )

    if not files:
        raise ValueError(f"No image files found in {input_folder}")

    imgs = [Image.open(f).convert("RGB") for f in files]

    if output_name == "f05":
        left_fraction = 1 / 3
        top_fraction = 1.3 / 10
        bot_fraction = 0.5/ 10
        imgs = [
            img.crop(
                (
                    int(img.width * left_fraction),
                    int(img.height * top_fraction),
                    img.width,
                    int(img.height * (1 - bot_fraction)),
                )
            )
            for img in imgs
        ]

    width = min(img.width for img in imgs)
    height = min(img.height for img in imgs)
    imgs = [img.resize((width, height), Image.Resampling.LANCZOS) for img in imgs]

    labels = ["a", "b", "c", "d"]

    def draw_label(draw: ImageDraw.ImageDraw, panel_x: int, panel_y: int, label: str) -> None:
        font_size = max(24, min(width, height) // 10)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        padding = max(8, font_size // 3)
        radius = max(text_width, text_height) // 2 + padding
        margin = max(12, min(width, height) // 30)
        center_x = panel_x + width - margin - radius
        center_y = panel_y + height - margin - radius
        left = center_x - radius
        top = center_y - radius
        right = center_x + radius
        bottom = center_y + radius
        draw.ellipse((left, top, right, bottom), fill="black", outline="white")
        text_x = center_x - (text_width / 2)
        text_y = center_y - (text_height / 2) - bbox[1]
        draw.text((text_x, text_y), label, fill="white", font=font)

    if len(imgs) == 3:
        canvas = Image.new("RGB", (2 * width, 2 * height), "white")
        canvas.paste(imgs[0], (0, 0))
        canvas.paste(imgs[1], (width, 0))
        canvas.paste(imgs[2], (width // 2, height))
        canvas_draw = ImageDraw.Draw(canvas)
        draw_label(canvas_draw, 0, 0, labels[0])
        draw_label(canvas_draw, width, 0, labels[1])
        draw_label(canvas_draw, width // 2, height, labels[2])
    else:
        while len(imgs) < 4:
            imgs.append(Image.new("RGB", (width, height), "white"))

        canvas = Image.new("RGB", (2 * width, 2 * height), "white")
        canvas.paste(imgs[0], (0, 0))
        canvas.paste(imgs[1], (width, 0))
        canvas.paste(imgs[2], (0, height))
        canvas.paste(imgs[3], (width, height))
        canvas_draw = ImageDraw.Draw(canvas)
        draw_label(canvas_draw, 0, 0, labels[0])
        draw_label(canvas_draw, width, 0, labels[1])
        draw_label(canvas_draw, 0, height, labels[2])
        draw_label(canvas_draw, width, height, labels[3])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    canvas.save(
        OUTPUT_DIR / f"{output_name}.png",
        format="PNG",
        dpi=(600, 600),
    )


build_figure(SOURCE_DIR / "Figure5_InterfaceDesign", "f05")
#build_figure(SOURCE_DIR / "Figure6_InteractiveFeatures", "Figure6") #removed figure
