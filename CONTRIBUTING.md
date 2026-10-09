# Contributing to DeskLedger

Thanks for helping. DeskLedger is open source under the
[MIT License](LICENSE). By sending a contribution you agree
that it can be distributed under that same licence.

## Scope

DeskLedger is a **local, single-user, Windows-only** bookkeeping tool: one person, one
business, one install. Please do not send changes that add macOS or Linux support,
multi-user or multi-business support, cloud hosting, or server deployment.

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
