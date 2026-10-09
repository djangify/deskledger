# Third-party notices

DeskLedger itself is licensed under the [MIT License](LICENSE).

DeskLedger is built on the open-source components below. Each keeps its own licence,
which is **not** changed by the DeskLedger licence. The packaged `DeskLedger.exe`
ships with the full licence text of every Python package in the
`third_party_licenses` folder next to it (generated at build time by
`tools/collect_licenses.py`). If you redistribute the `.exe`, keep that folder and
this file with it.

| Component | Licence | Notes |
|---|---|---|
| [Django](https://www.djangoproject.com/) | BSD-3-Clause | |
| [django-allauth](https://allauth.org/) | MIT | |
| [Adminita](https://github.com/djangify/adminita) | MIT | Same author as DeskLedger |
| [WhiteNoise](https://whitenoise.readthedocs.io/) | MIT | |
| [waitress](https://docs.pylonsproject.org/projects/waitress/) | ZPL 2.1 | |
| [Pillow](https://python-pillow.org/) | MIT-CMU (HPND style) | |
| [cryptography](https://cryptography.io/) | Apache-2.0 OR BSD-3-Clause | |
| [django-environ](https://github.com/joke2k/django-environ) | MIT | |
| [asgiref](https://github.com/django/asgiref), [sqlparse](https://github.com/andialbrecht/sqlparse), [tzdata](https://github.com/python/tzdata), [packaging](https://github.com/pypa/packaging) | BSD / Apache-2.0 | |
| [pywebview](https://pywebview.flowrl.com/) | BSD-3-Clause | Desktop window |
| pythonnet, clr_loader, proxy_tools, bottle, cffi, pycparser, typing_extensions | MIT / BSD / PSF | pywebview and cryptography dependencies |
| [python-magic-bin](https://github.com/julian-r/python-magic) | MIT | Windows only. Bundles libmagic (below) |
| libmagic / file(1) | BSD-2-Clause | See text below |
| [PyInstaller](https://pyinstaller.org/) | GPL-2.0 with the bootloader exception | Build tool. Its exception explicitly allows bundling into an application under any licence |
| [Python](https://www.python.org/) | PSF-2.0 | Interpreter bundled in the `.exe` |
| Microsoft Edge WebView2 runtime | Microsoft licence | **Not** bundled. Uses the copy already installed on Windows 10/11 |
| [Tailwind CSS](https://tailwindcss.com/) | MIT | Used to generate `static/css/output.css` |

## libmagic (file(1)) licence

Copyright (c) Ian F. Darwin 1986, 1987, 1989, 1990, 1991, 1992, 1994, 1995.
Software written by Ian F. Darwin and others; maintained 1994- Christos Zoulas.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this
   list of conditions and the following disclaimer in the documentation and/or
   other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
