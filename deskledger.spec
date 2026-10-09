# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for DeskLedger (desktop build).

Build from the project root, with the virtual environment active:

    pyinstaller deskledger.spec

Output: dist/DeskLedger/DeskLedger.exe  (a one-folder app — ship the whole DeskLedger folder)
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = []
binaries = []
hiddenimports = []

# Packages that load templates / static / submodules dynamically and therefore
# need everything bundled (collect_all = data files + binaries + submodules).
# cryptography + cffi carry compiled OpenSSL/cffi binaries that PyInstaller's
# import-following misses; without collect_all the .exe builds but crashes the
# first time it encrypts/decrypts (e.g. the stored OCR API key).
for pkg in ["django", "allauth", "adminita", "whitenoise", "waitress", "webview",
            "cryptography", "cffi", "magic"]:
    p_datas, p_binaries, p_hidden = collect_all(pkg)
    datas += p_datas
    binaries += p_binaries
    hiddenimports += p_hidden

# Local Django apps + the project package. Django imports these by name at
# runtime, so PyInstaller can't discover them by following imports alone.
for pkg in ["deskledger", "accounts", "bookkeeping", "business", "secure_uploads"]:
    hiddenimports += collect_submodules(pkg)

# Project-level templates and static source files.
datas += [
    ("templates", "templates"),
    ("static", "static"),
]

# Modules that DeskLedger references by string name (in settings: MIDDLEWARE,
# context processors, ROOT_URLCONF, included urlconfs). PyInstaller can't see
# these by following imports, so they must be listed explicitly.
hiddenimports += [
    "deskledger.settings",
    "deskledger.urls",
    "deskledger.wsgi",
    "deskledger.views",
    "deskledger.middleware",
    "deskledger.context_processors",
    "secure_uploads",
    "secure_uploads.middleware",
    "accounts.urls",
    "accounts.views",
    "accounts.apps",
    "business.urls",
    "business.apps",
    "bookkeeping.urls",
    "bookkeeping.apps",
]

# Lazily-imported bits that the analyzer can miss.
hiddenimports += [
    "environ",
    "magic",
    "PIL",
    "_cffi_backend",
    "cryptography.fernet",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.humanize.templatetags.humanize",
]


a = Analysis(
    ["desktop.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DeskLedger",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # set True temporarily if you need to see error output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="static/images/deskledger.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DeskLedger",
)
