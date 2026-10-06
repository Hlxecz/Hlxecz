"""Turn portrait-source.png into an animated monochrome ASCII portrait.

Run locally after installing Pillow: python scripts/generate_portrait.py
"""

from html import escape
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


ROOT = Path(__file__).resolve().parents[1]
COLS, ROWS = 125, 70
CELL_W, CELL_H = 3.2, 6.0
RAMP = " .,:;irsXA253hMHGS#9B&@"
WIDTH, HEIGHT = 440, 490


def main() -> None:
    image = Image.open(ROOT / "portrait-source.png").convert("L")
    image = ImageOps.autocontrast(image, cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(1.35)
    image = image.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    pixels = image.load()

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="ASCII portrait of Hyeung Jun">',
        '<rect width="440" height="490" rx="12" fill="#0d1117"/>',
        '<rect x=".5" y=".5" width="439" height="489" rx="12" fill="none" stroke="#30363d"/>',
        '<path d="M0 30H440M0 459H440" stroke="#30363d"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        svg.append(f'<circle cx="{22 + 16 * i}" cy="15" r="5" fill="{color}"/>')
    svg.append('<text x="220" y="19" text-anchor="middle" fill="#8b949e" font-family="monospace" font-size="12">hlxecz@github: ~/portrait</text>')

    for row in range(ROWS):
        chars = []
        for col in range(COLS):
            value = pixels[col, row] / 255
            index = round((1 - value ** 1.2) * (len(RAMP) - 1))
            chars.append(RAMP[max(0, min(index, len(RAMP) - 1))])
        line = escape("".join(chars))
        top = 36 + row * CELL_H
        delay = row * .055
        svg.append(
            f'<clipPath id="row{row}"><rect x="20" y="{top:.1f}" width="0" height="{CELL_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{COLS * CELL_W:.1f}" begin="{delay:.3f}s" dur=".22s" fill="freeze"/>'
            '</rect></clipPath>'
        )
        svg.append(
            f'<text x="20" y="{top + 5:.1f}" xml:space="preserve" fill="#c9d1d9" font-family="Consolas,monospace" '
            f'font-size="6.1" textLength="{COLS * CELL_W:.1f}" lengthAdjust="spacing" clip-path="url(#row{row})">{line}</text>'
        )
    svg.append('<text x="20" y="478" fill="#8b949e" font-family="monospace" font-size="12">$ whoami <tspan fill="#58a6ff">Hyeung Jun</tspan></text>')
    svg.append('</svg>')
    (ROOT / "portrait.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")
    print("Updated portrait.svg")


if __name__ == "__main__":
    main()
