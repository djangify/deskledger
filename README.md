# DeskLedger

![MTD Bookkeeping Software](https://github.com/djangify/ deskledger/blob/9752bd38249676297c8e1e88fc151dbeccf84538/ deskledger-bookkeeping-dashboard.png)

<p align="center">
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  </a>

  <a href="https://tailwindcss.com/">
    <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
  </a>

  <img src="https://img.shields.io/badge/Database-SQLite--First-003B57?style=for-the-badge" alt="SQLite First">

  <img src="https://img.shields.io/badge/Runs-Local--First-4B5563?style=for-the-badge" alt="Local First">

  <img src="https://img.shields.io/badge/Desktop-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows Desktop">

</p>

<p align="center">
  <strong>Desk Ledger</strong><br>
  A lightweight, local-first bookkeeping tool for sole professionals and the self-employed.
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#desktop-app-windows">Desktop App</a> •
  <a href="#local-development">Local Development</a> •
  <a href="#documentation">Documentation</a>
</p>

---

## Overview

DeskLedger is a Django-based bookkeeping application designed specifically for a one-personal business - solo professionals and self-employed. It provides a simple, privacy-focused way to track income, expenses, and VAT—all while keeping your data under your complete control.

It is **local-first**: it runs on your own machine as a standalone Windows app, and your books never leave your computer.

**Key Principles:**

- **You own your data** — Everything is stored locally in SQLite
- **Privacy first** — No cloud, no accounts to sign up for, no data sharing
- **Simple and focused** — Built for solo professionals, not enterprise accounting
- **UK tax year aware** — Automatically handles April-to-April tax years and UK dates.

## Features

- **Transaction Management** — Track income and expenses with categorisation
- **VAT Calculations** — Automatic VAT rate application and tracking
- **Quarterly Summaries** — View your finances by tax quarters (Q1-Q4)
- **Tax Year Reports** — Year-to-date profit/loss statements
- **CSV Exports** — Export all your data when needed
- **Receipt Storage** — Attach receipt images to expenses
- **Recurring Entries** — Set up automatic monthly transactions
- **Multi-Currency Display** — Each user can choose their preferred symbol (£, €, or $) in Settings
- **Native Desktop App** — Run as a standalone Windows app in its own window — no browser required (see [Desktop App](#desktop-app-windows))
- **Daily Backups** — Automatic daily database backups, saved alongside your data in `data/db/backups/`
- **Multi-user Ready** — Support for multiple user accounts

### Admin Interface

DeskLedger uses [Adminita](https://github.com/djangify/adminita), a clean and modern Django admin theme. Adminita provides a new look for the Django admin panel with improved typography, spacing, and visual hierarchy.

## Quick Start

DeskLedger is designed to run on your own machine. There are two ways to run it:

| Method | Best For | Difficulty |
|--------|----------|------------|
| [Desktop App (Windows)](#desktop-app-windows) | A standalone Windows app for non-technical users — no Python needed | Easy |
| [Local Development](#local-development) | Running from source, testing, or personal use on your machine | Easy |

> Prefer to run DeskLedger on a server instead? That's not covered here by design — DeskLedger is built for local, single-user use. If you want to host it yourself, it's an ordinary Django app and you can wire up your own server setup.

---

## Local Development

Run DeskLedger locally on your machine from source. This runs the Django development server, which is perfect for single-user use.

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/djangify/ deskledger.git
   cd  deskledger
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv

   # On Windows:
   .venv\Scripts\activate

   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` if you want to change any defaults (see [Configuration](#configuration) below). For local use the defaults are fine.

5. **Initialize the database**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser account**

   ```bash
   python manage.py createsuperuser
   ```

   Or create a default demo user:

   ```bash
   python manage.py create_default_user
   ```

   This creates a user with email `demo@example.com` and password `demo123`.

7. **Collect static files**

   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run the development server**

   ```bash
   python manage.py runserver
   ```

9. **Access the application**

   Open your browser and navigate to:
   - **Application:** http://127.0.0.1:8000
   - **Admin Panel:** http://127.0.0.1:8000/admin

### Running on a Different Port

```bash
python manage.py runserver 0.0.0.0:8080
```

### Accessing from Other Devices on Your Network

To access DeskLedger from other devices on your own network (phone, tablet, another computer):

1. Add your local IP to `ALLOWED_HOSTS` in `.env`:
   ```
   ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
   ```

2. Run the server binding to all interfaces:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

3. Access from other devices at `http://192.168.1.100:8000` (use your actual local IP).

---

## Desktop App (Windows)

DeskLedger can run as a true **local-first desktop application** — it opens in its own native window (no browser, no address bar) and can be packaged into a single standalone `.exe` that needs **no Python installation** on the end user's machine.

Under the hood this uses [PyWebView](https://pywebview.flowrl.com/) for the window, [waitress](https://docs.pylonsproject.org/projects/waitress/) as the local server, and [PyInstaller](https://pyinstaller.org/) to bundle everything (Python, Django, your code) into one folder.

### Run it in its own window (for yourself)

Double-click **`start_desktop.bat`**, or from a terminal:

```bash
python desktop.py
```

This sets up the virtual environment, applies migrations, starts the local server, and opens DeskLedger in a desktop window. The first launch also creates the default login (see below).

### Build a standalone `.exe` (to share with others)

Double-click **`build_exe.bat`**, or run it from a terminal:

```bash
build_exe.bat
```

This installs dependencies and PyInstaller, collects static files, and runs PyInstaller using ` deskledger.spec`. When it finishes you'll have:

```
dist/DeskLedger/DeskLedger.exe
```

**To distribute:** zip the **entire `dist/DeskLedger` folder** and share the zip. The `.exe` needs the `_internal` folder beside it, so don't send the `.exe` on its own. End users just unzip and double-click `DeskLedger.exe` — no Python, no setup. A simple, non-technical guide for them is in **[HOW-TO-OPEN- deskledger.md](HOW-TO-OPEN- deskledger.md)**.

### Default login

The desktop app creates a default account on first launch:

- **Email:** `demo@example.com`
- **Password:** `demo123`

(Override these by setting `DEFAULT_USER_EMAIL` / `DEFAULT_USER_PASSWORD` in `.env` before building. You can change the password later in the app's Settings.)

### Where your data lives

| Run mode | Database & receipts location |
|----------|------------------------------|
| `start_desktop.bat` / `python desktop.py` (dev) | `data/` inside the project folder |
| Packaged `DeskLedger.exe` | `%LOCALAPPDATA%\DeskLedger` (persists across app updates) |

The packaged app keeps user data **outside** the program folder so it survives reinstalls and isn't lost when you replace the app with a new build.

### Requirements & notes

- **Windows 10 or 11.** The build is Windows-only — it must be built *on* Windows, and the resulting `.exe` runs only on Windows. A Mac build would need to be produced on a Mac.
- PyWebView uses the **WebView2** runtime, which ships with Windows 11 and most updated Windows 10 machines. On a rare PC without it, Windows offers it as a free one-time download.
- New apps trigger a **"Windows protected your PC"** SmartScreen warning. This is normal for unsigned indie software — click **More info → Run anyway**. This is covered in the end-user guide.
- The app icon is read from `static/images/ deskledger.ico` (referenced by ` deskledger.spec`). Replace that file to change the icon.
- If the build fails mentioning `magic` / `libmagic`, run `pip install python-magic-bin` and rebuild. To see detailed errors, set `console=True` in ` deskledger.spec`.

---

## Configuration

### Environment Variables

DeskLedger reads its configuration from a `.env` file in the project root. For local, single-user use the defaults are fine and you can skip this entirely.

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `True` |
| `SECRET_KEY` | Django secret key | `change-me-in-production` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `ENCRYPTION_KEY` | Fernet key used to encrypt sensitive fields (e.g. your OCR API key). Optional — if unset, a per-install key is generated and stored next to your data. | *(auto-generated)* |

#### Example `.env`

```env
DEBUG=True
SECRET_KEY=a-long-random-string
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Project Structure

```
 deskledger/
├── accounts/           # User authentication and management
├── bookkeeping/        # Core transaction tracking
│   ├── models.py       # Income, Expense, Category, RecurringEntry
│   ├── views/          # Transaction and report views
│   └── utils.py        # Tax year utilities
├── business/           # Business profile management
├──  deskledger/             # Django project settings
│   ├── settings.py     # Application configuration
│   ├── urls.py         # URL routing
│   └── views.py        # Dashboard and home views
├── templates/          # HTML templates
├── static/             # CSS, JS, images (incl. app icon  deskledger.ico)
├── data/               # SQLite database and media (gitignored)
│   ├── db/             # Database files (and daily backups under db/backups/)
│   └── media/          # Uploaded receipts
├── desktop.py          # Desktop app launcher (PyWebView + waitress)
├──  deskledger.spec         # PyInstaller build config for the .exe
├── start_desktop.bat   # Run the app in its own window (dev)
├── build_exe.bat       # Build the standalone Windows .exe
├── HOW-TO-OPEN- deskledger.md  # Plain-language guide for end users
├── start.bat           # Run via the browser (Django dev server)
├── requirements.txt    # Python dependencies
└── manage.py           # Django management script
```

---

## Usage Guide

### First-Time Setup

1. **Log in** with your created account
2. **Create a Business** — Navigate to Business → Add Business
3. **Set your tax year** — The system defaults to the current UK tax year
4. **Start tracking** — Add income and expenses from the dashboard

### Personalising Reports

When you generate printable reports, DeskLedger displays your email address by default. To include your full name and business name on reports:

1. Go to **Admin Panel** (`/admin`)
2. Navigate to **Users** and select your account
3. Add your **First Name** and **Last Name**
4. Ensure you've created a **Business** with your business name

Reports will then display your name, email, and business name in the header — useful for professional record-keeping.

### Adding Transactions

**Income:**
- Navigate to Bookkeeping → Add Income
- Enter date, description, amount, and category
- Optionally add client name and invoice number

**Expenses:**
- Navigate to Bookkeeping → Add Expense
- Enter date, description, amount, and category
- Set VAT rate (0%, 5%, or 20%)
- Upload receipt image (optional)

### Reports

Access reports from the Dashboard:

- **Quarterly Summary** — View income, expenses, and profit by quarter
- **Category Breakdown** — See spending by category
- **CSV Export** — Download data for your accountant

### Tax Years

DeskLedger follows the UK tax year (6 April – 5 April):

- **Q1:** April – June
- **Q2:** July – September
- **Q3:** October – December
- **Q4:** January – March

Switch between tax years using the dropdown in the navigation bar.

---

## API Reference

DeskLedger does not currently expose a public API. All interactions are through the web interface.

---

## Troubleshooting

### Common Issues

**Static files not loading**
- Run `python manage.py collectstatic --noinput`
- Check that WhiteNoise is properly configured (it is by default)

**Database locked errors**
- SQLite can occasionally have issues with concurrent writes; DeskLedger is designed for single-user use, so this should be rare.

**Permission denied on data directory**
- Ensure the application user has write access to the `data/` directory

### Getting Help

- **Issues:** https://github.com/djangify/ deskledger/issues

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Clone your fork
3. Create a virtual environment and install dependencies
4. Create a branch for your feature
5. Make your changes
6. Run tests (when available)
7. Submit a pull request

---

## License

This project is licensed under the MIT License. See the [LICENSE](license.md) file for details.

---

## Acknowledgements

Built with:

- [Django](https://www.djangoproject.com/) — The web framework
- [django-allauth](https://django-allauth.readthedocs.io/) — Authentication
- [WhiteNoise](http://whitenoise.evans.io/) — Static file serving
- [waitress](https://docs.pylonsproject.org/projects/waitress/) — WSGI server (desktop app)
- [PyWebView](https://pywebview.flowrl.com/) — Native desktop window
- [PyInstaller](https://pyinstaller.org/) — Packaging the standalone `.exe`
- [Tailwind CSS](https://tailwindcss.com/) — Styling

---
 # DISCLAIMER

DeskLedger is provided "as is" without warranty of any kind. If you choose to run this software, you do so at your own risk. The developer accepts no responsibility for data loss, inaccuracies, or any issues arising from its use. Always maintain your own backups and verify calculations independently.

<p align="center">
  Made for solo professionals and the self employed<br>
  <a href="https://todiane.com/blog/introducing- deskledger/">Introducing Desk Ledger</a>
</p>


Maintained by [Diane Corriette](https://github.com/todiane)
