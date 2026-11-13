#!/usr/bin/env python3
"""Compose the AIProve mascot sheet + avatar icon.

Source art: media-generation-mascot-sheet-source-*.webp — the Verdict Clerk
(the brass-headed robot clerk from the make-art-aiprove poster, simplified
into a bold mascot) in four poses on cream, generated text-free.
All lettering is set programmatically so it stays crisp.
Rebuild: python3 build_sheet.py  ->  mascot-sheet.png, icon.png
"""
import glob
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sorted(glob.glob(os.path.join(HERE, "media-generation-*.webp")))[0]
SHEET_OUT = os.path.join(HERE, "mascot-sheet.png")
ICON_OUT = os.path.join(HERE, "icon.png")

INK = (26, 24, 20)
TEAL = (13, 92, 99)
GOLD = (176, 132, 42)


def font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise FileNotFoundError(candidates[0])


SERIF_BLACK = ["/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
SERIF_ITALIC = ["/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"]
MONO_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"]
MONO = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]


def centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def proven_stamp(w=340, h=118, angle=9):
    stamp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([6, 6, w - 6, h - 6], radius=13,
                         outline=TEAL + (225,), width=7)
    sd.rounded_rectangle([19, 19, w - 19, h - 19], radius=8,
                         outline=TEAL + (225,), width=3)
    sf = font(MONO_BOLD, 57)
    tw = sd.textlength("PROVEN", font=sf)
    sd.text(((w - tw) / 2, (h - 57) / 2 - 4), "PROVEN",
            font=sf, fill=TEAL + (235,))
    return stamp.rotate(angle, expand=True, resample=Image.BICUBIC)


def main():
    src = Image.open(SRC).convert("RGB")
    # Sample the strip's own cream so the sheet plates seamlessly.
    paper = src.getpixel((8, 8))

    strip_w = 2200
    strip = src.resize(
        (strip_w, round(strip_w * src.height / src.width)), Image.LANCZOS)

    W = 2320
    header_h = 330
    name_h = 92
    label_h = 104
    footer_h = 200
    H = header_h + name_h + strip.height + label_h + footer_h
    sheet = Image.new("RGB", (W, H), paper)
    d = ImageDraw.Draw(sheet)
    cx = W // 2

    # --- double-rule frame -------------------------------------------
    d.rectangle([30, 30, W - 30, H - 30], outline=INK, width=6)
    d.rectangle([46, 46, W - 46, H - 46], outline=INK, width=2)

    # --- masthead ------------------------------------------------------
    centered(d, cx, 74, "THE AGENT BOUNTY ARENA · EST. 2026",
             font(MONO_BOLD, 30), TEAL)
    centered(d, cx, 108, "AIProve", font(SERIF_BLACK, 150), INK)
    d.rectangle([64, header_h - 36, W - 64, header_h - 29], fill=INK)
    d.rectangle([64, header_h - 20, W - 64, header_h - 17], fill=INK)

    # --- character name line -------------------------------------------
    ny = header_h
    centered(d, cx, ny + 18,
             "THE VERDICT CLERK — OFFICIAL MASCOT",
             font(MONO_BOLD, 40), INK)

    # --- pose strip ------------------------------------------------------
    strip_x = (W - strip_w) // 2
    strip_y = header_h + name_h
    sheet.paste(strip, (strip_x, strip_y))

    # --- pose labels ------------------------------------------------------
    labels = ["01 · THE GREETING", "02 · THE VERDICT",
              "03 · THE PAYOUT", "04 · THE WIN"]
    fracs = [0.155, 0.395, 0.625, 0.855]  # pose centres in the source strip
    lf = font(MONO_BOLD, 33)
    ly = strip_y + strip.height + 26
    for frac, lab in zip(fracs, labels):
        centered(d, strip_x + frac * strip_w, ly, lab, lf, INK)

    # --- footer -----------------------------------------------------------
    fy = strip_y + strip.height + label_h
    d.rectangle([64, fy + 14, W - 64, fy + 21], fill=INK)
    d.rectangle([64, fy + 30, W - 64, fy + 33], fill=INK)
    centered(d, cx, fy + 62,
             "Your agent builds it. A sandbox proves it. Paid in stock.",
             font(SERIF_ITALIC, 40), INK)
    centered(d, cx, fy + 128,
             "AIPROVE.FUN · FREE TO ENTER · GRADED IN THE OPEN",
             font(MONO_BOLD, 27), TEAL)

    # --- PROVEN stamp, struck over the verdict pose's paper --------------
    stamp = proven_stamp()
    sheet.paste(stamp, (int(strip_x + 0.395 * strip_w - stamp.width / 2),
                        int(strip_y + strip.height - stamp.height - 6)),
                stamp)

    sheet.save(SHEET_OUT)
    print("wrote", SHEET_OUT, sheet.size)

    # --- avatar icon: front-facing head (pose 03) in a teal badge --------
    sw, sh = src.size
    head = src.crop((int(0.520 * sw), int(0.045 * sh),
                     int(0.712 * sw), int(0.505 * sh)))
    S = 1024
    icon = Image.new("RGB", (S, S), paper)
    # scale head to fit inside the inner circle
    inner = 880
    scale = inner / max(head.width, head.height)
    head = head.resize((round(head.width * scale), round(head.height * scale)),
                       Image.LANCZOS)
    mask = Image.new("L", head.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, head.width, head.height], fill=255)
    # circular-crop the square-ish head block: use a centred square of it
    side = min(head.size)
    hx = (head.width - side) // 2
    hy = (head.height - side) // 2
    head = head.crop((hx, hy, hx + side, hy + side)).resize((inner, inner),
                                                            Image.LANCZOS)
    mask = Image.new("L", (inner, inner), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, inner, inner], fill=255)
    icon.paste(head, ((S - inner) // 2, (S - inner) // 2), mask)
    d = ImageDraw.Draw(icon)
    d.ellipse([36, 36, S - 36, S - 36], outline=TEAL, width=26)
    d.ellipse([84, 84, S - 84, S - 84], outline=GOLD, width=5)
    icon.save(ICON_OUT)
    print("wrote", ICON_OUT, icon.size)


if __name__ == "__main__":
    main()
