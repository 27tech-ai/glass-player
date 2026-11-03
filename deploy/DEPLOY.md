# Deploy Glass Player as a website

The whole player is static files — no build step, no server code. The repo root **is** the website root.

## Option A — GitHub Pages (automatic, already wired)

This repo contains `.github/workflows/pages.yml`: every push to `main` republishes the site.

1. Push this repo to GitHub (see "First push" below).
2. Repo → **Settings → Pages** → Source: **GitHub Actions**.
3. Push anything to `main` (or run the workflow manually from the Actions tab).
4. Your site: `https://<your-username>.github.io/<repo-name>/`

`.nojekyll` is included so GitHub serves the files exactly as they are.

## Option B — Cloudflare Pages (fastest global CDN, free)

1. dash.cloudflare.com → **Workers & Pages → Create → Pages → Upload assets** (or connect the GitHub repo).
2. Project name: e.g. `glass-player`. **Build command: (leave empty)**. **Output directory: `/`** (repo root).
3. Deploy. Your site: `https://glass-player.pages.dev` (custom domain can be attached in one click).
4. The included `_headers` file is picked up automatically: fresh HTML/app code on every visit,
   week-long caching for the playback engines and icons, and no Referer leakage of stream URLs.

Both hosts give **HTTPS for free** — required for the PWA/service worker and for "install app" prompts.

## Your own CORS proxy on Cloudflare (recommended — makes more channels play)

Public proxies are slow and often blocked by providers. Your own free Worker fixes that:
follow the 4 steps at the top of [`cors-proxy-worker.js`](./cors-proxy-worker.js) in this folder.
Once set, the player tries your proxy **first** for any channel that direct playback can't reach.

> Note: an HTTPS site cannot load plain-http streams directly (browser mixed-content rule).
> The proxy chain — especially your own Worker — is how the web player works around that.
> (The Capacitor APK build doesn't have this limit: its config allows cleartext.)

## First push (one time)

```bash
cd glass-m3u-player
git init && git add . && git commit -m "Glass Player v7 — final"
gh repo create glass-player --public --source=. --push   # or: create the repo on github.com, then
# git remote add origin https://github.com/<you>/glass-player.git && git push -u origin main
```

After that, updates are just `git add . && git commit -m "update" && git push` —
GitHub Pages republishes automatically, and Cloudflare Pages (if connected to the repo) does too.
