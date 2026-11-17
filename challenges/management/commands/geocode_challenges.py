import json
import time
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand
from challenges.models import Challenge


class Command(BaseCommand):
    help = "Backfills missing latitude and longitude coordinates for existing challenges via OpenStreetMap Nominatim."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Maximum number of challenges to geocode in this run.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Fetch coordinates without saving to the database.'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']

        qs = Challenge.objects.filter(
            latitude__isnull=True
        ) | Challenge.objects.filter(
            longitude__isnull=True
        )
        qs = qs.distinct()

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("All challenges already have coordinates. Nothing to backfill."))
            return

        if limit:
            challenges_to_process = list(qs[:limit])
            self.stdout.write(self.style.NOTICE(f"Found {total} challenges needing coordinates. Processing up to {limit}..."))
        else:
            challenges_to_process = list(qs)
            self.stdout.write(self.style.NOTICE(f"Found {total} challenges needing coordinates. Beginning geocoding backfill..."))

        success_count = 0
        fail_count = 0

        headers = {
            'User-Agent': 'CivicConnect-Backfill/1.0 (admin@civicconnect.org)',
            'Accept': 'application/json',
        }

        for i, ch in enumerate(challenges_to_process, 1):
            if not ch.location or not ch.location.strip():
                self.stdout.write(self.style.WARNING(f"[{i}/{len(challenges_to_process)}] Challenge #{ch.pk} '{ch.title}': No location string; skipping."))
                fail_count += 1
                continue

            query = urllib.parse.urlencode({'q': ch.location.strip(), 'format': 'json', 'limit': 1})
            url = f"https://nominatim.openstreetmap.org/search?{query}"

            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode('utf-8'))

                if data and len(data) > 0:
                    lat = float(data[0]['lat'])
                    lng = float(data[0]['lon'])
                    self.stdout.write(self.style.SUCCESS(
                        f"[{i}/{len(challenges_to_process)}] Challenge #{ch.pk} '{ch.title}': Found ({lat}, {lng})"
                    ))
                    if not dry_run:
                        ch.latitude = lat
                        ch.longitude = lng
                        ch.save(update_fields=['latitude', 'longitude'])
                    success_count += 1
                else:
                    self.stdout.write(self.style.WARNING(
                        f"[{i}/{len(challenges_to_process)}] Challenge #{ch.pk} '{ch.title}': No coordinates found for '{ch.location}'."
                    ))
                    fail_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"[{i}/{len(challenges_to_process)}] Challenge #{ch.pk} '{ch.title}': Geocoding request failed: {e}"
                ))
                fail_count += 1

            # Sleep 1 second between requests to respect Nominatim usage policy
            if i < len(challenges_to_process):
                time.sleep(1)

        summary_msg = f"Geocoding backfill finished: {success_count} geocoded, {fail_count} skipped/failed."
        if dry_run:
            summary_msg += " (DRY RUN - no changes saved)"
        self.stdout.write(self.style.SUCCESS(summary_msg))

