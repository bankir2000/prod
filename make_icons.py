"""Generate PWA icons (jerrycan on dark green) in the app's night-theme palette."""
from pathlib import Path

from PIL import Image, ImageDraw

BG = (13, 15, 13)
BG_GRAD = (26, 40, 26)
ACCENT = (125, 212, 68)
ACCENT_DARK = (74, 138, 56)
OUT_DIR = Path(__file__).parent / "icons"
MASTER = 1024
SS = 2  # supersampling factor for smooth edges


def draw_jerrycan(draw: ImageDraw.ImageDraw, size: int, scale: float) -> None:
    """Draw the jerrycan centered on the canvas.

    Args:
        draw: Pillow drawing context.
        size: Canvas side in pixels.
        scale: 1.0 fills ~70% of the canvas; lower values leave a safe zone.
    """
    unit = size * 0.70 * scale / 100
    cx, cy = size / 2, size / 2 + 13 * unit

    def pt(x: float, y: float) -> tuple[float, float]:
        return cx + x * unit, cy + y * unit

    # Body
    draw.rounded_rectangle([*pt(-38, -52), *pt(38, 44)], radius=9 * unit, fill=ACCENT)
    # Spout and cap
    draw.rectangle([*pt(-34, -66), *pt(-20, -50)], fill=ACCENT)
    draw.rectangle([*pt(-37, -71), *pt(-17, -64)], fill=ACCENT_DARK)
    # Handle cut-out (dark window)
    draw.rounded_rectangle([*pt(-6, -43), *pt(26, -29)], radius=5 * unit, fill=BG)
    # Embossed X and frame on the body
    w = max(2, int(5 * unit))
    draw.line([pt(-26, -17), pt(26, 35)], fill=ACCENT_DARK, width=w)
    draw.line([pt(26, -17), pt(-26, 35)], fill=ACCENT_DARK, width=w)
    draw.rounded_rectangle(
        [*pt(-28, -19), *pt(28, 37)], radius=4 * unit, outline=ACCENT_DARK, width=w
    )


def render(size: int, scale: float, rounded: bool) -> Image.Image:
    """Render one icon at the given size.

    Args:
        size: Output side in pixels.
        scale: Content scale (use ~0.78 for maskable icons).
        rounded: Whether to round the background corners (regular icons only).
    """
    big = size * SS
    img = Image.new("RGBA", (big, big), BG)
    d = ImageDraw.Draw(img)
    # Subtle vertical gradient
    for y in range(big):
        t = y / big
        color = tuple(int(BG[i] + (BG_GRAD[i] - BG[i]) * t) for i in range(3))
        d.line([(0, y), (big, y)], fill=color)
    draw_jerrycan(d, big, scale)
    if rounded:
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, big - 1, big - 1], radius=int(big * 0.22), fill=255
        )
        img.putalpha(mask)
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for size in (192, 512):
        render(size, 1.0, rounded=True).save(OUT_DIR / f"icon-{size}.png")
        render(size, 0.78, rounded=False).save(OUT_DIR / f"maskable-{size}.png")
    render(180, 0.9, rounded=False).convert("RGB").save(OUT_DIR / "apple-touch-icon.png")
    render(48, 1.0, rounded=True).save(OUT_DIR / "favicon-48.png")
    render(256, 1.0, rounded=True).save(
        OUT_DIR / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)]
    )


if __name__ == "__main__":
    main()
