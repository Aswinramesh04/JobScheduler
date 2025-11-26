from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Deprecated: clear_data is no longer used. This command is a no-op."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("clear_data is deprecated and does nothing."))
