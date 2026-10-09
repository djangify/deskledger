# Contributing to DeskLedger

Thanks for helping. DeskLedger is open source under the
[MIT License](LICENSE). By sending a contribution you agree
that it can be distributed under that same licence.

## Scope

DeskLedger is a **local, single-user, Windows-only** bookkeeping tool: one copy, one
person, one business. That is how it works today. macOS and Linux are not supported and
have not been tested (a port is one of the ideas below). Please do not send changes for
cloud hosting or server deployment.

Several larger ideas are open to contributors (below), including multi-business and
multi-user support and a macOS and Linux version. Open an issue to talk about the approach
before you start on any of them.

## Ideas to work on

Pick one, open an issue to say you are working on it, then send a pull request.

**Larger changes (discuss first)**

1. **Multi-business support.** One person keeps several businesses in one copy, with a way
   to switch between them. Today Income, Expense and Recurring entries belong to a user but
   not to a business, and Categories are shared. It needs a business link on those models, a
   data migration for existing books, and the business filter in the dashboard, reports and
   CSV exports.
2. **Multi-user support.** Several people each keep their own separate books in one copy.
   Today Categories have no user field, so they are shared between users. It needs
   per-user categories (with a migration), a clear way to add users, and tests proving one
   user can never see another user's data.
3. **International tax dates.** Desk Ledger can show amounts in £, € or $, but that only
   changes the symbol. The tax year (6 April to 5 April) and the quarters that follow it are
   fixed in `bookkeeping/utils.py` (`get_tax_year_from_date`, `get_tax_year_bounds`) and used
   by the income, expense, export and report views, the tax year switcher and the dashboard.
   Quarters are stored on each income and expense record when it is saved. A setting for the
   tax year start date, with quarters to match, would make Desk Ledger usable outside the UK.
   It needs a way to recalculate the stored quarters for existing records, tests for dates
   either side of the year boundary, and the hardcoded £ in the VAT check message in
   `bookkeeping/models.py` to follow the chosen currency.
4. **A macOS and Linux version.** Desk Ledger only runs on Windows today, and nothing has
   been tested on a Mac or Linux. A port would need:
   - Start scripts to replace the Windows `.bat` files (`start.bat`, `start_desktop.bat`,
     `build_exe.bat` and `DeskLedger-Reset-Password.bat`).
   - A data folder that is not `%LOCALAPPDATA%`. The location is chosen in
     `deskledger/settings.py` and `desktop.py` (the `platformdirs` library is one way to pick
     the right place on each system). `desktop.py` also opens the first-login file with
     `os.startfile`, which only exists on Windows.
   - File-type detection. `requirements.txt` uses `python-magic-bin`, which is Windows only.
     Mac and Linux need `python-magic` plus the system libmagic library (for example
     `brew install libmagic` or `apt install libmagic1`). Never install both packages
     together.
   - Packaged builds for each system (a `.app` for macOS, a binary or AppImage for Linux) with
     PyInstaller, which has to be run on the system it builds for. PyWebView uses a different
     window backend on each system.
   - Tests, and a GitHub Actions run, on each system.
   - Updating the README and the setup guide, which currently say Windows only.

**Medium**

5. **Build and publish the Windows app automatically.** A GitHub Actions workflow on
   `windows-latest` that runs the tests, runs `build_exe.bat`, zips `dist/DeskLedger` and
   attaches it to a release when a tag is pushed.
6. **Back up now, and restore.** A button in Settings to make a backup straight away, and a
   way to restore one. Today a backup is saved once a day when the app opens, and restoring
   means copying files by hand.
7. **CSV import.** You can export income and expenses as CSV today. Importing a CSV (for
   example a bank statement) with a step to match the columns would help people move over
   from spreadsheets.
8. **A Windows installer and a signed app.** An installer in place of the zip, and a code
   signed `.exe` so Windows SmartScreen does not warn on the first run. Signing needs a
   certificate, so talk to the maintainer first.

**Good first issues**

9. **Tests for the accounts and business apps.** `accounts/tests.py` and
   `business/tests.py` are empty. Tests for the settings page, the change-password link,
   creating and editing a business, and the user-scoped views are welcome.
10. **Screenshots for the README and the setup guide.** The README has one image. Clear
   screenshots of the dashboard, adding an expense with a receipt and the reports would help
   new users.

## Set up

```bash
git clone https://github.com/djangify/deskledger.git
cd deskledger
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py create_default_user   # prints a random password
python manage.py runserver
```

## Before you open a pull request

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

All tests must pass. Add a test for any bug you fix or behaviour you add.
Do not commit your `.env`, your `data/` folder, your virtual environment or any real
financial records.

## Changing the CSS

`static/css/output.css` is generated from `static/src/input.css` with Tailwind:

```bash
npm install
npx @tailwindcss/cli -i static/src/input.css -o static/css/output.css
```

Commit the regenerated `output.css`.
