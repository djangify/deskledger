"""
DeskLedger desktop launcher.

Runs the Django app on a local production server (waitress) in a background
thread and displays it inside a native desktop window using PyWebView, so users
get an app window instead of a browser tab.

Run in development:   python desktop.py
Packaged as an .exe:  this file is the PyInstaller entry point (see deskledger.spec)
"""

import os
import socket
import sys
import threading
import time
import urllib.request
from pathlib import Path


def _writable_data_dir() -> Path:
    """Match the DATA_DIR logic in settings.py so we can store a secret key."""
    if getattr(sys, "frozen", False):
        base = (
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or str(Path.home())
        )
        return Path(base) / "DeskLedger"
    return Path(__file__).resolve().parent / "data"


def _ensure_secret_key(data_dir: Path) -> None:
    """
    Make sure a SECRET_KEY is available. In a packaged build there's no .env,
    so we generate one once and persist it in the user's data folder.
    """
    if os.environ.get("SECRET_KEY"):
        return
    if (Path(__file__).resolve().parent / ".env").exists() and not getattr(
        sys, "frozen", False
    ):
        # Dev run with a .env present — let settings read it.
        return
    key_file = data_dir / "secret_key.txt"
    try:
        if key_file.exists():
            os.environ["SECRET_KEY"] = key_file.read_text(encoding="utf-8").strip()
        else:
            from django.core.management.utils import get_random_secret_key

            key = get_random_secret_key()
            data_dir.mkdir(parents=True, exist_ok=True)
            key_file.write_text(key, encoding="utf-8")
            os.environ["SECRET_KEY"] = key
    except Exception:
        # Fall back to settings' built-in default if anything goes wrong.
        pass


def _resource_path(rel: str) -> str:
    """Resolve a bundled resource path (works in dev and in the frozen .exe)."""
    base = getattr(sys, "_MEIPASS", None) or str(Path(__file__).resolve().parent)
    return str(Path(base) / rel)


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_ready(url: str, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status < 500:
                    return True
        except Exception:
            time.sleep(0.25)
    return False


def main() -> None:
    # --- Environment: desktop mode, served locally over http on loopback ---
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "deskledger.settings")
    os.environ["DESKLEDGER_DESKTOP"] = "1"
    # DEBUG=True keeps things simple for a local single-user app: it serves
    # media files and avoids the HTTPS redirect that production mode forces.
    os.environ.setdefault("DEBUG", "True")

    data_dir = _writable_data_dir()
    _ensure_secret_key(data_dir)

    import django

    django.setup()

    # --- Apply any pending database migrations on startup ---
    from django.core.management import call_command

    try:
        call_command("migrate", interactive=False, verbosity=0)
    except Exception as exc:  # pragma: no cover - surfaced to the user
        print(f"Database setup failed: {exc}")

    # First run: create the login with a random password. The packaged app has no
    # console, so the password is saved to first_login.txt in the data folder and
    # that file is opened for the user. Run "DeskLedger.exe --reset-password" to
    # get a new random password if the old one is forgotten.
    note = data_dir / "first_login.txt"
    before = note.stat().st_mtime if note.exists() else None
    reset = "--reset-password" in sys.argv
    try:
        call_command("create_default_user", reset=reset, verbosity=0)
    except Exception as exc:  # pragma: no cover
        print(f"Could not create the default user: {exc}")
    after = note.stat().st_mtime if note.exists() else None
    if after != before and hasattr(os, "startfile"):
        try:
            os.startfile(str(note))  # opens in Notepad
        except OSError:
            pass
    if reset:
        # Nothing else to do: the new password has been shown.
        os._exit(0)

    # --- Start the web server in a background thread ---
    from waitress import serve
    from deskledger.wsgi import application

    port = _find_free_port()
    host = "127.0.0.1"
    url = f"http://{host}:{port}/"

    server_thread = threading.Thread(
        target=lambda: serve(application, host=host, port=port, threads=8),
        daemon=True,
    )
    server_thread.start()

    if not _wait_until_ready(url + "health/", timeout=30):
        print("DeskLedger server did not start in time.")
        # Still try to open the window; it will show an error if truly dead.

    # --- Open the native window ---
    import webview

    webview.create_window(
        "DeskLedger",
        url,
        width=1280,
        height=860,
        min_size=(900, 600),
    )

    # Window icon. The bundled .exe already carries the icon (set in deskledger.spec);
    # this also sets it where the GUI backend supports it. Guarded so an
    # unsupported backend can never stop the app from launching.
    icon_path = _resource_path("static/images/deskledger.ico")
    try:
        if os.path.exists(icon_path):
            webview.start(icon=icon_path)
        else:
            webview.start()
    except TypeError:
        # Older/!supported backends don't accept the icon argument.
        webview.start()

    # Window closed — exit immediately (daemon server thread is torn down).
    os._exit(0)


if __name__ == "__main__":
    main()
