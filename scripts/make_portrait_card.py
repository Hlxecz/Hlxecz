"""Frame the edited portrait as a self-contained SVG for GitHub README rendering."""

import base64
from pathlib import Path


root = Path(__file__).resolve().parents[1]
photo = base64.b64encode((root / "portrait-photo.png").read_bytes()).decode("ascii")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="440" height="490" viewBox="0 0 440 490" role="img" aria-label="Portrait of Hyeung Jun">
<defs>
  <clipPath id="photo-clip"><rect x="20" y="42" width="400" height="400" rx="8"/></clipPath>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1117" stop-opacity="0"/><stop offset="1" stop-color="#0d1117" stop-opacity=".8"/></linearGradient>
</defs>
<rect width="440" height="490" rx="12" fill="#0d1117"/>
<rect x=".5" y=".5" width="439" height="489" rx="12" fill="none" stroke="#30363d"/>
<path d="M0 30H440M0 459H440" stroke="#30363d"/>
<circle cx="22" cy="15" r="5" fill="#ff5f56"/><circle cx="38" cy="15" r="5" fill="#ffbd2e"/><circle cx="54" cy="15" r="5" fill="#27c93f"/>
<text x="220" y="19" text-anchor="middle" fill="#8b949e" font-family="monospace" font-size="12">hlxecz@github: ~/portrait</text>
<g clip-path="url(#photo-clip)">
  <image x="20" y="42" width="400" height="400" xlink:href="data:image/png;base64,{photo}"/>
  <rect x="20" y="350" width="400" height="92" fill="url(#fade)"/>
  <rect x="20" y="42" width="400" height="2" fill="#58a6ff" opacity="0">
    <animate attributeName="y" from="42" to="440" begin="0s" dur="2.4s" fill="freeze"/>
    <animate attributeName="opacity" values="0;.34;0" begin="0s" dur="2.4s" fill="freeze"/>
  </rect>
</g>
<rect x="20.5" y="42.5" width="399" height="399" rx="8" fill="none" stroke="#58a6ff" stroke-opacity=".4"/>
<text x="35" y="417" fill="#f0f6fc" font-family="Consolas,monospace" font-size="21" font-weight="bold">HYEUNG JUN</text>
<text x="35" y="435" fill="#9fc8ff" font-family="Consolas,monospace" font-size="11">@Hlxecz  /  developer</text>
<text x="20" y="478" fill="#8b949e" font-family="monospace" font-size="12">$ whoami <tspan fill="#58a6ff">Hyeung Jun</tspan></text>
</svg>'''
(root / "portrait-card.svg").write_text(svg, encoding="utf-8")
print("Updated portrait-card.svg")
