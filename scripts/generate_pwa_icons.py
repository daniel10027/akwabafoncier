"""One-off script to generate brand PWA icons (not part of the app runtime)."""
from PIL import Image, ImageDraw

ORANGE = (247, 127, 0, 255)
ORANGE_DARK = (212, 100, 10, 255)
WHITE = (255, 255, 255, 255)
GREEN = (0, 155, 85, 255)


def rounded_square(size, radius_ratio=0.22):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = int(size * radius_ratio)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=ORANGE)
    return img, draw


def draw_icon(size):
    img, draw = rounded_square(size)

    # Subtle darker gradient band at the bottom for depth
    band_h = int(size * 0.28)
    band = Image.new('RGBA', (size, band_h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(band)
    bdraw.rectangle([0, 0, size, band_h], fill=(0, 0, 0, 28))
    img.alpha_composite(band, (0, size - band_h))

    # White location-pin glyph symbolizing a verified parcel
    cx = size / 2
    pin_w = size * 0.34
    top = size * 0.20
    bottom = size * 0.72
    draw = ImageDraw.Draw(img)

    # Pin body (teardrop): circle + triangle
    circle_r = pin_w / 2
    circle_cy = top + circle_r
    draw.ellipse(
        [cx - circle_r, circle_cy - circle_r, cx + circle_r, circle_cy + circle_r],
        fill=WHITE,
    )
    draw.polygon(
        [
            (cx - circle_r * 0.82, circle_cy + circle_r * 0.55),
            (cx + circle_r * 0.82, circle_cy + circle_r * 0.55),
            (cx, bottom),
        ],
        fill=WHITE,
    )

    # Inner dot (green, representing "verified")
    inner_r = circle_r * 0.42
    draw.ellipse(
        [cx - inner_r, circle_cy - inner_r, cx + inner_r, circle_cy + inner_r],
        fill=GREEN,
    )

    # Small checkmark inside the dot
    ck_w = inner_r * 1.15
    draw.line(
        [
            (cx - ck_w * 0.5, circle_cy),
            (cx - ck_w * 0.12, circle_cy + ck_w * 0.42),
            (cx + ck_w * 0.55, circle_cy - ck_w * 0.42),
        ],
        fill=WHITE,
        width=max(2, int(size * 0.018)),
        joint='curve',
    )

    # Base line representing land/parcel under the pin
    base_y = size * 0.84
    draw.rounded_rectangle(
        [size * 0.24, base_y, size * 0.76, base_y + size * 0.045],
        radius=size * 0.02,
        fill=(255, 255, 255, 200),
    )

    return img


for sz in (192, 512):
    icon = draw_icon(sz)
    icon.save(f'static/img/icon-{sz}.png')

# Maskable variant (icon-512-maskable.png) with extra safe-area padding
def draw_maskable(size):
    base = draw_icon(int(size * 0.7))
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=0, fill=ORANGE)
    offset = (size - base.width) // 2
    canvas.alpha_composite(base, (offset, offset))
    return canvas

maskable = draw_maskable(512)
maskable.save('static/img/icon-512-maskable.png')

# Apple touch icon (180x180, no transparency, solid background required)
apple = draw_icon(180).convert('RGB')
apple.save('static/img/apple-touch-icon.png')

print("Icons generated.")
