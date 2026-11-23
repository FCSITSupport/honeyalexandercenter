"""Flatten index.html into one self-contained page plus a Cloudflare Worker that serves it.

Usage: python3 -I flatten.py <project_dir> <fonts_css>
"""
import base64, json, re, sys, urllib.request
from pathlib import Path

root = Path(sys.argv[1])
fonts_css = Path(sys.argv[2]).read_text()
html = (root / "index.html").read_text()

# 1. Fonts: keep only the latin @font-face blocks, inline each woff2 as base64.
blocks = re.findall(r"/\* latin \*/\s*(@font-face\s*{[^}]*})", fonts_css)
faces = []
for b in blocks:
    url = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", b).group(1)
    data = urllib.request.urlopen(url, timeout=30).read()
    b64 = base64.b64encode(data).decode()
    faces.append(b.replace(url, f"data:font/woff2;base64,{b64}"))
font_style = "<style>\n" + "\n".join(faces) + "\n</style>"

google = re.compile(
    r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
    r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*'
    r'<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">'
)
assert google.search(html), "Google Fonts links not found"
html = google.sub(lambda _: font_style, html)

# 2. Photo: inline as a data URI.
img = base64.b64encode((root / "assets/honey-alexander-center.jpg").read_bytes()).decode()
assert 'src="assets/honey-alexander-center.jpg"' in html
html = html.replace('src="assets/honey-alexander-center.jpg"', f'src="data:image/jpeg;base64,{img}"')

# 3. og:image needs an absolute URL; the Worker serves the photo at /og.jpg.
html = html.replace('content="assets/honey-alexander-center.jpg"',
                    'content="https://www.honeyalexandercenter.org/og.jpg"')
assert "assets/" not in html, "a relative asset path is left"

out = root / "dist"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(html)

# 4. Worker: serves the page at every path, plus the photo at /og.jpg for link previews.
worker = f"""// Honey Alexander Center: single-page site served from a Cloudflare Worker.
// Generated from index.html; edit that file and regenerate rather than editing this one.
const HTML = {json.dumps(html)};
const OG_JPG = "{img}";

export default {{
  async fetch(request) {{
    const url = new URL(request.url);
    if (request.method !== "GET" && request.method !== "HEAD") {{
      return new Response("Method not allowed", {{ status: 405, headers: {{ Allow: "GET, HEAD" }} }});
    }}
    if (url.pathname === "/og.jpg") {{
      const bytes = Uint8Array.from(atob(OG_JPG), (c) => c.charCodeAt(0));
      return new Response(bytes, {{
        headers: {{ "content-type": "image/jpeg", "cache-control": "public, max-age=86400" }},
      }});
    }}
    if (url.pathname !== "/" && url.pathname !== "/index.html") {{
      return Response.redirect(url.origin + "/", 301);
    }}
    return new Response(HTML, {{
      headers: {{
        "content-type": "text/html; charset=utf-8",
        "cache-control": "public, max-age=3600",
        "x-content-type-options": "nosniff",
        "referrer-policy": "strict-origin-when-cross-origin",
      }},
    }});
  }},
}};
"""
(out / "worker.js").write_text(worker)
print(f"fonts inlined: {len(faces)}")
for f in ("index.html", "worker.js"):
    print(f, (out / f).stat().st_size, "bytes")
