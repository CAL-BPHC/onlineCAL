from typing import Iterable, List, Set, Tuple

from django.core.management.base import BaseCommand, CommandError

from ...models import CustomUser


class Command(BaseCommand):
    help = (
        "Make users Portal Admins by email. Provide emails as positional args. "
        "Non-existent emails are ignored but logged."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "emails",
            nargs="*",
            help="Email addresses to make Portal Admins.",
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
            raise CommandError("No emails provided. Pass emails as arguments.")

        updated_count = 0
        missing: List[str] = []

        for email in sorted(emails):
            updated, found = self._make_portal_admin_for_email(email, dry_run)
            updated_count += updated
            if not found:
                missing.append(email)

        summary = f"Summary: to_update={len(emails)} updated={updated_count} not_found={len(missing)}"
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
        return emails

    def _make_portal_admin_for_email(
        self, email: str, dry_run: bool
    ) -> Tuple[int, bool]:
        qs = CustomUser.objects.filter(email__iexact=email)
        if not qs.exists():
            return 0, False

        updated = 0
        for user in qs:
            if dry_run:
                self.stdout.write(f"Would make Portal Admin: email={user.email}")
            else:
                if user.role != CustomUser.Role.PORTAL_ADMIN:
                    user.role = CustomUser.Role.PORTAL_ADMIN
                    user.is_staff = True
                    user.save(update_fields=["role", "is_staff"])
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated user to Portal Admin: email={user.email}"
                        )
                    )
                else:
                    self.stdout.write(
                        f"Already Portal Admin: email={user.email} (no change)"
                    )
        return updated, True
