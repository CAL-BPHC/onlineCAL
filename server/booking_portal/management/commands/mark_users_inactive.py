from pathlib import Path
from typing import Iterable, List, Set, Tuple

from django.core.management.base import BaseCommand, CommandError

from ...models import CustomUser


class Command(BaseCommand):
    help = (
        "Mark users inactive by email. Provide emails as positional args or via --file. "
        "Non-existent emails are ignored but logged."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "emails",
            nargs="*",
            help="Email addresses to mark inactive.",
        )
        parser.add_argument(
            "--file",
            dest="file",
            help="Path to a file containing one email per line.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be changed without performing updates.",
        )

    def handle(self, *args, **options):
        emails = self._collect_emails(options)
        dry_run: bool = options.get("dry_run", False)

        if not emails:
            raise CommandError(
                "No emails provided. Pass emails as arguments or use --file <path>."
            )

        inactivated_count = 0
        missing: List[str] = []

        for email in sorted(emails):
            inactivated, found = self._mark_inactive_for_email(email, dry_run)
            inactivated_count += inactivated
            if not found:
                missing.append(email)

        summary = f"Summary: to_update={len(emails)} inactivated={inactivated_count} not_found={len(missing)}"
        self.stdout.write(summary)

        if missing:
            self.stdout.write("Missing emails:")
            for email in missing:
                self.stderr.write(f" - {email}")

    @staticmethod
    def _normalize_emails(values: Iterable[str]) -> List[str]:
        out: List[str] = []
        for v in values:
            v = (v or "").strip()
            if not v:
                continue
            parts = [p.strip() for p in v.split(",") if p.strip()]
            out.extend(parts)
        return out

    def _collect_emails(self, options) -> Set[str]:
        emails: Set[str] = set()
        cli_emails: List[str] = options.get("emails") or []
        emails.update(self._normalize_emails(cli_emails))

        file_path = options.get("file")
        if file_path:
            path = Path(file_path).expanduser()
            if not path.exists():
                raise CommandError(f"File not found: {path}")
            with path.open("r", encoding="utf-8") as f:
                file_emails = [line.strip() for line in f if line.strip()]
                emails.update(self._normalize_emails(file_emails))
        return emails

    def _mark_inactive_for_email(self, email: str, dry_run: bool) -> Tuple[int, bool]:
        qs = CustomUser.objects.filter(email__iexact=email)
        if not qs.exists():
            return 0, False

        updated = 0
        for user in qs:
            if dry_run:
                self.stdout.write(f"Would mark inactive email={user.email}")
            else:
                if user.is_active:
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Marked user inactive email={user.email}")
                    )
                else:
                    self.stdout.write(
                        f"Already inactive email={user.email} (no change)"
                    )
        return updated, True
