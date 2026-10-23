# Deploy to Vercel (always online, no PC needed)

Vercel can't keep a SQLite file, so the app uses a free hosted Postgres.

## 1. Free database (Neon)
1. Sign up at https://neon.tech -> create a project.
2. Copy the **pooled connection string** (looks like `postgresql://...neon.tech/neondb?sslmode=require`).

## 2. Create tables + Manager account (run once, on your PC)
```bash
pip install -r requirements.txt
# Windows PowerShell:  $env:DATABASE_URL="<your neon string>"
export DATABASE_URL="<your neon string>"
python manage.py migrate
python manage.py createsuperuser     # your Manager login
python manage.py seed_categories
```

## 3. Push to GitHub
```bash
git init && git add . && git commit -m "StockManager"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

## 4. Vercel
1. https://vercel.com/new -> import the repo (Framework: Other).
2. Environment Variables:
   - `DATABASE_URL` = your Neon string
   - `DJANGO_SECRET_KEY` = long random string (`python -c "import secrets;print(secrets.token_urlsafe(60))"`)
   - `DJANGO_DEBUG` = `False`
   - `CSRF_EXTRA_ORIGINS` = `https://your-custom-domain` (only if you add one)
3. Deploy. Link it from your portfolio.

Notifications are computed on the server per request and the page polls every 30s,
so they work on Vercel; sound/vibration play while the site is open in a browser.
