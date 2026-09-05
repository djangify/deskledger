"""
Management command: python manage.py backup_db

Creates a timestamped copy of db.sqlite3 in data/db/backups/.
Keeps the last 30 backups and removes older ones automatically.

To run it on a schedule, point Windows Task Scheduler (or cron on
macOS/Linux) at: python manage.py backup_db
"""

import shutil
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Back up the SQLite database to data/db/backups/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep",
            type=int,
            default=30,
            help="Number of backups to retain (default: 30)",
        )

    def handle(self, *args, **options):
        keep = options["keep"]

        db_path = Path(settings.DATABASES["default"]["NAME"])
        backup_dir = db_path.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        if not db_path.exists():
            self.stderr.write(self.style.ERROR(f"Database not found: {db_path}"))
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"db_backup_{timestamp}.sqlite3"

        shutil.copy2(db_path, backup_path)
        self.stdout.write(
            self.style.SUCCESS(f"Backup created: {backup_path.name}")
        )

        # Prune old backups
        backups = sorted(backup_dir.glob("db_backup_*.sqlite3"))
        if len(backups) > keep:
            to_delete = backups[: len(backups) - keep]
            for old in to_delete:
                old.unlink()
                self.stdout.write(f"Removed old backup: {old.name}")
