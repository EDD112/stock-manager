# StockManager v3 — Inventory Management System

A complete Django-based inventory management system with role-based access control, real-time notifications with sound and vibration alerts, user account management, and dark mode support.

---

## Table of Contents

1. [Features](#features)
2. [Role Permissions](#role-permissions)
3. [Requirements](#requirements)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [Running the Server](#running-the-server)
6. [How the System Works](#how-the-system-works)
7. [URL Map](#url-map)
8. [Troubleshooting](#troubleshooting)

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Role-Based Access** | Manager and Stockman roles with separated permissions |
| 2 | **User Management** | Managers can create, activate/deactivate, and reset passwords for Stockman accounts |
| 3 | **Access Restriction** | Stockman cannot access Activity Logs or Login Activity |
| 4 | **Notification Bell** | Real-time bell icon with badge count for expired, low stock, out of stock, and expiring products |
| 5 | **Sound & Vibration Alerts** | Plays a notification sound and vibrates the device when new inventory alerts are detected (requires HTTPS) |
| 6 | **Per-User Notifications** | Each user has independent read/dismiss states — clearing or reading notifications only affects your own account |
| 7 | **Clear All Notifications** | Both Manager and Stockman can clear their own notifications via a confirmation modal |
| 8 | **Dashboard Popup Alerts** | Popup modal appears on the dashboard when inventory conditions need attention (per-user, re-appears for new conditions) |
| 9 | **Dark Mode** | Toggle in the top bar — persists across sessions |
| 10 | **Export Reports** | Excel (.xlsx) and PDF (.pdf) exports for inventory and expiration data |
| 11 | **Charts** | Bar chart (stock per category) and Pie/Doughnut chart (stock status) on the dashboard |
| 12 | **Soft Delete** | Deactivate products/categories instead of permanently deleting — can be restored anytime |
| 13 | **Login Tracking** | Records who logged in, when, from which IP, and user agent |
| 14 | **Mobile Responsive** | Full-screen notification panel on mobile, responsive sidebar, touch-friendly UI |

---

## Role Permissions

| Feature | Manager | Stockman |
|---------|---------|----------|
| Dashboard | ✅ | ✅ |
| Products / Categories / Batches | ✅ | ✅ |
| Expiration Tracker | ✅ | ✅ |
| Notification Bell (view, read, clear) | ✅ | ✅ (inventory only) |
| Sound & Vibration Alerts | ✅ | ✅ |
| Activity Logs | ✅ | ❌ |
| Login Activity | ✅ | ❌ |
| Manage Users (create/deactivate) | ✅ | ❌ |

---

## Requirements

- **Python** 3.10 or higher (tested up to Python 3.14)
- **pip** (Python package manager)
- A modern web browser (Chrome, Edge, Firefox)
- For mobile sound/vibration: HTTPS (see "Running with HTTPS" below)

### Python Packages (auto-installed)

- Django 4.2
- django-jazzmin (admin panel theme)
- cryptography (SSL certificate generation for HTTPS)
- openpyxl (Excel export)
- reportlab (PDF export)

---

## Step-by-Step Setup

### Step 1: Download and Extract

Download the ZIP file and extract it. You should see a folder called `stock_manager_out` containing `manage.py` and other project files.

### Step 2: Open a Terminal

Open **PowerShell** (Windows), **Terminal** (Mac/Linux), and navigate to the project folder:

```bash
cd path/to/stock_manager_out
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Django, django-jazzmin, cryptography, openpyxl, and reportlab.

### Step 6: Run Database Migrations

```bash
python manage.py makemigrations accounts activity login_tracker
python manage.py migrate
```

This creates the database tables for users, notifications, products, categories, activity logs, etc.

### Step 7: Create a Superuser (Manager Account)

```bash
python manage.py createsuperuser
```

Enter a username, email (optional), and password when prompted. This account is automatically assigned the **Manager** role with full system access.

### Step 8: Assign Profiles to Existing Users (Optional)

If you're upgrading from an older version:

```bash
python manage.py assign_profiles
```

### Step 9: Seed Default Category Types (Optional)

```bash
bash setup.sh
```

Or if you only want the category types without re-running the full setup, use the Django shell.

### Alternative: Run Setup Script (Does Steps 5–9 Automatically)

Instead of doing steps 5–9 manually, you can run:

```bash
bash setup.sh
```

This single command installs dependencies, runs migrations, creates a superuser, assigns profiles, and seeds default category types.

---

## Running the Server

### Option A: Standard HTTP (PC Only)

Best for development on your PC. No sound/vibration on mobile.

```bash
python manage.py runserver 0.0.0.0:8000
```

Open in your browser: **http://127.0.0.1:8000/**

### Option B: HTTPS with `runsecure` (PC + Mobile with Sound & Vibration)

This enables HTTPS so that notification sounds and vibration work on your phone.

**Step 1: Allow port 8443 through your firewall (Windows, run as Administrator once):**

```powershell
netsh advfirewall firewall add rule name="StockManager HTTPS" dir=in action=allow protocol=TCP localport=8443
```

Also allow port 8000 if not already done:

```powershell
netsh advfirewall firewall add rule name="StockManager HTTP" dir=in action=allow protocol=TCP localport=8000
```

**Step 2: Find your PC's local IP address:**

```powershell
ipconfig
```

Look for **IPv4 Address** under your Wi-Fi adapter (e.g., `192.168.1.22`).

**Step 3: Start the HTTPS server:**

```bash
python manage.py runsecure
```

This generates a self-signed SSL certificate (`cert.pem` and `key.pem`) automatically on first run.

**Step 4: Open on your phone:**

On your phone's browser, go to: **https://192.168.1.22:8443/** (replace with your PC's IP).

Chrome will show a certificate warning — tap **Advanced** → **Proceed to site**. This is safe because it's your own self-signed certificate on your local network.

**Step 5: Tap anywhere on the page once** to unlock audio (required by mobile browsers). After that, sounds and vibration will work automatically when new notifications appear.

### Important Notes for Mobile

- Your phone and PC must be on the **same Wi-Fi network**
- Sound and vibration **only work while the browser tab is open** — they stop if you close the browser or switch apps
- Vibration works on **Android Chrome** — iPhones do not support the Vibration API, but sound will still work
- The system checks for new notifications every **30 seconds**

---

## How the System Works

### Roles

- **Manager**: Created via `createsuperuser` command. Has full access to all features including Activity Logs, Login Activity, and User Management.
- **Stockman**: Created inside the system by a Manager (via the "Manage Users" page). Limited to Dashboard, Inventory, and Expiration Tracker.

### Creating Stockman Accounts

1. Log in as a Manager
2. Go to the sidebar → **Manage Users**
3. Click **Create Stockman**
4. Fill in username, password, and optional name
5. The account is created with the Stockman role

### Notification System

The system automatically generates notifications for:
- **Expired products** — batches past their expiry date
- **Expiring soon** — batches expiring within 7 days
- **Low stock** — products with low stock status
- **Out of stock** — products with zero quantity

**How notifications behave:**
- A **bell icon** in the top bar shows the number of unread notifications
- Click/tap the bell to see the notification list
- Tap a notification to mark it as **read** (per-user — doesn't affect other users)
- Tap **Mark all read** to mark all as read (per-user only)
- Tap **Clear all** to dismiss all notifications from your view (per-user — other users still see theirs)
- Cleared notifications stay dismissed even though the inventory condition still exists
- New notifications for **new** conditions will still appear

**Sound and vibration alerts** (HTTPS only):
- When new unread notifications are detected during the 30-second polling cycle, the system plays a beep sound and vibrates the device
- On first page load, if there are existing unread notifications, it alerts after your first tap
- The bell icon briefly flashes red when an alert triggers

### Dashboard Popup

When you open the dashboard, a popup modal appears if there are inventory conditions that need attention (expired, low stock, out of stock). This popup:
- Is **per-user** — one user dismissing it doesn't affect another
- **Re-appears** when new conditions are detected (it tracks a hash of the current alerts)

### Dark Mode

Click the moon/sun icon in the top bar to toggle dark mode. The preference is saved in your browser's localStorage.

---

## URL Map

| URL | Page | Access |
|-----|------|--------|
| `/` | Dashboard (charts + popup alerts) | All |
| `/inventory/` | Products (with export + deactivate) | All |
| `/inventory/inactive/` | Inactive/Deactivated Products | All |
| `/inventory/categories/` | Categories | All |
| `/inventory/category-types/` | Category Types | All |
| `/inventory/inactive-categories/` | Inactive Categories | All |
| `/activity/` | Activity Logs | Manager only |
| `/expiration/` | Expiration Tracker (with export) | All |
| `/login-activity/` | Login Activity Log | Manager only |
| `/accounts/manage-users/` | User Management | Manager only |
| `/accounts/create-stockman/` | Create Stockman Account | Manager only |
| `/accounts/notifications/` | Notification API (JSON) | All (filtered by role) |
| `/accounts/login/` | Login Page | Public |
| `/admin/` | Admin Panel (Jazzmin dark theme) | Superuser |

---

## Troubleshooting

### "CSRF verification failed" when logging in on mobile

This happens if your PC's IP address isn't trusted by Django. The system auto-trusts all `192.168.0.x` and `192.168.1.x` addresses on port 8443. If your network uses a different subnet (e.g., `192.168.2.x`), add this line to `inventory_system/settings.py` inside the `CSRF_TRUSTED_ORIGINS` list:

```python
CSRF_TRUSTED_ORIGINS.append('https://192.168.2.22:8443')
```

### No sound or vibration on mobile

- Make sure you're using `https://` (not `http://`) — run `python manage.py runsecure`
- Tap anywhere on the page at least once to unlock audio
- Check your phone isn't on silent/vibrate-only mode
- Open Chrome DevTools console — you should see `[Notif] Audio unlocked`
- Type `testNotifAlert()` in the console to manually test sound and vibration

### "The directory 'static' does not exist" warning

This is harmless. The system uses CDN links for CSS/JS instead of local static files.

### Phone can't connect to the server

- Ensure your phone and PC are on the **same Wi-Fi network**
- Check Windows Firewall allows ports 8000 and 8443 (see firewall commands above)
- Verify your IP with `ipconfig` — it may have changed

### `ssl.wrap_socket` error

You're using Python 3.12+ which removed the old SSL API. Use `python manage.py runsecure` instead of `django-sslserver` — it's built into this project and works with modern Python.

### Notifications keep coming back after clearing

Make sure you're using the latest version with the `NotificationDismissed` model. Run `python manage.py migrate` to apply the new migration.
