# Study Library — static site

A self-contained set of HTML study guides + a library landing page (`index.html`). No code from
`daily-review/` is included — just the rendered guides. Everything is plain HTML/CSS/JS (web fonts
load from Google Fonts), so it hosts anywhere with **zero build step**.

```
study-site/
  index.html            # the library landing page (links to each guide)
  guides/
    vm-paging.html       # LtRAM OS · Lesson 1 — Virtual Memory & the Page-Table Walk
    arom.html            # AROM — The Kernel's Write (LtRAM explainer)
    ucp.html             # Utility-Based Cache Partitioning (paper field guide)
    college-kr.html      # 가성비 미국 유학 가이드 (Korean)
```

---

## Option A — Netlify Drop (easiest, ~30 seconds, no account, no terminal)

1. On any computer, open **https://app.netlify.com/drop** in a browser.
2. Drag the whole **`study-site`** folder onto the page.
3. It uploads and gives you a public URL like `https://sunny-otter-12ab34.netlify.app`.
   - That URL is your library. Direct guide links also work, e.g. `…/guides/ucp.html`.
4. **On your phone:** open that URL, then "Add to Home Screen" so it's one tap.
5. *(Optional)* Make a free Netlify account to keep the site, rename it, or update it later.
   **To update:** just drag the folder onto the Drop page again.

That's it — this is the recommended path.

---

## Option B — GitHub Pages (free, a stable URL, needs a GitHub account + git)

From a terminal in this `study-site` folder:

```bash
git init
git add -A
git commit -m "Study library"
# create an EMPTY public repo on github.com first (e.g. "study-guides"), then:
git remote add origin https://github.com/<your-username>/study-guides.git
git branch -M main
git push -u origin main
```

Then on GitHub: **repo → Settings → Pages → Source: `main` / `(root)` → Save.**
Your site appears at `https://<your-username>.github.io/study-guides/` within a minute or two.

**To update:** copy a new guide into `guides/`, add a card in `index.html`, then
`git add -A && git commit -m "update" && git push`.

---

## Adding a new guide later
1. Copy the guide's `study-guide.html` into `guides/` with a short name (e.g. `guides/foo.html`).
2. Add an `<a class="cardlink" href="guides/foo.html">…</a>` card block in `index.html`
   (copy an existing one and edit the title/description/tags).
3. Re-deploy (drag the folder again for Netlify, or `git push` for Pages).

## Notes
- **Public.** Anyone with the URL can read these. They contain nothing sensitive (a published-paper
  explainer, general college advice, general OS/kernel concepts) — no proprietary code.
- The `guides/` files are **copies**. Editing the originals under `daily-review/…/sessions/` does
  not update the site until you re-copy them here and re-deploy.
