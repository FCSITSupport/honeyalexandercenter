# Honey Alexander Center

Single-page website for the Honey Alexander Center, 2400 Clifton Ave, Nashville, TN: home to Family & Children's Service, Retrieving Independence and Tennessee Youth Courts.

Live at https://honeyalexandercenter.org

## How it's served

1. GitHub Pages builds this repo's `main` branch to https://fcsitsupport.github.io/honeyalexandercenter/.
2. The Cloudflare Worker `honeywebsite` ([`cloudflare/worker.js`](cloudflare/worker.js)) serves that site at `honeyalexandercenter.org` and `www.honeyalexandercenter.org`.

To change the site, edit `index.html` and push to `main`. The domain shows the change within about 5 minutes (the Pages build plus the Worker's 5-minute cache).

The Worker code is only stored here for reference; Cloudflare does not redeploy it on push. If you edit `cloudflare/worker.js`, deploy it again in the Cloudflare dashboard (Workers & Pages → honeywebsite → Edit code).

## Files

- `index.html`: the site.
- `assets/`: the building photo and the three tenant logos.
- `cloudflare/worker.js`: the deployed Worker.
- `dist/`: an alternative self-contained build. `dist/index.html` has the photo and fonts embedded, and `dist/worker.js` serves it on its own without GitHub. Rebuild it after editing `index.html` (needs internet to fetch the fonts):

```bash
python3 -I flatten.py . fonts.css
```
