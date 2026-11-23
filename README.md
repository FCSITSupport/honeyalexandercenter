# Honey Alexander Center

Single-page website for the Honey Alexander Center, 2400 Clifton Ave, Nashville, TN: home to Family & Children's Service and Retrieving Independence.

- `index.html` is the site. GitHub Pages serves it from the repository root.
- `assets/` holds the building photo.
- `dist/` holds a self-contained build: `dist/index.html` (photo and fonts embedded) and `dist/worker.js` for a Cloudflare Worker.

To rebuild `dist/` after editing `index.html` (needs internet to fetch the fonts):

```bash
python3 -I flatten.py . fonts.css
```
