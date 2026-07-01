# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix inconsistent migration history'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations WHERE app='accounts' AND name='0001_initial'")
            count = cursor.fetchone()[0]
            if count == 0:
                from django.utils import timezone
                now = timezone.now()
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    ['accounts', '0001_initial', now]
                )
                self.stdout.write(self.style.SUCCESS('Inserted accounts.0001_initial migration record'))
            else:
                self.stdout.write('accounts.0001_initial already exists')
