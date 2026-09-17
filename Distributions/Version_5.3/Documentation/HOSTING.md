# 🌐 Corvus Documentation Website Hosting Guide

This guide explains how to host the official **Corvus Master Documentation Website** (`webpage_corvus`) online for free!

---

## 1. 🐙 GitHub Pages (Recommended - 1-Click Free Hosting)

GitHub Pages provides free, automatic web hosting directly from your Corvus GitHub repository.

### Option A: Hosting from `docs/` folder (Easiest)
1. In your Corvus repository root directory, create a folder named `docs/`.
2. Copy all files from `Documentation/webpage_corvus/` into `docs/`.
3. Push changes to GitHub:
   ```bash
   git add docs/
   git commit -m "Add documentation site to docs/"
   git push origin main
   ```
4. On GitHub, go to your repository **Settings** -> **Pages**.
5. Under **Build and deployment** -> **Branch**, select `main` branch and folder `/docs`.
6. Click **Save**.
7. Your documentation website will be live at:  
   `https://<your-username>.github.io/Corvus-Programming-Language-/`

---

## 2. ▲ Vercel (Instant Global CDN)

1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New** -> **Project**.
3. Import your `Corvus-Programming-Language-` repository.
4. Set **Root Directory** to `Documentation/webpage_corvus` (or `webpage_corvus`).
5. Click **Deploy**.
6. Vercel will provide a free production URL (e.g. `corvus-docs.vercel.app`).

---

## 3. 🌐 Netlify

1. Log in to [netlify.com](https://netlify.com) with GitHub.
2. Click **Add new site** -> **Import an existing project**.
3. Select GitHub and pick the Corvus repository.
4. Set **Base directory** to `Documentation/webpage_corvus`.
5. Set **Publish directory** to `.` (current).
6. Click **Deploy Corvus Docs**.

---

## 4. ⚡ Cloudflare Pages

1. Log in to the Cloudflare Dashboard and select **Workers & Pages**.
2. Click **Create Application** -> **Pages** -> **Connect to Git**.
3. Select your Corvus repository.
4. Set **Build output directory** to `Documentation/webpage_corvus`.
5. Click **Save and Deploy**.
